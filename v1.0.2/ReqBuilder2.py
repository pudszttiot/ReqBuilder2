import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QTextEdit, QLineEdit
from PyQt5.QtCore import QThread, pyqtSignal

class PipreqsWorker(QThread):
    status_signal = pyqtSignal(str)

    def __init__(self, project_dir, output_path):
        super().__init__()
        self.project_dir = project_dir
        self.output_path = output_path

    def run(self):
        """Run pipreqs command and update the status message."""
        try:
            # Run pipreqs command and capture output
            process = subprocess.Popen(
                ['pipreqs', '--force', '--savepath', self.output_path, self.project_dir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, 
                creationflags=subprocess.CREATE_NO_WINDOW  # Hide the console window on Windows
            )
            stdout, stderr = process.communicate()

            # Update based on return code
            if process.returncode == 0:
                self.status_signal.emit(f"Success: requirements.txt generated at {self.output_path}")
            else:
                self.status_signal.emit(f"Error: {stderr.strip()}")

        except FileNotFoundError:
            self.status_signal.emit("Error: pipreqs command not found. Please install pipreqs or check your environment.")
        except PermissionError:
            self.status_signal.emit("Error: Permission denied. Please check your access rights.")
        except Exception as e:
            self.status_signal.emit(f"Exception occurred: {str(e)}")


class PipreqsGUI(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the window
        self.setWindowTitle('ReqBuilder 2')
        self.setGeometry(300, 300, 400, 300)

        # Set up the layout
        self.layout = QVBoxLayout()

        # Add widgets
        self.status_label = QLabel("Status: Waiting for action", self)
        self.layout.addWidget(self.status_label)

        self.select_button = QPushButton('Select Project Directory', self)
        self.select_button.clicked.connect(self.select_directory)
        self.layout.addWidget(self.select_button)

        self.custom_output_label = QLabel("Custom Output Path (Optional):", self)
        self.layout.addWidget(self.custom_output_label)

        self.output_path_input = QLineEdit(self)
        self.layout.addWidget(self.output_path_input)

        self.generate_button = QPushButton('Generate requirements.txt', self)
        self.generate_button.clicked.connect(self.generate_requirements)
        self.layout.addWidget(self.generate_button)

        self.clear_output_button = QPushButton('Clear Output', self)
        self.clear_output_button.clicked.connect(self.clear_output)
        self.layout.addWidget(self.clear_output_button)

        self.output_text = QTextEdit(self)
        self.output_text.setReadOnly(True)
        self.layout.addWidget(self.output_text)

        # Set layout for the window
        self.setLayout(self.layout)

        # To store the selected directory
        self.project_dir = None

    def select_directory(self):
        """Open file dialog to select project directory."""
        self.project_dir = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if not self.project_dir:
            self.status_label.setText("No directory selected.")
            return
        self.status_label.setText(f"Selected Directory: {self.project_dir}")

    def generate_requirements(self):
        """Generate requirements.txt using pipreqs."""
        if not self.project_dir:
            self.output_text.append("Error: No project directory selected.")
            self.status_label.setText("Status: No project directory selected.")
            return

        self.status_label.setText("Generating requirements.txt...")
        self.output_text.clear()

        # Get the custom output path
        output_path = self.output_path_input.text() or f'{self.project_dir}/requirements.txt'

        # Inform user if default path is used
        if not self.output_path_input.text():
            self.output_text.append(f"Using default output path: {output_path}")

        # Create worker thread to handle pipreqs process
        self.worker = PipreqsWorker(self.project_dir, output_path)
        self.worker.status_signal.connect(self.update_output)
        self.worker.start()

    def update_output(self, text):
        """Update the output text area and status message."""
        cursor = self.output_text.textCursor()
        cursor.movePosition(cursor.End)
        self.output_text.setTextCursor(cursor)
        self.output_text.append(text)
        self.status_label.setText(text)

    def clear_output(self):
        """Clear the output text area."""
        self.output_text.clear()
        self.status_label.setText("Status: Waiting for action")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PipreqsGUI()
    window.show()
    sys.exit(app.exec_())
