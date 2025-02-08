import sys
import subprocess
import requests
import webbrowser
from packaging import version
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QLabel, QTextEdit, QLineEdit, QMessageBox, QDesktopWidget
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import os

__version__ = "1.0.8"
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
    status_signal = pyqtSignal(str)  # For the status label
    output_signal = pyqtSignal(str)  # For the output text box

    def __init__(self, project_dir, output_path):
        super().__init__()
        self.project_dir = project_dir
        self.output_path = output_path

    def run(self):
        """Run pipreqs in a separate thread to avoid freezing the UI."""
        try:
            self.status_signal.emit("🔄 Generating requirements.txt... Please wait.")
            cmd = ["pipreqs", self.project_dir, "--force", "--encoding=utf-8", "--savepath", self.output_path]

            if sys.platform == "win32":
                process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")

            if process.returncode == 0:
                self.status_signal.emit("✅ requirements.txt successfully generated.")
                self.output_signal.emit(f"✅ Successfully saved at: {self.output_path}\n\n{process.stdout}")
            else:
                self.status_signal.emit("❌ Failed to generate requirements.txt.")
                self.output_signal.emit(f"❌ Error: {process.stderr.strip()}")
        except Exception as e:
            self.status_signal.emit("⚠️ An error occurred.")
            self.output_signal.emit(f"⚠️ Exception: {str(e)}")


class PipreqsGUI(QWidget):
    """Main GUI for pipreqs tool."""
    def __init__(self):
        super().__init__()
        self.project_dir = None
        self.init_ui()

    def init_ui(self):
        """Initialize the GUI components."""
        self.setWindowTitle(f'ReqBuilder 2 (v{__version__})')
        self.setWindowIcon(QIcon(r"../Images/ReqBuilder_2_Logo.png"))
        self.setFixedSize(450, 850)  # Prevent resizing of the window

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

        # Set word wrap for status label
        self.status_label = QLabel('<span style="color: #F5F5F5; font-weight: bold;">Status:</span> Waiting for action')
        self.status_label.setWordWrap(True)  # Enable text wrapping
        self.status_label.setObjectName("status_label")
        layout.addWidget(self.status_label)


        self.setLayout(layout)

        self.center_window()  # Center the window on the screen

    def center_window(self):
        """Center the window on the screen."""
        screen_geometry = QDesktopWidget().availableGeometry()  # Get screen size
        window_geometry = self.frameGeometry()  # Get window size
        center_point = screen_geometry.center()  # Get center of the screen
        window_geometry.moveCenter(center_point)  # Move window to the center
        self.move(window_geometry.topLeft())  # Move window to the top-left of the geometry

    def select_directory(self):
        """Open file dialog to select a project directory."""
        project_dir = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if project_dir:
            self.project_dir = project_dir
            # Set the text with HTML for custom styling
            self.status_label.setText(f"<font color='#ffffff'>Selected Directory:</font> {self.project_dir}")
            
            # Change the background color to green (successful directory selection)
            self.status_label.setStyleSheet("QLabel#status_label { "
                                            "color: #00ff00; "
                                            "background-color: #065535; "
                                            "padding: 5px; }")  # Green background
            
        else:
            self.status_label.setText("<font color='#fe0000'>No directory selected.</font>")
            
            # Change the background color to red (no directory selected)
            self.status_label.setStyleSheet("QLabel#status_label { "
                                            "color: #ff0000; "
                                            "background-color: #190000; "
                                            "padding: 5px; }")

            



    def generate_requirements(self):
        """Start the process to generate requirements.txt."""
        if not self.project_dir:
            self.status_label.setText("⚠️ No project directory selected.")
            self.output_text.append("Error: No project directory selected.")
            self.status_label.setStyleSheet("QLabel#status_label { color: #ff0000; background-color: #190000; padding: 5px; }")
            return

        output_path = self.output_path_input.text().strip() or f'{self.project_dir}/requirements.txt'

        self.status_label.setText("🔄 Generating requirements.txt...")
        self.status_label.setStyleSheet("QLabel#status_label { color: #ffff00; background-color: #333300; padding: 5px; }")
        
        self.output_text.clear()

        self.worker = PipreqsWorker(self.project_dir, output_path)
        self.worker.status_signal.connect(self.update_status)
        self.worker.output_signal.connect(self.update_output)
        self.worker.start()


    def update_output(self, message):
        """Update the output text area (without affecting status label)."""
        self.output_text.append(message)

    def update_status(self, message):
        """Update the status label separately from the output box."""
        self.status_label.setText(message)


    def clear_output(self):
        """Clear the output text area and reset status."""
        self.output_text.clear()
        self.status_label.setText('<span style="color: #F5F5F5; font-weight: bold;">Status:</span> Waiting for action')

        # Change status label color to green (successful directory selection)
        self.status_label.setStyleSheet("QLabel#status_label { color: #FFF01F; }")

    def check_for_updates(self):
        """Check if a new version is available when the button is clicked."""
        self.status_label.setText("Checking for updates...")  # Only show when button is clicked
        # Change status label color to green (successful directory selection)
        self.status_label.setStyleSheet("QLabel#status_label { "
                                       "color: #ffaa00; "
                                       "background-color: #664400; "
                                       "padding: 5px; "  # Optional: Add some padding for better visibility
                                       "border-radius: 5px; "  # Optional: Add rounded corners
                                       "font-weight: bold; "  # Optional: Make the text bold
                                       "}")


        
        self.update_checker = UpdateChecker()
        self.update_checker.update_signal.connect(self.notify_update)
        self.update_checker.start()

    def notify_update(self, latest_version, update_url):
        """Notify the user about a new version."""
        if latest_version:
            msg = f"A newer version (v{latest_version}) is available!\nDo you want to download it now?"
            reply = QMessageBox.question(self, "Update Available", msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                webbrowser.open(update_url)
        else:
            self.status_label.setText("You're using the latest version!")
            self.status_label.setStyleSheet("QLabel#status_label { "
                                           "color: #c14cf5; "
                                           "background-color: #1d002b; "
                                           "padding: 5px; "  # Optional: Add some padding for better visibility
                                           "border-radius: 5px; "  # Optional: Add rounded corners
                                           "font-weight: bold; "  # Optional: Make the text bold
                                           "}")


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
