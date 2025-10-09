import io
import logging
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from typing import List, Tuple, Optional
import math

logger = logging.getLogger(__name__)

# A4 dimensions at 300 DPI
A4_WIDTH_PX = 2480  # 210mm at 300 DPI
A4_HEIGHT_PX = 3508  # 297mm at 300 DPI
A4_SIZE_PX = (A4_WIDTH_PX, A4_HEIGHT_PX)

# Passport photo dimensions (51x51mm at 300 DPI = ~600x600 px)
PASSPORT_SIZE_PX = 600
PASSPORT_SIZE_MM = 51

def calculate_grid_layout(
    a4_size: Tuple[int, int],
    photo_size: int,
    margin: int = 60,
    spacing: int = 30
) -> Tuple[int, int, int, int]:
    """
    Calculate optimal grid layout for passport photos on A4
    
    Args:
        a4_size: A4 canvas size in pixels (width, height)
        photo_size: Passport photo size in pixels (square)
        margin: Margin from edges in pixels
        spacing: Spacing between photos in pixels
    
    Returns:
        Tuple of (cols, rows, x_offset, y_offset)
    """
    canvas_width, canvas_height = a4_size
    
    # Available space after margins
    available_width = canvas_width - (2 * margin)
    available_height = canvas_height - (2 * margin)
    
    # Calculate how many photos fit
    cols = (available_width + spacing) // (photo_size + spacing)
    rows = (available_height + spacing) // (photo_size + spacing)
    
    # Ensure at least 1 photo fits
    cols = max(1, cols)
    rows = max(1, rows)
    
    # Calculate actual offsets to center the grid
    total_grid_width = cols * photo_size + (cols - 1) * spacing
    total_grid_height = rows * photo_size + (rows - 1) * spacing
    
    x_offset = (canvas_width - total_grid_width) // 2
    y_offset = (canvas_height - total_grid_height) // 2
    
    return cols, rows, x_offset, y_offset

def make_a4_sheet(
    passport_img: Image.Image, 
    copies: int = 12, 
    margin: int = 60,
    spacing: int = 30,
    add_cut_lines: bool = True
) -> io.BytesIO:
    """
    Generate A4 sheet with multiple passport photos
    
    Args:
        passport_img: PIL Image of passport photo (should be 600x600)
        copies: Number of copies to include
        margin: Margin from edges in pixels
        spacing: Spacing between photos in pixels
        add_cut_lines: Add cutting guide lines
    
    Returns:
        BytesIO buffer containing PDF data
    """
    try:
        # Ensure passport photo is correct size
        photo = passport_img.copy()
        if photo.size != (PASSPORT_SIZE_PX, PASSPORT_SIZE_PX):
            photo = photo.resize((PASSPORT_SIZE_PX, PASSPORT_SIZE_PX), Image.LANCZOS)
        
        # Create A4 canvas
        sheet = Image.new('RGB', A4_SIZE_PX, (255, 255, 255))
        
        # Calculate grid layout
        cols, rows, x_offset, y_offset = calculate_grid_layout(
            A4_SIZE_PX, PASSPORT_SIZE_PX, margin, spacing
        )
        
        logger.info(f"A4 Layout: {cols}x{rows} grid, offset: ({x_offset}, {y_offset})")
        
        # Place photos in grid
        photos_placed = 0
        for row in range(rows):
            for col in range(cols):
                if photos_placed >= copies:
                    break
                
                x = x_offset + col * (PASSPORT_SIZE_PX + spacing)
                y = y_offset + row * (PASSPORT_SIZE_PX + spacing)
                
                # Ensure photo fits within canvas
                if x + PASSPORT_SIZE_PX <= A4_WIDTH_PX and y + PASSPORT_SIZE_PX <= A4_HEIGHT_PX:
                    sheet.paste(photo, (x, y))
                    photos_placed += 1
            
            if photos_placed >= copies:
                break
        
        # Add cutting lines if requested
        if add_cut_lines:
            sheet = add_cutting_guides(sheet, cols, rows, x_offset, y_offset, spacing)
        
        # Convert to PDF using ReportLab for better print quality
        pdf_buffer = create_pdf_from_image(sheet)
        
        logger.info(f"A4 sheet created with {photos_placed} photos")
        return pdf_buffer
        
    except Exception as e:
        logger.error(f"A4 sheet generation failed: {str(e)}")
        # Return empty PDF as fallback
        return create_empty_pdf()

