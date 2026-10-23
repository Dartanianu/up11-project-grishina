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

    def get_connection(self):
        if self.pool is None:
            print("Пул соединений недоступен (не был создан).")
            return None
        else:
            return self.pool.getconn()

    def release_connection(self, conn):
        if self.pool is not None and conn is not None:
            self.pool.putconn(conn)

    def close_all(self):
        if self.pool is not None:
            self.pool.closeall()
            print("Все соединения закрыты.")
        else:
            print("Пул не был создан — закрывать нечего.")

    def get_products(self):
        conn = self.get_connection()

        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                p.product_id, 
                p.name,
                p.description,
                p.compound,
                p.price, 
                p.image_path,
                p.manufacture_id,
                p.category_id,
                p.subcategory_id,
                COALESCE(SUM(si.quantity), 0) AS total_quantity
                FROM products p
                LEFT JOIN stock_items si ON p.product_id = si.product_id
                GROUP BY p.product_id;
            """)
            result = cur.fetchall()
            cur.close()
            return result
        except psycopg2.Error as e:
            print(f"Ошибка при выполнение запроса  SELECT products: {e}")
            return []
        finally:
            self.release_connection(conn)
        
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
            print(f"Ошибка при выполнение SELECT: {e}")
            return []
        finally:
            self.release_connection(conn)

    def execute_update(self, sql, params=None):
        conn = self.get_connection()
        if conn is None:
            return []

        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            conn.commit()
            cur.close()
            return True
        except psycopg2.Error as e:
            print(f"Ошибка при выполнение UPDATE/INSERT/DELETE: {e}")
            return False
        finally:
            self.release_connection(conn)