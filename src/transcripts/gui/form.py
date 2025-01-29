import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QInputDialog,
)
from PyQt6.QtCore import QThread, pyqtSignal
from ..utils import download, transcribe


class TranscriptionThread(QThread):
    """Thread for handling video transcription."""

    finished = pyqtSignal(str)

    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path

    def run(self):
        """Run the transcription process."""
        try:
            transcript = transcribe(self.video_path)
            self.finished.emit(transcript)
        except Exception as e:
            self.finished.emit(f"Error: {str(e)}")


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
        self.transcribe_button = QPushButton("Transcribe Video")
        self.transcribe_button.clicked.connect(self.transcribe_video)
        layout.addWidget(self.transcribe_button)

        # Create button to download video from URL
        self.download_button = QPushButton("Download Video from URL")
        self.download_button.clicked.connect(self.download_video)
        layout.addWidget(self.download_button)

    def transcribe_video(self):
        """Handle video transcription."""
        self.transcribe_button.setEnabled(False)

        # Open file dialog to select video
        video_path = self.open_file_dialog(
            "Select Video", "Video files (*.mp4 *.avi *.mkv)"
        )
        if not video_path:
            self.transcribe_button.setEnabled(True)
            return

        # Start transcription in a separate thread
        self.thread = TranscriptionThread(video_path)
        self.thread.finished.connect(self.handle_transcription_finished)
        self.thread.start()

    def handle_transcription_finished(self, transcript):
        """Handle the completion of the transcription."""
        self.transcribe_button.setEnabled(True)

        if transcript.startswith("Error:"):
            QMessageBox.critical(self, "Transcription Error", transcript)
        else:
            # Open file dialog to save transcript
            transcript_path = self.open_file_dialog(
                "Save Transcript", "Text files (*.txt)", save=True
            )
            if transcript_path:
                try:
                    with open(transcript_path, "w") as f:
                        f.write(transcript)
                except Exception as e:
                    QMessageBox.critical(
                        self, "File Error", f"Could not save transcript: {str(e)}"
                    )

    def download_video(self):
        """Handle video download from a URL."""
        url, ok = QInputDialog.getText(self, "Input URL", "Enter video URL:")
        if ok and url:
            save_path = self.open_file_dialog(
                "Save Video", "Video files (*.mp4)", save=True
            )
            if save_path:
                try:
                    download(url, save_path)
                    QMessageBox.information(
                        self, "Success", "Video downloaded successfully."
                    )
                except Exception as e:
                    QMessageBox.critical(
                        self, "Download Error", f"Could not download video: {str(e)}"
                    )

    def open_file_dialog(self, title, filter, save=False):
        """Open a file dialog and return the selected file path."""
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle(title)
        if save:
            file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
            file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        else:
            file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter(filter)
        if file_dialog.exec():
            return file_dialog.selectedFiles()[0]
        return None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
