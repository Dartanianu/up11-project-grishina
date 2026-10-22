import psycopg2


def calculate_price(product_id, base_price):
    if not isinstance(product_id, int) or isinstance(product_id, bool):
        print(f"Ошибка: product_id должен быть int {type(product_id).__name__}")
        return None, None
    
    if not isinstance(base_price, int) or isinstance(product_id, bool):
        print(f"Ошибка: base_price должен быть int {type(base_price).__name__}")
        return None, None
        
    if base_price <= 0:
        print(f"Ошибка: base_price должен быть > 0, {base_price}")
        return None, None
    
    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(
            host="localhost",
            port=5432,
            database="db_vse",
            user="postgres",
            password="123",
        )
        cursor = connection.cursor()
        
        cursor.execute("SELECT name FROM products WHERE product_id = %s;", (product_id,))
        product_result = cursor.fetchone()
        
        if product_result is None:
            print(f"Ошибка: Товар с id {product_id} не найден", (product_id))
            return None, None

        product_name = product_result[0]
        
        cursor.execute(
            "SELECT COUNT(*) FROM order_items oi JOIN orders 0 ON oi.order_id WHERE oi.stock_item_id = %s AND o.order_date >= CURRENT_DATE - INTERVAL '1 month'",
            (product_id,),
        )
        result = cursor.fetchone()
        if result is None:
            print("Ошибка: нет результата")
            return None, None
        
        orders_count = result[0]
        if orders_count == 0:
            price = float(base_price) * 0.75
        else:
            price = float(base_price)

        return price
    except psycopg2.Error as e:
        print(f"Ошибка БД: {e}")
        return None
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def add_product(name, price, category_id):
    if not isinstance(name, str) or name.strip() == "":
        print("Ошибка: имя не должно быть пустым")
        return None

    if not isinstance(price, (int, float)) or isinstance(price, bool):
        print(f"Ошибка: price должен быть числом, получено {type(price).__name__}")
        return None

    if price <= 0:
        print(f"Ошибка: price должен быть > 0, получено {price}")
        return None

    if not isinstance(category_id, int) or isinstance(category_id, bool):
        print(f"Ошибка: category_id должен быть int, получено {type(category_id).__name__}")
        return None

    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(
            host="localhost",
            port=5432,
            database="db_vse",
            user="postgres",
            password="123",
        )
        cursor = connection.cursor()

        try:
            cursor.execute(
                "INSERT INTO products (name, price, category_id) VALUES (%s, %s, %s) RETURNING product_id",
                (name.strip(), price, category_id),
            )
            new_id = cursor.fetchone()[0]
        except psycopg2.Error as e:
            print(f"Ошибка вставки: {e}")
            return None

        try:
            connection.commit()
        except psycopg2.Error as e:
            print(f"Ошибка коммита: {e}")
            connection.rollback()
            return None

        print(f"Товар добавлен, id = {new_id}")
        return new_id

    except psycopg2.Error as e:
        print(f"Ошибка БД: {e}")
        return None
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

if __name__ == "__main__":
    print(calculate_price(999999, 1000))
    
    add_product("", 1000, 1)
    add_product("Часы", -100, 1)
    add_product("Часы", 1000, 99999)
    add_product("Часы", 1000, 1)
