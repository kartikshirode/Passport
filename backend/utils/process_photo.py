import io
import logging
from PIL import Image, ImageOps, ImageEnhance
import numpy as np
import cv2
from typing import Tuple, Optional, Union
import traceback

try:
    from rembg import remove, new_session
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    logging.warning("rembg not available, background removal will be skipped")

# Initialize logging
logger = logging.getLogger(__name__)

def pil_to_cv2(img: Image.Image) -> np.ndarray:
    """Convert PIL Image to OpenCV format"""
    return cv2.cvtColor(np.array(img.convert('RGB')), cv2.COLOR_RGB2BGR)

def cv2_to_pil(img_cv2: np.ndarray) -> Image.Image:
    """Convert OpenCV image to PIL format"""
    return Image.fromarray(cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB))

def detect_face_bbox_cv2(img_cv2_gray: np.ndarray, scaleFactor: float = 1.3, minNeighbors: int = 5) -> Optional[Tuple[int, int, int, int]]:
    """
    Detect face bounding box using OpenCV Haar Cascades
    
    Args:
        img_cv2_gray: Grayscale OpenCV image
        scaleFactor: Detection scale factor
        minNeighbors: Minimum neighbors for detection
    
    Returns:
        Tuple of (x, y, w, h) or None if no face detected
    """
    try:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(
            img_cv2_gray, 
            scaleFactor=scaleFactor, 
            minNeighbors=minNeighbors,
            minSize=(30, 30)
        )
        
        if len(faces) == 0:
            return None
            
        # Return largest face
        faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
        x, y, w, h = faces[0]
        return (int(x), int(y), int(w), int(h))
        
    except Exception as e:
        logger.error(f"Face detection error: {str(e)}")
        return None

def detect_face_landmarks_cv2(img_cv2_gray: np.ndarray) -> Optional[list]:
    """
    Detect facial landmarks for more precise alignment
    Returns key points if available
    """
    try:
        # This is a placeholder for more advanced landmark detection
        # In production, you might use dlib or MediaPipe
        # For now, we'll use the face bounding box
        return None
    except Exception:
        return None

def crop_centered_square_from_bbox(
    img_pil: Image.Image, 
    bbox: Tuple[int, int, int, int], 
    scale: float = 2.2
) -> Image.Image:
    """
    Create a square crop centered on the detected face
    
    Args:
        img_pil: PIL Image
        bbox: Face bounding box (x, y, w, h)
        scale: Scale factor for crop size (2.2 gives ~70-80% face coverage)
    
    Returns:
        Cropped PIL Image
    """
    x, y, w, h = bbox
    
    # Calculate face center
    cx = x + w / 2
    cy = y + h / 2
    
    # Calculate crop size based on face size and scale
    crop_size = int(max(w, h) * scale)
    
    # Ensure crop stays within image bounds
    left = int(max(cx - crop_size / 2, 0))
    top = int(max(cy - crop_size / 2, 0))
    right = int(min(left + crop_size, img_pil.width))
    bottom = int(min(top + crop_size, img_pil.height))
    
    # Adjust if crop goes outside bounds
    if right - left < crop_size:
        if left == 0:
            right = min(crop_size, img_pil.width)
        else:
            left = max(0, right - crop_size)
    
    if bottom - top < crop_size:
        if top == 0:
            bottom = min(crop_size, img_pil.height)
        else:
            top = max(0, bottom - crop_size)
    
    return img_pil.crop((left, top, right, bottom))

def remove_background_rembg(img: Image.Image) -> Image.Image:
    """
    Remove background using rembg (U²-Net)
    
    Args:
        img: PIL Image (RGB or RGBA)
    
    Returns:
        PIL Image with alpha channel (RGBA)
    """
    if not REMBG_AVAILABLE:
        logger.warning("rembg not available, returning original image")
        return img.convert('RGBA')
    
    try:
        # Use the default u2net model for best quality
        # For faster processing, you could use u2netp (smaller model)
        session = new_session('u2net')
        result = remove(img, session=session)
        return result.convert('RGBA')
        
    except Exception as e:
        logger.error(f"Background removal error: {str(e)}")
        # Fallback: return original with full alpha
        rgba_img = img.convert('RGBA')
        return rgba_img

def enhance_image_quality(img: Image.Image, brightness: float = 1.0, contrast: float = 1.0) -> Image.Image:
    """
    Enhance image brightness and contrast
    
    Args:
        img: PIL Image
        brightness: Brightness factor (1.0 = no change)
        contrast: Contrast factor (1.0 = no change)
    
    Returns:
        Enhanced PIL Image
    """
    try:
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(brightness)
        
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast)
        
        return img
        
    except Exception as e:
        logger.error(f"Image enhancement error: {str(e)}")
        return img

