from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from services.barcode_service import BarcodeService
from services.huggingface_service import HuggingFaceService
from utils.image_processor import ImageProcessor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Konfigurasi
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16MB
app.config['UPLOAD_FOLDER'] = 'uploads'

# Pastikan folder upload ada
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize services
barcode_service = BarcodeService()
nutrition_service = HuggingFaceService()  # Menggunakan Hugging Face
image_processor = ImageProcessor()

@app.route('/')
def home():
    return jsonify({
        'message': 'Food Nutrition Scanner API',
        'version': '1.0.0',
        'endpoints': {
            '/api/scan-barcode': 'POST - Scan barcode dari gambar',
            '/api/analyze-food': 'POST - Analisis foto makanan dengan AI'
        }
    })

@app.route('/api/scan-barcode', methods=['POST'])
def scan_barcode():
    """
    Endpoint untuk scan barcode dari gambar
    """
    try:
        # Validasi apakah ada file yang diupload
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Tidak ada file gambar yang diupload'
            }), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Nama file kosong'
            }), 400
        
        # Validasi format file
        if not image_processor.allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Format file tidak didukung. Gunakan: jpg, jpeg, png'
            }), 400
        
        # Proses gambar
        image = image_processor.process_uploaded_file(file)
        
        # Scan barcode
        barcode_data = barcode_service.scan_barcode(image)
        
        if not barcode_data:
            return jsonify({
                'success': False,
                'error': 'Tidak ditemukan barcode pada gambar'
            }), 404
        
        # Ambil informasi nutrisi dari API
        nutrition_info = barcode_service.get_nutrition_info(barcode_data)
        
        return jsonify({
            'success': True,
            'barcode': barcode_data,
            'nutrition': nutrition_info
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze-food', methods=['POST'])
def analyze_food():
    """
    Endpoint untuk analisis foto makanan menggunakan Groq LLM
    """
    try:
        # Validasi apakah ada file yang diupload
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Tidak ada file gambar yang diupload'
            }), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Nama file kosong'
            }), 400
        
        # Validasi format file
        if not image_processor.allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Format file tidak didukung. Gunakan: jpg, jpeg, png'
            }), 400
        
        # Ambil deskripsi tambahan jika ada
        additional_info = request.form.get('description', '')
        
        # Proses gambar
        image = image_processor.process_uploaded_file(file)
        
        # Convert image ke base64 untuk dikirim ke LLM
        image_base64 = image_processor.image_to_base64(image)
        
        # Analisis dengan Groq LLM
        nutrition_analysis = nutrition_service.analyze_food_image(
            image_base64, 
            additional_info
        )
        
        return jsonify({
            'success': True,
            'analysis': nutrition_analysis
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'services': {
            'barcode_scanner': 'operational',
            'huggingface_llava': 'operational' if os.getenv('HUGGINGFACE_API_KEY') else 'not configured'
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True') == 'True'
    app.run(host='0.0.0.0', port=port, debug=debug)
