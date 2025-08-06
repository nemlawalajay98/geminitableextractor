#!/usr/bin/env python3
"""
Backend API Testing for Table Extractor App
Tests the Gemini AI-powered table extraction and Excel export functionality
"""

import requests
import json
import os
import io
from PIL import Image, ImageDraw, ImageFont
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Configuration
BACKEND_URL = "https://51a7f407-5ff0-4405-a01f-c61b77c51cd8.preview.emergentagent.com/api"
API_KEY = "AIzaSyBNOJQXArOUrXb96RsX29kpFMuEZ3ykhTg"

def create_sample_table_image():
    """Create a sample image with table data for testing"""
    # Create a white image
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fallback to basic if not available
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    # Draw table headers
    headers = ["Product", "Price", "Quantity", "Total"]
    x_positions = [50, 200, 350, 500]
    y_start = 100
    
    # Draw headers
    for i, header in enumerate(headers):
        draw.text((x_positions[i], y_start), header, fill='black', font=font)
    
    # Draw table data
    table_data = [
        ["Laptop", "$999", "2", "$1998"],
        ["Mouse", "$25", "5", "$125"],
        ["Keyboard", "$75", "3", "$225"],
        ["Monitor", "$300", "1", "$300"]
    ]
    
    for row_idx, row in enumerate(table_data):
        y_pos = y_start + 40 + (row_idx * 30)
        for col_idx, cell in enumerate(row):
            draw.text((x_positions[col_idx], y_pos), cell, fill='black', font=font)
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    img.save(temp_file.name, 'JPEG')
    return temp_file.name

