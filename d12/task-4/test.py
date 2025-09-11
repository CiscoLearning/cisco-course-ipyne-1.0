"""
Test script for the ThousandEyes API wrapper.
This script validates the authentication, API, and utility functionality.
"""

from dotenv import load_dotenv
import te_wrapper as TE

def main():
    """
    Main test function to validate wrapper functionality.
    Tests authentication, API client, and utility functions.
    """
    load_dotenv()
    
    try:
        te = TE.ThousandEyes()
        print("ThousandEyesAuth initialized successfully.")
        
        headers = te.auth.get_headers()
        print("Headers generated successfully:")
        for key, value in headers.items():
            if key == "Authorization":
                print(f"{key}: {value[:10]}...")
            else:
                print(f"{key}: {value}")
                
    except ValueError as e:
        print(f"Authentication Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    print("\n" + "="*50)
    print("Testing API functionality...")
    try:
        agents_data = te.api.get_agents()
        agents = agents_data.get('agents', [])
        if agents:
            first_agent = agents[0]
            print(f"First agent: {first_agent.get('agentName')} (ID: {first_agent.get('agentId')})")
            print(f"Location: {first_agent.get('location')}")
            print(f"Country: {first_agent.get('countryId')}")
        else:
            print("No agents found.")
    except Exception as e:
        print(f"API Error: {e}")
    
    print("\n" + "="*50)
    print("Testing utility workflow...")
    try:
        import os
        test_name = os.getenv('TEST_NAME', 'Wrapper Test')
        target_url = os.getenv('TARGET', 'https://cisco.com')
        
        results = te.utils.create_and_run_test(test_name, target_url, wait_for_results=False)
        if results:
            print(f"Workflow completed successfully!")
            print(f"Test ID: {results.get('testId')}")
        else:
            print("Workflow failed")
    except Exception as e:
        print(f"Utility Error: {e}")

if __name__ == "__main__":
    main()