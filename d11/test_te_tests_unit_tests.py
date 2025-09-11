"""
Unit tests for ThousandEyes API Test Automation Script
Tests all functions with proper mocking for CI/CD integration
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
from te_tests import (
    get_first_agent_id,
    find_existing_test_id,
    create_test,
    get_test_results,
    analyze_results,
    save_report,
    api_request,
    main
)


class TestData:
    """Test data fixtures for unit tests"""
    
    AGENT_DATA = {
        "agents": [{"agentId": "3", "agentName": "Singapore", "countryId": "SG"}]
    }

    TESTS_DATA = {
        "tests": [
            {
                "interval": 3600,
                "testId": "6969142",
                "testName": "Cisco.com Test",
                "createdBy": "Student (student@cisco.com)",
                "createdDate": "2025-04-10T13:42:26Z",
                "type": "http-server",
                "enabled": True,
                "url": "https://cisco.com",
            }
        ]
    }

    TEST_RESULTS = {
        "test": {
            "testId": "6969142",
            "testName": "Cisco.com Test",
            "type": "http-server",
            "url": "https://cisco.com",
        },
        "results": [
            {
                "agent": {"agentId": "3", "agentName": "Singapore", "countryId": "SG"},
                "date": "2025-04-10T15:20:39Z",
                "responseCode": 200,
                "responseTime": 125,
                "redirectTime": 1741,
                "dnsTime": 90,
                "sslTime": 8,
                "connectTime": 4,
                "waitTime": 23,
                "receiveTime": 1,
                "totalTime": 126,
                "throughput": 16682395,
                "wireSize": 18384,
                "serverIp": "23.54.57.29",
                "sslCipher": "TLS_AES_256_GCM_SHA384",
                "sslVersion": "TLSv1.3",
                "healthScore": 0.99988276,
            }
        ],
    }

    ENV = {
        "TE_API_TOKEN": "mock-token-123",
        "TEST_NAME": "Cisco.com Test",
        "TARGET": "https://cisco.com",
    }


class BaseTestCase(unittest.TestCase):
    """Base test case with common setup and teardown"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock environment variables
        self.env_patcher = patch("te_tests.TE_API_TOKEN", TestData.ENV["TE_API_TOKEN"])
        self.env_patcher.start()
        
        self.test_name_patcher = patch("te_tests.TEST_NAME", TestData.ENV["TEST_NAME"])
        self.test_name_patcher.start()
        
        self.target_patcher = patch("te_tests.TARGET", TestData.ENV["TARGET"])
        self.target_patcher.start()
        
        # Mock logger to prevent actual logging during tests
        self.logger_patcher = patch("te_tests.logger")
        self.mock_logger = self.logger_patcher.start()
        
        # Create mock responses
        self.success_response = MagicMock()
        self.success_response.ok = True
        self.success_response.status_code = 200
        
        self.error_response = MagicMock()
        self.error_response.ok = False
        self.error_response.status_code = 500
        self.error_response.text = "API Error"

    def tearDown(self):
        """Clean up patches"""
        self.env_patcher.stop()
        self.test_name_patcher.stop()
        self.target_patcher.stop()
        self.logger_patcher.stop()


class TestApiRequest(BaseTestCase):
    """Test the centralized api_request function"""
    
    @patch("te_tests.session")
    def test_successful_get_request(self, mock_session):
        """Test successful GET request"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        
        response = api_request("GET", "agents")
        
        self.assertEqual(response, mock_response)
        mock_session.get.assert_called_once()
    
    @patch("te_tests.session")
    def test_successful_post_request(self, mock_session):
        """Test successful POST request"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_session.post.return_value = mock_response
        
        payload = {"test": "data"}
        response = api_request("POST", "tests", json_data=payload)
        
        self.assertEqual(response, mock_response)
        mock_session.post.assert_called_once()
    
    @patch("te_tests.session")
    def test_rate_limit_handling(self, mock_session):
        """Test rate limit detection"""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {'X-Organization-Rate-Limit-Reset': '60'}
        mock_session.get.return_value = mock_response
        
        # Should raise exception due to raise_for_status
        mock_response.raise_for_status.side_effect = Exception("Rate limited")
        
        with self.assertRaises(Exception):
            api_request("GET", "agents")
        
        # Check that warning was logged
        self.mock_logger.warning.assert_called_with("Rate limit hit. Retry after 60 seconds.")


