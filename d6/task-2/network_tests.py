"""
Network Device Testing Tool
A Python module for monitoring and validating device configurations using pyATS

This tool allows you to:
- Connect to devices using pyATS testbed
- Parse device information and status
- Validate OSPF neighbor relationships
- Check ACL configurations
"""

from genie.testbed import load as load_testbed

# TASK 1 FUNCTIONS - Complete the following functions

def get_device_info(device):
    """
    Connect to device and extract OS version and uptime information.
    
    Args:
        device: pyATS device object from testbed
        
    Returns:
        None (prints device information)
    """
    device.connect(log_stdout=False)
    output = device.parse("show version")
    os_version = output['version']['version']
    uptime = output['version']['uptime']
    print(f"OS Version: {os_version}")
    print(f"Uptime: {uptime}")

# TASK 2 FUNCTIONS - Complete the following functions

def check_ospf_neighbors(device):
    """
    Verify OSPF neighbor relationships and validate FULL state adjacencies.
    
    Args:
        device: pyATS device object from testbed
        
    Returns:
        None (prints neighbor status and test result)
    """
    device.connect(log_stdout=False)
    try:
        output = device.parse("show ip ospf neighbor")
    except:
        print(f"No OSPF Neighbors on {device.name}")
        return
    
    ospf_neighbors = output["interfaces"]
    test_pass = False
    
    for interface, neighbors in ospf_neighbors.items():
        for neighbor_ip, neighbor_info in neighbors["neighbors"].items():
            state = neighbor_info["state"]
            print(f"Neighbor: {neighbor_ip}, State: {state}")
            if state == "FULL/BDR" or state == "FULL/DR":
                test_pass = True
    
    if test_pass:
        print("PASS")
    else:
        print("FAIL")

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
    # Load testbed and get device
    testbed = load_testbed("testbed.yaml")
    device = testbed.devices["R1"]
    
    # Test device information extraction
    print("Testing device information extraction...")
    get_device_info(device)
    
    # Test OSPF neighbor validation
    print("\nTesting OSPF neighbor validation...")
    check_ospf_neighbors(device)