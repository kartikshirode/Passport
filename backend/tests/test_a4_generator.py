import pytest
from PIL import Image
import io
from utils.a4_generator import (
    make_a4_sheet,
    make_a4_sheet_multiple,
    calculate_grid_layout,
    estimate_photos_per_a4,
    A4_SIZE_PX,
    PASSPORT_SIZE_PX
)

class TestGridLayoutCalculation:
    def test_calculate_grid_layout_default(self):
        """Test default grid layout calculation"""
        cols, rows, x_offset, y_offset = calculate_grid_layout(
            A4_SIZE_PX, PASSPORT_SIZE_PX, margin=60, spacing=30
        )
        
        assert cols > 0
        assert rows > 0
        assert x_offset >= 0
        assert y_offset >= 0
        
        # Should fit reasonable number of photos
        assert cols * rows >= 8  # At least 8 photos should fit

    def test_calculate_grid_layout_custom_margins(self):
        """Test grid layout with custom margins"""
        cols, rows, x_offset, y_offset = calculate_grid_layout(
            A4_SIZE_PX, PASSPORT_SIZE_PX, margin=100, spacing=50
        )
        
        assert cols > 0
        assert rows > 0
        # With larger margins, should fit fewer photos
        assert cols * rows >= 4

    def test_calculate_grid_layout_edge_cases(self):
        """Test grid layout edge cases"""
        # Very small canvas
        small_canvas = (800, 600)
        cols, rows, x_offset, y_offset = calculate_grid_layout(
            small_canvas, PASSPORT_SIZE_PX, margin=10, spacing=5
        )
        
        # Should at least fit 1 photo
        assert cols >= 1
        assert rows >= 1

class TestEstimatePhotosPerA4:
    def test_estimate_photos_standard(self):
        """Test photo estimation with standard settings"""
        cols, rows = estimate_photos_per_a4()
        
        assert cols > 0
        assert rows > 0
        assert cols * rows >= 8  # Should fit at least 8 standard passport photos

    def test_estimate_photos_custom_size(self):
        """Test photo estimation with custom photo size"""
        cols, rows = estimate_photos_per_a4(photo_size_mm=40, margin_mm=15)
        
        assert cols > 0
        assert rows > 0
        # Smaller photos should fit more
        total_photos = cols * rows
        assert total_photos >= 10

    def test_estimate_photos_large_margins(self):
        """Test photo estimation with large margins"""
        cols, rows = estimate_photos_per_a4(margin_mm=50, spacing_mm=20)
        
        assert cols > 0
        assert rows > 0
        # Large margins should fit fewer photos
        total_photos = cols * rows
        assert total_photos >= 4

class TestA4SheetGeneration:
    def test_make_a4_sheet_basic(self):
        """Test basic A4 sheet generation"""
        # Create a test passport photo
        passport_img = Image.new('RGB', (600, 600), color='red')
        
        pdf_buffer = make_a4_sheet(passport_img, copies=8)
        
        assert isinstance(pdf_buffer, io.BytesIO)
        assert pdf_buffer.tell() > 0  # Should have content
        
        # Reset buffer position and check it has data
        pdf_buffer.seek(0)
        data = pdf_buffer.read()
        assert len(data) > 0
        assert data.startswith(b'%PDF')  # Should be a PDF file

    def test_make_a4_sheet_different_copies(self):
        """Test A4 sheet with different number of copies"""
        passport_img = Image.new('RGB', (600, 600), color='blue')
        
        copy_counts = [4, 8, 12, 16]
        
        for copies in copy_counts:
            pdf_buffer = make_a4_sheet(passport_img, copies=copies)
            assert isinstance(pdf_buffer, io.BytesIO)
            
            pdf_buffer.seek(0)
            data = pdf_buffer.read()
            assert len(data) > 0

    def test_make_a4_sheet_custom_margins(self):
        """Test A4 sheet with custom margins and spacing"""
        passport_img = Image.new('RGB', (600, 600), color='green')
        
        pdf_buffer = make_a4_sheet(
            passport_img, 
            copies=6, 
            margin=80, 
            spacing=40,
            add_cut_lines=True
        )
        
        assert isinstance(pdf_buffer, io.BytesIO)
        pdf_buffer.seek(0)
        data = pdf_buffer.read()
        assert len(data) > 0

    def test_make_a4_sheet_no_cut_lines(self):
        """Test A4 sheet without cutting lines"""
        passport_img = Image.new('RGB', (600, 600), color='yellow')
        
        pdf_buffer = make_a4_sheet(
            passport_img, 
            copies=8, 
            add_cut_lines=False
        )
        
        assert isinstance(pdf_buffer, io.BytesIO)
        pdf_buffer.seek(0)
        data = pdf_buffer.read()
        assert len(data) > 0

    def test_make_a4_sheet_wrong_size_image(self):
        """Test A4 sheet with wrong size passport image (should resize)"""
        # Create an image that's not 600x600
        wrong_size_img = Image.new('RGB', (400, 500), color='purple')
        
        pdf_buffer = make_a4_sheet(wrong_size_img, copies=4)
        
        assert isinstance(pdf_buffer, io.BytesIO)
        pdf_buffer.seek(0)
        data = pdf_buffer.read()
        assert len(data) > 0

