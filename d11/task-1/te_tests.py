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
import logging  # Add this import for structured logging
from typing import Optional, Dict, Any
from datetime import datetime  # Add this for timestamp generation

import requests
from dotenv import load_dotenv

load_dotenv()

# Configure logging with both console and file output
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"thousandeyes_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("ThousandEyes")

# Environment variables - update .env file with your credentials
TE_API_TOKEN = os.getenv("TE_API_TOKEN")
TEST_NAME = os.getenv("TEST_NAME")
TARGET = os.getenv("TARGET")

BASE_URL = "https://api.thousandeyes.com/v7"
HEADERS = {
    "Authorization": f"Bearer {TE_API_TOKEN}",
    "Content-Type": "application/json",
}

# TASK 1: Add Structured Logging

def get_first_agent_id() -> Optional[int]:
    """
    Retrieve the first available agent ID for test creation.
    
    This function demonstrates the standard pattern for ThousandEyes API calls
    with proper error handling and agent selection logic.
    
    Returns:
        int: First available agent ID, or None if no agents found
    """
    logger.info("Attempting to fetch the first agent ID.")
    url = f"{BASE_URL}/agents"
    response = requests.get(url, headers=HEADERS)

    if response.ok:
        agents = response.json().get("agents", [])
        if agents:
            agent = agents[0]
            logger.info(
                f"Successfully fetched agent: {agent['agentName']} (ID: {agent['agentId']})"
            )
            return int(agent["agentId"])
        else:
            logger.warning("No agents found in your account.")
    else:
        logger.error(
            f"Failed to fetch agents: {response.status_code} - {response.text}"
        )
    return None

def find_existing_test_id(test_name: str) -> Optional[int]:
    """
    Find existing test by name to avoid duplicate creation.
    
    Args:
        test_name (str): Name of test to search for
        
    Returns:
        int: Test ID if found, None otherwise
    """
    logger.info(f"Attempting to find existing test with name: '{test_name}'")
    url = f"{BASE_URL}/tests/http-server"
    response = requests.get(url, headers=HEADERS)

    if response.ok:
        for test in response.json().get("tests", []):
            if test.get("testName") == test_name:
                logger.info(f"Found existing test ID: {test['testId']}")
                return int(test["testId"])
        logger.info(f"No existing test named '{test_name}' found.")
    else:
        logger.error(f"Failed to retrieve tests: {response.status_code} - {response.text}")
    return None

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
    logger.info(f"Attempting to create a new test: '{test_name}'")
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
        logger.info(f"Successfully created test '{test_name}' (ID: {test_id})")
        return int(test_id)
    else:
        logger.error(f"Error creating test: {response.status_code} - {response.text}")
        return None

def get_test_results(test_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieves results for a specific test.
    
    Args:
        test_id (int): Test ID from create_test() response
        
    Returns:
        dict: Test results data including metrics and performance data
    """
    logger.info(f"Attempting to fetch test results for test ID: {test_id}")
    url = f"{BASE_URL}/test-results/{test_id}/http-server"
    response = requests.get(url, headers=HEADERS)

    if response.ok:
        logger.info(f"Successfully fetched test results for test ID {test_id}")
        return response.json()
    else:
        logger.error(
            f"Failed to retrieve test results: {response.status_code} - {response.text}"
        )
        return None

def analyze_results(results: Dict[str, Any]) -> None:
    """
    Analyzes test results and provides formatted summary statistics.
    
    Args:
        results (dict): Test results dictionary from get_test_results()
    """
    logger.info("Analyzing test results.")
    entries = results.get("results", [])
    if not entries:
        logger.warning("No HTTP Server test results available for analysis.")
        return

    result = entries[0]
    # Consolidate multiple print statements into a single formatted log entry
    output = f"""
========== HTTP SERVER TEST RESULTS ==========
Test Name     : {TEST_NAME}
Agent         : {result['agent']['agentName']} (ID: {result['agent']['agentId']})
Test Date     : {result['date']}
Target URL    : {TARGET}
----------------------------------------------
Response Code : {result.get('responseCode')}
Response Time : {result.get('responseTime')} ms
Redirect Time : {result.get('redirectTime')} ms
DNS Time      : {result.get('dnsTime')} ms
SSL Time      : {result.get('sslTime')} ms
Connect Time  : {result.get('connectTime')} ms
Wait Time     : {result.get('waitTime')} ms
Receive Time  : {result.get('receiveTime')} ms
Total Time    : {result.get('totalTime')} ms
Throughput    : {result.get('throughput')} bytes/sec
Wire Size     : {result.get('wireSize')} bytes
Server IP     : {result.get('serverIp')}
SSL Cipher    : {result.get('sslCipher')}
SSL Version   : {result.get('sslVersion')}
Health Score  : {result.get('healthScore', 0):.4f}
==============================================
"""
    logger.info(output)

def save_report(test_name: str, results: Dict[str, Any]) -> None:
    """
    Save test results to local JSON file for analysis.
    
    Args:
        test_name (str): Name of test for filename generation
        results (dict): Test results data to save as JSON
    """
    filename = f"{test_name}_report.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Report saved to: {filename}")

# TASK 2: Add Error Handling

# TASK 3: Implement Rate Limiting and Retry Mechanisms (placeholder)

def api_request(method: str, endpoint: str, json_data=None, params=None):
    """
    Centralized API request handler with retry logic and rate limit handling.
    
    Args:
        method (str): HTTP method (GET, POST, etc.)
        endpoint (str): API endpoint path (without base URL)
        json_data: Optional JSON payload for POST requests
        params: Optional query parameters
        
    Returns:
        Response object or raises exception
    """
    # Will be implemented in Task 3
    pass

def main():
    """Main execution function with proper logging."""
    logger.info("Starting ThousandEyes test automation...")

    agent_id = get_first_agent_id()
    if agent_id is None:
        logger.error("No valid agent available. Exiting.")
        sys.exit(1)

    test_id = find_existing_test_id(TEST_NAME)
    is_new = False

    if test_id is not None:
        logger.info(f"Found existing test ID: {test_id}")
    else:
        logger.info(
            f"No existing test named '{TEST_NAME}' found. Creating a new test..."
        )
        test_id = create_test(TEST_NAME, TARGET, agent_id)
        is_new = True

    if test_id is None:
        logger.error("Test creation failed. Exiting.")
        sys.exit(1)

    if is_new:
        logger.info(
            "Waiting 90 seconds for the first test result to become available..."
        )
        time.sleep(90)

    results = get_test_results(test_id)
    if results:
        analyze_results(results)
        save_report(TEST_NAME, results)
    else:
        logger.error("No results returned. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    main()