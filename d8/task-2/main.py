"""
Cisco Meraki Dashboard API Client
A Python module for retrieving data from Cisco Meraki Dashboard API

This tool allows you to:
- Authenticate with Meraki Dashboard API
- Retrieve organization and network information
- Get device inventory and status
- Save data to JSON files for offline analysis
"""

import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# TASK 1: API AUTHENTICATION AND SETUP

def get_api_key():
    """
    Retrieves Meraki API key from environment variables.
    
    Returns:
        str: API key for Meraki Dashboard authentication
    """
    api_key = os.getenv('MERAKI_API_KEY')
    if not api_key:
        raise ValueError("MERAKI_API_KEY not found in environment variables")
    return api_key

def get_headers():
    """
    Creates authentication headers for Meraki API requests.
    
    Returns:
        dict: Headers dictionary with API key and content type
    """
    return {
        'X-Cisco-Meraki-API-Key': get_api_key(),
        'Content-Type': 'application/json'
    }

# TASK 2: API CLIENT AND DATA RETRIEVAL

def make_api_request(endpoint):
    """
    Makes authenticated request to Meraki API endpoint.
    
    Args:
        endpoint (str): API endpoint path
        
    Returns:
        dict or list: JSON response from API
    """
    base_url = "https://api.meraki.com/api/v1"
    url = f"{base_url}{endpoint}"
    
    try:
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except Exception as err:
        print(f"Unexpected error: {err}")
    return None

def get_organizations():
    """
    Retrieves all organizations accessible with the API key.
    
    Returns:
        list: List of organization dictionaries
    """
    endpoint = "/organizations"
    return make_api_request(endpoint) or []

def get_networks(org_id):
    """
    Retrieves all networks for a specific organization.
    
    Args:
        org_id (str): Organization ID
        
    Returns:
        list: List of network dictionaries
    """
    endpoint = f"/organizations/{org_id}/networks"
    return make_api_request(endpoint) or []

def get_network_inventory(network_id):
    """
    Retrieves device inventory for a specific network.
    
    Args:
        network_id (str): Network ID
        
    Returns:
        list: List of device dictionaries
    """
    endpoint = f"/networks/{network_id}/devices"
    return make_api_request(endpoint) or []

# TASK 3: DEVICE STATUS AND MONITORING

# COMPLETE THE CODE. Remove the ''' markers and finish the implementation.
'''
def get_device_availabilities(network_id, serial):
    """
    Retrieves availability data for a specific device.
    
    Args:
        network_id (str): Network ID
        serial (str): Device serial number
        
    Returns:
        list: List of availability data points
    """
    endpoint = f"/networks/{network_id}/devices/{serial}/clients/overview"
    return make_api_request(endpoint) or []
'''

def get_device_statuses(org_id):
    """
    Retrieve device status information for all devices in organization.
    
    Args:
        org_id (str): Organization ID
        
    Returns:
        list: List of device status dictionaries or empty list if error
    """
    # COMPLETE THE FUNCTION LOGIC HERE
    pass

def get_device_details(devices, statuses):
    """
    Combine device inventory with status information.
    
    Args:
        devices (list): Device inventory list
        statuses (list): Device status list
        
    Returns:
        list: Combined device information with status
    """
    # COMPLETE THE FUNCTION LOGIC HERE
    pass

# TASK 4: DATA PERSISTENCE AND ERROR HANDLING

# COMPLETE THE CODE. Remove the ''' markers and finish the implementation.
'''
def save_to_file(data, filename):
    """
    Saves data to a JSON file.
    
    Args:
        data: Data to save (dict or list)
        filename (str): Output filename
    """
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=2)
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving to file: {e}")
'''

def generate_network_report(org_name, network_name, devices, statuses):
    """
    Generate comprehensive network report with statistics.
    
    Args:
        org_name (str): Organization name
        network_name (str): Network name
        devices (list): Device inventory list
        statuses (list): Device status list
        
    Returns:
        dict: Comprehensive network report
    """
    # COMPLETE THE FUNCTION LOGIC HERE
    pass

def main():
    """
    Main function handling CLI arguments and orchestrating API operations.
    """
    try:
        print("Fetching Meraki organization data...")
        organizations = get_organizations()
        
        if not organizations:
            print("No organizations found or API error occurred.")
            return
        
        # Display organization information
        print(f"\nFound {len(organizations)} organization(s):")
        for org in organizations:
            print(f"  - {org['name']} (ID: {org['id']})")
        
        # Get networks for first organization
        first_org = organizations[0]
        print(f"\nFetching networks for {first_org['name']}...")
        networks = get_networks(first_org['id'])
        
        if not networks:
            print("No networks found.")
            return
        
        print(f"Found {len(networks)} network(s):")
        for net in networks:
            print(f"  - {net['name']} (ID: {net['id']})")
        
        # Get inventory for first network
        first_network = networks[0]
        print(f"\nFetching device inventory for {first_network['name']}...")
        devices = get_network_inventory(first_network['id'])
        
        if devices:
            print(f"Found {len(devices)} device(s):")
            for device in devices:
                print(f"  - {device.get('name', 'Unnamed')} ({device['model']}) - {device['serial']}")
        else:
            print("No devices found or network has no inventory.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()