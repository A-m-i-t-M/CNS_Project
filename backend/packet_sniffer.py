from scapy.all import sniff, IP, TCP, UDP
import logging
import json
from collections import defaultdict
import time
from datetime import datetime
from scapy.layers.http import HTTPRequest
from scapy.layers.dns import DNS

ip_rate_limit = defaultdict(list)  # Tracks timestamps of packets per IP
RATE_LIMIT = 10  # Max packets allowed per IP within the time window
TIME_WINDOW = 10  # Time window in seconds

# Set up logging
logging.basicConfig(filename="logs/packet_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# Load rules from a JSON file
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

def add_rule(new_rule):
    rules.append(new_rule)
    save_rules(rules)

def is_rate_limited(ip):
    """
    Check if an IP exceeds the rate limit.
    """
    now = time.time()
    ip_rate_limit[ip] = [t for t in ip_rate_limit[ip] if now - t <= TIME_WINDOW]  # Clean up old timestamps
    if len(ip_rate_limit[ip]) >= RATE_LIMIT:
        return True
    ip_rate_limit[ip].append(now)
    return False

def extract_metadata(packet):
    metadata = {}
    if IP in packet:
        metadata["src_ip"] = packet[IP].src
        metadata["dst_ip"] = packet[IP].dst
        metadata["protocol"] = "HTTP" if packet.haslayer(HTTPRequest) else \
                               "DNS" if packet.haslayer(DNS) else \
                               "TCP" if TCP in packet else \
                               "UDP" if UDP in packet else "OTHER"
        metadata["size"] = len(packet)
    return metadata


def is_within_time_range(start, end):
    """
    Check if the current time is within the specified range.
    """
    now = datetime.now().time()
    start_time = datetime.strptime(start, "%H:%M").time()
    end_time = datetime.strptime(end, "%H:%M").time()
    return start_time <= now <= end_time

def match_packet(metadata, rules):
    for rule in rules:
        if rule.get("start_time") and rule.get("end_time"):
            if not is_within_time_range(rule["start_time"], rule["end_time"]):
                continue

def process_packet(packet):
    metadata = extract_metadata(packet)
    if metadata:
        if is_rate_limited(metadata["src_ip"]):
            log_message = f"Action: block (rate-limited) | Packet: {metadata}"
            logging.info(log_message)
            print(f"Rate-limited: {metadata}")
            return

        action = match_packet(metadata, rules)
        log_message = f"Action: {action} | Packet: {metadata}"
        logging.info(log_message)
        if action == "block":
            print(f"Blocked: {metadata}")
        else:
            print(f"Allowed: {metadata}")


while True:
    command = input("Enter 'add' to add a rule or 'exit' to quit: ")
    if command == "add":
        src_ip = input("Enter source IP: ")
        protocol = input("Enter protocol (TCP/UDP): ")
        action = input("Enter action (allow/block): ")
        size_min = int(input("Enter minimum size: "))
        size_max = int(input("Enter maximum size: "))
        new_rule = {
            "action": action,
            "src_ip": src_ip,
            "protocol": protocol,
            "size_min": size_min,
            "size_max": size_max
        }
        add_rule(new_rule)
        print(f"Rule added: {new_rule}")
    elif command == "exit":
        break

print("Starting packet capture with filtering. Press Ctrl+C to stop.")
sniff(prn=process_packet)
