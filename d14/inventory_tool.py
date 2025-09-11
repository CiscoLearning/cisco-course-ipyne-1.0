"""
Network Device Inventory Management Tool
A Python module for managing network device inventory data

This tool allows you to:
- Read device inventory from CSV files
- Manage device data programmatically  
- Convert data between different formats
- Query device information
"""

import csv
import json
import yaml
import argparse
from pathlib import Path

def read_inventory(filename):
    """
    Read device inventory from CSV file.
    
    Args:
        filename (str): Path to CSV inventory file
        
    Returns:
        list: List of device dictionaries with inventory data
    """
    devices = []
    try:
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                devices.append(row)
    except FileNotFoundError:
        print(f"Error: Inventory file {filename} not found")
    except Exception as e:
        print(f"Error reading inventory: {e}")
    
    return devices

def get_device_data(inventory_data, device_name):
    """
    Get device data from inventory by device name.
    
    Args:
        inventory_data (list): List of device dictionaries
        device_name (str): Name of device to retrieve
        
    Returns:
        dict: Device data dictionary or None if not found
    """
    for device in inventory_data:
        if device.get('Name') == device_name:
            return device
    return None

def write_json(data, filename):
    """
    Write device data to JSON file.
    
    Args:
        data (list): List of device dictionaries
        filename (str): Output JSON filename
    """
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=2)
        print(f"Data written to {filename}")
    except Exception as e:
        print(f"Error writing JSON: {e}")

def write_yaml(data, filename):
    """
    Write device data to YAML file.
    
    Args:
        data (list): List of device dictionaries
        filename (str): Output YAML filename
    """
    try:
        with open(filename, 'w') as file:
            yaml.dump(data, file, default_flow_style=False)
        print(f"Data written to {filename}")
    except Exception as e:
        print(f"Error writing YAML: {e}")

def main():
    """Main function handling CLI arguments and inventory operations."""
    parser = argparse.ArgumentParser(description="Network Device Inventory Management Tool")
    parser.add_argument('action', choices=['list', 'add', 'export'], help='Action to perform')
    parser.add_argument('--name', help='Device name for add action')
    parser.add_argument('--ip', help='Management IP for add action')
    parser.add_argument('--user', help='Username for add action')
    parser.add_argument('--password', help='Password for add action')
    parser.add_argument('--desc', help='Description for add action')
    parser.add_argument('--format', choices=['json', 'yaml'], help='Export format')
    parser.add_argument('--output', help='Output filename for export')
    parser.add_argument('--inventory', default='inventory.csv', help='Inventory file')
    
    args = parser.parse_args()
    
    if args.action == 'list':
        devices = read_inventory(args.inventory)
        print(f"Found {len(devices)} devices:")
        for device in devices:
            print(f"  {device['Name']} ({device['Management IP']}) - {device['Description']}")
    
    elif args.action == 'export':
        devices = read_inventory(args.inventory)
        if devices:
            if args.format == 'json':
                filename = args.output or 'inventory.json'
                write_json(devices, filename)
            elif args.format == 'yaml':
                filename = args.output or 'inventory.yaml'
                write_yaml(devices, filename)

if __name__ == "__main__":
    main()