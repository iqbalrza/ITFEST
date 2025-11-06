from groq import Groq
from PIL import Image
import io
import base64
import json
import os


class HuggingFaceService:
    """
    Service untuk analisis nutrisi makanan menggunakan Groq API
    """
    
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY tidak ditemukan di environment variables")
        
        self.client = Groq(api_key=self.api_key)
        self.model = os.getenv('GROQ_MODEL', 'meta-llama/llama-4-scout-17b-16e-instruct')
        
        print(f"Using Groq API with model: {self.model}")
    
    def analyze_food_image(self, image_base64, additional_info=""):
        """
        Analisis foto makanan menggunakan Groq API
        
        Args:
            image_base64: Base64 encoded image
            additional_info: Informasi tambahan tentang makanan (opsional)
            
        Returns:
            dict: Estimasi informasi nutrisi
        """
        try:
            print(f"Calling Groq API with model: {self.model}")
            
            # Buat prompt untuk analisis nutrisi
            prompt_text = self._create_nutrition_prompt(additional_info)
            
            # Call Groq API dengan vision
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt_text
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.3,
                max_tokens=2000,
                top_p=1,
                stream=False
            )
            
            # Extract response
            response_text = completion.choices[0].message.content
            
            print(f"Groq response: {response_text[:200]}")
            
            # Parse JSON dari response
            nutrition_data = self._parse_nutrition_response(response_text)
            
            return nutrition_data
            
        except Exception as e:
            print(f"Error in Groq API call: {str(e)}")
            import traceback
            traceback.print_exc()
            
            error_str = str(e)
            
            # Check if it's a model error
            if 'decommissioned' in error_str.lower() or 'not supported' in error_str.lower():
                return {
                    'error': f'Model tidak tersedia: {self.model}',
                    'suggestion': 'Model mungkin sudah tidak didukung. Coba model lain atau gunakan scan barcode.'
                }
            elif 'invalid' in error_str.lower() and 'model' in error_str.lower():
                return {
                    'error': f'Model tidak valid: {self.model}',
                    'suggestion': 'Periksa nama model di file .env'
                }
            
            return {
                'error': f'Error analyzing image: {str(e)}',
                'suggestion': 'Coba lagi atau gunakan fitur scan barcode'
            }
    
    def _create_nutrition_prompt(self, additional_info):
        """
        Buat prompt untuk analisis nutrisi
        
        Args:
            additional_info: Informasi tambahan dari user
            
        Returns:
            str: Prompt yang telah diformat
        """
        prompt = """Analisis foto makanan ini dan berikan estimasi informasi nutrisi dalam bahasa Indonesia seperti format berikut:

Identifikasi SEMUA komponen/bahan yang terlihat dalam gambar (nasi, lauk, sayur, dll), lalu berikan estimasi kandungan gizi per komponen.

Berikan response dalam format JSON:

{
  "dish_name": "Nama hidangan (misal: Nasi Padang, Nasi Goreng, dll)",
  "components": [
    "Komponen 1 (misal: Nasi putih)",
    "Komponen 2 (misal: Rendang)",
    "Komponen 3 (misal: Sayur singkong)",
    "..."
  ],
  "nutrition_table": [
    {
      "component": "Nasi putih",
      "portion": "1 piring (200 g)",
      "calories": "260",
      "protein": "5",
      "fat": "0.5",
      "carbohydrates": "57"
    },
    {
      "component": "Rendang sapi",
      "portion": "1 potong (100 g)",
      "calories": "193",
      "protein": "20",
      "fat": "11",
      "carbohydrates": "5"
    }
  ],
  "total_nutrition": {
    "total_calories": "total kalori semua komponen",
    "total_protein": "total protein (g)",
    "total_fat": "total lemak (g)",
    "total_carbohydrates": "total karbohidrat (g)"
  },
  "notes": [
    "Catatan tambahan tentang makanan"
  ]
}

PENTING:
- Identifikasi SEMUA komponen makanan yang terlihat
- Berikan estimasi porsi yang realistis (dalam gram atau ml)
- Hitung nutrisi per komponen (kalori, protein, lemak, karbohidrat)
- Berikan total keseluruhan
- Berikan HANYA output JSON tanpa teks tambahan"""
        
        if additional_info:
            prompt += f"\n\nInformasi tambahan: {additional_info}"
        
        return prompt
    
    def _parse_nutrition_response(self, response_text):
        """
        Parse response dari LLM menjadi structured data
        
        Args:
            response_text: Raw response dari LLM
            
        Returns:
            dict: Parsed nutrition data
        """
        try:
            # Extract JSON dari response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                nutrition_data = json.loads(json_str)
                
                # Validasi struktur data
                required_fields = ['dish_name', 'components', 'nutrition_table', 'total_nutrition']
                if all(field in nutrition_data for field in required_fields):
                    # Pastikan nutrition_table memiliki data
                    if nutrition_data.get('nutrition_table'):
                        return nutrition_data
                
                # Jika struktur tidak sesuai, return dengan default
                return {
                    'dish_name': nutrition_data.get('food_name', 'Makanan tidak teridentifikasi'),
                    'components': ['Tidak dapat diidentifikasi secara detail'],
                    'nutrition_table': [],
                    'total_nutrition': {
                        'total_calories': 'N/A',
                        'total_protein': 'N/A',
                        'total_fat': 'N/A',
                        'total_carbohydrates': 'N/A'
                    },
                    'notes': ['Format response tidak sesuai, silakan coba lagi'],
                    'raw_analysis': response_text
                }
            else:
                # Jika tidak ada JSON, return raw text
                return {
                    'dish_name': 'Tidak teridentifikasi',
                    'components': [],
                    'nutrition_table': [],
                    'total_nutrition': {
                        'total_calories': 'N/A',
                        'total_protein': 'N/A',
                        'total_fat': 'N/A',
                        'total_carbohydrates': 'N/A'
                    },
                    'notes': ['Model memberikan deskripsi text, bukan JSON terstruktur'],
                    'raw_analysis': response_text
                }
                
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {str(e)}")
            return {
                'dish_name': 'Error parsing',
                'components': [],
                'nutrition_table': [],
                'total_nutrition': {
                    'total_calories': 'N/A',
                    'total_protein': 'N/A',
                    'total_fat': 'N/A',
                    'total_carbohydrates': 'N/A'
                },
                'notes': [f'Gagal parse JSON: {str(e)}'],
                'raw_analysis': response_text
            }
        except Exception as e:
            print(f"Unexpected error in parsing: {str(e)}")
            return {
                'dish_name': 'Error',
                'components': [],
                'nutrition_table': [],
                'total_nutrition': {
                    'total_calories': 'N/A',
                    'total_protein': 'N/A',
                    'total_fat': 'N/A',
                    'total_carbohydrates': 'N/A'
                },
                'notes': [f'Error: {str(e)}'],
                'raw_analysis': response_text
            }
