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
        # COMPLETE THE CODE: Initialize the wrapper and display version
        # 1. Create a ThousandEyes instance: te = te_wrapper.ThousandEyes()
        # 2. Print the wrapper version using te_wrapper.__version__
        # 3. Print "Initialized successfully!\n"
        
        
        # COMPLETE THE CODE: Test authentication by getting and displaying headers
        # 1. Get headers using te.auth.get_headers()
        # 2. Print "Authentication headers:"
        # 3. Loop through headers and print them (mask the Authorization token)
        
        
        # COMPLETE THE CODE: Test API functionality by fetching agents
        # 1. Print "Fetching available agents..."
        # 2. Get agents using te.api.get_agents()
        # 3. Extract the 'agents' list from the response
        # 4. If agents exist, print the count and first 3 agents
        # 5. Otherwise print "No agents found."
        
        
        # COMPLETE THE CODE: Test utility functions
        # 1. Print "Testing utility functions..."
        # 2. Get first agent ID using te.utils.get_first_agent_id()
        # 3. Print the first agent ID
        # 4. Look for existing test using te.utils.find_test_by_name()
        #    (use TEST_NAME from environment or 'Demo Test' as default)
        # 5. Print whether test was found or not
        
        
        print("\nDemo completed successfully!")
        
    except Exception as e:
        print(f"Error during demo: {e}")

if __name__ == "__main__":
    main()