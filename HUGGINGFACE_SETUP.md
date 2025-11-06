# Cara Mendapatkan Hugging Face API Key

## 📝 Step-by-Step

### 1. Buat Akun Hugging Face
1. Kunjungi: https://huggingface.co/
2. Klik **Sign Up** di pojok kanan atas
3. Daftar dengan email atau akun Google/GitHub
4. Verifikasi email Anda

### 2. Dapatkan API Token (Access Token)
1. Login ke akun Hugging Face Anda
2. Klik foto profil di pojok kanan atas
3. Pilih **Settings**
4. Di menu sebelah kiri, klik **Access Tokens**
5. Klik tombol **New token**
6. Isi form:
   - **Name**: `food-nutrition-scanner` (atau nama lain)
   - **Role**: Pilih **read** (cukup untuk inference)
7. Klik **Generate token**
8. **Copy token** yang muncul (hanya ditampilkan sekali!)

### 3. Masukkan ke File `.env`
Buka file `.env` dan update:
```properties
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 🤖 Model LLaVA yang Tersedia

Ganti `HUGGINGFACE_MODEL` di `.env` dengan salah satu:

### 1. **LLaVA 1.5** (Recommended - Tercepat)
```properties
HUGGINGFACE_MODEL=llava-hf/llava-1.5-7b-hf
```
- Model: 7B parameters
- Speed: ⚡⚡⚡ Cepat
- Accuracy: ⭐⭐⭐ Good

### 2. **LLaVA 1.6 Mistral** (Balanced)
```properties
HUGGINGFACE_MODEL=llava-hf/llava-v1.6-mistral-7b-hf
```
- Model: 7B parameters (Mistral base)
- Speed: ⚡⚡ Medium
- Accuracy: ⭐⭐⭐⭐ Better

### 3. **LLaVA 1.6 Yi** (High Accuracy)
```properties
HUGGINGFACE_MODEL=llava-hf/llava-v1.6-34b-hf
```
- Model: 34B parameters (Yi base)
- Speed: ⚡ Slower
- Accuracy: ⭐⭐⭐⭐⭐ Best

## ⚠️ Catatan Penting

### Free Tier Limits
Hugging Face Inference API (free tier):
- **Rate limit**: ~60 requests/hour
- **Timeout**: 60 seconds per request
- **Model loading**: Model bisa sleep jika tidak digunakan (butuh 20-30 detik untuk wake up pertama kali)

### Error "Model Loading"
Jika dapat error `503 - Model loading`:
- Tunggu 20-30 detik
- Coba request lagi
- Ini normal untuk free tier

### Upgrade ke Pro (Opsional)
Untuk performa lebih baik:
- Kunjungi: https://huggingface.co/pricing
- **Pro**: $9/bulan
  - Faster inference
  - No cold start
  - Higher rate limits

## 🚀 Testing

Setelah setup API key:
```powershell
# Install dependencies
pip install -r requirements.txt

# Run app
python app.py
```

Test dengan:
```powershell
# Test health check
curl http://localhost:5000/api/health

# Test food analysis
curl -X POST -F "image=@path/to/food.jpg" http://localhost:5000/api/analyze-food
```

## 🔧 Troubleshooting

### Error: "Invalid token"
- Pastikan token dimulai dengan `hf_`
- Regenerate token di Hugging Face settings

### Error: "Model not found"
- Pastikan nama model benar
- Cek availability di: https://huggingface.co/models?pipeline_tag=image-text-to-text

### Slow Response
- Normal untuk free tier
- Model perlu "warm up" di first request
- Consider upgrade ke Pro tier

## 📚 References

- Hugging Face Docs: https://huggingface.co/docs/api-inference/
- LLaVA Models: https://huggingface.co/collections/llava-hf/
- Pricing: https://huggingface.co/pricing
