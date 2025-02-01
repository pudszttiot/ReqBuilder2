import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QLabel, QTextEdit, QLineEdit
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QThread, pyqtSignal, Qt


class PipreqsWorker(QThread):
    """Background worker for running the pipreqs command."""
    status_signal = pyqtSignal(str)

    def __init__(self, project_dir, output_path):
        super().__init__()
        self.project_dir = project_dir
        self.output_path = output_path

    def run(self):
        """Run the pipreqs command and emit status updates."""
        try:
            # Use subprocess.run for better handling of the process
            result = subprocess.run(
                ['pipreqs', '--force', '--savepath', self.output_path, self.project_dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW  # Hide console window on Windows
            )

            # Check the result of the process and emit status
            if result.returncode == 0:
                self.status_signal.emit(f"Success: requirements.txt generated at {self.output_path}")
            else:
                self.status_signal.emit(f"Error: {result.stderr.strip() or 'Unknown error occurred'}")

        except FileNotFoundError:
            self.status_signal.emit("Error: pipreqs command not found. Please install pipreqs.")
        except PermissionError:
            self.status_signal.emit("Error: Permission denied. Check your access rights.")
        except Exception as e:
            self.status_signal.emit(f"Unexpected error: {str(e)}")


class PipreqsGUI(QWidget):
    """Main GUI for pipreqs tool."""
    def __init__(self):
        super().__init__()
        self.project_dir = None
        self.init_ui()

    def init_ui(self):
        """Initialize the GUI components."""
        self.setWindowTitle('ReqBuilder 2')
        self.setGeometry(300, 300, 400, 400)
        self.setWindowIcon(QIcon(r"../Images/builder1.png"))

        # Main layout
        layout = QVBoxLayout()

        # Add image at the top
        self.image_label = QLabel(self)
        pixmap = QPixmap(r"../Images/ReqBuilder2_2.png")  # Replace with your image file
        self.image_label.setPixmap(pixmap.scaledToWidth(300, Qt.SmoothTransformation))
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        # Project directory selection button
        select_button = QPushButton('Select Project Directory')
        select_button.clicked.connect(self.select_directory)
        layout.addWidget(select_button)

        # Custom output path input
        layout.addWidget(QLabel("Custom Output Path (Optional):"))
        self.output_path_input = QLineEdit()
        layout.addWidget(self.output_path_input)

        # Generate requirements button
        generate_button = QPushButton('Generate requirements.txt')
        generate_button.clicked.connect(self.generate_requirements)
        layout.addWidget(generate_button)

        # Clear output button
        clear_output_button = QPushButton('Clear Output')
        clear_output_button.clicked.connect(self.clear_output)
        layout.addWidget(clear_output_button)

        # Output text area
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        # Status label
        self.status_label = QLabel("Status: Waiting for action")
        layout.addWidget(self.status_label)

        # Set main layout
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

        # Determine output path (use default if none provided)
        output_path = self.output_path_input.text().strip() or f'{self.project_dir}/requirements.txt'

        if not self.output_path_input.text().strip():
            self.update_output(f"Using default output path: {output_path}")

        self.status_label.setText("Generating requirements.txt...")
        self.output_text.clear()

        # Create and start the background worker
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


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Load custom stylesheet with error handling
    try:
        with open("style.qss", "r") as file:
            app.setStyleSheet(file.read())
    except FileNotFoundError:
        print("Warning: style.qss not found. Proceeding without custom styling.")

    window = PipreqsGUI()
    window.show()

    sys.exit(app.exec_())
