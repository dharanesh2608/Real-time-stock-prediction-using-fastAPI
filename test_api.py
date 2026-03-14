import requests
import json

def test_api_endpoints():
    """Test the API with different stock symbols"""
    base_url = "http://127.0.0.1:8000"
    
    # Test symbols
    test_symbols = ["AAPL", "GOOGL", "INVALID", "XYZ123", "META", "FACEBOOK"]
    
    print("Testing API Endpoints")
    print("=" * 40)
    
    for symbol in test_symbols:
        print(f"\n🔍 Testing symbol: {symbol}")
        
        # Test fetch-data endpoint
        try:
            response = requests.post(
                f"{base_url}/fetch-data",
                json={"symbol": symbol},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {symbol} - SUCCESS")
                print(f"   Data points: {data['data_points']}")
                print(f"   Latest date: {data['latest_date']}")
                print(f"   Columns: {', '.join(data['columns'])}")
            else:
                error_data = response.json()
                print(f"❌ {symbol} - ERROR {response.status_code}")
                print(f"   Message: {error_data.get('detail', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ {symbol} - REQUEST FAILED: {str(e)}")

if __name__ == "__main__":
    test_api_endpoints()