class TestGetFirstAgentId(BaseTestCase):
    """Test get_first_agent_id function"""
    
    @patch("te_tests.api_request")
    def test_successful_agent_retrieval(self, mock_api_request):
        """Test successful agent retrieval"""
        mock_response = MagicMock()
        mock_response.json.return_value = TestData.AGENT_DATA
        mock_api_request.return_value = mock_response
        
        agent_id = get_first_agent_id()
        
        self.assertEqual(agent_id, 3)
        mock_api_request.assert_called_once_with("GET", "agents")
        self.mock_logger.info.assert_any_call("Attempting to fetch the first agent ID.")
        self.mock_logger.info.assert_any_call(
            "Successfully fetched agent: Singapore (ID: 3)"
        )
    
    @patch("te_tests.api_request")
    def test_no_agents_found(self, mock_api_request):
        """Test handling when no agents are found"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"agents": []}
        mock_api_request.return_value = mock_response
        
        agent_id = get_first_agent_id()
        
        self.assertIsNone(agent_id)
        mock_api_request.assert_called_once_with("GET", "agents")
        self.mock_logger.warning.assert_called_with("No agents found in your account.")
    
    @patch("te_tests.api_request")
    def test_api_error(self, mock_api_request):
        """Test handling of API errors"""
        mock_api_request.side_effect = Exception("API Error")
        
        agent_id = get_first_agent_id()
        
        self.assertIsNone(agent_id)
        mock_api_request.assert_called_once_with("GET", "agents")
        self.mock_logger.error.assert_called_with("Failed to fetch agents: API Error")


class TestFindExistingTestId(BaseTestCase):
    """Test find_existing_test_id function"""
    
    @patch("te_tests.api_request")
    def test_find_existing_test(self, mock_api_request):
        """Test finding an existing test"""
        mock_response = MagicMock()
        mock_response.json.return_value = TestData.TESTS_DATA
        mock_api_request.return_value = mock_response
        
        test_id = find_existing_test_id("Cisco.com Test")
        
        self.assertEqual(test_id, 6969142)
        mock_api_request.assert_called_once_with("GET", "tests/http-server")
        self.mock_logger.info.assert_any_call(
            "Attempting to find existing test with name: 'Cisco.com Test'"
        )
        self.mock_logger.info.assert_any_call("Found existing test ID: 6969142")
    
    @patch("te_tests.api_request")
    def test_no_existing_test(self, mock_api_request):
        """Test when no existing test is found"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "tests": [{"testId": "7890123", "testName": "Different Test"}]
        }
        mock_api_request.return_value = mock_response
        
        test_id = find_existing_test_id("Cisco.com Test")
        
        self.assertIsNone(test_id)
        self.mock_logger.info.assert_any_call("No existing test named 'Cisco.com Test' found.")
    
    @patch("te_tests.api_request")
    def test_api_error(self, mock_api_request):
        """Test API error handling"""
        mock_api_request.side_effect = Exception("Connection error")
        
        test_id = find_existing_test_id("Cisco.com Test")
        
        self.assertIsNone(test_id)
        self.mock_logger.error.assert_called_with("Failed to retrieve tests: Connection error")


