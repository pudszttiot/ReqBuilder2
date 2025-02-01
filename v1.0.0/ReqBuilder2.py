import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QTextEdit
from PyQt5.QtCore import Qt

class PipreqsGUI(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the window
        self.setWindowTitle('Pipreqs GUI')
        self.setGeometry(300, 300, 400, 300)

        # Set up the layout
        self.layout = QVBoxLayout()

        # Add widgets
        self.status_label = QLabel("Status: Waiting for action", self)
        self.layout.addWidget(self.status_label)

        self.select_button = QPushButton('Select Project Directory', self)
        self.select_button.clicked.connect(self.select_directory)
        self.layout.addWidget(self.select_button)

        self.generate_button = QPushButton('Generate requirements.txt', self)
        self.generate_button.clicked.connect(self.generate_requirements)
        self.layout.addWidget(self.generate_button)

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
        if self.project_dir:
            self.status_label.setText(f"Selected Directory: {self.project_dir}")

    def generate_requirements(self):
        """Generate requirements.txt using pipreqs."""
        if not self.project_dir:
            self.output_text.append("Error: No project directory selected.")
            return

        self.status_label.setText("Generating requirements.txt...")
        self.output_text.clear()

        try:
            # Run the pipreqs command
            result = subprocess.run(
                ['pipreqs', '--force', '--ignore', 'tests', '--savepath', f'{self.project_dir}/requirements.txt', self.project_dir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            if result.returncode == 0:
                self.output_text.append(f"Success: requirements.txt generated at {self.project_dir}/requirements.txt")
            else:
                self.output_text.append(f"Error: {result.stderr}")
                self.status_label.setText("Error generating requirements.txt.")
        except Exception as e:
            self.output_text.append(f"Exception occurred: {str(e)}")
            self.status_label.setText("An error occurred.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PipreqsGUI()
    window.show()
    sys.exit(app.exec_())
