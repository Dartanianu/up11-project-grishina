import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
            }
            QLable {
                color: #000000
            }
        """)

        self.setWindowTitle("Сумки и аксессуары")
        self.resize(800, 600)
        
        self.setWindowIcon(QIcon('resources/icon.ico'))
        
        central = QWidget()
        layout = QVBoxLayout()
        logo = QLabel()
        logo.setPixmap(QPixmap('resources/logo.png'))
        layout.addWidget(logo)
        
        central.setLayout(layout)
        self.setCentralWidget(central)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())