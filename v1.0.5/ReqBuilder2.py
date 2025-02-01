import sys
import subprocess
import requests
from packaging import version
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QLabel, QTextEdit, QLineEdit, QMessageBox
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QThread, pyqtSignal, Qt

__version__ = "1.0.5"
UPDATE_CHECK_URL = "https://api.github.com/repos/pudszttiot/ReqBuilder2/releases/latest"

class UpdateChecker(QThread):
    """Background worker to check for software updates."""
    update_signal = pyqtSignal(str, str)  # (latest_version, update_url)

    def run(self):
        try:
            response = requests.get(UPDATE_CHECK_URL, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            latest_version = data["tag_name"].lstrip("v")
            update_url = data["html_url"]
            
            if version.parse(latest_version) > version.parse(__version__):
                self.update_signal.emit(latest_version, update_url)
            else:
                self.update_signal.emit("", "")  # No update available
        except requests.RequestException as e:
            print(f"Update check failed: {e}")

class PipreqsWorker(QThread):
    """Background thread to generate requirements.txt."""
    status_signal = pyqtSignal(str)

    def __init__(self, project_dir, output_path):
        super().__init__()
        self.project_dir = project_dir
        self.output_path = output_path

    def run(self):
        """Run pipreqs in a separate thread to avoid freezing the UI."""
        try:
            self.status_signal.emit("Generating requirements.txt...")
            cmd = ["pipreqs", self.project_dir, "--force", "--encoding=utf-8", "--savepath", self.output_path]
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")

            if process.returncode == 0:
                self.status_signal.emit(f"✅ requirements.txt generated at: {self.output_path}")
            else:
                self.status_signal.emit(f"❌ Error: {process.stderr.strip()}")
        except Exception as e:
            self.status_signal.emit(f"⚠️ Exception: {str(e)}")


class PipreqsGUI(QWidget):
    """Main GUI for pipreqs tool."""
    def __init__(self):
        super().__init__()
        self.project_dir = None
        self.init_ui()

    def init_ui(self):
        """Initialize the GUI components."""
        self.setWindowTitle(f'ReqBuilder 2 (v{__version__})')
        self.setGeometry(300, 300, 400, 450)
        self.setWindowIcon(QIcon(r"../Images/builder1.png"))

        layout = QVBoxLayout()

        self.image_label = QLabel(self)
        pixmap = QPixmap(r"../Images/ReqBuilder2_2.png")
        self.image_label.setPixmap(pixmap.scaledToWidth(300, Qt.SmoothTransformation))
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        select_button = QPushButton('Select Project Directory')
        select_button.clicked.connect(self.select_directory)
        layout.addWidget(select_button)

        layout.addWidget(QLabel("Custom Output Path (Optional):"))
        self.output_path_input = QLineEdit()
        layout.addWidget(self.output_path_input)

        generate_button = QPushButton('Generate requirements.txt')
        generate_button.clicked.connect(self.generate_requirements)
        layout.addWidget(generate_button)

        clear_output_button = QPushButton('Clear Output')
        clear_output_button.clicked.connect(self.clear_output)
        layout.addWidget(clear_output_button)

        self.update_button = QPushButton("Check for Updates")
        self.update_button.clicked.connect(self.check_for_updates)
        layout.addWidget(self.update_button)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        self.status_label = QLabel("Status: Waiting for action")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def select_directory(self):
        """Open file dialog to select a project directory."""
        project_dir = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if project_dir:
            self.project_dir = project_dir
            self.status_label.setText(f"Selected Directory: {self.project_dir}")
        else:
            self.status_label.setText("No directory selected.")

    def generate_requirements(self):
        """Start the process to generate requirements.txt."""
        if not self.project_dir:
            self.update_output("Error: No project directory selected.")
            return

        output_path = self.output_path_input.text().strip() or f'{self.project_dir}/requirements.txt'
        if not self.output_path_input.text().strip():
            self.update_output(f"Using default output path: {output_path}")

        self.status_label.setText("Generating requirements.txt...")
        self.output_text.clear()

        self.worker = PipreqsWorker(self.project_dir, output_path)
        self.worker.status_signal.connect(self.update_output)
        self.worker.start()

    def update_output(self, message):
        """Update the output text area and status label."""
        self.output_text.append(message)
        self.status_label.setText(message)

    def clear_output(self):
        """Clear the output text area and reset status."""
        self.output_text.clear()
        self.status_label.setText("Status: Waiting for action")

    def check_for_updates(self):
        """Check if a new version is available when the button is clicked."""
        self.status_label.setText("Checking for updates...")  # Only show when button is clicked
        self.update_checker = UpdateChecker()
        self.update_checker.update_signal.connect(self.notify_update)
        self.update_checker.start()

    def notify_update(self, latest_version, update_url):
        """Notify the user about a new version."""
        if latest_version:
            msg = f"A newer version (v{latest_version}) is available!\nDownload here: {update_url}"
            self.status_label.setText(msg)
            self.output_text.append(msg)
            
            # Show notification dialog
            QMessageBox.information(self, "Update Available", msg)
        else:
            self.status_label.setText("You're using the latest version.")  # No updates available

if __name__ == '__main__':
    app = QApplication(sys.argv)

    try:
        with open("style.qss", "r") as file:
            app.setStyleSheet(file.read())
    except FileNotFoundError:
        print("Warning: style.qss not found. Proceeding without custom styling.")

    window = PipreqsGUI()
    window.show()

    sys.exit(app.exec_())
