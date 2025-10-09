import pytest
import asyncio
import io
from fastapi.testclient import TestClient
from PIL import Image
import tempfile
import os

# Import your app
from main import app

client = TestClient(app)

@pytest.fixture
def sample_image():
    """Create a sample test image"""
    # Create a simple test image
    img = Image.new('RGB', (400, 400), color='red')
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    return buf

@pytest.fixture
def sample_image_file():
    """Create a sample image file for testing"""
    img = Image.new('RGB', (400, 400), color='blue')
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
        img.save(tmp, format='JPEG')
        tmp.flush()
        return tmp.name

class TestHealthEndpoint:
    def test_health_check(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

class TestRootEndpoint:
    def test_root_endpoint(self):
        """Test root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "endpoints" in data

class TestImageProcessing:
    def test_process_photo_success(self, sample_image_file):
        """Test successful photo processing"""
        with open(sample_image_file, 'rb') as f:
            files = {"file": ("test.jpg", f, "image/jpeg")}
            data = {
                "bg_color": "white",
                "make_a4": False,
                "face_scale": 2.2
            }
            response = client.post("/process", files=files, data=data)
        
        os.unlink(sample_image_file)  # cleanup
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        assert "file" in result
        assert result["is_pdf"] == False

    def test_process_photo_with_a4(self, sample_image_file):
        """Test photo processing with A4 generation"""
        with open(sample_image_file, 'rb') as f:
            files = {"file": ("test.jpg", f, "image/jpeg")}
            data = {
                "bg_color": "blue",
                "make_a4": True
            }
            response = client.post("/process", files=files, data=data)
        
        os.unlink(sample_image_file)  # cleanup
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        assert result["is_pdf"] == True
        assert result["copies"] == 12

    def test_process_photo_invalid_file(self):
        """Test processing with invalid file"""
        # Create a text file instead of image
        files = {"file": ("test.txt", io.StringIO("not an image"), "text/plain")}
        response = client.post("/process", files=files)
        
        assert response.status_code == 400
        assert "File must be an image" in response.json()["detail"]

    def test_process_photo_no_file(self):
        """Test processing without file"""
        response = client.post("/process")
        assert response.status_code == 422  # Validation error

    def test_process_photo_large_file(self):
        """Test processing with oversized file"""
        # Create a large image (simulate > 8MB)
        large_img = Image.new('RGB', (5000, 5000), color='green')
        buf = io.BytesIO()
        large_img.save(buf, format='JPEG', quality=100)
        buf.seek(0)
        
        files = {"file": ("large.jpg", buf, "image/jpeg")}
        response = client.post("/process", files=files)
        
        # Should be handled by file size validation
        assert response.status_code in [400, 413]

class TestBatchProcessing:
    def test_batch_process_success(self, sample_image_file):
        """Test successful batch processing"""
        # Create multiple test images
        files_data = []
        temp_files = []
        
        for i in range(3):
            img = Image.new('RGB', (300, 300), color=(i*50, i*50, i*50))
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                img.save(tmp, format='JPEG')
                tmp.flush()
                temp_files.append(tmp.name)
                files_data.append(("files", (f"test{i}.jpg", open(tmp.name, 'rb'), "image/jpeg")))
        
        try:
            data = {
                "bg_color": "white",
                "make_a4": True
            }
            response = client.post("/batch-process", files=files_data, data=data)
            
            assert response.status_code == 200
            result = response.json()
            assert result["success"] == True
            assert result["processed_count"] == 3
            assert result["is_pdf"] == True
        finally:
            # Cleanup
            for f in files_data:
                f[1][1].close()
            for tmp_file in temp_files:
                os.unlink(tmp_file)

    def test_batch_process_too_many_files(self):
        """Test batch processing with too many files"""
        files_data = []
        for i in range(15):  # More than allowed limit
            files_data.append(("files", (f"test{i}.jpg", io.BytesIO(b"fake"), "image/jpeg")))
        
        response = client.post("/batch-process", files=files_data)
        assert response.status_code == 400
        assert "Maximum 10 files allowed" in response.json()["detail"]

class TestImageValidation:
    def test_very_small_image(self):
        """Test with very small image"""
        small_img = Image.new('RGB', (50, 50), color='red')
        buf = io.BytesIO()
        small_img.save(buf, format='JPEG')
        buf.seek(0)
        
        files = {"file": ("small.jpg", buf, "image/jpeg")}
        response = client.post("/process", files=files)
        
        # Should handle small images gracefully
        assert response.status_code in [200, 400]

    def test_different_image_formats(self):
        """Test with different image formats"""
        formats = [('PNG', 'image/png'), ('WEBP', 'image/webp')]
        
        for fmt, mime_type in formats:
            img = Image.new('RGB', (300, 300), color='blue')
            buf = io.BytesIO()
            img.save(buf, format=fmt)
            buf.seek(0)
            
            files = {"file": (f"test.{fmt.lower()}", buf, mime_type)}
            response = client.post("/process", files=files)
            
            # Should handle different formats
            assert response.status_code == 200

class TestBackgroundColors:
    def test_different_background_colors(self, sample_image_file):
        """Test with different background colors"""
        colors = ['white', 'blue', 'red', 'light_blue', '#FF5733']
        
        for color in colors:
            with open(sample_image_file, 'rb') as f:
                files = {"file": ("test.jpg", f, "image/jpeg")}
                data = {"bg_color": color}
                response = client.post("/process", files=files, data=data)
                
                assert response.status_code == 200
                result = response.json()
                assert result["success"] == True
        
        os.unlink(sample_image_file)  # cleanup

class TestAdvancedSettings:
    def test_custom_face_scale(self, sample_image_file):
        """Test with custom face scale"""
        with open(sample_image_file, 'rb') as f:
            files = {"file": ("test.jpg", f, "image/jpeg")}
            data = {
                "face_scale": 1.8,
                "brightness": 1.2,
                "contrast": 0.9
            }
            response = client.post("/process", files=files, data=data)
        
        os.unlink(sample_image_file)  # cleanup
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True

@pytest.mark.asyncio
class TestAsyncOperations:
    async def test_concurrent_processing(self):
        """Test concurrent processing capabilities"""
        # This would test if the API can handle multiple simultaneous requests
        # Implementation depends on your specific async setup
        pass

# Performance tests
class TestPerformance:
    def test_processing_time(self, sample_image_file):
        """Test that processing completes within reasonable time"""
        import time
        
        start_time = time.time()
        
        with open(sample_image_file, 'rb') as f:
            files = {"file": ("test.jpg", f, "image/jpeg")}
            response = client.post("/process", files=files)
        
        processing_time = time.time() - start_time
        os.unlink(sample_image_file)  # cleanup
        
        assert response.status_code == 200
        # Should complete within 10 seconds (adjust based on your requirements)
        assert processing_time < 10.0

# Error handling tests
class TestErrorHandling:
    def test_corrupted_image(self):
        """Test with corrupted image data"""
        corrupted_data = b"this is not an image"
        files = {"file": ("corrupted.jpg", io.BytesIO(corrupted_data), "image/jpeg")}
        
        response = client.post("/process", files=files)
        assert response.status_code == 400

    def test_empty_file(self):
        """Test with empty file"""
        files = {"file": ("empty.jpg", io.BytesIO(b""), "image/jpeg")}
        response = client.post("/process", files=files)
        assert response.status_code == 400

# Integration tests
class TestIntegration:
    def test_full_workflow(self, sample_image_file):
        """Test complete workflow from upload to download"""
        # 1. Health check
        health_response = client.get("/health")
        assert health_response.status_code == 200
        
        # 2. Process image
        with open(sample_image_file, 'rb') as f:
            files = {"file": ("test.jpg", f, "image/jpeg")}
            data = {
                "bg_color": "white",
                "make_a4": False
            }
            process_response = client.post("/process", files=files, data=data)
        
        assert process_response.status_code == 200
        result = process_response.json()
        assert result["success"] == True
        assert "file" in result
        
        # 3. Verify result format
        file_data = result["file"]
        assert file_data.startswith("data:image/png;base64,")
        
        os.unlink(sample_image_file)  # cleanup

if __name__ == "__main__":
    pytest.main([__file__, "-v"])