class TestCreateTest(BaseTestCase):
    """Test create_test function"""
    
    @patch("te_tests.api_request")
    def test_successful_creation(self, mock_api_request):
        """Test successful test creation"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"testId": "6969142"}
        mock_api_request.return_value = mock_response
        
        test_id = create_test("Cisco.com Test", "https://cisco.com", 3)
        
        self.assertEqual(test_id, 6969142)
        self.mock_logger.info.assert_any_call("Attempting to create a new test: 'Cisco.com Test'")
        self.mock_logger.info.assert_any_call(
            "Successfully created test 'Cisco.com Test' (ID: 6969142)"
        )
    
    @patch("te_tests.api_request")
    def test_creation_failure(self, mock_api_request):
        """Test failed test creation"""
        mock_api_request.side_effect = Exception("Creation failed")
        
        test_id = create_test("Cisco.com Test", "https://cisco.com", 3)
        
        self.assertIsNone(test_id)
        self.mock_logger.error.assert_called_with("Error creating test: Creation failed")


class TestGetTestResults(BaseTestCase):
    """Test get_test_results function"""
    
    @patch("te_tests.api_request")
    def test_successful_retrieval(self, mock_api_request):
        """Test successful results retrieval"""
        mock_response = MagicMock()
        mock_response.json.return_value = TestData.TEST_RESULTS
        mock_api_request.return_value = mock_response
        
        results = get_test_results(6969142)
        
        self.assertEqual(results, TestData.TEST_RESULTS)
        mock_api_request.assert_called_once_with("GET", "test-results/6969142/http-server")
        self.mock_logger.info.assert_any_call(
            "Attempting to fetch test results for test ID: 6969142"
        )
        self.mock_logger.info.assert_any_call(
            "Successfully fetched test results for test ID 6969142"
        )
    
    @patch("te_tests.api_request")
    def test_retrieval_failure(self, mock_api_request):
        """Test failed results retrieval"""
        mock_api_request.side_effect = Exception("Not found")
        
        results = get_test_results(6969142)
        
        self.assertIsNone(results)
        self.mock_logger.error.assert_called_with("Failed to retrieve test results: Not found")


class TestAnalyzeResults(BaseTestCase):
    """Test analyze_results function"""
    
    def test_analyze_valid_results(self):
        """Test analysis of valid results"""
        analyze_results(TestData.TEST_RESULTS)
        
        # Get the logged output
        calls = self.mock_logger.info.call_args_list
        output = ""
        for call in calls:
            if len(call[0]) > 0 and "HTTP SERVER TEST RESULTS" in str(call[0][0]):
                output = call[0][0]
                break
        
        # Verify key elements are present
        expected_elements = [
            "HTTP SERVER TEST RESULTS",
            "Singapore",
            "Response Code : 200",
            "Response Time : 125 ms",
            "DNS Time      : 90 ms",
            "Server IP     : 23.54.57.29",
        ]
        
        for element in expected_elements:
            self.assertIn(element, output)
        
        # Check formatted health score
        self.assertRegex(output, r"Health Score\s+:\s+0\.9999")
    
    def test_no_results(self):
        """Test handling of empty results"""
        analyze_results({"results": []})
        
        self.mock_logger.warning.assert_called_with(
            "No HTTP Server test results available for analysis."
        )


class TestSaveReport(BaseTestCase):
    """Test save_report function"""
    
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_successful_save(self, mock_json_dump, mock_file_open):
        """Test successful report saving"""
        save_report("Cisco.com Test", TestData.TEST_RESULTS)
        
        mock_file_open.assert_called_once_with("Cisco.com Test_report.json", "w")
        mock_json_dump.assert_called_once()
        
        args, kwargs = mock_json_dump.call_args
        self.assertEqual(args[0], TestData.TEST_RESULTS)
        self.assertEqual(kwargs["indent"], 2)
        
        self.mock_logger.info.assert_called_with("Report saved to: Cisco.com Test_report.json")
    
    @patch("builtins.open")
    def test_save_failure(self, mock_file_open):
        """Test handling of save failures"""
        mock_file_open.side_effect = IOError("Permission denied")
        
        save_report("Cisco.com Test", TestData.TEST_RESULTS)
        
        self.mock_logger.error.assert_called_with("Failed to save report: Permission denied")


class TestMain(BaseTestCase):
    """Test main function"""
    
    @patch("te_tests.save_report")
    @patch("te_tests.analyze_results")
    @patch("te_tests.get_test_results")
    @patch("te_tests.create_test")
    @patch("te_tests.find_existing_test_id")
    @patch("te_tests.get_first_agent_id")
    @patch("time.sleep")
    def test_main_flow(self, mock_sleep, mock_get_agent, mock_find_test, 
                       mock_create_test, mock_get_results, mock_analyze, mock_save):
        """Test main workflow with existing test"""
        # Setup mocks
        mock_get_agent.return_value = 3
        mock_find_test.return_value = 6969142
        mock_get_results.return_value = TestData.TEST_RESULTS
        
        # Run main
        main()
        
        # Verify workflow
        mock_get_agent.assert_called_once()
        mock_find_test.assert_called_once_with("Cisco.com Test")
        mock_create_test.assert_not_called()  # Should not create new test
        mock_get_results.assert_called_once_with(6969142)
        mock_analyze.assert_called_once_with(TestData.TEST_RESULTS)
        mock_save.assert_called_once_with("Cisco.com Test", TestData.TEST_RESULTS)
        mock_sleep.assert_not_called()  # No wait for existing test
    

if __name__ == "__main__":
    unittest.main()