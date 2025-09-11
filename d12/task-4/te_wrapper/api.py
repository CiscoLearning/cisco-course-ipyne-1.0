"""API client for interacting with the ThousandEyes API."""

from typing import Any, Dict
import requests
from .auth import ThousandEyesAuth

class ThousandEyesAPI:
    """API client for interacting with the ThousandEyes API."""
    
    def __init__(self, api_token: str = None):
        """
        Initializes the API client.
        
        Args:
            api_token: The ThousandEyes API token. If not provided, it attempts
                      to read from the TE_API_TOKEN environment variable.
        """
        self.auth = ThousandEyesAuth(api_token=api_token)
        self.base_url = "https://api.thousandeyes.com/v7"
    
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Makes a request to the ThousandEyes API.
        
        Args:
            method: The HTTP method (e.g., 'GET', 'POST', 'DELETE')
            endpoint: The API endpoint (e.g., 'agents', 'tests/http-server')
            **kwargs: Additional arguments to pass to the requests method
            
        Returns:
            The response object from the request
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self.auth.get_headers()
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response
    
    def get_agents(self) -> Dict[str, Any]:
        """
        Retrieves all agents from the ThousandEyes account.
        
        Returns:
            A dictionary containing the agents data from the API response
        """
        response = self._request("GET", "agents")
        return response.json()
    
    def get_http_tests(self) -> Dict[str, Any]:
        """
        Retrieves all HTTP Server tests from the ThousandEyes account.
        
        Returns:
            A dictionary containing the tests data from the API response
        """
        response = self._request("GET", "tests/http-server")
        return response.json()
    
    def create_http_test(self, test_name: str, target_url: str, agent_id: int, interval: int = 3600) -> Dict[str, Any]:
        """
        Creates a new HTTP Server test.
        
        Args:
            test_name: The name of the test
            target_url: The URL to test
            agent_id: The ID of the agent to use for the test
            interval: The test interval in seconds (default: 3600)
            
        Returns:
            A dictionary containing the created test data from the API response
        """
        payload = {
            "testName": test_name,
            "type": "agent-to-server",
            "protocol": "ICMP",
            "url": target_url,
            "interval": interval,
            "enabled": True,
            "agents": [{"agentId": agent_id}]
        }
        response = self._request("POST", "tests/http-server", json=payload)
        return response.json()
    
    def get_http_test_results(self, test_id: int) -> Dict[str, Any]:
        """
        Retrieves test results for a specific HTTP Server test.
        
        Args:
            test_id: The ID of the test to retrieve results for
            
        Returns:
            A dictionary containing the test results data from the API response
        """
        response = self._request("GET", f"test-results/{test_id}/http-server")
        return response.json()
    
    def delete_http_test(self, test_id: int) -> bool:
        """
        Deletes an HTTP Server test.
        
        Args:
            test_id: The ID of the test to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            self._request("DELETE", f"tests/http-server/{test_id}")
            return True
        except Exception:
            return False