def process_passport_photo(
    pil_img: Image.Image, 
    bg_color: str = 'white',
    face_scale: float = 2.2,
    brightness: float = 1.0,
    contrast: float = 1.0,
    enhance_quality: bool = True,
    crop_data: dict = None
) -> Image.Image:
    """
    Main function to process a photo into passport format
    
    Args:
        pil_img: Input PIL Image
        bg_color: Background color (white, blue, red, or hex #RRGGBB)
        face_scale: Face scaling factor for cropping
        brightness: Brightness adjustment factor
        contrast: Contrast adjustment factor
        enhance_quality: Apply quality enhancements
    
    Returns:
        Processed PIL Image (600x600, RGB)
    """
    try:
        # Convert to RGBA for processing
        img = pil_img.convert('RGBA')
        logger.info(f"Processing image: {img.size}")
        
        # Step 1: Face detection and cropping
        if crop_data:
            # Use custom crop data if provided
            logger.info("Using custom crop data")
            x = crop_data.get('x', 0)
            y = crop_data.get('y', 0)
            width = crop_data.get('width', min(img.width, img.height))
            height = crop_data.get('height', min(img.width, img.height))
            rotation = crop_data.get('rotation', 0)
            
            # Apply rotation if specified
            if rotation != 0:
                img = img.rotate(-rotation, expand=True, fillcolor='white')
            
            # Apply crop
            cropped = img.crop((x, y, x + width, y + height))
        else:
            # Automatic face detection and cropping
            img_cv2 = pil_to_cv2(img)
            gray = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2GRAY)
            bbox = detect_face_bbox_cv2(gray)
            
            if bbox is None:
                logger.warning("No face detected, using center crop")
                # Fallback: center crop to square
                side = min(img.width, img.height)
                left = (img.width - side) // 2
                top = (img.height - side) // 2
                cropped = img.crop((left, top, left + side, top + side))
            else:
                logger.info(f"Face detected at: {bbox}")
                cropped = crop_centered_square_from_bbox(img, bbox, scale=face_scale)
        
        # Step 2: Background removal
        logger.info("Removing background...")
        fg_with_alpha = remove_background_rembg(cropped)
        
        # Step 3: Background composite
        bg_rgba = _parse_color(bg_color)
        background = Image.new('RGBA', fg_with_alpha.size, bg_rgba)
        composed = Image.alpha_composite(background, fg_with_alpha)
        
        # Step 4: Convert to RGB and enhance if requested
        final_rgb = composed.convert('RGB')
        
        if enhance_quality:
            final_rgb = enhance_image_quality(final_rgb, brightness, contrast)
        
        # Step 5: Resize to passport specifications (600x600 at 300 DPI)
        final = final_rgb.resize((600, 600), Image.LANCZOS)
        
        logger.info("Photo processing completed successfully")
        return final
        
    except Exception as e:
        logger.error(f"Photo processing failed: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Emergency fallback: return resized original
        try:
            fallback = pil_img.convert('RGB').resize((600, 600), Image.LANCZOS)
            return fallback
        except Exception:
            # Last resort: create blank white image
            return Image.new('RGB', (600, 600), (255, 255, 255))

def _parse_color(c: Union[str, tuple, list]) -> Tuple[int, int, int, int]:
    """
    Parse color input into RGBA tuple
    
    Args:
        c: Color as string name, hex code, or RGB(A) tuple/list
    
    Returns:
        RGBA tuple (r, g, b, a)
    """
    if isinstance(c, (list, tuple)) and len(c) >= 3:
        r, g, b = int(c[0]), int(c[1]), int(c[2])
        a = int(c[3]) if len(c) > 3 else 255
        return (r, g, b, a)
    
    if isinstance(c, str):
        c = c.strip().lower()
        
        # Named colors for passport photos
        named_colors = {
            'white': (255, 255, 255),
            'blue': (0, 102, 204),
            'light_blue': (173, 216, 230),
            'red': (204, 0, 0),
            'light_red': (255, 182, 193),
            'black': (0, 0, 0),
            'gray': (128, 128, 128),
            'light_gray': (211, 211, 211)
        }
        
        if c in named_colors:
            r, g, b = named_colors[c]
            return (r, g, b, 255)
        
        # Hex color parsing
        if c.startswith('#') and len(c) == 7:
            try:
                r = int(c[1:3], 16)
                g = int(c[3:5], 16)
                b = int(c[5:7], 16)
                return (r, g, b, 255)
            except ValueError:
                pass
    
    # Default to white
    logger.warning(f"Could not parse color '{c}', defaulting to white")
    return (255, 255, 255, 255)

def validate_image(img: Image.Image) -> Tuple[bool, str]:
    """
    Validate image for passport photo processing
    
    Args:
        img: PIL Image to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check image size
        if img.width < 200 or img.height < 200:
            return False, "Image too small. Minimum 200x200 pixels required."
        
        if img.width > 4000 or img.height > 4000:
            return False, "Image too large. Maximum 4000x4000 pixels allowed."
        
        # Check if image has reasonable content
        img_array = np.array(img.convert('RGB'))
        if np.std(img_array) < 10:
            return False, "Image appears to be blank or has very low contrast."
        
        return True, ""
        
    except Exception as e:
        return False, f"Image validation error: {str(e)}"