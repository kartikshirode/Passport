#!/usr/bin/env python3
"""
Enhanced U²-Net ONNX model management and optimization utilities.

This module provides:
- ONNX model downloading and caching
- Performance benchmarking
- Model optimization for production deployment
- CPU-optimized inference setup

Usage:
    python convert_u2net_to_onnx.py --benchmark --optimize
"""

import io
import logging
import time
import argparse
import sys
from pathlib import Path
from PIL import Image
import onnx
import onnxruntime as ort
import numpy as np
from typing import Optional, Tuple
import os
import requests
import traceback

logger = logging.getLogger(__name__)

# Performance optimization settings
ONNX_OPTIMIZATION_LEVEL = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
ONNX_PROVIDERS = ['CPUExecutionProvider']

def download_u2net_onnx(model_path: str = "u2net.onnx") -> bool:
    """
    Download U²-Net ONNX model from a reliable source
    
    Args:
        model_path: Path to save the ONNX model
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # This is a placeholder URL - you would need to host the ONNX model
        # or convert it yourself from the original PyTorch model
        model_url = "https://example.com/u2net.onnx"
        
        if os.path.exists(model_path):
            logger.info(f"ONNX model already exists at {model_path}")
            return True
        
        logger.info(f"Downloading U²-Net ONNX model to {model_path}")
        response = requests.get(model_url, stream=True)
        response.raise_for_status()
        
        with open(model_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info("ONNX model downloaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download ONNX model: {str(e)}")
        return False

def convert_pytorch_to_onnx(
    pytorch_model_path: str,
    onnx_model_path: str,
    input_shape: tuple = (1, 3, 320, 320)
) -> bool:
    """
    Convert PyTorch U²-Net model to ONNX format
    
    Args:
        pytorch_model_path: Path to PyTorch model file
        onnx_model_path: Path to save ONNX model
        input_shape: Input tensor shape (batch, channels, height, width)
    
    Returns:
        True if conversion successful, False otherwise
    """
    try:
        import torch
        import torch.onnx
        from rembg.models import u2net
        
        logger.info("Converting PyTorch U²-Net to ONNX...")
        
        # Load the PyTorch model
        model = u2net.U2NET(3, 1)
        model.load_state_dict(torch.load(pytorch_model_path, map_location='cpu'))
        model.eval()
        
        # Create dummy input
        dummy_input = torch.randn(*input_shape)
        
        # Export to ONNX
        torch.onnx.export(
            model,
            dummy_input,
            onnx_model_path,
            export_params=True,
            opset_version=11,
            do_constant_folding=True,
            input_names=['input'],
            output_names=['output'],
            dynamic_axes={
                'input': {0: 'batch_size', 2: 'height', 3: 'width'},
                'output': {0: 'batch_size', 2: 'height', 3: 'width'}
            }
        )
        
        # Verify the ONNX model
        onnx_model = onnx.load(onnx_model_path)
        onnx.checker.check_model(onnx_model)
        
        logger.info(f"ONNX model saved successfully to {onnx_model_path}")
        return True
        
    except Exception as e:
        logger.error(f"PyTorch to ONNX conversion failed: {str(e)}")
        logger.error(traceback.format_exc())
        return False

class ONNXBackgroundRemover:
    """
    ONNX-optimized background removal using U²-Net
    """
    
    def __init__(self, model_path: str = "u2net.onnx"):
        """
        Initialize ONNX runtime session
        
        Args:
            model_path: Path to ONNX model file
        """
        self.model_path = model_path
        self.session = None
        self.input_name = None
        self.output_name = None
        
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize ONNX runtime session"""
        try:
            if not os.path.exists(self.model_path):
                logger.warning(f"ONNX model not found at {self.model_path}")
                return
            
            # Set up ONNX runtime with CPU optimization
            providers = ['CPUExecutionProvider']
            
            # Try to use more optimized providers if available
            available_providers = ort.get_available_providers()
            if 'DmlExecutionProvider' in available_providers:  # DirectML on Windows
                providers.insert(0, 'DmlExecutionProvider')
            elif 'CoreMLExecutionProvider' in available_providers:  # CoreML on macOS
                providers.insert(0, 'CoreMLExecutionProvider')
            
            self.session = ort.InferenceSession(
                self.model_path,
                providers=providers
            )
            
            # Get input/output names
            self.input_name = self.session.get_inputs()[0].name
            self.output_name = self.session.get_outputs()[0].name
            
            logger.info(f"ONNX session initialized with providers: {providers}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ONNX session: {str(e)}")
            self.session = None
    
    def preprocess_image(self, image: Image.Image, target_size: tuple = (320, 320)) -> np.ndarray:
        """
        Preprocess image for U²-Net inference
        
        Args:
            image: PIL Image
            target_size: Target size for inference
        
        Returns:
            Preprocessed numpy array
        """
        # Resize image
        img_resized = image.resize(target_size, Image.LANCZOS)
        
        # Convert to RGB if not already
        if img_resized.mode != 'RGB':
            img_resized = img_resized.convert('RGB')
        
        # Convert to numpy array and normalize
        img_array = np.array(img_resized).astype(np.float32) / 255.0
        
        # Normalize with ImageNet statistics
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        img_array = (img_array - mean) / std
        
        # Change from HWC to CHW format
        img_array = np.transpose(img_array, (2, 0, 1))
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    def postprocess_mask(self, mask: np.ndarray, original_size: tuple) -> Image.Image:
        """
        Postprocess the output mask
        
        Args:
            mask: Raw model output
            original_size: Original image size (width, height)
        
        Returns:
            Processed mask as PIL Image
        """
        # Remove batch dimension and get first channel
        mask = mask[0, 0, :, :]
        
        # Apply sigmoid to get probabilities
        mask = 1.0 / (1.0 + np.exp(-mask))
        
        # Convert to 0-255 range
        mask = (mask * 255).astype(np.uint8)
        
        # Convert to PIL Image and resize to original size
        mask_img = Image.fromarray(mask, mode='L')
        mask_img = mask_img.resize(original_size, Image.LANCZOS)
        
        return mask_img
    
    def remove_background(self, image: Image.Image) -> Optional[Image.Image]:
        """
        Remove background from image using ONNX model
        
        Args:
            image: Input PIL Image
        
        Returns:
            Image with removed background (RGBA) or None if failed
        """
        if self.session is None:
            logger.warning("ONNX session not available")
            return None
        
        try:
            original_size = image.size
            
            # Preprocess image
            input_array = self.preprocess_image(image)
            
            # Run inference
            outputs = self.session.run(
                [self.output_name],
                {self.input_name: input_array}
            )
            
            # Postprocess mask
            mask_img = self.postprocess_mask(outputs[0], original_size)
            
            # Apply mask to original image
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Convert mask to alpha channel
            r, g, b, a = image.split()
            result = Image.merge('RGBA', (r, g, b, mask_img))
            
            return result
            
        except Exception as e:
            logger.error(f"ONNX background removal failed: {str(e)}")
            return None

