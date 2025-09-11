"""
Network Device Testing Tool
A Python module for monitoring and validating device configurations using pyATS

This tool allows you to:
- Connect to devices using pyATS testbed
- Parse device information and status
- Validate OSPF neighbor relationships
- Check interface status and configurations
"""

from genie.testbed import load as load_testbed

def get_device_info(device):
    """
    Connect to device and extract OS version and uptime information.
    
    Args:
        device: pyATS device object from testbed
        
    Returns:
        None (prints device information)
    """
    # COMPLETE THE CODE: Remove the ''' markers and complete the function
    '''
    device.connect(log_stdout=False)
    output = device.parse("show version")
    os_version = output['version']['version']
    uptime = output['version']['uptime']
    print(f"OS Version: {os_version}")
    print(f"Uptime: {uptime}")
    '''
    pass

def check_ospf_neighbors(device):
    """
    Verify OSPF neighbor relationships and validate FULL state adjacencies.
    
    Args:
        device: pyATS device object from testbed
        
    Returns:
        bool: True if all neighbors are in FULL state
    """
    # COMPLETE THE FUNCTION LOGIC HERE
    pass

# TASK 3 FUNCTIONS - Complete the following functions

def check_acl(device):
    """
    Validate specific ACL configuration on the device.
    
    Args:
        device: pyATS device object from testbed
        
    Returns:
        None (prints ACL status and test result)  
    """
    # COMPLETE THE FUNCTION LOGIC HERE
    pass


if __name__ == "__main__":
    # Test area - this code only runs when script is executed directly
    # You'll implement the main functionality here in later steps
    pass