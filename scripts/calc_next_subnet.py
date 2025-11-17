#!/usr/bin/env python3
import sys
import ipaddress
import csv

def error_and_exit(msg):
    print(msg)
    sys.exit(1)

def load_existing_subnets(csv_path, block):
    used = []
    try:
        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cidr = row.get("SubnetCIDR") or row.get("SubnetCidr") or row.get("cidr")
                if not cidr:
                    continue
                try:
                    subnet = ipaddress.ip_network(cidr, strict=False)
                    if subnet.subnet_of(block):
                        used.append(subnet)
                except:
                    continue
    except FileNotFoundError:
        error_and_exit("CSV_NOT_FOUND")
    return used

def calculate_free_subnet(block_str, subnet_size, csv_path):
    try:
        block = ipaddress.ip_network(block_str, strict=False)
    except:
        error_and_exit("INVALID_BLOCK")

    try:
        new_prefix = int(subnet_size)
        if new_prefix < block.prefixlen or new_prefix > 30:
            error_and_exit("INVALID_SUBNET_SIZE")
    except:
        error_and_exit("INVALID_SUBNET_SIZE")

    used_subnets = load_existing_subnets(csv_path, block)
    all_subnets = list(block.subnets(new_prefix=new_prefix))
    free_subnets = [s for s in all_subnets if s not in used_subnets]

    if not free_subnets:
        print("NO_AVAILABLE_SUBNET")
        return

    print(str(free_subnets[0]))

def main():
    if len(sys.argv) != 4:
        error_and_exit("USAGE: calc_next_subnet.py <block> <subnet_size> <csv_path>")
    block, size, csv_path = sys.argv[1], sys.argv[2], sys.argv[3]
    calculate_free_subnet(block, size, csv_path)

if __name__ == "__main__":
    main()
