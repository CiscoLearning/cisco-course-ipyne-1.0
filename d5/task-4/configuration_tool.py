"""
Network Device Configuration Tool
A Python module for automating network device configuration using Netmiko

This tool allows you to:
- Connect to network devices using Netmiko
- Send configuration commands
- Apply configuration templates
- Manage device configurations programmatically
"""

# Imports for device connectivity and inventory management
from inventory_tool import read_inventory, get_device_data
from netmiko import ConnectHandler
from jinja2 import Template
import click

# TASK 1: DEVICE CONNECTIVITY FUNCTIONS

def get_conn_info(dev_data):
    """
    Converts inventory device data into Netmiko connection parameters.
    
    Args:
        dev_data (dict): Device data from inventory, expected to have keys
                        'Management IP', 'Username', and 'Password'.
        
    Returns:
        dict: Connection parameters formatted for Netmiko ConnectHandler
    """
    return {
        "device_type": "cisco_ios",
        "host": dev_data["Management IP"],
        "username": dev_data["Username"],
        "password": dev_data["Password"],
        "secret": dev_data["Password"],
    }

def connect_device(device):
    """
    Establishes connection to a network device using Netmiko.
    
    Args:
        device (dict): Connection parameters dictionary from get_conn_info(),
                      containing device_type, host, username, password, and secret.
        
    Returns:
        ConnectHandler or None: Netmiko connection object ready for sending commands,
                               or None if connection fails.
    """
    try:
        conn = ConnectHandler(**device)
        conn.enable()
        return conn
    except Exception as e:
        print(f"Error connecting to device {device.get('host')}: {e}")
        return None

def send_command(connection, command):
    """
    Sends a show command to device and returns output.
    
    Args:
        connection: Netmiko ConnectHandler object from connect_device()
        command (str): Show command to execute (e.g., 'show version', 'show ip route')
        
    Returns:
        str: Command output from device, or error message if no connection available
    """
    if connection:
        return connection.send_command(command)
    return "No connection available"


# TASK 2: CONFIGURATION FUNCTIONS

def send_config(device, commands):
    """
    Sends configuration commands to a network device.
    
    Args:
        device (dict): Connection parameters for the device from get_conn_info()
        commands (list): List of configuration command strings to execute
        
    Returns:
        str: Configuration output from device, or error message if failed
    """
    conn = connect_device(device)
    if not conn:
        return "Connection failed; configuration not sent."
    
    try:
        output = conn.send_config_set(commands)
    except Exception as e:
        output = f"Error sending configuration: {e}"
    finally:
        conn.disconnect()
    
    return output

def render_interface_config(action, interface, ip_address, subnet_mask):
    """
    Generates interface configuration using Jinja2 template.
    
    Args:
        interface_name (str): Interface name (e.g., 'GigabitEthernet0/1')
        ip_address (str): IP address to configure
        subnet_mask (str): Subnet mask for the interface
        
    Returns:
        str: Rendered configuration commands as string
    """
    if action == "create":
        config_vars = {
            "interface": interface,
            "ip_address": ip_address,
            "subnet": subnet_mask
        }
        template_string = """
interface {{ interface }}
ip address {{ ip_address }} {{ subnet }}
no shutdown
"""
    else:  # delete action
        config_vars = {"interface": interface}
        template_string = """
interface {{ interface }}
no ip address
shutdown
"""
    
    # Render template and convert to command list
    rendered_config = Template(template_string).render(**config_vars)
    commands = [line.strip() for line in rendered_config.splitlines() if line.strip()]
    return commands


# TASK 3: Interface Status Functions

def get_interface_brief(device):
    """
    Retrieves interface brief information from device.
    
    Args:
        connection: Netmiko ConnectHandler object from connect_device()
        
    Returns:
        str: Interface brief output from 'show ip interface brief' command
    """
    conn = connect_device(device)
    if not conn:
        return "Connection failed; cannot retrieve interface brief."
    
    try:
        output = conn.send_command("show ip interface brief")
    except Exception as e:
        output = f"Error retrieving interface brief: {e}"
    finally:
        conn.disconnect()
    
    return output



# TASK 4: CLI INTERFACE FUNCTIONS

@click.command()
@click.argument('device_name')
@click.option('--command', help='Command to send to device')
@click.option('--config', help='Configuration commands (comma-separated)')
def cli_main(device_name, command, config):
    """
    Command-line interface for device configuration tool.
    
    Args:
        device_name (str): Name of device from inventory
        command (str): Show command to execute
        config (str): Configuration commands to send
    """
    try:
        # Load inventory and get device data
        inventory = read_inventory("inventory.csv")
        device_data = get_device_data(inventory, device_name)
        
        if not device_data:
            click.echo(f"Device {device_name} not found in inventory")
            return
            
        # Get connection info
        conn_info = get_conn_info(device_data)
        
        # Handle command or configuration
        if command:
            # For commands, establish connection for interactive use
            connection = connect_device(conn_info)
            if not connection:
                click.echo(f"Failed to connect to {device_name}")
                return
            output = send_command(connection, command)
            click.echo(f"Output from {device_name}:")
            click.echo(output)
            connection.disconnect()
        elif config:
            # For configuration, let send_config handle connection management
            config_commands = config.split(',')
            output = send_config(conn_info, config_commands)
            click.echo(f"Configuration output from {device_name}:")
            click.echo(output)
        else:
            click.echo("Please specify --command or --config option")
            
    except Exception as e:
        click.echo(f"Error: {e}")

def main():
    """Test the interface status display functionality."""
    try:
        # Load inventory data
        inventory_data = read_inventory("inventory.csv")
        print(f"Loaded {len(inventory_data)} devices from inventory")
        R1_data = get_device_data(inventory_data, "R1")
        
        if R1_data:
            conn_info = get_conn_info(R1_data)
            
            # Get raw interface information
            brief = get_interface_brief(conn_info)
            print("Raw Interface Brief Output:")
            print(brief)
            print()
            
            # Parse and display formatted interface information
            print("Formatted Interface Status:")
            for line in brief.splitlines()[1:]:  # Skip header line
                parts = line.split()
                if len(parts) >= 5:
                    interface = parts[0]
                    ip_address = parts[1]
                    status = parts[4]
                    print(f"Interface {interface}: IP: {ip_address}, Status: {status}")
        else:
            print("Device R1 not found in inventory")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Interactive CLI interface
    cli_main()