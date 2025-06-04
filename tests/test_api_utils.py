"""
Unit tests for API utilities
"""

import pytest
from unittest.mock import patch, MagicMock
from src.core.api_utils import (
    api_request,
    validate_hyperliquid_credentials,
    round_down_by_step
)


class TestAPIUtils:
    """Test cases for API utility functions"""

    def test_round_down_by_step(self):
        """Test round_down_by_step function"""
        assert round_down_by_step(1.234, 0.1) == 1.2
        assert round_down_by_step(1.999, 0.1) == 1.9
        assert round_down_by_step(0.055, 0.01) == 0.05

    def test_validate_hyperliquid_credentials_valid(self):
        """Test validation with valid credentials"""
        valid_address = "0x742d35Cc6634C0532925a3b8D4521f8f7e0e5D00"
        valid_private_key = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        
        is_valid, message = validate_hyperliquid_credentials(valid_address, valid_private_key)
        assert is_valid is True
        assert "válido" in message

    def test_validate_hyperliquid_credentials_invalid_address(self):
        """Test validation with invalid address"""
        invalid_address = "invalid_address"
        valid_private_key = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        
        is_valid, message = validate_hyperliquid_credentials(invalid_address, valid_private_key)
        assert is_valid is False

    @patch('src.core.api_utils.requests.get')
    def test_api_request_success(self, mock_get):
        """Test successful API request"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = api_request("https://test.com")
        assert result == {"success": True}

    @patch('src.core.api_utils.requests.get')
    def test_api_request_failure(self, mock_get):
        """Test API request failure"""
        mock_get.side_effect = Exception("Network error")
        
        with pytest.raises(Exception):
            api_request("https://test.com", retries=1) 