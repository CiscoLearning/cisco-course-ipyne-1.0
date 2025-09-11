"""
Test script for the ThousandEyes API wrapper.
This script validates the authentication functionality.
"""

from dotenv import load_dotenv
import te_wrapper as TE

def main():
    """
    Main test function to validate wrapper authentication functionality.
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

if __name__ == "__main__":
    main()