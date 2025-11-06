"""
Test script untuk testing API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_home():
    """Test home endpoint"""
    print("\n=== Testing Home Endpoint ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_scan_barcode(image_path):
    """Test barcode scanning"""
    print(f"\n=== Testing Barcode Scan: {image_path} ===")
    try:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(f"{BASE_URL}/api/scan-barcode", files=files)
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except FileNotFoundError:
        print(f"File not found: {image_path}")
    except Exception as e:
        print(f"Error: {str(e)}")

def test_analyze_food(image_path, description=""):
    """Test food analysis"""
    print(f"\n=== Testing Food Analysis: {image_path} ===")
    try:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            data = {'description': description} if description else {}
            response = requests.post(f"{BASE_URL}/api/analyze-food", files=files, data=data)
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except FileNotFoundError:
        print(f"File not found: {image_path}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("=" * 60)
    print("Food Nutrition Scanner API - Test Script")
    print("=" * 60)
    
    # Test basic endpoints
    test_home()
    test_health_check()
    
    # Uncomment dan sesuaikan path untuk testing dengan gambar
    # test_scan_barcode("path/to/your/barcode.jpg")
    # test_analyze_food("path/to/your/food.jpg", "Nasi goreng dengan telur")
    
    print("\n" + "=" * 60)
    print("Testing selesai!")
    print("=" * 60)
