#!/usr/bin/env python3
"""
Standalone demo script for the ThousandEyes wrapper package.
This script demonstrates how external users would consume the wrapper.
"""
import os
from dotenv import load_dotenv
import te_wrapper

def main():
    """Demonstrates the wrapper functionality."""
    # Load environment variables
    load_dotenv()
    
    print("ThousandEyes API Wrapper Demo")
    print("=" * 40)
    
    try:
        # Initialize the wrapper
        te = te_wrapper.ThousandEyes()
        print(f"Wrapper version: {te_wrapper.__version__}")
        print("Initialized successfully!\n")
        
        # Test authentication
        headers = te.auth.get_headers()
        print("Authentication headers:")
        for key, value in headers.items():
            if key == "Authorization":
                print(f"  {key}: {value[:15]}...")
            else:
                print(f"  {key}: {value}")
        print()
        
        # Test API functionality
        print("Fetching available agents...")
        agents_data = te.api.get_agents()
        agents = agents_data.get('agents', [])
        
        if agents:
            print(f"Found {len(agents)} agents:")
            for agent in agents[:3]:  # Show first 3 agents
                print(f"  - {agent.get('agentName')} (ID: {agent.get('agentId')}) - {agent.get('location')}")
        else:
            print("No agents found.")
        print()
        
        # Test utilities
        print("Testing utility functions...")
        first_agent_id = te.utils.get_first_agent_id()
        print(f"First agent ID: {first_agent_id}")
        
        # Look for existing tests
        test_name = os.getenv('TEST_NAME', 'Demo Test')
        existing_test_id = te.utils.find_test_by_name(test_name)
        if existing_test_id:
            print(f"Found existing test '{test_name}' with ID: {existing_test_id}")
        else:
            print(f"No existing test named '{test_name}' found")
        
        print("\nDemo completed successfully!")
        
    except Exception as e:
        print(f"Error during demo: {e}")

if __name__ == "__main__":
    main()