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

def get_device_availabilities(network_id, serial):
    """
    Retrieves availability data for a specific device.
    
    Args:
        network_id (str): Network ID
        serial (str): Device serial number
        
    Returns:
        list: List of availability data points
    """
    endpoint = f"/networks/{network_id}/devices/{serial}/availabilities"
    return make_api_request(endpoint) or []

def get_device_statuses(org_id):
    """
    Retrieve device status information for all devices in organization.
    
    Args:
        org_id (str): Organization ID
        
    Returns:
        list: List of device status dictionaries or empty list if error
    """
    endpoint = f"/organizations/{org_id}/devices/statuses"
    return make_api_request(endpoint) or []

def get_device_details(devices, statuses):
    """
    Combine device inventory with status information.
    
    Args:
        devices (list): Device inventory list
        statuses (list): Device status list
        
    Returns:
        list: Combined device information with status
    """
    # Create a status lookup dictionary by serial number
    status_lookup = {s['serial']: s['status'] for s in statuses if 'serial' in s}
    
    # Add status to each device
    detailed_devices = []
    for device in devices:
        device_info = device.copy()
        device_info['status'] = status_lookup.get(device['serial'], 'unknown')
        detailed_devices.append(device_info)
    
    return detailed_devices

# TASK 4: DATA PERSISTENCE AND ERROR HANDLING

def save_to_file(data, filename):
    """
    Saves data to a JSON file.
    
    Args:
        data: Data to save (dict or list)
        filename (str): Output filename
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Data saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving to {filename}: {e}")
        return False

def generate_network_report(org_name, network_name, devices, statuses):
    """
    Generate a comprehensive network report.
    
    Args:
        org_name (str): Organization name
        network_name (str): Network name
        devices (list): Device inventory
        statuses (list): Device statuses
        
    Returns:
        dict: Complete network report
    """
    # Combine devices with status
    detailed_devices = get_device_details(devices, statuses)
    
    # Calculate statistics
    total_devices = len(detailed_devices)
    online_devices = sum(1 for d in detailed_devices if d['status'] == 'online')
    offline_devices = sum(1 for d in detailed_devices if d['status'] == 'offline')
    
    # Build report structure
    report = {
        'timestamp': datetime.now().isoformat(),
        'organization': org_name,
        'network': network_name,
        'summary': {
            'total_devices': total_devices,
            'online_devices': online_devices,
            'offline_devices': offline_devices,
            'availability_percentage': round((online_devices / total_devices * 100), 2) if total_devices > 0 else 0
        },
        'devices': detailed_devices
    }
    
    return report

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
        
        # Save organizations data
        save_to_file(organizations, "organizations.json")
        
        # Get first organization
        first_org = organizations[0]
        print(f"Organization: {first_org['name']}")
        
        # Get networks
        networks = get_networks(first_org['id'])
        if not networks:
            print("No networks found.")
            return
        
        # Save networks data
        save_to_file(networks, "networks.json")
        
        # Get first network
        first_network = networks[0]
        print(f"Network: {first_network['name']}")
        
        # Get inventory
        devices = get_network_inventory(first_network['id'])
        print(f"Devices: {len(devices)} found")
        
        # Save inventory data
        save_to_file(devices, "devices.json")
        
        # Get device statuses
        print("\nFetching device status information...")
        statuses = get_device_statuses(first_org['id'])
        
        if statuses:
            # Generate and save comprehensive report
            print("\nGenerating network report...")
            report = generate_network_report(
                first_org['name'],
                first_network['name'],
                devices,
                statuses
            )
            
            # Save complete report
            save_to_file(report, "network_report.json")
            
            # Display summary
            print("\nNetwork Report Summary:")
            print(f"  Organization: {report['organization']}")
            print(f"  Network: {report['network']}")
            print(f"  Total Devices: {report['summary']['total_devices']}")
            print(f"  Online: {report['summary']['online_devices']}")
            print(f"  Offline: {report['summary']['offline_devices']}")
            print(f"  Availability: {report['summary']['availability_percentage']}%")
        else:
            print("Unable to retrieve device status information.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()