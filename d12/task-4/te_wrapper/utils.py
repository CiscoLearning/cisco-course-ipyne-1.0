"""Utility functions for common ThousandEyes operations."""

import time
import requests
from typing import Optional, Dict, Any
from .api import ThousandEyesAPI

class ThousandEyesUtils:
    """Utility class providing high-level operations for ThousandEyes."""
    
    def __init__(self, api_client: ThousandEyesAPI):
        """
        Initializes the utility class.
        
        Args:
            api_client: An instance of ThousandEyesAPI
        """
        self.api = api_client
    
    def get_first_agent_id(self) -> Optional[int]:
        """
        Gets the ID of the first available agent.
        
        Returns:
            The agent ID if available, None otherwise
        """
        try:
            agents_data = self.api.get_agents()
            agents = agents_data.get('agents', [])
            if agents:
                return agents[0].get('agentId')
            return None
        except Exception:
            return None
    
    def find_test_by_name(self, test_name: str) -> Optional[int]:
        """
        Finds a test by its name and returns the test ID.
        
        Args:
            test_name: The name of the test to find
            
        Returns:
            The test ID if found, None otherwise
        """
        try:
            tests_data = self.api.get_http_tests()
            tests = tests_data.get('tests', [])
            for test in tests:
                if test.get('testName') == test_name:
                    return test.get('testId')
            return None
        except Exception:
            return None
    
    def wait_for_test_results(self, test_id: int, max_wait_seconds: int = 300) -> Optional[Dict[str, Any]]:
        """
        Waits for test results to become available.
        
        Args:
            test_id: The ID of the test to wait for
            max_wait_seconds: Maximum time to wait in seconds (default: 300)
            
        Returns:
            The test results if available within the wait time, None otherwise
        """
        start_time = time.time()
        while time.time() - start_time < max_wait_seconds:
            try:
                results = self.api.get_http_test_results(test_id)
                if results.get('results'):
                    return results
            except Exception:
                pass
            print(f"Waiting for test results... ({int(time.time() - start_time)}s elapsed)")
            time.sleep(30)
        print(f"Timeout reached after {max_wait_seconds} seconds")
        return None
    
    def delete_test_by_name(self, test_name: str) -> bool:
        """
        Deletes a test by its name.
        
        Args:
            test_name: The name of the test to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        test_id = self.find_test_by_name(test_name)
        if test_id:
            return self.api.delete_http_test(test_id)
        return False
    
    def create_and_run_test(self, test_name: str, target_url: str, wait_for_results: bool = True) -> Optional[Dict[str, Any]]:
        """
        Creates a new test and optionally waits for the first results.
        
        Args:
            test_name: The name of the test
            target_url: The URL to test
            wait_for_results: Whether to wait for the first results (default: True)
            
        Returns:
            The test results if wait_for_results is True and results are available,
            otherwise the test creation response
        """
        # Get the first available agent
        agent_id = self.get_first_agent_id()
        if not agent_id:
            print("No agents available")
            return None
        
        # Check if test already exists
        existing_test_id = self.find_test_by_name(test_name)
        if existing_test_id:
            print(f"Test '{test_name}' already exists with ID {existing_test_id}")
            if wait_for_results:
                return self.wait_for_test_results(existing_test_id)
            return {"testId": existing_test_id}
        
        # Create new test
        print(f"Creating test '{test_name}' for {target_url}")
        try:
            test_response = self.api.create_http_test(test_name, target_url, agent_id)
            test_id = test_response.get('testId')
            if not test_id:
                print("Failed to create test")
                return None
            
            print(f"Test created successfully with ID {test_id}")
            
            if wait_for_results:
                print("Waiting for first test results...")
                return self.wait_for_test_results(test_id)
            
            return test_response
        except requests.exceptions.HTTPError as e:
            print(f"Error creating test: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response details: {e.response.text}")
            return None
        except Exception as e:
            print(f"Error creating test: {e}")
            return None