def make_a4_sheet_multiple(
    passport_images: List[Image.Image],
    margin: int = 60,
    spacing: int = 30,
    add_cut_lines: bool = True
) -> io.BytesIO:
    """
    Generate A4 sheet with multiple different passport photos
    
    Args:
        passport_images: List of PIL Images
        margin: Margin from edges in pixels
        spacing: Spacing between photos in pixels
        add_cut_lines: Add cutting guide lines
    
    Returns:
        BytesIO buffer containing PDF data
    """
    try:
        if not passport_images:
            return create_empty_pdf()
        
        # Create A4 canvas
        sheet = Image.new('RGB', A4_SIZE_PX, (255, 255, 255))
        
        # Calculate grid layout
        cols, rows, x_offset, y_offset = calculate_grid_layout(
            A4_SIZE_PX, PASSPORT_SIZE_PX, margin, spacing
        )
        
        # Place photos in grid
        photos_placed = 0
        photo_index = 0
        
        for row in range(rows):
            for col in range(cols):
                if photo_index >= len(passport_images):
                    break
                
                x = x_offset + col * (PASSPORT_SIZE_PX + spacing)
                y = y_offset + row * (PASSPORT_SIZE_PX + spacing)
                
                # Ensure photo fits within canvas
                if x + PASSPORT_SIZE_PX <= A4_WIDTH_PX and y + PASSPORT_SIZE_PX <= A4_HEIGHT_PX:
                    photo = passport_images[photo_index].copy()
                    if photo.size != (PASSPORT_SIZE_PX, PASSPORT_SIZE_PX):
                        photo = photo.resize((PASSPORT_SIZE_PX, PASSPORT_SIZE_PX), Image.LANCZOS)
                    
                    sheet.paste(photo, (x, y))
                    photos_placed += 1
                    photo_index += 1
            
            if photo_index >= len(passport_images):
                break
        
        # Add cutting lines if requested
        if add_cut_lines:
            sheet = add_cutting_guides(sheet, cols, rows, x_offset, y_offset, spacing)
        
        # Convert to PDF
        pdf_buffer = create_pdf_from_image(sheet)
        
        logger.info(f"Multi-photo A4 sheet created with {photos_placed} photos")
        return pdf_buffer
        
    except Exception as e:
        logger.error(f"Multi-photo A4 sheet generation failed: {str(e)}")
        return create_empty_pdf()

def add_cutting_guides(
    sheet: Image.Image,
    cols: int,
    rows: int,
    x_offset: int,
    y_offset: int,
    spacing: int,
    line_color: Tuple[int, int, int] = (200, 200, 200)
) -> Image.Image:
    """
    Add subtle cutting guide lines to A4 sheet
    
    Args:
        sheet: A4 sheet PIL Image
        cols, rows: Grid dimensions
        x_offset, y_offset: Grid positioning
        spacing: Spacing between photos
        line_color: RGB color for guide lines
    
    Returns:
        PIL Image with cutting guides
    """
    try:
        from PIL import ImageDraw
        
        draw = ImageDraw.Draw(sheet)
        line_width = 1
        
        # Draw vertical lines between columns
        for col in range(1, cols):
            x = x_offset + col * (PASSPORT_SIZE_PX + spacing) - spacing // 2
            draw.line(
                [(x, y_offset - 10), (x, y_offset + rows * (PASSPORT_SIZE_PX + spacing) - spacing + 10)],
                fill=line_color,
                width=line_width
            )
        
        # Draw horizontal lines between rows
        for row in range(1, rows):
            y = y_offset + row * (PASSPORT_SIZE_PX + spacing) - spacing // 2
            draw.line(
                [(x_offset - 10, y), (x_offset + cols * (PASSPORT_SIZE_PX + spacing) - spacing + 10, y)],
                fill=line_color,
                width=line_width
            )
        
        return sheet
        
    except Exception as e:
        logger.error(f"Failed to add cutting guides: {str(e)}")
        return sheet

def create_pdf_from_image(image: Image.Image) -> io.BytesIO:
    """
    Convert PIL Image to PDF using ReportLab for print quality
    
    Args:
        image: PIL Image to convert
    
    Returns:
        BytesIO buffer containing PDF
    """
    try:
        buffer = io.BytesIO()
        
        # Save image temporarily to get it into PDF
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG', dpi=(300, 300))
        img_buffer.seek(0)
        
        # Create PDF with ReportLab
        pdf_canvas = canvas.Canvas(buffer, pagesize=A4)
        
        # Convert pixels to points (72 DPI for PDF)
        # A4 is 210x297mm = 595x842 points
        pdf_width, pdf_height = A4
        
        # Draw the image to fill the entire A4 page
        pdf_canvas.drawInlineImage(
            img_buffer,
            0, 0,  # Position
            pdf_width, pdf_height  # Size
        )
        
        pdf_canvas.save()
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        logger.error(f"PDF creation failed: {str(e)}")
        return create_empty_pdf()

def create_empty_pdf() -> io.BytesIO:
    """
    Create an empty A4 PDF as fallback
    
    Returns:
        BytesIO buffer containing empty PDF
    """
    buffer = io.BytesIO()
    try:
        pdf_canvas = canvas.Canvas(buffer, pagesize=A4)
        pdf_canvas.drawString(100, 750, "Error: Could not generate passport photo sheet")
        pdf_canvas.save()
    except Exception:
        pass
    
    buffer.seek(0)
    return buffer

def estimate_photos_per_a4(
    photo_size_mm: float = PASSPORT_SIZE_MM,
    margin_mm: float = 20,
    spacing_mm: float = 10
) -> Tuple[int, int]:
    """
    Estimate how many passport photos fit on A4
    
    Args:
        photo_size_mm: Photo size in millimeters
        margin_mm: Margin in millimeters
        spacing_mm: Spacing between photos in millimeters
    
    Returns:
        Tuple of (columns, rows)
    """
    # A4 dimensions in mm
    a4_width_mm = 210
    a4_height_mm = 297
    
    # Available space
    available_width = a4_width_mm - (2 * margin_mm)
    available_height = a4_height_mm - (2 * margin_mm)
    
    # Calculate grid
    cols = int((available_width + spacing_mm) // (photo_size_mm + spacing_mm))
    rows = int((available_height + spacing_mm) // (photo_size_mm + spacing_mm))
    
    return max(1, cols), max(1, rows)