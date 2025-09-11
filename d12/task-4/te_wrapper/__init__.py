"""ThousandEyes API wrapper package."""

__version__ = "0.1.0"

# TASK 1: Authentication module
from .auth import ThousandEyesAuth

# TASK 2: API client module
from .api import ThousandEyesAPI

# TASK 3: Utilities module
from .utils import ThousandEyesUtils

class ThousandEyes:
    """
    A wrapper class for the ThousandEyes API.
    """
    def __init__(self, api_token: str = None):
        """
        Initializes the ThousandEyes wrapper.
        
        Args:
            api_token: The ThousandEyes API token. If not provided, it attempts
                      to read from the TE_API_TOKEN environment variable.
        """
        self.auth = ThousandEyesAuth(api_token=api_token)
        self.api = ThousandEyesAPI(api_token=api_token)
        self.utils = ThousandEyesUtils(self.api)

__all__ = [
    "ThousandEyes",
    "__version__",
]