"""
Unit tests for utilities module.
"""
import pytest
import tempfile
import os
from unittest.mock import patch, mock_open

from src.utils.utils import distance, saveJSONConfig, readJSONConfig, loadImage


class TestDistance:
    """Test cases for distance function."""
    
    def test_distance_calculation(self):
        """Test basic distance calculation."""
        result = distance(0, 0, 3, 4)
        assert result == 5.0
    
    def test_distance_same_point(self):
        """Test distance between same points."""
        result = distance(1, 1, 1, 1)
        assert result == 0.0
    
    def test_distance_negative_coordinates(self):
        """Test distance with negative coordinates."""
        result = distance(-3, -4, 0, 0)
        assert result == 5.0
    
    def test_distance_float_coordinates(self):
        """Test distance with float coordinates."""
        result = distance(0.0, 0.0, 1.5, 2.0)
        assert abs(result - 2.5) < 0.0001
    
    def test_distance_invalid_input(self):
        """Test distance with invalid input types."""
        with pytest.raises(TypeError):
            distance("invalid", 0, 3, 4)
        
        with pytest.raises(TypeError):
            distance(0, None, 3, 4)


class TestJSONConfig:
    """Test cases for JSON configuration functions."""
    
    def test_save_and_load_json_config(self):
        """Test saving and loading JSON configuration."""
        test_data = {"test_key": "test_value", "number": 42}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            # Test saving
            saveJSONConfig(temp_path, test_data)
            assert os.path.exists(temp_path)
            
            # Test loading
            loaded_data = readJSONConfig(temp_path)
            assert loaded_data == test_data
            
        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_load_nonexistent_config(self):
        """Test loading non-existent configuration file."""
        result = readJSONConfig("/nonexistent/path/config.json")
        assert result is None
    
    def test_load_invalid_json(self):
        """Test loading invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content {")
            temp_path = f.name
        
        try:
            result = readJSONConfig(temp_path)
            assert result is None
        finally:
            os.unlink(temp_path)
    
    @patch('builtins.open', mock_open())
    @patch('os.rename')
    @patch('src.utils.utils.createDirByFilePath')
    def test_save_config_error_handling(self, mock_create_dir, mock_rename):
        """Test error handling in save config."""
        mock_rename.side_effect = OSError("Permission denied")
        
        with pytest.raises(OSError):
            saveJSONConfig("/test/path.json", {"test": "data"})


class TestImageLoading:
    """Test cases for image loading functionality."""
    
    def test_load_nonexistent_image(self):
        """Test loading non-existent image file."""
        with pytest.raises(FileNotFoundError):
            loadImage("/nonexistent/image.png")
    
    @patch('os.path.exists')
    @patch('PIL.Image.open')
    def test_load_image_with_resize(self, mock_image_open, mock_exists):
        """Test loading image with resize option."""
        mock_exists.return_value = True
        
        # Mock image object
        mock_image = mock_image_open.return_value.__enter__.return_value
        mock_image.copy.return_value = mock_image
        mock_image.resize.return_value = mock_image
        mock_image.convert.return_value = mock_image
        mock_image.size = (100, 100)
        
        # Mock Image.new
        with patch('PIL.Image.new') as mock_new:
            mock_new.return_value.convert.return_value = mock_image
            mock_image.paste = lambda img, mask: None
            
            # Test the function
            result = loadImage("/test/image.png", resize=(50, 50))
            
            # Verify resize was called
            mock_image.resize.assert_called_once()
            assert result is not None


@pytest.mark.integration
class TestFileOperations:
    """Integration tests for file operations."""
    
    def test_full_config_workflow(self):
        """Test complete configuration save/load workflow."""
        test_config = {
            "app_settings": {
                "debug": True,
                "max_objects": 1000
            },
            "user_preferences": {
                "theme": "dark",
                "language": "en"
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_config.json")
            
            # Save configuration
            saveJSONConfig(config_path, test_config)
            
            # Verify file exists
            assert os.path.exists(config_path)
            
            # Load and verify
            loaded_config = readJSONConfig(config_path)
            assert loaded_config == test_config
            
            # Test nested access
            assert loaded_config["app_settings"]["debug"] is True
            assert loaded_config["user_preferences"]["theme"] == "dark"