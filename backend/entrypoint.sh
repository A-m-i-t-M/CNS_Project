#!/bin/sh
python3 -u packet_sniffer.py &
uvicorn api:app --host 0.0.0.0 --port 8000
