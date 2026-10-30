from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox
)
from main import MainWindow


class LoginWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.main_window = None
        
        self.setWindowTitle("Авторизация")
        self.resize(300, 200)
        
        layout = QVBoxLayout()
        
        # Заголовок, поле ввода
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        layout.addWidget(QLabel("Логин:"))
        layout.addWidget(self.login_input)
        
        # Кнопка Войти
        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.check_login)
        layout.addWidget(self.login_button)
        
        self.setLayout(layout)
    
    # Проверка Логина
    def check_login(self):
        login = self.login_input.text().strip()
        
        # Если поле пустое, не делает запрос
        if not login:
            QMessageBox.warning(self, "Ошибка", "Введите логин")
            return
        
        conn = self.db.get_connection()
        if conn is None:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
            return
        
        result = None
        
        try:
            cursor = conn.cursor()
            query = """
                SELECT 
                    u.user_id, 
                    u.role_id, 
                    u.last_name, 
                    u.first_name, 
                    u.second_name, 
                    roles.name 
                FROM users u 
                LEFT JOIN roles ON u.role_id = roles.role_id 
                WHERE login = %s
            """
            cursor.execute(query, (login,))
            result = cursor.fetchone()
            
            # Если логина нет в Бд, Ошибка
            if not result:
                QMessageBox.warning(self, "Ошибка", "Неверный логин")
                return
                
            # Если отчества нет, выводим только фамилию и имя
            if result[4] is None:
                self.full_name = f"{result[2]} {result[3]}"
            else:
                self.full_name = (
                    f"{result[2]} {result[3]} {result[4]} ({result[5]})"
                )
            cursor.close()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка БД: {e}")
            return
        finally:
            self.db.release_connection(conn)
        
        self.user_id = result[0]
        self.role_id = result[1]
        
        # Открываем главное окно и закрываем авторизацию
        self.main_window = MainWindow(
            db=self.db, 
            role_id=self.role_id, 
            full_name=self.full_name
        )
        self.main_window.show()
        self.close()