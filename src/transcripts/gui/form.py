import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton
)

class MainWindow(QMainWindow):
    """
    Main window, containing:
    - URL input field
    - Transcript output file location selection
    - Progress bar
    - Log output
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transcripts")
        self.setMinimumSize(400, 200)
        
        # Create a central widget and set the layout to it
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # URL field
        self.url_field = QLineEdit()
        self.url_field.setPlaceholderText("Enter URL here")

        # Download button
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.download_transcript)


        layout = QVBoxLayout()
        layout.addWidget(self.url_field)
        layout.addWidget(self.download_button)
        central_widget.setLayout(layout)  # Set layout to central widget instead of main window

    def download_transcript(self):
        # Check URL
        url = self.url_field.text()
        from ..utils import normalize_url
        is_valid, result = normalize_url(url)
        if not is_valid:
            print(result)
            return
        
        # Download and transcribe
        from ..utils import download_and_transcribe
        transcript = download_and_transcribe(url=url)
        print(transcript)
        

        
