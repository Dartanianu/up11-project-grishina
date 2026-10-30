import psycopg2
from psycopg2 import pool


class Database:
    def __init__(self, host, port, dbname, user, password):
        try:
            self.pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=5,
                host=host,
                port=port,
                dbname=dbname,
                user=user,
                password=password
            )
            print("Пул соединений создан успешно.")
        except psycopg2.Error as e:
            print(f"Ошибка БД: {e}")
            self.pool = None
        except UnicodeDecodeError as e:
            print(f"Ошибка подключения: {e}")
            self.pool = None
    
    # Подключение к  БД
    def get_connection(self):
        if self.pool is None:
            print("Пул соединений недоступен (не был создан).")
            return None
        return self.pool.getconn()

    # Возращение подключения в пул доступных
    def release_connection(self, conn):
        if self.pool is not None and conn is not None:
            self.pool.putconn(conn)

    # Закрытие подключений
    def close_all(self):
        if self.pool is not None:
            self.pool.closeall()
            print("Все соединения закрыты.")
        else:
            print("Пул не был создан — закрывать нечего.")

    # Получение продуктов из БД
    def get_products(self, order='ASC', category=None, search=None):
        conn = self.get_connection()
        if conn is None:
            return []
        
        # Проверка
        if order.upper() not in ('ASC', 'DESC'):
            order = 'ASC'

        try:
            cur = conn.cursor()

            # Базовый запрос
            base_sql = """
            SELECT 
                p.product_id, 
                p.name,
                p.description,
                p.compound,
                p.price, 
                p.image_path,
                manu.name AS manufacture_name,
                c.name AS category_name,
                subc.name AS subcategory_name,
                COALESCE(SUM(si.quantity), 0) AS total_quantity
            FROM products p
            LEFT JOIN manufactures manu 
                ON p.manufacture_id = manu.manufacture_id
            LEFT JOIN categories c 
                ON p.category_id = c.category_id
            LEFT JOIN subcategories subc 
                ON p.subcategory_id = subc.subcategory_id
            LEFT JOIN stock_items si 
                ON p.product_id = si.product_id
            """

            conditions = []
            params = []

            # Если выбрана категория, добавляем ее в поиск
            if category:
                conditions.append("c.name = %s")
                params.append(category)

            # Если введен в поиск, ищем по всем полям
            if search:
                conditions.append("""(
                    p.name ILIKE %s OR
                    p.compound ILIKE %s OR
                    p.description ILIKE %s OR
                    manu.name ILIKE %s OR
                    c.name ILIKE %s
                )""")
                pattern = f"%{search}%"
                params.extend([pattern] * 5)

            # Соедение всех запросов с помощью WHERE
            if conditions:
                base_sql += " WHERE " + " AND ".join(conditions) + " "

            base_sql += """
            GROUP BY 
                p.product_id, p.name, p.description, p.compound,
                p.price, p.image_path, manu.name, c.name, subc.name
            ORDER BY p.price {order};
            """.format(order=order)

            cur.execute(base_sql, params)
            result = cur.fetchall()
            cur.close()
            return result
        except psycopg2.Error as e:
            print(f"Ошибка при выполнении запроса SELECT products: {e}")
            return []
        finally:
            self.release_connection(conn)

    # Получение категорий
    def get_categories(self):
        conn = self.get_connection()
        if conn is None:
            return []
        try:
            cur = conn.cursor()
            # Уникальные названия категорий
            cur.execute("SELECT DISTINCT name FROM categories ORDER BY name")
            result = [row[0] for row in cur.fetchall()]
            cur.close()
            return result
        except psycopg2.Error as e:
            print(f"Ошибка при выполнении запроса SELECT categories: {e}")
            return []
        finally:
            self.release_connection(conn)

    # Функция запросов SELECT
    def execute_query(self, sql, params=None):
        conn = self.get_connection()
        if conn is None:
            return []

        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            result = cur.fetchall()
            cur.close()
            return result
        except psycopg2.Error as e:
            print(f"Ошибка при выполнении SELECT: {e}")
            return []
        finally:
            self.release_connection(conn)

    # Функция запросов UPDATE/INSERT/DELETE
    def execute_update(self, sql, params=None):
        conn = self.get_connection()
        if conn is None:
            return False

        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            conn.commit()
            cur.close()
            return True
        except psycopg2.Error as e:
            print(f"Ошибка при выполнении UPDATE/INSERT/DELETE: {e}")
            return False
        finally:
            self.release_connection(conn)