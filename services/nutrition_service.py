from groq import Groq
import os
import json
import base64


class NutritionService:
    """
    Service untuk analisis nutrisi makanan menggunakan Groq LLM
    """
    
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY tidak ditemukan di environment variables")
        
        self.client = Groq(api_key=self.api_key)
        self.model = os.getenv('GROQ_MODEL', 'llama-3.2-11b-vision-preview')
    
    def analyze_food_image(self, image_base64, additional_info=""):
        """
        Analisis foto makanan menggunakan Groq LLM dengan vision capabilities
        
        Args:
            image_base64: Base64 encoded image
            additional_info: Informasi tambahan tentang makanan (opsional)
            
        Returns:
            dict: Estimasi informasi nutrisi
        """
        try:
            # Buat prompt untuk analisis nutrisi
            prompt = self._create_nutrition_prompt(additional_info)
            
            # Call Groq API dengan vision
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
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
            
            # Parse response
            response_text = completion.choices[0].message.content
            
            # Parse JSON dari response
            nutrition_data = self._parse_nutrition_response(response_text)
            
            return nutrition_data
            
        except Exception as e:
            print(f"Error in Groq API call: {str(e)}")
            return {
                'error': f'Error analyzing image: {str(e)}',
                'suggestion': 'Pastikan gambar jelas dan API key valid'
            }
    
    def _create_nutrition_prompt(self, additional_info):
        """
        Buat prompt untuk analisis nutrisi
        
        Args:
            additional_info: Informasi tambahan dari user
            
        Returns:
            str: Prompt yang telah diformat
        """
        prompt = """Analisis foto makanan ini dan berikan estimasi informasi nutrisi dalam bahasa Indonesia.

Tugas Anda:
1. Identifikasi jenis makanan/minuman yang ada di gambar
2. Estimasi porsi/berat makanan (dalam gram atau ml)
3. Berikan estimasi nilai nutrisi per porsi dan per 100g/100ml

Berikan response dalam format JSON berikut:

{
  "food_name": "Nama makanan/minuman",
  "description": "Deskripsi singkat tentang makanan",
  "estimated_portion": "Estimasi porsi (contoh: 250g, 1 mangkuk, dll)",
  "confidence_level": "tinggi/sedang/rendah",
  "nutrition_per_portion": {
    "calories": "kalori (kcal)",
    "protein": "protein (g)",
    "carbohydrates": "karbohidrat (g)",
    "fat": "lemak (g)",
    "fiber": "serat (g)",
    "sugar": "gula (g)",
    "sodium": "natrium (mg)"
  },
  "nutrition_per_100g": {
    "calories": "kalori (kcal)",
    "protein": "protein (g)",
    "carbohydrates": "karbohidrat (g)",
    "fat": "lemak (g)",
    "fiber": "serat (g)",
    "sugar": "gula (g)",
    "sodium": "natrium (mg)"
  },
  "vitamins_minerals": [
    "Vitamin/mineral yang signifikan"
  ],
  "health_notes": [
    "Catatan kesehatan atau tips"
  ],
  "ingredients_estimate": [
    "Estimasi bahan-bahan utama"
  ]
}

PENTING: 
- Berikan hanya output JSON, tanpa teks tambahan
- Semua nilai numerik harus dalam string dengan satuan
- Jika tidak yakin, berikan range nilai dan tulis confidence_level sebagai "rendah"
- Berikan estimasi yang realistis berdasarkan visual makanan
"""
        
        if additional_info:
            prompt += f"\n\nInformasi tambahan dari user: {additional_info}"
        
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
            # Coba extract JSON dari response
            # Kadang LLM menambahkan text sebelum/sesudah JSON
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                nutrition_data = json.loads(json_str)
                return nutrition_data
            else:
                # Jika tidak ada JSON, return raw text
                return {
                    'raw_analysis': response_text,
                    'note': 'Response tidak dalam format JSON yang diharapkan'
                }
                
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {str(e)}")
            return {
                'raw_analysis': response_text,
                'error': 'Gagal parse JSON response',
                'note': 'Data ditampilkan dalam format raw'
            }
    
    def analyze_food_text(self, food_description):
        """
        Analisis deskripsi makanan (text only) untuk mendapatkan estimasi nutrisi
        
        Args:
            food_description: Deskripsi makanan dalam text
            
        Returns:
            dict: Estimasi informasi nutrisi
        """
        try:
            prompt = f"""Berdasarkan deskripsi makanan berikut, berikan estimasi informasi nutrisi dalam format JSON:

Deskripsi: {food_description}

{self._create_nutrition_prompt("")}
"""
            
            completion = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",  # Model text-only
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000,
                top_p=1,
                stream=False
            )
            
            response_text = completion.choices[0].message.content
            nutrition_data = self._parse_nutrition_response(response_text)
            
            return nutrition_data
            
        except Exception as e:
            print(f"Error in text analysis: {str(e)}")
            return {
                'error': f'Error analyzing text: {str(e)}'
            }
