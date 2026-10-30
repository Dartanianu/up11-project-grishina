import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QScrollArea, QPushButton, QMessageBox, QComboBox, QLineEdit
)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from database import Database
from discount import calculate_price, calculate_discount


def create_card(products, db):
    card = QWidget()
    card.setObjectName("productCard")

    main_layout = QHBoxLayout(card)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(15)

    image_lable = QLabel()
    image_lable.setFixedSize(100, 100)
    image_lable.setAlignment(Qt.AlignCenter)
    image_lable.setStyleSheet("border: 1px solid #000000;")

    file_name = products[5]

    # Если картинки нет в БД, берем стандартную
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

    title = QLabel(f"{products[6]} | {products[1]}")
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

    old_price = products[4]
    new_price = calculate_price(products[0], old_price, db)

    discount = calculate_discount(old_price, new_price)

    old_price_lable = QLabel(f"<s>{old_price}</s>")
    old_price_lable.setStyleSheet("color: red; border: none;")

    new_price_label = QLabel(f"{new_price} ₽")

    total_quantity = products[9]

    # В наличии меньше 3 - красный, большая скидка - зеленая цена, иначе обычный
    if total_quantity <= 3:
        card.setStyleSheet(
            "border: 1px solid #000000; border-radius: 4px; "
            "background-color: #FF8080;"
        )
        new_price_label.setStyleSheet(
            "font-weight: bold; color: black; border: none;"
        )
    elif discount > 15:
        card.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #000000; "
            "border-radius: 4px;"
        )
        new_price_label.setStyleSheet(
            "color: #2E8B57; font-weight: bold; border: none;"
        )
    else:
        card.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #000000; "
            "border-radius: 4px;"
        )
        new_price_label.setStyleSheet(
            "font-weight: bold; color: black; border: none;"
        )

    # Если скидки нет, прячем старую цену
    if discount > 0:
        old_price_lable.show()
    else:
        old_price_lable.hide()

    price_layout = QVBoxLayout()
    price_layout.setContentsMargins(0, 0, 0, 0)
    price_layout.addWidget(old_price_lable)
    price_layout.addSpacing(2)
    price_layout.addWidget(new_price_label)
    price_layout.addStretch()

    main_layout.addLayout(price_layout)

    return card


class MainWindow(QMainWindow):
    def __init__(self, db, role_id=None, full_name=None):
        super().__init__()
        self.db = db
        self.role_id = role_id
        self.full_name = full_name

        self.setWindowTitle("Сумки и аксессуары")
        self.resize(800, 600)
        self.setWindowIcon(QIcon('resources/icon.ico'))

        # Общие стили для всего окна
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
                font-family: 'Calibri';
            }
            QLabel {
                color: #000000;
            }
            QPushButton {
                background-color: #70B2AF;
                color: white;
                font-family: Calibri;
                border: none;
                border-radius: 10;
                padding: 8px 16px;
            }
        """)

        central = QWidget()
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.setCentralWidget(central)

        # Header
        header = QWidget()
        header.setObjectName("header")
        header.setStyleSheet("#header { background-color: #D2F6E7;}")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 8, 10, 8)
        header_layout.setSpacing(10)

        self.logo = QLabel()
        logo_pixmap = QPixmap('resources/logo.png')
        if not logo_pixmap.isNull():
            self.logo.setPixmap(
                logo_pixmap.scaledToHeight(50, Qt.SmoothTransformation)
            )
        else:
            self.logo.setText("LOGO")
        self.logo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header_layout.addWidget(self.logo)

        header_layout.addStretch(1)

        self.order_button = QPushButton("Оформить заказ")
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.admin_button = QPushButton("Админ-панель")

        header_layout.addWidget(self.order_button)
        header_layout.addWidget(self.manager_button)
        header_layout.addWidget(self.admin_button)

        self.name = QLabel(f"ФИО: {self.full_name}")
        self.name.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(self.name)

        self.logout_button = QPushButton("Выход")
        self.logout_button.clicked.connect(self.logout)
        header_layout.addWidget(self.logout_button)

        root_layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        scroll_content.setStyleSheet(
            "#scrollContent { background-color: #FFFFFF; }"
        )

        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = QLabel("Сумки и аксессуары - Каталог")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-size: 28px; font-weight: bold; padding: 10px;"
        )
        layout.addWidget(title)

        # Блок сортировки
        sort_layout = QHBoxLayout()
        sort_label = QLabel("Сортировка по цене:")
        sort_label.setStyleSheet("font-size: 14px;")

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["По возрастанию", "По убыванию"])
        self.sort_combo.currentIndexChanged.connect(self.load_products)

        sort_layout.addWidget(sort_label)
        sort_layout.addWidget(self.sort_combo)
        sort_layout.addStretch()
        layout.addLayout(sort_layout)

        # Блок фильтрации
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Фильтрация:")
        filter_label.setStyleSheet("font-size: 14px;")

        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Все категории")
        self.filter_combo.addItems(self.db.get_categories())
        self.filter_combo.currentIndexChanged.connect(self.load_products)

        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch() # Добавил отступ именно сюда
        layout.addLayout(filter_layout)

        # Блок поиска
        search_layout = QHBoxLayout()
        search_label = QLabel("Поиск:")
        search_label.setStyleSheet("font-size: 14px;")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск...")
        self.search_input.textChanged.connect(self.load_products)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Сюда будут добавляться карточки товаров
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setSpacing(10)
        layout.addLayout(self.cards_layout)

        self.load_products()

        version = QLabel("v1.0")
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet("font-size: 14px; padding-bottom: 10px;")
        layout.addWidget(version)

        layout.addStretch()
        scroll.setWidget(scroll_content)

        root_layout.addWidget(scroll, 1)

        self.setup_role_interface()

    # Функция загрузки товаров
    def load_products(self):
        # Удаляем старые карточки с экрана перед загрузкой новых
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # Сортировка
        order = 'ASC' if self.sort_combo.currentIndex() == 0 else 'DESC'

        # Категория
        selected_category = self.filter_combo.currentText()
        if selected_category == "Все категории":
            selected_category = None

        # Текст поиска
        search_text = self.search_input.text().strip() or None

        # Запрос товаров из БД
        products = self.db.get_products(order, selected_category, search_text)

        print(
            f"Загружено товаров: {len(products)} "
            f"(порядок: {order}, категория: {selected_category or 'все'}, "
            f"поиск: {search_text or '—'})"
        )

        # Создание карточек товаров
        for product in products:
            card = create_card(product, self.db)
            self.cards_layout.addWidget(card)

    # Функция показа кнопок в зависимости от роли
    def setup_role_interface(self):
        self.order_button.hide()
        self.manager_button.hide()
        self.admin_button.hide()

        if self.role_id == 1:
            self.admin_button.show()
            self.manager_button.show()
        elif self.role_id == 2:
            self.manager_button.show()
        elif self.role_id == 3:
            self.order_button.show()

    def closeEvent(self, event):
        event.accept()

    # Выхода из аккаунта
    def logout(self):
        reply = QMessageBox.question(
            self,
            "Подтверждение выхода",
            "Вы уверены, что хотите выйти?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            from login_window import LoginWindow
            self.login_window = LoginWindow(self.db)
            self.login_window.show()
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = Database(
        host='localhost',
        port=5432,
        dbname="database",
        user="postgres",
        password="123"
    )
    app.aboutToQuit.connect(db.close_all)

    from login_window import LoginWindow
    login_window = LoginWindow(db)
    login_window.show()
    sys.exit(app.exec())