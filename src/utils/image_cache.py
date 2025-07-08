"""
Image caching module to improve performance and reduce memory usage.
"""
import logging
import os
from functools import lru_cache
from typing import Optional, Tuple
from PIL import Image


class ImageCache:
    """
    Singleton image cache for efficient loading and caching of images.
    """
    _instance = None
    _cache = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._cache = {}
            self._initialized = True
    
    @lru_cache(maxsize=128)
    def load_image(self, path: str, resize: Optional[Tuple[int, int]] = None) -> Image.Image:
        """
        Load and cache an image with optional resizing.
        
        Args:
            path: Path to the image file
            resize: Optional tuple (width, height) to resize the image
            
        Returns:
            PIL Image object
            
        Raises:
            FileNotFoundError: If image file doesn't exist
            Exception: If image loading fails
        """
        cache_key = f"{path}_{resize}"
        
        if cache_key in self._cache:
            return self._cache[cache_key].copy()
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Image file not found: {path}")
        
        try:
            with Image.open(path) as img:
                image_copy = img.copy()
                
                if resize:
                    image_copy = image_copy.resize(resize, Image.Resampling.LANCZOS)
                
                # Cache the image
                self._cache[cache_key] = image_copy
                logging.debug(f"Cached image: {path}")
                
                return image_copy.copy()
                
        except Exception as e:
            logging.error(f"Error loading image {path}: {e}")
            raise
    
    def clear_cache(self):
        """Clear the image cache."""
        self._cache.clear()
        self.load_image.cache_clear()
        logging.info("Image cache cleared")
    
    def get_cache_size(self) -> int:
        """Get the number of cached images."""
        return len(self._cache)
    
    def get_cache_info(self):
        """Get cache statistics."""
        return self.load_image.cache_info()


# Global instance
image_cache = ImageCache()


def load_cached_image(path: str, resize: Optional[Tuple[int, int]] = None) -> Image.Image:
    """
    Convenience function to load a cached image.
    
    Args:
        path: Path to the image file
        resize: Optional tuple (width, height) to resize the image
        
    Returns:
        PIL Image object
    """
    return image_cache.load_image(path, resize)


def clear_image_cache():
    """Clear the global image cache."""
    image_cache.clear_cache()


def get_cache_stats():
    """Get cache statistics."""
    return {
        'size': image_cache.get_cache_size(),
        'lru_info': image_cache.get_cache_info()
    }