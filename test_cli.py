
import unittest
import json
import os
import sys
from unittest.mock import patch, MagicMock
from io import StringIO

# Add current directory to path
sys.path.append(os.getcwd())

# Import the new modules
from commands import models, make_key, usage
import utils

class TestOpenRouterCLI(unittest.TestCase):

    def setUp(self):
        self.mock_app_config = {"provisioning_key": "sk-test-prov-123"}
        self.mock_user_config = {"key_hash": "hash-123"}
        
        # Patch load_json_config/save_json_config in utils
        self.load_patcher = patch('utils.load_json_config')
        self.save_patcher = patch('utils.save_json_config')
        self.mock_load = self.load_patcher.start()
        self.mock_save = self.save_patcher.start()
        
        # Default behavior for configs
        def side_effect(filename):
            if filename == "app.config":
                return self.mock_app_config
            if filename == "user.config":
                return self.mock_user_config
            return {}
        self.mock_load.side_effect = side_effect

    def tearDown(self):
        self.load_patcher.stop()
        self.save_patcher.stop()

    @patch('utils.urllib.request.urlopen')
    def test_models_command(self, mock_urlopen):
        # Mock API response for models
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "data": [
                {"id": "openai/gpt-4", "name": "GPT-4", "pricing": {"prompt": "1", "completion": "2"}},
                {"id": "unauthorized/model", "name": "Bad Model"},
                {"id": "anthropic/claude-3", "name": "Claude 3"}
            ]
        }).encode("utf-8")
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response

        captured_stdout = StringIO()
        sys.stdout = captured_stdout 
        
        try:
            args = MagicMock()
            models.run(args)
            
            output = captured_stdout.getvalue()
            self.assertIn("GPT-4", output)
            self.assertIn("Claude 3", output)
            self.assertNotIn("Bad Model", output)
        finally:
            sys.stdout = sys.__stdout__

    @patch('utils.urllib.request.urlopen')
    def test_make_key_command(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "data": {
                "key_hash": "new-hash-456",
                "name": "test-key"
            },
            "key": "sk-or-new-key-123"
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Force empty user config
        self.mock_load.side_effect = lambda f: self.mock_app_config if f == "app.config" else {}
        
        captured_stderr = StringIO()
        captured_stdout = StringIO()
        sys.stderr = captured_stderr
        sys.stdout = captured_stdout
        
        try:
            args = MagicMock()
            args.name = "test-key"
            make_key.run(args)
            
            output_std = captured_stdout.getvalue()
            self.assertIn("NEW KEY GENERATED: sk-or-new-key-123", output_std)
            
            self.mock_save.assert_called_with("user.config", {
                "key_hash": "new-hash-456",
                "created_at": unittest.mock.ANY,
                "key_name": "test-key"
            })
        finally:
            sys.stderr = sys.__stderr__
            sys.stdout = sys.__stdout__

    @patch('utils.urllib.request.urlopen')
    def test_usage_command(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "data": {
                "limit": 10.0,
                "usage": 5.5,
            }
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        captured_stdout = StringIO()
        sys.stdout = captured_stdout
        
        try:
            args = MagicMock()
            usage.run(args)
            
            output = captured_stdout.getvalue()
            self.assertIn("Usage:   $5.5", output)
            self.assertIn("Limit:   $10.0", output)
        finally:
            sys.stdout = sys.__stdout__

if __name__ == '__main__':
    unittest.main()
