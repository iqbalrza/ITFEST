# Food Nutrition Scanner API

Aplikasi Flask untuk scanning barcode makanan kemasan dan analisis nutrisi menggunakan foto dengan AI (Groq LLM).

## Fitur

1. **Scan Barcode**: Scan barcode dari foto makanan kemasan dan dapatkan informasi nutrisi lengkap dari database Open Food Facts
2. **Analisis Foto Makanan**: Upload foto makanan dan dapatkan estimasi nilai nutrisi menggunakan Groq LLM dengan vision capabilities

## Teknologi yang Digunakan

- **Flask**: Web framework Python
- **pyzbar**: Library untuk scanning barcode
- **OpenCV & Pillow**: Image processing
- **Hugging Face LLaVA**: Vision-Language Model untuk analisis nutrisi dari foto
- **Open Food Facts API**: Database produk makanan global

## Instalasi

### 1. Clone atau Download Project

```bash
cd "c:\Users\iqbal\Documents\Code Labs\ITFEST"
```

### 2. Buat Virtual Environment (Opsional tapi Direkomendasikan)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

**Catatan untuk Windows:**
- Untuk `pyzbar`, Anda perlu install **zbar** terlebih dahulu:
  1. Download zbar dari: http://zbar.sourceforge.net/download.html
  2. Atau install via conda: `conda install -c conda-forge pyzbar`
  3. Atau gunakan: `pip install pyzbar-windows` sebagai alternatif

### 4. Setup Environment Variables

Copy file `.env.example` menjadi `.env`:

```powershell
Copy-Item .env.example .env
```

Edit file `.env` dan isi dengan API key Anda:

```
HUGGINGFACE_API_KEY=your-huggingface-api-key-here
```

**Cara mendapatkan Hugging Face API Key:**
1. Buka https://huggingface.co/
2. Daftar/login
3. Masuk ke Settings → Access Tokens
4. Buat token baru dengan role **read**
5. Copy token ke file `.env`

📖 **Panduan lengkap**: Lihat file `HUGGINGFACE_SETUP.md`

## Menjalankan Aplikasi

```powershell
python app.py
```

Aplikasi akan berjalan di `http://localhost:5000`

## API Endpoints

### 1. Home / Info
```
GET /
```
Menampilkan informasi API dan daftar endpoints.

### 2. Scan Barcode
```
POST /api/scan-barcode
```

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: 
  - `image`: File gambar (jpg, jpeg, png)

**Response:**
```json
{
  "success": true,
  "barcode": "8992761001234",
  "nutrition": {
    "product_name": "Nama Produk",
    "brands": "Brand Name",
    "quantity": "250g",
    "nutrition_facts": {
      "energy_kcal": "150 kcal",
      "protein": "3 g",
      "carbohydrates": "25 g",
      "fat": "5 g",
      ...
    },
    "ingredients": "...",
    "nutriscore_grade": "B"
  }
}
```

### 3. Analyze Food Image
```
POST /api/analyze-food
```

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: 
  - `image`: File gambar (jpg, jpeg, png)
  - `description`: (Opsional) Deskripsi tambahan tentang makanan

**Response:**
```json
{
  "success": true,
  "analysis": {
    "food_name": "Nasi Goreng",
    "description": "Nasi goreng dengan telur dan ayam",
    "estimated_portion": "1 piring (300g)",
    "confidence_level": "tinggi",
    "nutrition_per_portion": {
      "calories": "450 kcal",
      "protein": "18 g",
      "carbohydrates": "55 g",
      "fat": "15 g",
      ...
    },
    "nutrition_per_100g": {
      "calories": "150 kcal",
      "protein": "6 g",
      ...
    },
    "health_notes": [
      "Tinggi karbohidrat",
      "Sumber protein yang baik"
    ]
  }
}
```

### 4. Health Check
```
GET /api/health
```

## Contoh Penggunaan dengan cURL

### Scan Barcode:
```powershell
curl -X POST -F "image=@path/to/barcode.jpg" http://localhost:5000/api/scan-barcode
```

### Analyze Food:
```powershell
curl -X POST -F "image=@path/to/food.jpg" -F "description=Nasi goreng dengan telur" http://localhost:5000/api/analyze-food
```

## Contoh Penggunaan dengan Python

```python
import requests

# Scan barcode
with open('barcode.jpg', 'rb') as f:
    files = {'image': f}
    response = requests.post('http://localhost:5000/api/scan-barcode', files=files)
    print(response.json())

# Analyze food
with open('food.jpg', 'rb') as f:
    files = {'image': f}
    data = {'description': 'Nasi goreng dengan telur'}
    response = requests.post('http://localhost:5000/api/analyze-food', files=files, data=data)
    print(response.json())
```

## Struktur Project

```
ITFEST/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── .env.example               # Example environment variables
├── .env                       # Your environment variables (create this)
├── services/
│   ├── barcode_service.py     # Barcode scanning service
│   └── nutrition_service.py   # Groq LLM nutrition analysis service
├── utils/
│   └── image_processor.py     # Image processing utilities
└── uploads/                   # Temporary upload folder (auto-created)
```

## Tips Penggunaan

### Untuk Scan Barcode:
- Pastikan barcode jelas dan tidak blur
- Pencahayaan yang baik akan meningkatkan akurasi
- Foto barcode dari jarak yang cukup dekat

### Untuk Analisis Foto Makanan:
- Ambil foto dengan pencahayaan yang baik
- Foto dari atas (top-down) biasanya lebih baik
- Sertakan informasi tambahan jika perlu (porsi, bahan, dll)
- Hasil adalah **estimasi** berdasarkan visual - bukan nilai pasti

## Troubleshooting

### Error: "No module named 'pyzbar'"
Solusi: Install zbar library terlebih dahulu (lihat bagian instalasi)

### Error: "GROQ_API_KEY tidak ditemukan"
Solusi: Pastikan file `.env` sudah dibuat dan berisi API key yang valid

### Error: Barcode tidak terdeteksi
Solusi: 
- Coba foto ulang dengan lebih jelas
- Pastikan barcode tidak terpotong
- Coba dengan pencahayaan yang lebih baik

## Pengembangan Lebih Lanjut

Beberapa ide untuk pengembangan:
- [ ] Tambahkan frontend web/mobile
- [ ] Simpan history pencarian
- [ ] Tambahkan user authentication
- [ ] Export data ke PDF
- [ ] Integrasikan dengan database nutrisi lokal
- [ ] Tambahkan fitur meal planning
- [ ] Tambahkan fitur tracking kalori harian

## Lisensi

MIT License

## Kontribusi

Pull requests are welcome! Untuk perubahan besar, silakan buka issue terlebih dahulu.

---

**Note**: Aplikasi ini menggunakan estimasi AI untuk analisis foto makanan. Hasil tidak 100% akurat dan sebaiknya digunakan sebagai referensi saja, bukan untuk kebutuhan medis atau diet ketat.
