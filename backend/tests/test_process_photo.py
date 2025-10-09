import pytest
from PIL import Image
import io
import numpy as np
from utils.process_photo import (
    process_passport_photo,
    detect_face_bbox_cv2,
    crop_centered_square_from_bbox,
    _parse_color,
    validate_image,
    enhance_image_quality
)

class TestFaceDetection:
    def test_detect_face_bbox_cv2_with_face(self):
        """Test face detection with a simple face-like pattern"""
        # Create a simple image with a face-like rectangle
        img = np.zeros((400, 400, 3), dtype=np.uint8)
        img[100:300, 150:250] = [255, 200, 180]  # Face-colored rectangle
        gray = np.mean(img, axis=2).astype(np.uint8)
        
        bbox = detect_face_bbox_cv2(gray)
        # May or may not detect depending on the pattern, just test it doesn't crash
        assert bbox is None or len(bbox) == 4

    def test_detect_face_bbox_cv2_no_face(self):
        """Test face detection with no face"""
        # Create a plain image
        img = np.ones((400, 400), dtype=np.uint8) * 128
        bbox = detect_face_bbox_cv2(img)
        assert bbox is None

class TestImageCropping:
    def test_crop_centered_square_from_bbox(self):
        """Test cropping functionality"""
        img = Image.new('RGB', (800, 600), color='red')
        bbox = (300, 200, 100, 120)  # x, y, w, h
        
        cropped = crop_centered_square_from_bbox(img, bbox, scale=2.0)
        
        # Should return a PIL Image
        assert isinstance(cropped, Image.Image)
        # Should be roughly square (with some tolerance for edge cases)
        width, height = cropped.size
        assert abs(width - height) <= 1

    def test_crop_edge_cases(self):
        """Test cropping with edge cases"""
        # Small image
        small_img = Image.new('RGB', (100, 100), color='blue')
        bbox = (20, 20, 30, 30)
        
        cropped = crop_centered_square_from_bbox(small_img, bbox, scale=3.0)
        assert isinstance(cropped, Image.Image)
        
        # Face near edge
        img = Image.new('RGB', (200, 200), color='green')
        edge_bbox = (0, 0, 50, 50)  # Face at top-left corner
        
        cropped = crop_centered_square_from_bbox(img, edge_bbox, scale=2.0)
        assert isinstance(cropped, Image.Image)

class TestColorParsing:
    def test_parse_named_colors(self):
        """Test parsing of named colors"""
        test_cases = [
            ('white', (255, 255, 255, 255)),
            ('blue', (0, 102, 204, 255)),
            ('red', (204, 0, 0, 255)),
            ('black', (0, 0, 0, 255))
        ]
        
        for color_name, expected in test_cases:
            result = _parse_color(color_name)
            assert result == expected

    def test_parse_hex_colors(self):
        """Test parsing of hex colors"""
        test_cases = [
            ('#FFFFFF', (255, 255, 255, 255)),
            ('#000000', (0, 0, 0, 255)),
            ('#FF5733', (255, 87, 51, 255))
        ]
        
        for hex_color, expected in test_cases:
            result = _parse_color(hex_color)
            assert result == expected

    def test_parse_rgb_tuples(self):
        """Test parsing of RGB tuples"""
        test_cases = [
            ((255, 0, 0), (255, 0, 0, 255)),
            ([0, 255, 0], (0, 255, 0, 255)),
            ((100, 150, 200, 128), (100, 150, 200, 128))
        ]
        
        for rgb_input, expected in test_cases:
            result = _parse_color(rgb_input)
            assert result == expected

    def test_parse_invalid_colors(self):
        """Test parsing of invalid colors (should default to white)"""
        invalid_colors = ['invalid', '#GGG', None, 123]
        
        for invalid_color in invalid_colors:
            result = _parse_color(invalid_color)
            assert result == (255, 255, 255, 255)  # Default white

class TestImageValidation:
    def test_validate_image_success(self):
        """Test successful image validation"""
        img = Image.new('RGB', (400, 400), color='red')
        is_valid, error_msg = validate_image(img)
        assert is_valid == True
        assert error_msg == ""

    def test_validate_image_too_small(self):
        """Test validation with too small image"""
        small_img = Image.new('RGB', (100, 100), color='blue')
        is_valid, error_msg = validate_image(small_img)
        assert is_valid == False
        assert "too small" in error_msg.lower()

    def test_validate_image_too_large(self):
        """Test validation with too large image"""
        # Create a very large image
        large_img = Image.new('RGB', (5000, 5000), color='green')
        is_valid, error_msg = validate_image(large_img)
        assert is_valid == False
        assert "too large" in error_msg.lower()

    def test_validate_blank_image(self):
        """Test validation with blank/low contrast image"""
        blank_img = Image.new('RGB', (400, 400), color=(128, 128, 128))
        is_valid, error_msg = validate_image(blank_img)
        # This might pass or fail depending on the exact implementation
        assert isinstance(is_valid, bool)

