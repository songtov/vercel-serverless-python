from http.server import BaseHTTPRequestHandler
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

def get_current_time():
    now = datetime.now()
    return now.strftime('%Y%m%d')

def filter_rain_data(data):
    filtered_data = []
    for item in data:
        if item['category'] == 'PCP':
            filtered_data.append(item)
    return filtered_data

def rains_today(data):
    for item in data:
        if item['fcstDate'] == get_current_time() and item['fcstValue'] != '강수없음':
            return True
    return False

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Get API credentials
        api_key = os.getenv("API_KEY")
        if not api_key:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('Error: API_KEY not found in environment variables'.encode('utf-8'))
            return

        # Base URL for the weather API
        base_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
        
        # Parameters for the API request
        params = {
            'serviceKey': api_key,
            'numOfRows': '500',
            'dataType': 'JSON',
            'base_date': get_current_time(),
            'base_time': '0500',
            'nx': '63',
            'ny': '126'
        }
        

        try:
            # Make the API request
            response = requests.get(base_url, params=params)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    filtered_rain_data = filter_rain_data(data['response']['body']['items']['item'])
                    result = {
                        "status": "success",
                        "rains_today": rains_today(filtered_rain_data),
                        "message": "Rains today" if rains_today(filtered_rain_data) else "No rains today"
                    }
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode('utf-8'))

                    
                except ValueError as e:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "status": "error",
                        "message": f'Error parsing JSON: {str(e)}'
                    }).encode('utf-8'))
            else:
                self.send_response(response.status_code)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": f'Weather API request failed with status code: {response.status_code}'
                }).encode('utf-8'))
                
        except requests.exceptions.RequestException as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "error",
                "message": f'Request failed: {str(e)}'
            }).encode('utf-8'))
