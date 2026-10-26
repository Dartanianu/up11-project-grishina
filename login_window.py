import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox
)
from database import Database
from main import MainWindow


class LoginWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.main_window = None
        
        self.setWindowTitle("Авторизация")
        self.resize(300, 200)
        
        layout = QVBoxLayout()
        
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        layout.addWidget(QLabel("Логин:"))
        layout.addWidget(self.login_input)
        
        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.check_login)
        layout.addWidget(self.login_button)
        
        self.setLayout(layout)
    
    def check_login(self):
        login = self.login_input.text().strip()
        
        if not login:
            QMessageBox.warning(self, "Ошибка", "Введите логин")
            return
        
        conn = self.db.get_connection()
        if conn is None:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT u.user_id, u.role_id, u.last_name, u.first_name, u.second_name, roles.name FROM users u LEFT JOIN roles ON u.role_id = roles.role_id WHERE login = %s", (login,))
            result = cursor.fetchone()
            if result[4] is None:
                self.full_name = f"{result[2]} {result[3]}"
            else:
                self.full_name = f"{result[2]} {result[3]} {result[4]} ({result[5]})"
            cursor.close()
        finally:
            self.db.release_connection(conn)
        
        if result is None:
            QMessageBox.warning(self, "Ошибка", "Неверный логин")
            return
        
        self.user_id = result[0]
        self.role_id = result[1]
        
        self.main_window = MainWindow(db=self.db, role_id=self.role_id, full_name=self.full_name)
        self.main_window.show()
        self.close()