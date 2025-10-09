#!/usr/bin/env python3
"""
Production startup script for Passport Photo API.

This script handles:
- Environment validation
- Dependency checks
- Model preparation
- Health checks
- Graceful startup with proper logging

Usage:
    python startup.py [--check-only] [--optimize-models]
"""

import os
import sys
import time
import logging
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('startup')

class ProductionStartup:
    """Production startup manager for Passport Photo API."""
    
    def __init__(self):
        self.required_env_vars = [
            'ENVIRONMENT',
            'CORS_ORIGINS'
        ]
        self.optional_env_vars = {
            'LOG_LEVEL': 'info',
            'HOST': '0.0.0.0',
            'PORT': '8000',
            'RATE_LIMIT_REQUESTS': '10',
            'RATE_LIMIT_WINDOW': '60',
            'MAX_FILE_SIZE': '8388608'
        }
        self.required_packages = [
            'fastapi',
            'uvicorn',
            'opencv-python',
            'pillow',
            'numpy',
            'rembg'
        ]
        self.startup_checks = []
        
    def validate_environment(self) -> bool:
        """Validate environment variables and configuration."""
        logger.info("🔍 Validating environment configuration...")
        
        success = True
        
        # Check required environment variables
        for var in self.required_env_vars:
            if not os.getenv(var):
                logger.error(f"❌ Required environment variable missing: {var}")
                success = False
            else:
                logger.info(f"✅ {var}: {os.getenv(var)}")
        
        # Set optional environment variables with defaults
        for var, default in self.optional_env_vars.items():
            value = os.getenv(var, default)
            os.environ[var] = value
            logger.info(f"🔧 {var}: {value}")
        
        # Validate specific configurations
        try:
            port = int(os.getenv('PORT', '8000'))
            if not (1024 <= port <= 65535):
                logger.error(f"❌ Invalid port number: {port}")
                success = False
        except ValueError:
            logger.error(f"❌ PORT must be a number: {os.getenv('PORT')}")
            success = False
        
        try:
            max_size = int(os.getenv('MAX_FILE_SIZE', '8388608'))
            if max_size <= 0:
                logger.error(f"❌ MAX_FILE_SIZE must be positive: {max_size}")
                success = False
        except ValueError:
            logger.error(f"❌ MAX_FILE_SIZE must be a number: {os.getenv('MAX_FILE_SIZE')}")
            success = False
        
        return success
    
    def check_dependencies(self) -> bool:
        """Check if all required Python packages are installed."""
        logger.info("📦 Checking Python dependencies...")
        
        missing_packages = []
        
        for package in self.required_packages:
            try:
                __import__(package.replace('-', '_'))
                logger.info(f"✅ {package}")
            except ImportError:
                missing_packages.append(package)
                logger.error(f"❌ {package}")
        
        if missing_packages:
            logger.error("❌ Missing required packages:")
            for package in missing_packages:
                logger.error(f"   pip install {package}")
            return False
        
        return True
    
    def check_system_resources(self) -> bool:
        """Check system resources and requirements."""
        logger.info("💻 Checking system resources...")
        
        try:
            import psutil
            
            # Check available memory
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            
            if available_gb < 1.0:
                logger.warning(f"⚠️  Low available memory: {available_gb:.1f} GB")
                logger.warning("   Image processing may be slow or fail")
            else:
                logger.info(f"✅ Available memory: {available_gb:.1f} GB")
            
            # Check CPU cores
            cpu_count = psutil.cpu_count()
            logger.info(f"✅ CPU cores: {cpu_count}")
            
            # Check disk space
            disk = psutil.disk_usage('.')
            free_gb = disk.free / (1024**3)
            
            if free_gb < 1.0:
                logger.warning(f"⚠️  Low disk space: {free_gb:.1f} GB")
            else:
                logger.info(f"✅ Free disk space: {free_gb:.1f} GB")
            
            return True
            
        except ImportError:
            logger.warning("⚠️  psutil not available, skipping resource checks")
            return True
        except Exception as e:
            logger.error(f"❌ Resource check failed: {e}")
            return False
    
    def prepare_models(self, optimize: bool = False) -> bool:
        """Prepare and validate AI models."""
        logger.info("🤖 Preparing AI models...")
        
        try:
            # Test rembg model loading
            from rembg import new_session
            logger.info("📥 Loading background removal model...")
            session = new_session('u2net')
            logger.info("✅ Background removal model ready")
            
            # Test OpenCV
            import cv2
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            if os.path.exists(cascade_path):
                logger.info("✅ Face detection model ready")
            else:
                logger.error("❌ Face detection cascade not found")
                return False
            
            # Optimize models if requested
            if optimize:
                logger.info("⚡ Optimizing models for production...")
                # Add ONNX optimization if available
                try:
                    from utils.convert_u2net_to_onnx import download_u2net_onnx
                    onnx_path = "models/u2net_optimized.onnx"
                    os.makedirs("models", exist_ok=True)
                    
                    if not os.path.exists(onnx_path):
                        success = download_u2net_onnx(onnx_path)
                        if success:
                            logger.info(f"✅ Optimized model ready: {onnx_path}")
                        else:
                            logger.warning("⚠️  Could not download optimized model")
                    else:
                        logger.info(f"✅ Using existing optimized model: {onnx_path}")
                        
                except ImportError:
                    logger.warning("⚠️  ONNX optimization not available")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Model preparation failed: {e}")
            return False
    
    def run_health_checks(self) -> bool:
        """Run comprehensive health checks."""
        logger.info("🏥 Running health checks...")
        
        try:
            # Test image processing pipeline
            from PIL import Image
            import numpy as np
            from utils.process_photo import process_passport_photo
            
            # Create test image
            test_array = np.random.randint(0, 255, (400, 400, 3), dtype=np.uint8)
            test_image = Image.fromarray(test_array, 'RGB')
            
            logger.info("🧪 Testing image processing pipeline...")
            start_time = time.time()
            result = process_passport_photo(test_image, bg_color='white')
            process_time = time.time() - start_time
            
            if result and result.size == (600, 600):
                logger.info(f"✅ Image processing test passed ({process_time:.2f}s)")
            else:
                logger.error("❌ Image processing test failed")
                return False
            
            # Test A4 generation
            from utils.a4_generator import make_a4_sheet
            logger.info("📄 Testing A4 generation...")
            
            pdf_bytes = make_a4_sheet(result, copies=6)
            if pdf_bytes and len(pdf_bytes) > 1000:  # Basic size check
                logger.info("✅ A4 generation test passed")
            else:
                logger.error("❌ A4 generation test failed")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            logger.error(f"   Error details: {str(e)}")
            return False
    
    def start_server(self) -> bool:
        """Start the FastAPI server with proper configuration."""
        logger.info("🚀 Starting FastAPI server...")
        
        try:
            host = os.getenv('HOST', '0.0.0.0')
            port = int(os.getenv('PORT', '8000'))
            log_level = os.getenv('LOG_LEVEL', 'info').lower()
            
            # Build uvicorn command
            cmd = [
                sys.executable, '-m', 'uvicorn',
                'main:app',
                '--host', host,
                '--port', str(port),
                '--log-level', log_level
            ]
            
            # Add production settings
            if os.getenv('ENVIRONMENT') == 'production':
                cmd.extend(['--workers', '2'])  # Adjust based on CPU cores
                cmd.extend(['--access-log'])
            else:
                cmd.extend(['--reload'])
            
            logger.info(f"🌐 Server starting on {host}:{port}")
            logger.info(f"📝 Log level: {log_level}")
            
            # Start server
            subprocess.run(cmd, check=True)
            return True
            
        except KeyboardInterrupt:
            logger.info("🛑 Server stopped by user")
            return True
        except Exception as e:
            logger.error(f"❌ Server startup failed: {e}")
            return False
    
    def run_startup_sequence(self, check_only: bool = False, optimize_models: bool = False) -> bool:
        """Run the complete startup sequence."""
        logger.info("🚀 Starting Passport Photo API...")
        logger.info(f"   Environment: {os.getenv('ENVIRONMENT', 'development')}")
        logger.info(f"   Check only: {check_only}")
        logger.info(f"   Optimize models: {optimize_models}")
        
        # Run all checks
        checks = [
            ("Environment Validation", self.validate_environment),
            ("Dependency Check", self.check_dependencies),
            ("System Resources", self.check_system_resources),
            ("Model Preparation", lambda: self.prepare_models(optimize_models)),
            ("Health Checks", self.run_health_checks)
        ]
        
        for check_name, check_func in checks:
            logger.info(f"🔄 {check_name}...")
            
            start_time = time.time()
            success = check_func()
            elapsed = time.time() - start_time
            
            if success:
                logger.info(f"✅ {check_name} passed ({elapsed:.1f}s)")
            else:
                logger.error(f"❌ {check_name} failed")
                return False
        
        logger.info("🎉 All startup checks passed!")
        
        if check_only:
            logger.info("✅ Check-only mode completed successfully")
            return True
        
        # Start the server
        return self.start_server()

def main():
    """Main startup function with CLI interface."""
    parser = argparse.ArgumentParser(
        description='Production startup script for Passport Photo API',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--check-only', 
        action='store_true',
        help='Run checks only, do not start server'
    )
    parser.add_argument(
        '--optimize-models',
        action='store_true', 
        help='Download and optimize models for production'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize startup manager
    startup = ProductionStartup()
    
    # Run startup sequence
    success = startup.run_startup_sequence(
        check_only=args.check_only,
        optimize_models=args.optimize_models
    )
    
    if success:
        logger.info("🏁 Startup completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 Startup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()