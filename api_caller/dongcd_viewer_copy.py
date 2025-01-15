from qgis.PyQt.QtWidgets import (QDockWidget, QVBoxLayout, QPushButton, 
                                QFileDialog, QTableWidget, QTableWidgetItem, 
                                QWidget, QLineEdit, QHBoxLayout, QLabel)
from qgis.PyQt.QtCore import Qt
import csv

class CsvViewerDockWidget(QDockWidget):
    def __init__(self, iface):
        super().__init__("법정동코드 미리보기 by Bong")
        self.iface = iface
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea)

        # Create widget and layout
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        # Add button to open CSV file
        self.open_button = QPushButton("Open CSV")
        self.open_button.clicked.connect(self.open_csv)
        self.layout.addWidget(self.open_button)

        # 검색 기능 추가
        self.search_layout = QHBoxLayout()
        self.search_label = QLabel("검색:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("검색어를 입력하세요...")
        self.search_input.textChanged.connect(self.search_table)
        
        self.search_layout.addWidget(self.search_label)
        self.search_layout.addWidget(self.search_input)
        self.layout.insertLayout(1, self.search_layout)  # Open CSV 버튼과 테이블 사이에 추가

        # 원본 데이터 저장용 변수
        self.original_data = []
        
        # Add table widget to display CSV content
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.setWidget(self.widget)

    def search_table(self):
        search_text = self.search_input.text().lower()
        
        # 검색어가 비어있으면 원본 데이터 모두 표시
        if not search_text:
            self.display_data(self.original_data)
            return
            
        # 검색 결과 필터링
        filtered_data = []
        for row_data in self.original_data:
            if any(search_text in str(cell).lower() for cell in row_data):
                filtered_data.append(row_data)
                
        # 필터링된 결과 표시
        self.display_data(filtered_data)
        
    def display_data(self, data):
        self.table.setRowCount(len(data))
        for row, row_data in enumerate(data):
            for col, cell_data in enumerate(row_data):
                self.table.setItem(row, col, QTableWidgetItem(str(cell_data)))
        self.table.resizeColumnsToContents()

    def open_csv(self):
        # 시작 디렉토리 지정
        start_directory = "C:/Users/dohwa/Desktop/유틸리티/법정동코드/법정동코드 전체자료_250113"
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "CSV 파일 선택",
            start_directory,
            "CSV files (*.csv)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as csv_file:
                    csv_reader = csv.reader(csv_file)
                    headers = next(csv_reader)
                    self.original_data = list(csv_reader)  # 원본 데이터 저장

                # 테이블 초기화
                self.table.clear()
                self.table.setColumnCount(len(headers))
                self.table.setHorizontalHeaderLabels(headers)
                
                # 데이터 표시
                self.display_data(self.original_data)
                
                # 검색창 초기화
                self.search_input.clear()
                
            except UnicodeDecodeError:
                # ... existing error handling code ...

# Create and show the dock widget
csv_viewer = CsvViewerDockWidget(iface)
iface.addDockWidget(Qt.RightDockWidgetArea, csv_viewer)
csv_viewer.show()