def benchmark_models(test_image: Image.Image, iterations: int = 5) -> dict:
    """
    Benchmark different background removal approaches
    
    Args:
        test_image: Test PIL Image
        iterations: Number of iterations for timing
    
    Returns:
        Dictionary with benchmark results
    """
    import time
    results = {}
    
    # Test rembg (original)
    try:
        from rembg import remove
        start_time = time.time()
        for _ in range(iterations):
            result = remove(test_image)
        avg_time = (time.time() - start_time) / iterations
        results['rembg'] = {'avg_time': avg_time, 'available': True}
    except Exception as e:
        results['rembg'] = {'avg_time': None, 'available': False, 'error': str(e)}
    
    # Test ONNX
    try:
        onnx_remover = ONNXBackgroundRemover()
        if onnx_remover.session is not None:
            start_time = time.time()
            for _ in range(iterations):
                result = onnx_remover.remove_background(test_image)
            avg_time = (time.time() - start_time) / iterations
            results['onnx'] = {'avg_time': avg_time, 'available': True}
        else:
            results['onnx'] = {'avg_time': None, 'available': False, 'error': 'Session not initialized'}
    except Exception as e:
        results['onnx'] = {'avg_time': None, 'available': False, 'error': str(e)}
    
    return results

def optimize_for_production():
    """
    Setup optimizations for production deployment
    """
    try:
        # Set ONNX runtime optimizations
        os.environ['OMP_NUM_THREADS'] = str(os.cpu_count())
        os.environ['ONNXRUNTIME_LOG_SEVERITY_LEVEL'] = '3'  # Error level only
        
        # Pre-download models if needed
        model_path = "u2net.onnx"
        if not os.path.exists(model_path):
            logger.info("ONNX model not found, attempting download...")
            download_u2net_onnx(model_path)
        
        logger.info("Production optimizations applied")
        
    except Exception as e:
        logger.error(f"Failed to apply production optimizations: {str(e)}")

if __name__ == "__main__":
    # Example usage and testing
    logging.basicConfig(level=logging.INFO)
    
    # Test ONNX conversion (if you have PyTorch model)
    # convert_pytorch_to_onnx("u2net.pth", "u2net.onnx")
    
    # Test ONNX background removal
    try:
        test_img = Image.new('RGB', (320, 320), (255, 0, 0))
        remover = ONNXBackgroundRemover()
        result = remover.remove_background(test_img)
        if result:
            print("ONNX background removal test successful")
        else:
            print("ONNX background removal test failed")
    except Exception as e:
        print(f"Test failed: {e}")
    
    # Run benchmarks
    # results = benchmark_models(test_img)
    # print("Benchmark results:", results)