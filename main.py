import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QScrollArea, QPushButton
)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from database import Database


def create_card(products):
    card = QWidget()
    card.setObjectName("productCard")
    card.setStyleSheet("""
        #productCard {
            border: 1px solid #000000;
            border-radius: 4px;
            background-color: #FFFFFF;
        }
    """)

    main_layout = QHBoxLayout(card)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(15)

    image_lable = QLabel()
    image_lable.setFixedSize(100, 100)
    image_lable.setAlignment(Qt.AlignCenter)
    image_lable.setStyleSheet("border: 1px solid #000000;")

    file_name = products[5]
    
    if file_name:
        image_path = os.path.join("Images", file_name)
    else:
        image_path = os.path.join("resources", "picture.png")

    pixmap = QPixmap(image_path)
    
    if pixmap.isNull():
        image_lable.setText("IMG")
    else:
        image_lable.setPixmap(
            pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        
    main_layout.addWidget(image_lable)

    text_layout = QVBoxLayout()
    text_layout.setSpacing(5)
    
    title = QLabel(f"Производство | {products[1]}")
    title.setStyleSheet("font-weight: bold; font-size: 14px; border: none;")
    
    category_label = QLabel(f"Категория: {products[7]}")
    category_label.setStyleSheet("border: none;")
    
    quantity_label = QLabel(f"Количество: {products[9]}")
    quantity_label.setStyleSheet("border: none;")
    
    compound_label = QLabel(f"Состав: {products[3]}")
    compound_label.setStyleSheet("border: none;")
    compound_label.setWordWrap(True)

    text_layout.addWidget(title)
    text_layout.addWidget(category_label)
    text_layout.addWidget(quantity_label)
    text_layout.addWidget(compound_label)
    text_layout.addStretch()

    main_layout.addLayout(text_layout, 1)

    price_label = QLabel(f"{products[4]} ₽")
    price_label.setAlignment(Qt.AlignTop | Qt.AlignRight)
    price_label.setStyleSheet("font-size: 14px; border: none;")
    main_layout.addWidget(price_label)

    return card


class MainWindow(QMainWindow):
    def __init__(self, role_id=None):
        super().__init__()
        self.role_id = role_id
        self.setup_ui()
        self.setup_role_interface()
        
        self.db = Database(
            host='localhost',
            port=5432,
            dbname="database",
            user="postgres",
            password="123"
        )

        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
                font-family: 'Calibri';
            }
            QLabel {
                color: #000000;
            }
        """)

        self.setWindowTitle("Сумки и аксессуары")
        self.resize(800, 600)
        self.setWindowIcon(QIcon('resources/icon.ico'))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        scroll_content.setStyleSheet("#scrollContent { background-color: #FFFFFF; }") 

        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = QLabel("Сумки и аксессуары - Каталог")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        logo = QLabel()
        logo.setPixmap(QPixmap('resources/logo.png'))
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        products = self.db.get_products()
        print(f"Загружено товаров: {len(products)}")
        for product in products:
            card = create_card(product)
            layout.addWidget(card)

        version = QLabel("v1.0")
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet("font-size: 14px; padding-bottom: 10px;")
        layout.addWidget(version)

        layout.addStretch()

        scroll.setWidget(scroll_content)

        self.setCentralWidget(scroll)

    def closeEvent(self, event):
        self.db.close_all()
        event.accept()

    def setup_ui(self):
        self.order_button = QPushButton("Оформить заказ")
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.admin_button = QPushButton("Админ-панель")

    def setup_role_interface(self):
        if self.role_id == 1:
            self.admin_button.show()
            self.manager_button.show()
        elif self.role_id == 2:
            self.manager_button.show()
        elif self.role_id == 3:
            self.order_button.show()
        else:
            self.order_button.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = Database(
        host='localhost',
        port=5432,
        dbname="database",
        user="postgres",
        password="123"
    )
    from login_window import LoginWindow
    login_window = LoginWindow(db)
    login_window.show()
    sys.exit(app.exec())