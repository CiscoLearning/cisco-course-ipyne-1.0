"""
Device Inventory Tool
A Python module for managing network device inventories

This tool allows you to:
- Read device information from CSV files
- Format inventory data as JSON or YAML
- Add and remove devices from the inventory
- Use as a command-line tool or import as a module
"""

import csv
import json
import yaml  # PyYAML library for YAML formatting
import argparse  # For command-line argument parsing
import sys

# TASK 1 FUNCTIONS - Completed

def read_inventory(filename):
    """
    Reads device inventory from a CSV file and returns structured data.
    
    Args:
        filename (str): Path to the CSV inventory file
        
    Returns:
        list: List of dictionaries, each representing a device
    """
    inventory_data_list = []
    with open(filename, "r") as file:
        for row in csv.DictReader(file):
            inventory_data_list.append(row)
            
    return inventory_data_list

def get_device_data(inventory, device_name):
    """
    Retrieves the data for a specific device from an inventory list.

    This function iterates through a list of device dictionaries and returns
    the dictionary corresponding to the device with the matching name.

    Args:
        inventory (list): A list of dictionaries, where each dictionary
                          represents a device and is expected to have a "Name" key.
        device_name (str): The name of the device to search for within the inventory.

    Returns:
        dict or None: The dictionary containing the device's data if found,
                      otherwise None.
    """
    for device in inventory:
        if device["Name"] == device_name:
            return device
    return None


# TASK 2 FUNCTIONS - Formatting functions (completed)

def format_inventory_json(inventory_data):
    """
    Converts inventory data to formatted JSON string.
    
    Args:
        inventory_data (list): List of device dictionaries
        
    Returns:
        str: JSON formatted string with proper indentation
    """
    inventory_json = json.dumps(inventory_data, indent=4)
    return inventory_json

def format_inventory_yaml(inventory_data):
    """
    Converts inventory data to formatted YAML string.
    
    Args:
        inventory_data (list): List of device dictionaries
        
    Returns:
        str: YAML formatted string with proper indentation
    """
    inventory_yaml = yaml.dump(inventory_data, indent=4)
    return inventory_yaml


# TASK 3 FUNCTIONS - Device management functions (completed)

def add_device(inventory, new_device):
    """
    Adds a new device to the inventory list.
    
    Args:
        inventory (list): The current list of devices
        new_device (dict): Dictionary containing the new device details
    """
    inventory.append(new_device)

def save_inventory(filename, inventory):
    """
    Saves the inventory list back to a CSV file.
    
    Args:
        filename (str): The CSV file path to save to
        inventory (list): The inventory data to save
    """
    fieldnames = ["Name", "Management IP", "Username", "Password", "Description"]
    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(inventory)

def setup_cli():
    """
    Sets up the command-line interface for the inventory tool.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(description="Manage network device inventory")
    subparsers = parser.add_subparsers(dest="command")
    
    # Add subcommand for adding devices
    add_parser = subparsers.add_parser("add", help="Add a new device")
    add_parser.add_argument("--name", required=True, help="Device name")
    add_parser.add_argument("--ip", required=True, help="Management IP address")
    add_parser.add_argument("--user", required=True, help="Username")
    add_parser.add_argument("--password", required=True, help="Password")
    add_parser.add_argument("--desc", required=True, help="Device description")
    
    return parser


if __name__ == "__main__":
    # Load inventory data
    inventory_data = read_inventory("inventory.csv")
    
    # Set up command-line interface
    parser = setup_cli()
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle no command provided
    if args.command is None:
        print(inventory_data)
        sys.exit(0)
    
    # Handle the "add" command
    if args.command == "add":
        # Create new device dictionary from arguments
        new_device = {
            "Name": args.name,
            "Management IP": args.ip,
            "Username": args.user,
            "Password": args.password,
            "Description": args.desc
        }
        
        # Add device to inventory
        add_device(inventory_data, new_device)
        
        # Save updated inventory
        save_inventory("inventory.csv", inventory_data)
        
        # Print success message
        print(f"Device '{args.name}' added and saved!")