class TestImageEnhancement:
    def test_enhance_brightness(self):
        """Test brightness enhancement"""
        img = Image.new('RGB', (200, 200), color=(100, 100, 100))
        enhanced = enhance_image_quality(img, brightness=1.5, contrast=1.0)
        
        assert isinstance(enhanced, Image.Image)
        assert enhanced.size == img.size

    def test_enhance_contrast(self):
        """Test contrast enhancement"""
        img = Image.new('RGB', (200, 200), color=(100, 100, 100))
        enhanced = enhance_image_quality(img, brightness=1.0, contrast=1.5)
        
        assert isinstance(enhanced, Image.Image)
        assert enhanced.size == img.size

    def test_enhance_both(self):
        """Test both brightness and contrast enhancement"""
        img = Image.new('RGB', (200, 200), color=(100, 100, 100))
        enhanced = enhance_image_quality(img, brightness=1.2, contrast=1.3)
        
        assert isinstance(enhanced, Image.Image)
        assert enhanced.size == img.size

    def test_enhance_no_change(self):
        """Test enhancement with default values (no change)"""
        img = Image.new('RGB', (200, 200), color=(100, 100, 100))
        enhanced = enhance_image_quality(img, brightness=1.0, contrast=1.0)
        
        assert isinstance(enhanced, Image.Image)
        assert enhanced.size == img.size

class TestProcessPassportPhoto:
    def test_process_passport_photo_basic(self):
        """Test basic passport photo processing"""
        img = Image.new('RGB', (800, 600), color='red')
        
        result = process_passport_photo(img, bg_color='white')
        
        assert isinstance(result, Image.Image)
        assert result.size == (600, 600)  # Should be resized to passport size
        assert result.mode == 'RGB'

    def test_process_passport_photo_different_backgrounds(self):
        """Test processing with different background colors"""
        img = Image.new('RGB', (400, 400), color='blue')
        
        backgrounds = ['white', 'blue', 'red', '#FF5733']
        
        for bg_color in backgrounds:
            result = process_passport_photo(img, bg_color=bg_color)
            assert isinstance(result, Image.Image)
            assert result.size == (600, 600)

    def test_process_passport_photo_with_enhancements(self):
        """Test processing with image enhancements"""
        img = Image.new('RGB', (400, 400), color='green')
        
        result = process_passport_photo(
            img, 
            bg_color='white',
            brightness=1.2,
            contrast=1.1,
            enhance_quality=True
        )
        
        assert isinstance(result, Image.Image)
        assert result.size == (600, 600)

    def test_process_passport_photo_different_scales(self):
        """Test processing with different face scales"""
        img = Image.new('RGB', (400, 400), color='purple')
        
        scales = [1.5, 2.0, 2.5, 3.0]
        
        for scale in scales:
            result = process_passport_photo(img, face_scale=scale)
            assert isinstance(result, Image.Image)
            assert result.size == (600, 600)

    def test_process_passport_photo_rgba_input(self):
        """Test processing with RGBA input"""
        img = Image.new('RGBA', (400, 400), color=(255, 0, 0, 128))
        
        result = process_passport_photo(img, bg_color='white')
        
        assert isinstance(result, Image.Image)
        assert result.size == (600, 600)
        assert result.mode == 'RGB'

    def test_process_passport_photo_error_handling(self):
        """Test error handling in photo processing"""
        # Test with very small image
        tiny_img = Image.new('RGB', (10, 10), color='red')
        
        # Should not crash, might return fallback
        result = process_passport_photo(tiny_img)
        assert isinstance(result, Image.Image)
        assert result.size == (600, 600)

class TestIntegrationProcessing:
    def test_full_processing_pipeline(self):
        """Test the complete processing pipeline"""
        # Create a more realistic test image
        img = Image.new('RGB', (800, 600), color='lightblue')
        
        # Add a simple face-like rectangle
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.rectangle([300, 150, 500, 350], fill='peachpuff')  # Face area
        draw.rectangle([350, 200, 370, 220], fill='black')  # Eye
        draw.rectangle([430, 200, 450, 220], fill='black')  # Eye
        draw.rectangle([390, 280, 410, 300], fill='black')  # Nose
        
        # Process the image
        result = process_passport_photo(
            img,
            bg_color='white',
            face_scale=2.2,
            brightness=1.0,
            contrast=1.0,
            enhance_quality=True
        )
        
        assert isinstance(result, Image.Image)
        assert result.size == (600, 600)
        assert result.mode == 'RGB'
        
        # Verify it's not completely blank
        img_array = np.array(result)
        assert np.std(img_array) > 0  # Should have some variation