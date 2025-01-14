import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QLabel)
from PyQt5.QtCore import Qt
import requests
import urllib.parse

def parse_pnu(pnu):
    """
    Parse PNU code into its components
    
    :param pnu: 19-digit PNU code
    :return: Dictionary containing PNU components
    """
    if len(pnu) != 19:
        raise ValueError("PNU must be 19 digits")
        
    # 산구분코드 처리
    san_value = pnu[10:11]
    if not san_value:
        raise ValueError("Invalid PNU format: missing plat_gb_cd")
    
    return {
        'sigungu_cd': pnu[0:5],      # 시군구코드 (앞 5자리)
        'bjdong_cd': pnu[5:10],      # 법정동코드 (다음 5자리)
        'plat_gb_cd': str(int(san_value) - 1),  # 산여부 (0->-1, 1->0)
        'bun': pnu[11:15].zfill(4),  # 본번 (4자리로 채우기)
        'ji': pnu[15:].zfill(4)      # 부번 (4자리로 채우기)
    }

def fetch_building_info(service_key, sigungu_cd, bjdong_cd, plat_gb_cd, bun, ji, rows=1, page=1, response_type="json"):
    """
    Fetch building registry information based on parameters from the OpenAPI.

    :param service_key: Decoded service key from the public data portal
    :param sigungu_cd: City/district code
    :param bjdong_cd: Legal dong code
    :param plat_gb_cd: Land classification code (0: land, 1: mountain, etc.)
    :param bun: Main lot number
    :param ji: Sub lot number
    :param rows: Number of rows per page
    :param page: Page number
    :param response_type: Response format (json or xml)
    :return: API response in JSON format
    """
    # Base URL for the API
    base_url = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrTitleInfo"

    # API parameters
    params = {
        "serviceKey": service_key,
        "sigunguCd": sigungu_cd,
        "bjdongCd": bjdong_cd,
        "platGbCd": plat_gb_cd,
        "bun": bun,
        "ji": ji,
        "numOfRows": rows,
        "pageNo": page,
        "_type": response_type
    }

    try:
        # Send a GET request
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        if response_type == "json":
            # Print raw response for debugging
            print("Raw response:", response.text)
            
            # Check if response is empty
            if not response.text.strip():
                return {"error": "Empty response received from server"}
                
            try:
                return response.json()
            except ValueError as json_err:
                return {"error": f"Failed to parse JSON response: {json_err}", "raw_response": response.text}
        else:
            return response.text
    except requests.exceptions.ConnectionError:
        return {"error": "Connection error occurred. Please check your network or the API server."}
    except requests.exceptions.Timeout:
        return {"error": "The request timed out. Please try again later."}
    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred: {e}"}

def format_building_info(item):
    """건축물 정보를 보기 좋게 포맷팅"""
    return f"""
📍 기본 정보
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 건물명: {item['bldNm']}
• 지번 주소: {item['platPlc']}
• 도로명 주소: {item['newPlatPlc']}
• 동번호: {item['dongNm']}

🏗️ 건축물 규모
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 건축면적: {item['archArea']}㎡
• 연면적: {item['totArea']}㎡
• 용적률: {item['vlRat']}%
• 건폐율: {item['bcRat']}%
• 지상층수: {item['grndFlrCnt']}층
• 지하층수: {item['ugrndFlrCnt']}층
• 세대수: {item['hhldCnt']}세대

🏠 건축물 특성
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 구조: {item['strctCdNm']}
• 주용도: {item['mainPurpsCdNm']}
• 세부용도: {item['etcPurps']}
• 지붕: {item['roofCdNm']}

📅 인허가 정보
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 허가일: {item['pmsDay']}
• 사용승인일: {item['useAprDay']}"""

def print_response_summary(response):
    """API 응답 결과 요약 출력"""
    items = response['response']['body']['items']['item']
    total_count = response['response']['body']['totalCount']
    
    print(f"\n🏢 총 {total_count}개의 건축물이 검색되었습니다.\n")
    
    for item in items:
        print(format_building_info(item))
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

class BuildingInfoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Input area
        input_layout = QHBoxLayout()
        self.pnu_input = QLineEdit()
        self.pnu_input.setPlaceholderText("PNU를 입력하세요 (19자리)")
        self.search_btn = QPushButton("검색")
        self.search_btn.clicked.connect(self.search_building)
        
        input_layout.addWidget(self.pnu_input)
        input_layout.addWidget(self.search_btn)
        
        # Result area
        self.result_view = QTextEdit()
        self.result_view.setReadOnly(True)
        
        # Add widgets to main layout
        layout.addLayout(input_layout)
        layout.addWidget(self.result_view)
        
        # Window settings
        self.setWindowTitle('건축물대장 조회')
        self.setGeometry(300, 300, 800, 600)
        
    def search_building(self):
        try:
            pnu = self.pnu_input.text().strip()
            
            # Validate PNU
            if len(pnu) != 19:
                raise ValueError("PNU는 반드시 19자리여야 합니다.")
            
            if not pnu.isdigit():
                raise ValueError("PNU는 숫자로만 구성되어야 합니다.")
            
            # Parse PNU and get parameters
            params = parse_pnu(pnu)
            
            # Decode the service key
            service_key = urllib.parse.unquote("Lvn%2FX9ciaH3OcErj46QABbDpndkMA%2FBR6ZJmLMlTOO1No1vGocwgMhcp%2BVKl%2BShi8et1lD%2BVhhVAdQNi%2BtkKGw%3D%3D")
            
            # Fetch building information
            building_info = fetch_building_info(
                service_key=service_key,
                **params,
                rows=10,
                page=1
            )
            
            # Format and display results
            self.display_results(params, building_info)
            
        except ValueError as e:
            self.result_view.setText(f"❌ 오류: {e}")
        except Exception as e:
            self.result_view.setText(f"❌ 예상치 못한 오류가 발생했습니다: {e}")
    
    def display_results(self, params, building_info):
        # Format header information
        header = f"""=== 건축물대장 정보 ===
▶ 조회 파라미터:
  - 시군구코드: {params['sigungu_cd']}
  - 법정동코드: {params['bjdong_cd']}
  - 대지구분: {params['plat_gb_cd']}
  - 본번: {params['bun']}
  - 부번: {params['ji']}

▶ API 응답:"""
        
        # Get items from response
        items = building_info['response']['body']['items']['item']
        total_count = building_info['response']['body']['totalCount']
        
        # Format building information
        result_text = f"{header}\n\n🏢 총 {total_count}개의 건축물이 검색되었습니다.\n"
        
        for item in items:
            result_text += format_building_info(item)
            result_text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        self.result_view.setText(result_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BuildingInfoWindow()
    window.show()
    sys.exit(app.exec_())
