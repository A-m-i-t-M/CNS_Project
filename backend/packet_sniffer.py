from scapy.all import sniff, IP, TCP, UDP, get_if_list, Raw
import logging
import json
from collections import defaultdict
import time
from datetime import datetime
from scapy.layers.http import HTTPRequest, HTTP
import re
import threading
import time
import subprocess

ip_rate_limit = defaultdict(list)
RATE_LIMIT = 10
TIME_WINDOW = 10

logging.basicConfig(filename="logs/packet_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

def block_ip(ip):
    try:
        subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"])
        logging.info(f"Blocked IP: {ip}")
    except Exception as e:
        logging.error(f"Failed to block IP {ip}: {e}")

def load_rules():
    try:
        with open("logs/rules.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_rules(rules):
    with open("logs/rules.json", "w") as file:
        json.dump(rules, file, indent=4)

rules = load_rules()

def extract_http_info(packet):
    """
    Extract HTTP request information from the packet
    """
    if packet.haslayer(HTTPRequest):
        http_layer = packet[HTTPRequest]
        return {
            "method": http_layer.Method.decode() if http_layer.Method else None,
            "path": http_layer.Path.decode() if http_layer.Path else None,
            "headers": {
                "Host": http_layer.Host.decode() if http_layer.Host else None,
                "User-Agent": http_layer.User_Agent.decode() if http_layer.User_Agent else None
            }
        }
    elif TCP in packet and packet[TCP].dport == 4000:
        # Try to parse raw TCP data as HTTP
        if Raw in packet:
            payload = packet[Raw].load.decode('utf-8', errors='ignore')
            if payload.startswith('GET') or payload.startswith('POST'):
                # Extract method and path using regex
                match = re.match(r'(GET|POST|PUT|DELETE) (.*?) HTTP', payload)
                if match:
                    return {
                        "method": match.group(1),
                        "path": match.group(2),
                        "raw_payload": payload
                    }
    return None

def extract_metadata(packet):
    metadata = {}
    if IP in packet:
        metadata["src_ip"] = packet[IP].src
        metadata["dst_ip"] = packet[IP].dst
        metadata["protocol"] = "HTTP" if packet.haslayer(HTTPRequest) else \
                               "TCP" if TCP in packet else \
                               "UDP" if UDP in packet else "OTHER"
        metadata["size"] = len(packet)
        
    if TCP in packet or UDP in packet:
        metadata["src_port"] = packet[TCP].sport if TCP in packet else packet[UDP].sport
        metadata["dst_port"] = packet[TCP].dport if TCP in packet else packet[UDP].dport
            
        # If it's traffic to/from port 4000, try to extract HTTP info
        if metadata["src_port"] == 4000 or metadata["dst_port"] == 4000:
            http_info = extract_http_info(packet)
            if http_info:
                metadata["http_info"] = http_info
            print("Captured packet:", metadata)

    return metadata


def block_packet(metadata):
    """
    Function to block packets at the OS level using iptables.
    """
    src_ip = metadata.get("src_ip")
    dst_ip = metadata.get("dst_ip")
    src_port = metadata.get("src_port")
    dst_port = metadata.get("dst_port")

    # Example: Add iptables rule to block source IP
    if src_ip:
        try:
            # Block the source IP
            subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", src_ip, "-j", "DROP"], check=True)
            logging.info(f"Blocked packet from {src_ip}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error while blocking {src_ip}: {e}")
    
    # Example: Add iptables rule to block destination port
    if dst_port == 4000:
        try:
            # Block destination port
            subprocess.run(["sudo", "iptables", "-A", "INPUT", "-p", "tcp", "--dport", str(dst_port), "-j", "DROP"], check=True)
            logging.info(f"Blocked packet on port {dst_port}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error while blocking port {dst_port}: {e}")


def process_packet(packet):
    try:
        metadata = extract_metadata(packet)
        if metadata:
            if is_rate_limited(metadata.get("src_ip", "")):
                log_message = f"Action: block (rate-limited) | Packet: {metadata}"
                logging.info(log_message)
                return

            action = match_packet(metadata, rules)
            log_message = f"Action: {action} | Packet: {metadata}"
            logging.info(log_message)

            if action == "block":
                block_packet(metadata)
                return None
    except Exception as e:
        print(f"Error in process_packet: {e}")

# Rest of your functions remain the same
def is_rate_limited(ip):
    now = time.time()
    ip_rate_limit[ip] = [t for t in ip_rate_limit[ip] if now - t <= TIME_WINDOW]
    if len(ip_rate_limit[ip]) >= RATE_LIMIT:
        return True
    ip_rate_limit[ip].append(now)
    return False

def filter_by_port(metadata, rules):
    for rule in rules:
        if "port" in rule and "action" in rule:
            if rule["port"] == str(metadata.get("src_port")) or rule["port"] == str(metadata.get("dst_port")):
                print(f"{rule['action']} at port : {rule['port']}")
                return rule["action"]  
    return "allow"

def is_within_time_range(start, end):
    now = datetime.now().time()
    start_time = datetime.strptime(start, "%H:%M").time()
    end_time = datetime.strptime(end, "%H:%M").time()
    return start_time <= now <= end_time

def filter_by_ip(metadata, rules):
    """
    Check if the packet's metadata matches any IP-based rule.
    """
    for rule in rules:
        if "src_ip" in rule and "action" in rule:
            if rule["src_ip"] == metadata.get("src_ip"):
                print(f"{rule['action']} from ip: {rule['src_ip']}")
                return rule["action"]
    return "allow"

def match_packet(metadata, rules):
    for rule in rules:
        if rule.get("start_time") and rule.get("end_time"):
            if not is_within_time_range(rule["start_time"], rule["end_time"]):
                continue

        action = filter_by_ip(metadata, rules)
        if action != "allow":
            return action

        action = filter_by_port(metadata, rules)
        if action != "allow":
            return action
    return "allow"

def sniff_interface(iface):
    """
    Function to sniff on a single interface
    """
    print(f"Starting sniff on interface: {iface}")
    try:
        sniff(iface=iface, prn=process_packet, store=0)
    except Exception as e:
        print(f"Error on interface {iface}: {str(e)}")

# Get list of all interfaces
ifaces = get_if_list()

# Create and start a thread for each interface
threads = []
for iface in ifaces:
    thread = threading.Thread(target=sniff_interface, args=(iface,))
    thread.daemon = True  # Set as daemon so threads terminate when main program exits
    thread.start()
    threads.append(thread)
    print(f"Started thread for interface: {iface}")

# Keep the main thread running
try:
    while True:
        time.sleep(1)  # Sleep to prevent high CPU usage
except KeyboardInterrupt:
    print("\nStopping packet capture...")