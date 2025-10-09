#!/usr/bin/env python3
"""
Command-line interface for ONNX model management and optimization.

This script provides utilities for:
- Downloading and setting up ONNX models
- Performance benchmarking
- Model optimization for production

Usage examples:
    python onnx_cli.py --download
    python onnx_cli.py --benchmark --iterations 20
    python onnx_cli.py --optimize --input u2net.onnx --output u2net_optimized.onnx
"""

import argparse
import logging
import sys
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description='ONNX Model Management and Optimization CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download U²-Net ONNX model
  python onnx_cli.py --download
  
  # Benchmark performance
  python onnx_cli.py --benchmark --iterations 20
  
  # Optimize model for CPU
  python onnx_cli.py --optimize --input u2net.onnx --output u2net_opt.onnx
  
  # Full workflow: download, optimize, and benchmark
  python onnx_cli.py --download --optimize --benchmark
        """
    )
    
    # Command options
    parser.add_argument('--download', action='store_true',
                        help='Download U²-Net ONNX model')
    parser.add_argument('--benchmark', action='store_true',
                        help='Run performance benchmark')
    parser.add_argument('--optimize', action='store_true',
                        help='Optimize model for CPU inference')
    
    # File paths
    parser.add_argument('--model-path', default='u2net.onnx',
                        help='Path to ONNX model (default: u2net.onnx)')
    parser.add_argument('--input', help='Input model path for optimization')
    parser.add_argument('--output', help='Output path for optimized model')
    
    # Benchmark options
    parser.add_argument('--iterations', type=int, default=10,
                        help='Number of benchmark iterations (default: 10)')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not any([args.download, args.benchmark, args.optimize]):
        parser.print_help()
        return
    
    logger.info("🚀 ONNX Model Management CLI Started")
    
    try:
        # Import utilities (after argument parsing to show help quickly)
        from convert_u2net_to_onnx import (
            download_u2net_onnx,
            benchmark_onnx_performance,
            optimize_onnx_model_for_cpu,
            create_optimized_onnx_session
        )
        
        model_path = args.model_path
        success = True
        
        # Download model if requested
        if args.download:
            logger.info("📥 Downloading U²-Net ONNX model...")
            success = download_u2net_onnx(model_path)
            if success:
                logger.info(f"✅ Model downloaded to: {model_path}")
            else:
                logger.error("❌ Failed to download model")
                return
        
        # Optimize model if requested
        if args.optimize:
            input_path = args.input or model_path
            output_path = args.output or model_path.replace('.onnx', '_optimized.onnx')
            
            logger.info("⚡ Optimizing model for CPU...")
            success = optimize_onnx_model_for_cpu(input_path, output_path)
            if success:
                logger.info(f"✅ Optimized model saved to: {output_path}")
                model_path = output_path  # Use optimized model for benchmarking
            else:
                logger.error("❌ Model optimization failed")
        
        # Benchmark model if requested
        if args.benchmark and success:
            if not Path(model_path).exists():
                logger.error(f"❌ Model not found for benchmarking: {model_path}")
                return
                
            logger.info("🏃 Starting performance benchmark...")
            avg_time, memory_usage = benchmark_onnx_performance(model_path, args.iterations)
            
            if avg_time > 0:
                fps = 1 / avg_time
                logger.info("🎯 Benchmark Summary:")
                logger.info(f"   ⚡ Processing speed: {fps:.1f} FPS")
                logger.info(f"   🕐 Average time: {avg_time:.3f}s per image")
                if memory_usage > 0:
                    logger.info(f"   💾 Memory usage: {memory_usage:.1f} MB")
                
                # Performance recommendations
                if fps >= 5:
                    logger.info("🎉 Excellent performance! Ready for production.")
                elif fps >= 2:
                    logger.info("✅ Good performance for most use cases.")
                else:
                    logger.info("⚠️  Consider further optimization or hardware upgrade.")
            else:
                logger.error("❌ Benchmark failed")
        
        logger.info("🏁 CLI operations completed successfully!")
        
    except ImportError as e:
        logger.error(f"❌ Missing dependencies: {e}")
        logger.info("💡 Install with: pip install onnx onnxruntime numpy pillow")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()