from PIL import Image
import io
import base64
import numpy as np


class ImageProcessor:
    """
    Utility class untuk processing gambar
    """
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    MAX_IMAGE_SIZE = (1920, 1920)  # Max width, height
    
    def allowed_file(self, filename):
        """
        Check apakah file extension diperbolehkan
        
        Args:
            filename: Nama file
            
        Returns:
            bool: True jika extension valid
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def process_uploaded_file(self, file):
        """
        Process uploaded file menjadi PIL Image
        
        Args:
            file: Flask uploaded file object
            
        Returns:
            PIL.Image: Processed image
        """
        try:
            # Read file
            image = Image.open(file.stream)
            
            # Convert ke RGB jika perlu
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize jika terlalu besar
            image = self.resize_image(image)
            
            return image
            
        except Exception as e:
            raise ValueError(f"Error processing image: {str(e)}")
    
    def resize_image(self, image, max_size=None):
        """
        Resize image dengan mempertahankan aspect ratio
        
        Args:
            image: PIL Image
            max_size: Tuple (max_width, max_height)
            
        Returns:
            PIL.Image: Resized image
        """
        if max_size is None:
            max_size = self.MAX_IMAGE_SIZE
        
        # Get current size
        width, height = image.size
        max_width, max_height = max_size
        
        # Calculate new size
        if width > max_width or height > max_height:
            # Calculate ratio
            ratio = min(max_width / width, max_height / height)
            new_size = (int(width * ratio), int(height * ratio))
            
            # Resize
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        return image
    
    def image_to_base64(self, image):
        """
        Convert PIL Image ke base64 string
        
        Args:
            image: PIL Image
            
        Returns:
            str: Base64 encoded image
        """
        try:
            # Save image to bytes buffer
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=85)
            buffer.seek(0)
            
            # Encode to base64
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            
            return image_base64
            
        except Exception as e:
            raise ValueError(f"Error converting image to base64: {str(e)}")
    
    def base64_to_image(self, base64_string):
        """
        Convert base64 string ke PIL Image
        
        Args:
            base64_string: Base64 encoded image
            
        Returns:
            PIL.Image: Decoded image
        """
        try:
            # Decode base64
            image_data = base64.b64decode(base64_string)
            
            # Create PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            return image
            
        except Exception as e:
            raise ValueError(f"Error converting base64 to image: {str(e)}")
    
    def enhance_image_for_barcode(self, image):
        """
        Enhance image untuk meningkatkan akurasi barcode scanning
        
        Args:
            image: PIL Image
            
        Returns:
            numpy.ndarray: Enhanced image
        """
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Convert to grayscale
            if len(img_array.shape) == 3:
                from PIL import ImageEnhance
                
                # Enhance contrast
                enhancer = ImageEnhance.Contrast(image)
                enhanced = enhancer.enhance(2.0)
                
                # Enhance sharpness
                enhancer = ImageEnhance.Sharpness(enhanced)
                enhanced = enhancer.enhance(2.0)
                
                return np.array(enhanced)
            
            return img_array
            
        except Exception as e:
            print(f"Error enhancing image: {str(e)}")
            return np.array(image)
