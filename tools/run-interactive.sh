#!/bin/bash
# Simple script to run the simulation and restart it in case it crashes.
# Later on, it will copy the user's bots to a tournament server.

while :; do
    python3 ~/seekers/src/seekers.py
    sleep 0.5
done