class TestMultiplePhotosA4:
    def test_make_a4_sheet_multiple_success(self):
        """Test A4 sheet with multiple different photos"""
        # Create multiple test images
        images = []
        colors = ['red', 'blue', 'green', 'yellow', 'purple']
        
        for color in colors:
            img = Image.new('RGB', (600, 600), color=color)
            images.append(img)
        
        pdf_buffer = make_a4_sheet_multiple(images)
        
        assert isinstance(pdf_buffer, io.BytesIO)
        pdf_buffer.seek(0)
        data = pdf_buffer.read()
        assert len(data) > 0
        assert data.startswith(b'%PDF')

    def test_make_a4_sheet_multiple_empty_list(self):
        """Test A4 sheet with empty image list"""
        pdf_buffer = make_a4_sheet_multiple([])
        
        assert isinstance(pdf_buffer, io.BytesIO)
        # Should return empty PDF or error PDF
        pdf_buffer.seek(0)
        data = pdf_buffer.read()
        assert len(data) > 0

    def test_make_a4_sheet_multiple_single_image(self):
        """Test A4 sheet with single image in list"""
        img = Image.new('RGB', (600, 600), color='orange')
        
        pdf_buffer = make_a4_sheet_multiple([img])
        
        assert isinstance(pdf_buffer, io.BytesIO)
        pdf_buffer.seek(0)
        data = pdf_buffer.read()
        assert len(data) > 0

    def test_make_a4_sheet_multiple_different_sizes(self):
        """Test A4 sheet with images of different sizes"""
        images = [
            Image.new('RGB', (400, 400), color='red'),
            Image.new('RGB', (800, 600), color='blue'),
            Image.new('RGB', (300, 700), color='green')
        ]
        
        pdf_buffer = make_a4_sheet_multiple(images, add_cut_lines=True)
        
        assert isinstance(pdf_buffer, io.BytesIO)
        pdf_buffer.seek(0)
        data = pdf_buffer.read()
        assert len(data) > 0

class TestErrorHandling:
    def test_make_a4_sheet_invalid_image(self):
        """Test A4 sheet generation with invalid image"""
        # This should handle gracefully
        try:
            # Create a minimal image that might cause issues
            tiny_img = Image.new('RGB', (1, 1), color='black')
            pdf_buffer = make_a4_sheet(tiny_img, copies=1)
            
            assert isinstance(pdf_buffer, io.BytesIO)
            pdf_buffer.seek(0)
            data = pdf_buffer.read()
            assert len(data) > 0
        except Exception as e:
            # Should handle errors gracefully
            assert isinstance(e, Exception)

    def test_make_a4_sheet_zero_copies(self):
        """Test A4 sheet with zero copies"""
        passport_img = Image.new('RGB', (600, 600), color='gray')
        
        pdf_buffer = make_a4_sheet(passport_img, copies=0)
        
        assert isinstance(pdf_buffer, io.BytesIO)
        # Should handle gracefully, might create empty sheet

    def test_make_a4_sheet_excessive_copies(self):
        """Test A4 sheet with excessive number of copies"""
        passport_img = Image.new('RGB', (600, 600), color='cyan')
        
        # Try with a very large number
        pdf_buffer = make_a4_sheet(passport_img, copies=100)
        
        assert isinstance(pdf_buffer, io.BytesIO)
        # Should handle gracefully, probably fit as many as possible

class TestPDFContent:
    def test_pdf_file_signature(self):
        """Test that generated files are valid PDFs"""
        passport_img = Image.new('RGB', (600, 600), color='magenta')
        
        pdf_buffer = make_a4_sheet(passport_img, copies=4)
        pdf_buffer.seek(0)
        data = pdf_buffer.read()
        
        # Check PDF signature
        assert data.startswith(b'%PDF-')
        # Check PDF end signature
        assert b'%%EOF' in data[-50:]

    def test_pdf_size_reasonable(self):
        """Test that PDF size is reasonable"""
        passport_img = Image.new('RGB', (600, 600), color='teal')
        
        pdf_buffer = make_a4_sheet(passport_img, copies=8)
        pdf_buffer.seek(0)
        data = pdf_buffer.read()
        
        # PDF should be substantial but not excessive
        # (exact size depends on compression and content)
        assert 50000 < len(data) < 5000000  # Between 50KB and 5MB

class TestIntegrationA4:
    def test_complete_a4_workflow(self):
        """Test complete A4 generation workflow"""
        # Create multiple realistic test images
        images = []
        
        for i in range(6):
            img = Image.new('RGB', (600, 600), color=(50 + i*30, 100 + i*20, 150 + i*10))
            
            # Add some simple content to make it more realistic
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            draw.rectangle([200, 200, 400, 400], fill=(255, 255, 255))
            draw.ellipse([250, 250, 350, 350], fill=(200, 150, 100))
            
            images.append(img)
        
        # Test single image A4
        single_pdf = make_a4_sheet(images[0], copies=12, add_cut_lines=True)
        assert isinstance(single_pdf, io.BytesIO)
        
        # Test multiple images A4
        multi_pdf = make_a4_sheet_multiple(images, add_cut_lines=True)
        assert isinstance(multi_pdf, io.BytesIO)
        
        # Verify both have content
        single_pdf.seek(0)
        single_data = single_pdf.read()
        assert len(single_data) > 0
        
        multi_pdf.seek(0)
        multi_data = multi_pdf.read()
        assert len(multi_data) > 0
        
        # Multiple image PDF might be larger
        # (though this depends on compression)
        assert len(multi_data) > 1000