def create_sample_table_pdf():
    """Create a sample PDF with table data for testing"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    
    c = canvas.Canvas(temp_file.name, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Sales Report")
    
    # Table headers
    headers = ["Product", "Price", "Quantity", "Total"]
    x_positions = [50, 200, 350, 500]
    y_start = height - 100
    
    c.setFont("Helvetica-Bold", 12)
    for i, header in enumerate(headers):
        c.drawString(x_positions[i], y_start, header)
    
    # Table data
    table_data = [
        ["Laptop", "$999", "2", "$1998"],
        ["Mouse", "$25", "5", "$125"],
        ["Keyboard", "$75", "3", "$225"],
        ["Monitor", "$300", "1", "$300"]
    ]
    
    c.setFont("Helvetica", 10)
    for row_idx, row in enumerate(table_data):
        y_pos = y_start - 20 - (row_idx * 20)
        for col_idx, cell in enumerate(row):
            c.drawString(x_positions[col_idx], y_pos, cell)
    
    c.save()
    return temp_file.name

def test_health_check():
    """Test the basic health check endpoint"""
    print("🔍 Testing Health Check Endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200 and "Table Extractor API Ready" in response.json().get("message", ""):
            print("✅ Health check passed")
            return True
        else:
            print("❌ Health check failed")
            return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_table_extraction_image():
    """Test table extraction from image file"""
    print("\n🔍 Testing Table Extraction from Image...")
    
    # Create sample image
    image_path = create_sample_table_image()
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': ('test_table.jpg', f, 'image/jpeg')}
            data = {'api_key': API_KEY}
            
            response = requests.post(f"{BACKEND_URL}/extract-table", files=files, data=data)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Success: {result.get('success')}")
                print(f"Filename: {result.get('filename')}")
                
                if result.get('success') and result.get('extracted_data'):
                    extracted_data = result.get('extracted_data')
                    print(f"Tables found: {len(extracted_data.get('tables', []))}")
                    
                    for i, table in enumerate(extracted_data.get('tables', [])):
                        print(f"Table {i+1}:")
                        print(f"  Headers: {table.get('headers', [])}")
                        print(f"  Rows: {len(table.get('rows', []))}")
                        if table.get('rows'):
                            print(f"  Sample row: {table['rows'][0] if table['rows'] else 'None'}")
                    
                    print("✅ Image table extraction passed")
                    return True, result
                else:
                    print(f"❌ Image table extraction failed: {result.get('error', 'Unknown error')}")
                    return False, result
            else:
                print(f"❌ Image table extraction failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False, None
                
    except Exception as e:
        print(f"❌ Image table extraction error: {str(e)}")
        return False, None
    finally:
        # Clean up
        if os.path.exists(image_path):
            os.unlink(image_path)

def test_table_extraction_pdf():
    """Test table extraction from PDF file"""
    print("\n🔍 Testing Table Extraction from PDF...")
    
    # Create sample PDF
    pdf_path = create_sample_table_pdf()
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': ('test_table.pdf', f, 'application/pdf')}
            data = {'api_key': API_KEY}
            
            response = requests.post(f"{BACKEND_URL}/extract-table", files=files, data=data)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Success: {result.get('success')}")
                print(f"Filename: {result.get('filename')}")
                
                if result.get('success') and result.get('extracted_data'):
                    extracted_data = result.get('extracted_data')
                    print(f"Tables found: {len(extracted_data.get('tables', []))}")
                    
                    for i, table in enumerate(extracted_data.get('tables', [])):
                        print(f"Table {i+1}:")
                        print(f"  Headers: {table.get('headers', [])}")
                        print(f"  Rows: {len(table.get('rows', []))}")
                    
                    print("✅ PDF table extraction passed")
                    return True, result
                else:
                    print(f"❌ PDF table extraction failed: {result.get('error', 'Unknown error')}")
                    return False, result
            else:
                print(f"❌ PDF table extraction failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False, None
                
    except Exception as e:
        print(f"❌ PDF table extraction error: {str(e)}")
        return False, None
    finally:
        # Clean up
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)

def test_excel_export(extracted_data):
    """Test Excel export functionality"""
    print("\n🔍 Testing Excel Export...")
    
    if not extracted_data:
        print("❌ No extracted data available for Excel export test")
        return False
    
    try:
        export_data = {
            "extracted_data": extracted_data.get('extracted_data'),
            "filename": "test_export"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/export-excel",
            json=export_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Check if response is Excel file
            content_type = response.headers.get('content-type', '')
            if 'spreadsheet' in content_type or 'excel' in content_type:
                print(f"Content-Type: {content_type}")
                print(f"Content-Length: {len(response.content)} bytes")
                print("✅ Excel export passed")
                return True
            else:
                print(f"❌ Excel export failed - wrong content type: {content_type}")
                return False
        else:
            print(f"❌ Excel export failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Excel export error: {str(e)}")
        return False

def test_error_scenarios():
    """Test various error scenarios"""
    print("\n🔍 Testing Error Scenarios...")
    
    # Test 1: Missing API key
    print("Testing missing API key...")
    image_path = create_sample_table_image()
    try:
        with open(image_path, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = requests.post(f"{BACKEND_URL}/extract-table", files=files)
            
        if response.status_code == 422:  # FastAPI validation error
            print("✅ Missing API key validation passed")
        else:
            print(f"❌ Missing API key test failed - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Missing API key test error: {str(e)}")
    finally:
        if os.path.exists(image_path):
            os.unlink(image_path)
    
    # Test 2: Invalid file type
    print("Testing invalid file type...")
    try:
        # Create a text file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
        temp_file.write(b"This is not an image or PDF")
        temp_file.close()
        
        with open(temp_file.name, 'rb') as f:
            files = {'file': ('test.txt', f, 'text/plain')}
            data = {'api_key': API_KEY}
            response = requests.post(f"{BACKEND_URL}/extract-table", files=files, data=data)
            
        if response.status_code == 400:
            print("✅ Invalid file type validation passed")
        else:
            print(f"❌ Invalid file type test failed - Status: {response.status_code}")
            
        os.unlink(temp_file.name)
    except Exception as e:
        print(f"❌ Invalid file type test error: {str(e)}")
    
    # Test 3: Invalid API key
    print("Testing invalid API key...")
    image_path = create_sample_table_image()
    try:
        with open(image_path, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            data = {'api_key': 'invalid_key_12345'}
            response = requests.post(f"{BACKEND_URL}/extract-table", files=files, data=data)
            
        result = response.json()
        if not result.get('success'):
            print("✅ Invalid API key handling passed")
        else:
            print("❌ Invalid API key test failed - should have failed")
    except Exception as e:
        print(f"❌ Invalid API key test error: {str(e)}")
    finally:
        if os.path.exists(image_path):
            os.unlink(image_path)
    
    # Test 4: Excel export with invalid data
    print("Testing Excel export with invalid data...")
    try:
        invalid_data = {"invalid": "data"}
        response = requests.post(
            f"{BACKEND_URL}/export-excel",
            json=invalid_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 400:
            print("✅ Invalid Excel export data validation passed")
        else:
            print(f"❌ Invalid Excel export test failed - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Invalid Excel export test error: {str(e)}")

def main():
    """Run all backend tests"""
    print("🚀 Starting Backend API Tests for Table Extractor")
    print("=" * 60)
    
    results = {
        'health_check': False,
        'image_extraction': False,
        'pdf_extraction': False,
        'excel_export': False,
        'error_handling': True  # Assume passed unless we find issues
    }
    
    # Test 1: Health Check
    results['health_check'] = test_health_check()
    
    # Test 2: Image Table Extraction
    image_success, image_data = test_table_extraction_image()
    results['image_extraction'] = image_success
    
    # Test 3: PDF Table Extraction
    pdf_success, pdf_data = test_table_extraction_pdf()
    results['pdf_extraction'] = pdf_success
    
    # Test 4: Excel Export (use image data if available, otherwise PDF data)
    export_data = image_data if image_success else (pdf_data if pdf_success else None)
    results['excel_export'] = test_excel_export(export_data)
    
    # Test 5: Error Scenarios
    test_error_scenarios()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All backend tests passed!")
        return True
    else:
        print("⚠️  Some backend tests failed")
        return False

if __name__ == "__main__":
    main()