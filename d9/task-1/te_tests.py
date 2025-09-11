"""
ThousandEyes API Test Automation
A Python module for creating and monitoring ThousandEyes network tests

This tool allows you to:
- Authenticate with ThousandEyes API using OAuth Bearer Token
- Discover available test agents automatically
- Create HTTP server and network tests programmatically  
- Monitor test results and generate performance reports
"""

import os
import time
import json
import sys
from typing import Optional, Dict, Any

import requests
from dotenv import load_dotenv

load_dotenv()

# Environment variables - update .env file with your credentials
TE_API_TOKEN = os.getenv("TE_API_TOKEN")
TEST_NAME = os.getenv("TEST_NAME")
TARGET = os.getenv("TARGET")

BASE_URL = "https://api.thousandeyes.com/v7"
HEADERS = {
    "Authorization": f"Bearer {TE_API_TOKEN}",
    "Content-Type": "application/json",
}

# TASK 1: Agent Discovery and Authentication

def get_first_agent_id() -> Optional[int]:
    """
    Retrieve the first available agent ID for test creation.
    
    This function demonstrates the standard pattern for ThousandEyes API calls
    with proper error handling and agent selection logic.
    
    Returns:
        int: First available agent ID, or None if no agents found
    """
    url = f"{BASE_URL}/agents"
    response = requests.get(url, headers=HEADERS)

    if response.ok:
        agents = response.json().get("agents", [])
        if agents:
            agent = agents[0]
            print(f"[?] Using agent: {agent['agentName']} (ID: {agent['agentId']})")
            return int(agent["agentId"])
        else:
            print("[!] No agents found in your account.")
    else:
        print(f"[!] Failed to fetch agents: {response.status_code} - {response.text}")
    return None

# TASK 2: Test Management

def find_existing_test_id(test_name: str) -> Optional[int]:
    """
    Find existing test by name to avoid duplicate creation.
    
    Args:
        test_name (str): Name of test to search for
        
    Returns:
        int: Test ID if found, None otherwise
    """
    # COMPLETE THE CODE. Remove the ''' markers and finish the implementation
    '''
    url = f"{BASE_URL}/tests/http-server"
    response = requests.get(url, headers=HEADERS)

    if response.ok:
        for test in response.json().get("tests", []):
            if test.get("testName") == test_name:
                return int(test["testId"])
    else:
        print(f"[!] Failed to retrieve tests: {response.status_code} - {response.text}")
    return None
    '''

def create_test(
    test_name: str, target: str, agent_id: int, interval: int = 3600
) -> Optional[int]:
    """
    Creates an HTTP server test in ThousandEyes.
    
    Args:
        test_name (str): Descriptive name for the new test
        target (str): Target URL to monitor for HTTP server testing
        agent_id (int): Agent ID from get_first_agent_id() to use for testing
        interval (int): Test interval in seconds (default: 3600)
        
    Returns:
        int: Created test ID, or None if failed
    """
    # COMPLETE THE CODE. Remove the ''' markers and finish the implementation
    '''
    payload = {
        "testName": test_name,
        "type": "agent-to-server",
        "url": target,
        "interval": interval,
        "protocol": "ICMP",
        "enabled": True,
        "agents": [{"agentId": agent_id}],
    }

    url = f"{BASE_URL}/tests/http-server"
    response = requests.post(url, headers=HEADERS, json=payload)

    if response.status_code == 201:
        test_id = response.json().get("testId")
        print(f"[+] Created test '{test_name}' (ID: {test_id})")
        return int(test_id)
    else:
        print(f"[!] Error creating test: {response.status_code} - {response.text}")
        return None
    '''

# TASK 3: Test Results and Analysis

def get_test_results(test_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieves results for a specific test.
    
    Args:
        test_id (int): Test ID from create_test() response
        
    Returns:
        dict: Test results data including metrics and performance data
    """
    # COMPLETE THE CODE. Remove the ''' markers and finish the implementation
    '''
    url = f"{BASE_URL}/test-results/{test_id}/http-server"
    response = requests.get(url, headers=HEADERS)

    if response.ok:
        print(f"[+] Fetched test results for test ID {test_id}")
        return response.json()
    else:
        print(
            f"[!] Failed to retrieve test results: {response.status_code} - {response.text}"
        )
        return None
    '''

def analyze_results(results: Dict[str, Any]) -> None:
    """
    Analyzes test results and provides formatted summary statistics.
    
    Args:
        results (dict): Test results dictionary from get_test_results()
    """
    # COMPLETE THE CODE. Remove the ''' markers and finish the implementation
    '''
    entries = results.get("results", [])
    if not entries:
        print("[!] No HTTP Server test results available.")
        return

    result = entries[0]
    print("\n========== HTTP SERVER TEST RESULTS ==========")
    print(f" Test Name     : {TEST_NAME}")
    print(
        f" Agent         : {result['agent']['agentName']} (ID: {result['agent']['agentId']})"
    )
    print(f" Test Date     : {result['date']}")
    print(f" Target URL    : {TARGET}")
    print("----------------------------------------------")
    print(f" Response Code : {result.get('responseCode')}")
    print(f" Response Time : {result.get('responseTime')} ms")
    print(f" Redirect Time : {result.get('redirectTime')} ms")
    print(f" DNS Time      : {result.get('dnsTime')} ms")
    print(f" SSL Time      : {result.get('sslTime')} ms")
    print(f" Connect Time  : {result.get('connectTime')} ms")
    print(f" Wait Time     : {result.get('waitTime')} ms")
    print(f" Receive Time  : {result.get('receiveTime')} ms")
    print(f" Total Time    : {result.get('totalTime')} ms")
    print(f" Throughput    : {result.get('throughput')} bytes/sec")
    print(f" Wire Size     : {result.get('wireSize')} bytes")
    print(f" Server IP     : {result.get('serverIp')}")
    print(f" SSL Cipher    : {result.get('sslCipher')}")
    print(f" SSL Version   : {result.get('sslVersion')}")
    print(f" Health Score  : {result.get('healthScore'):.4f}")
    print("==============================================\n")
    '''

# TASK 4: Report Generation

def save_report(test_name: str, results: Dict[str, Any]) -> None:
    """
    Save test results to local JSON file for analysis.
    
    Args:
        test_name (str): Name of test for filename generation
        results (dict): Test results data to save as JSON
    """
    # COMPLETE THE CODE. Remove the ''' markers and finish the implementation
    '''
    filename = f"{test_name}_report.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[?] Report saved to: {filename}")
    '''

if __name__ == "__main__":
    print("[*] Starting ThousandEyes test automation...")

    agent_id = get_first_agent_id()
    if agent_id is None:
        sys.exit("[!] No valid agent available. Exiting.")
    else:
        print(f"[+] Successfully discovered agent ID: {agent_id}")