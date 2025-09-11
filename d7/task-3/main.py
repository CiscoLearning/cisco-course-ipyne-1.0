"""
Network Configuration Backup Tool
A Python module for automating configuration backups with Git version control

This tool allows you to:
- Initialize Git repositories for version control
- Backup device configurations using pyATS
- Compare configurations between backups
- Track changes with automated commits
- Log all operations with rotating file handler
"""

import git
import json
import yaml
import datetime
import argparse
import os
import logging
from genie.utils.diff import Diff
from pathlib import Path
from genie.testbed import load as load_testbed
from logging.handlers import TimedRotatingFileHandler
from inventory_tool import read_inventory

# TASK 1: Git repository management

def commit_backup(backup_dir, commit_message):
    """
    Initialize Git repository if needed and commit backup files.
    
    Args:
        backup_dir (str): Directory path containing backup files to commit
        commit_message (str): Descriptive commit message for the backup operation
    """
    try:
        repo = git.Repo(backup_dir)
    except git.exc.InvalidGitRepositoryError:
        repo = git.Repo.init(backup_dir)
    except Exception as e:
        print(f"Unexpected error: {e}")
        return
    
    repo.git.add(A=True)
    repo.index.commit(commit_message)
    print("Backup committed to Git repository.")

# TASK 2: Device backup functionality

def generate_testbed(inventory_file):
    """
    Generate pyATS testbed from inventory CSV file.
    
    Args:
        inventory_file (str): Path to CSV inventory file
        
    Returns:
        dict: Testbed dictionary for pyATS
    """
    testbed = {
        "testbed": {"name": "LabTestbed"},
        "devices": {}
    }
    for dev in read_inventory(inventory_file):
        testbed["devices"][dev["Name"]] = {
            "os": "iosxe",
            "type": "router",
            "connections": {
                "cli": {
                    "protocol": "ssh",
                    "ip": dev["Management IP"],
                    "port": "22"
                }
            },
            "credentials": {
                "default": {
                    "username": dev["Username"],
                    "password": dev["Password"]
                }
            }
        }
    return testbed

def fetch_running_config(testbed, device_name):
    """
    Retrieve running configuration from specified device.
    
    Args:
        testbed: Loaded pyATS testbed object
        device_name (str): Name of device to backup
        
    Returns:
        dict: Parsed configuration data or None if error
    """
    try:
        device = testbed.devices[device_name]
        device.connect(log_stdout=False)
        config = device.parse("show running-config")
        device.disconnect()
        return config
    except Exception as e:
        print(f"Error on {device_name}: {e}")
        return None

def backup_config(testbed, backup_dir):
    """
    Backup configurations from all devices in testbed.
    
    Args:
        testbed: Loaded pyATS testbed
        backup_dir (str): Directory to store backup files
        
    Returns:
        list: List of created backup file paths
    """
    backup_dir = Path(backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_files = []
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for device_name in testbed.devices:
        print(f"Backing up {device_name}...")
        config = fetch_running_config(testbed, device_name)
        if config:
            filename = backup_dir / f"{device_name}_{timestamp}.json"
            # Save parsed configuration as JSON for Genie Diff compatibility
            config_data = {"device": device_name, "timestamp": timestamp, "config": config}
            with open(filename, 'w') as f:
                json.dump(config_data, f, indent=2)
            backup_files.append(str(filename))
            print(f"Saved: {filename}")
        else:
            print(f"Skipped {device_name}")
    
    return backup_files

# TASK 3: Configuration comparison functionality

def get_latest_backups(backup_dir, device_name):
    """
    Find the two most recent backup files for a device.
    
    Args:
        backup_dir (str): Directory containing backup files
        device_name (str): Device name to find backups for
        
    Returns:
        tuple: (latest_file, previous_file) or (None, None) if insufficient files
    """
    backup_dir = Path(backup_dir)
    backup_files = list(backup_dir.glob(f"{device_name}_*.json"))
    backup_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    if len(backup_files) < 2:
        return None, None
    
    return str(backup_files[0]), str(backup_files[1])

def compare_configs(backup_dir, device_name):
    """
    Compare the two most recent configuration backups for a device.
    
    Args:
        backup_dir (str): Directory containing backup files  
        device_name (str): Device name to compare configs for
    """
    latest_backup, previous_backup = get_latest_backups(backup_dir, device_name)
    
    if not latest_backup or not previous_backup:
        print(f"Not enough backups to compare for {device_name}")
        return
    
    with open(previous_backup, "r") as old_file, open(latest_backup, "r") as new_file:
        old_data = json.load(old_file)
        new_data = json.load(new_file)
        
        # Compare only the config field, not timestamp
        diff = Diff(old_data.get("config", {}), new_data.get("config", {}))
        diff.findDiff()
        
        if diff.diffs:
            print(f"Differences found for {device_name}:")
            print(diff.diffs)
        else:
            print(f"No configuration changes detected for {device_name}")

# TASK 4: Logging and CLI functionality

def log_and_print(message, level="info"):
    """
    Log message to file and print to console.
    
    Args:
        message (str): Message to log to file and display to user
        level (str): Log level - "info", "error", or "warning" (default: "info")
    """
    # COMPLETE THE FUNCTION LOGIC HERE
    pass

def main():
    """Main function handling CLI arguments and backup orchestration."""
    parser = argparse.ArgumentParser(description="Network Device Configuration Backup Tool")
    parser.add_argument('--inventory', default='inventory.csv', help='Path to inventory file')
    parser.add_argument('--backup-dir', default='./backups', help='Directory to store backups')
    parser.add_argument('--no-commit', action='store_true', help='Disable committing backup to Git repository')
    parser.add_argument('--no-compare', action='store_true', help='Disable configuration comparison')
    
    args = parser.parse_args()
    
    testbed = load_testbed(generate_testbed(args.inventory))
    backup_files = backup_config(testbed, args.backup_dir)
    
    if not args.no_commit and backup_files:
        commit_msg = f"Backup on {datetime.datetime.now():%Y-%m-%d %H:%M:%S}"
        commit_backup(args.backup_dir, commit_msg)

    if not args.no_compare and backup_files:
        print("\nRunning configuration comparison...")
        for device_name in testbed.devices:
            compare_configs(args.backup_dir, device_name)

if __name__ == "__main__":
    main()