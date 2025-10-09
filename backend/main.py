import io
import base64
import logging
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import uvicorn

from utils.process_photo import process_passport_photo
from utils.a4_generator import make_a4_sheet
from middleware import (
    RateLimitMiddleware,
    ContentValidationMiddleware,
    SecurityHeadersMiddleware
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Passport Photo API",
    description="Professional passport photo processing with face detection and background removal",
    version="1.0.0"
)

# Security and rate limiting middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, calls=10, period=60)  # 10 requests per minute
app.add_middleware(ContentValidationMiddleware)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Passport Photo Processing API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "process": "/process",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "passport-photo-api",
        "timestamp": "2024-10-09"
    }

@app.post("/process")
async def process_photo(
    file: UploadFile = File(...),
    bg_color: str = Form("white"),
    make_a4: bool = Form(False),
    face_scale: float = Form(2.2),
    crop_x: Optional[int] = Form(None),
    crop_y: Optional[int] = Form(None),
    crop_width: Optional[int] = Form(None),
    crop_height: Optional[int] = Form(None),
    crop_rotation: Optional[float] = Form(None)
):
    """
    Process uploaded photo into passport format
    
    Args:
        file: Image file (JPG, PNG)
        bg_color: Background color (white, blue, red, or hex #RRGGBB)
        make_a4: Generate A4 sheet with multiple copies
        face_scale: Face scaling factor for cropping (default 2.2)
    
    Returns:
        JSON with processed image as base64 data URI
    """
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400, 
            detail="File must be an image (JPG, PNG, etc.)"
        )
    
    # Size limit (8MB)
    MAX_SIZE = 8 * 1024 * 1024
    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size too large. Maximum 8MB allowed."
        )
    
    try:
        # Convert to PIL Image
        image = Image.open(io.BytesIO(contents))
        if image.mode not in ['RGB', 'RGBA']:
            image = image.convert('RGBA')
        
        logger.info(f"Processing image: {image.size}, mode: {image.mode}")
        
        # Prepare crop data if provided
        crop_data = None
        if all(param is not None for param in [crop_x, crop_y, crop_width, crop_height]):
            crop_data = {
                'x': crop_x,
                'y': crop_y,
                'width': crop_width,
                'height': crop_height,
                'rotation': crop_rotation or 0
            }
        
        # Process to passport photo
        result_img = process_passport_photo(
            image, 
            bg_color=bg_color,
            face_scale=face_scale,
            crop_data=crop_data
        )
        
        if make_a4:
            # Generate A4 sheet with multiple copies
            pdf_buffer = make_a4_sheet(result_img, copies=12)
            pdf_data = pdf_buffer.getvalue()
            data_uri = 'data:application/pdf;base64,' + base64.b64encode(pdf_data).decode('utf-8')
            
            return JSONResponse({
                "success": True,
                "is_pdf": True,
                "file": data_uri,
                "format": "PDF",
                "size": "A4",
                "copies": 12
            })
        else:
            # Return single passport photo
            img_buffer = io.BytesIO()
            result_img.save(img_buffer, format='PNG', dpi=(300, 300))
            img_data = img_buffer.getvalue()
            data_uri = 'data:image/png;base64,' + base64.b64encode(img_data).decode('utf-8')
            
            return JSONResponse({
                "success": True,
                "is_pdf": False,
                "file": data_uri,
                "format": "PNG",
                "size": "600x600",
                "dpi": 300
            })
            
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Image processing failed: {str(e)}"
        )

@app.post("/batch-process")
async def batch_process_photos(
    files: list[UploadFile] = File(...),
    bg_color: str = Form("white"),
    make_a4: bool = Form(True)
):
    """
    Process multiple photos in batch
    
    Args:
        files: List of image files
        bg_color: Background color for all images
        make_a4: Generate combined A4 sheet
    
    Returns:
        JSON with processed images or combined A4 PDF
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 files allowed in batch processing"
        )
    
    processed_images = []
    
    for file in files:
        if not file.content_type.startswith("image/"):
            continue
            
        try:
            contents = await file.read()
            image = Image.open(io.BytesIO(contents)).convert('RGBA')
            result_img = process_passport_photo(image, bg_color=bg_color)
            processed_images.append(result_img)
        except Exception as e:
            logger.warning(f"Failed to process {file.filename}: {str(e)}")
            continue
    
    if not processed_images:
        raise HTTPException(
            status_code=400,
            detail="No valid images could be processed"
        )
    
    if make_a4:
        # Create A4 sheet with all processed images
        from utils.a4_generator import make_a4_sheet_multiple
        pdf_buffer = make_a4_sheet_multiple(processed_images)
        pdf_data = pdf_buffer.getvalue()
        data_uri = 'data:application/pdf;base64,' + base64.b64encode(pdf_data).decode('utf-8')
        
        return JSONResponse({
            "success": True,
            "is_pdf": True,
            "file": data_uri,
            "processed_count": len(processed_images),
            "format": "PDF"
        })
    else:
        # Return individual processed images
        results = []
        for i, img in enumerate(processed_images):
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG', dpi=(300, 300))
            img_data = img_buffer.getvalue()
            data_uri = 'data:image/png;base64,' + base64.b64encode(img_data).decode('utf-8')
            results.append({
                "index": i,
                "file": data_uri,
                "format": "PNG"
            })
        
        return JSONResponse({
            "success": True,
            "is_pdf": False,
            "images": results,
            "processed_count": len(processed_images)
        })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)