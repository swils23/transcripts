import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QFileDialog, QLabel
from PyQt6.QtCore import QThread, pyqtSignal


class TranscribeWorker(QThread):
    progress = pyqtSignal(str)  # Signal to update status
    finished = pyqtSignal(str)  # Signal to emit transcript
    error = pyqtSignal(str)  # Signal for error handling

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            from ..utils import normalize_url, download_and_transcribe

            # Check URL
            self.progress.emit("Validating URL...")
            is_valid, result = normalize_url(self.url)
            if not is_valid:
                self.error.emit(result)
                return

            # Download and transcribe
            self.progress.emit("Downloading...")
            transcript = download_and_transcribe(url=self.url)
            self.progress.emit("Transcription complete")
            self.finished.emit(transcript)

        except Exception as e:
            self.error.emit(str(e))


class TranscribeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transcribe")
        self.setMinimumSize(400, 200)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # URL field
        self.url_field = QLineEdit()
        self.url_field.setPlaceholderText("Enter URL here")
        layout.addWidget(self.url_field)

        # Download button
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.start_download)
        layout.addWidget(self.download_button)

        # Status label
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # Store worker reference
        self.worker = None
        self.transcript = None

    def start_download(self):
        if self.worker and self.worker.isRunning():
            return

        url = self.url_field.text()
        if not url:
            self.status_label.setText("Please enter a URL")
            return

        # Disable input while processing
        self.download_button.setEnabled(False)
        self.url_field.setEnabled(False)

        # Create and start worker thread
        self.worker = TranscribeWorker(url)
        self.worker.progress.connect(self.update_status)
        self.worker.finished.connect(self.handle_transcript)
        self.worker.error.connect(self.handle_error)
        self.worker.start()

    def update_status(self, message):
        self.status_label.setText(message)

    def handle_error(self, error_message):
        self.status_label.setText(f"Error: {error_message}")
        self.download_button.setEnabled(True)
        self.url_field.setEnabled(True)

    def handle_transcript(self, transcript):
        self.transcript = transcript
        self.save_transcript()

    def save_transcript(self):
        output_file, _ = QFileDialog.getSaveFileName(self, "Save Transcript", "", "Text Files (*.txt)")
        if output_file:
            try:
                with open(output_file, "w") as f:
                    f.write(self.transcript)
                self.status_label.setText("Transcript saved successfully")
            except Exception as e:
                self.status_label.setText(f"Error saving file: {str(e)}")

        # Reset UI
        self.download_button.setEnabled(True)
        self.url_field.setEnabled(True)
        self.transcript = None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transcript Manager")
        self.setMinimumSize(300, 150)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Create button to open transcribe window
        self.transcribe_button = QPushButton("Open Transcribe Window")
        self.transcribe_button.clicked.connect(self.open_transcribe_window)
        layout.addWidget(self.transcribe_button)

        # Store reference to transcribe window
        self.transcribe_window = None

    def open_transcribe_window(self):
        if self.transcribe_window is None:
            self.transcribe_window = TranscribeWindow()
        self.transcribe_window.show()
