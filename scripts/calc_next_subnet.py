#!/usr/bin/env python3

import sys
import ipaddress
import csv
import subprocess
import json

# -----------------------------------------------
# INPUTS
# -----------------------------------------------
if len(sys.argv) < 4:
    print("Usage: calc_next_subnet.py <block> <size> <subnet_csv> <project> <region>")
    sys.exit(1)

block_cidr = sys.argv[1]              # Example: 192.168.48.0/20
req_size = int(sys.argv[2])           # Example: 24
csv_file = sys.argv[3]                # Subnet.csv path
project = sys.argv[4]                 # GCP project ID
region = sys.argv[5]                  # GCP region

block = ipaddress.ip_network(block_cidr)

# -----------------------------------------------
# Step 1 — Read existing subnets from CSV
# -----------------------------------------------
used_cidrs = set()

try:
    with open(csv_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                used_cidrs.add(str(ipaddress.ip_network(row["SubnetCIDR"])))
            except:
                pass
except FileNotFoundError:
    # CSV empty or missing – skip
    pass

# -----------------------------------------------
# Step 2 — Fetch used subnets from GCP
# -----------------------------------------------
def get_gcp_subnets(project, region):
    try:
        cmd = [
            "gcloud", "compute", "subnetworks", "list",
            f"--project={project}",
            f"--regions={region}",
            "--format=json"
        ]
        output = subprocess.check_output(cmd).decode()
        data = json.loads(output)
        cidrs = [item["ipCidrRange"] for item in data]
        return set(cidrs)
    except:
        return set()

gcp_used_cidrs = get_gcp_subnets(project, region)

# Combine CSV + GCP CIDRs
all_used = used_cidrs.union(gcp_used_cidrs)

# -----------------------------------------------
# Step 3 — Generate subnets from block and pick next free
# -----------------------------------------------
all_subnets = list(block.subnets(new_prefix=req_size))

for sn in all_subnets:
    if str(sn) not in all_used:
        print(sn)
        sys.exit(0)

# -----------------------------------------------
# NO AVAILABLE SUBNET
# -----------------------------------------------
print("NO_AVAILABLE_SUBNET")
sys.exit(0)
