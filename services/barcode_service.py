import requests
from pyzbar import pyzbar
import cv2
import numpy as np
from PIL import Image
import os


class BarcodeService:
    """
    Service untuk scanning barcode dan mendapatkan informasi nutrisi
    """
    
    def __init__(self):
        self.food_api_url = os.getenv(
            'FOOD_API_URL', 
            'https://world.openfoodfacts.org/api/v2/product'
        )
    
    def scan_barcode(self, image):
        """
        Scan barcode dari gambar
        
        Args:
            image: PIL Image atau numpy array
            
        Returns:
            str: Barcode number atau None jika tidak ditemukan
        """
        try:
            # Convert PIL Image ke numpy array jika perlu
            if isinstance(image, Image.Image):
                image = np.array(image)
            
            # Convert RGB ke BGR untuk OpenCV
            if len(image.shape) == 3 and image.shape[2] == 3:
                image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            else:
                image_bgr = image
            
            # Decode barcode
            barcodes = pyzbar.decode(image_bgr)
            
            if barcodes:
                # Ambil barcode pertama yang ditemukan
                barcode = barcodes[0]
                barcode_data = barcode.data.decode('utf-8')
                barcode_type = barcode.type
                
                print(f"Barcode ditemukan: {barcode_data} (Type: {barcode_type})")
                return barcode_data
            
            return None
            
        except Exception as e:
            print(f"Error scanning barcode: {str(e)}")
            return None
    
    def get_nutrition_info(self, barcode):
        """
        Ambil informasi nutrisi dari Open Food Facts API
        
        Args:
            barcode: Barcode number
            
        Returns:
            dict: Informasi nutrisi produk
        """
        try:
            # Request ke Open Food Facts API
            url = f"{self.food_api_url}/{barcode}"
            headers = {
                'User-Agent': 'FoodNutritionScanner/1.0'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 1:
                    product = data.get('product', {})
                    
                    # Extract informasi nutrisi
                    nutrition_info = {
                        'product_name': product.get('product_name', 'Unknown'),
                        'brands': product.get('brands', 'Unknown'),
                        'categories': product.get('categories', 'Unknown'),
                        'image_url': product.get('image_url', ''),
                        'quantity': product.get('quantity', 'Unknown'),
                        'serving_size': product.get('serving_size', 'Unknown'),
                        'nutrition_facts': self._extract_nutrition_facts(product),
                        'ingredients': product.get('ingredients_text', 'Not available'),
                        'allergens': product.get('allergens', 'Not specified'),
                        'labels': product.get('labels', 'None'),
                        'nutriscore_grade': product.get('nutriscore_grade', 'N/A'),
                        'nova_group': product.get('nova_group', 'N/A')
                    }
                    
                    return nutrition_info
                else:
                    return {
                        'error': 'Produk tidak ditemukan di database',
                        'barcode': barcode,
                        'suggestion': 'Coba gunakan fitur analisis foto makanan'
                    }
            else:
                return {
                    'error': f'API error: {response.status_code}',
                    'barcode': barcode
                }
                
        except requests.exceptions.Timeout:
            return {
                'error': 'Request timeout',
                'barcode': barcode
            }
        except Exception as e:
            return {
                'error': f'Error fetching nutrition info: {str(e)}',
                'barcode': barcode
            }
    
    def _extract_nutrition_facts(self, product):
        """
        Extract nutrition facts dari data produk
        
        Args:
            product: Product data dari API
            
        Returns:
            dict: Nutrition facts per 100g
        """
        nutriments = product.get('nutriments', {})
        
        nutrition_facts = {
            'energy_kcal': nutriments.get('energy-kcal_100g', 'N/A'),
            'energy_kj': nutriments.get('energy_100g', 'N/A'),
            'fat': nutriments.get('fat_100g', 'N/A'),
            'saturated_fat': nutriments.get('saturated-fat_100g', 'N/A'),
            'carbohydrates': nutriments.get('carbohydrates_100g', 'N/A'),
            'sugars': nutriments.get('sugars_100g', 'N/A'),
            'fiber': nutriments.get('fiber_100g', 'N/A'),
            'proteins': nutriments.get('proteins_100g', 'N/A'),
            'salt': nutriments.get('salt_100g', 'N/A'),
            'sodium': nutriments.get('sodium_100g', 'N/A'),
        }
        
        # Filter out N/A values dan format
        formatted_facts = {}
        for key, value in nutrition_facts.items():
            if value != 'N/A':
                unit = 'kcal' if 'kcal' in key else ('kJ' if 'kj' in key else 'g')
                formatted_facts[key] = f"{value} {unit}"
            else:
                formatted_facts[key] = value
        
        return formatted_facts
