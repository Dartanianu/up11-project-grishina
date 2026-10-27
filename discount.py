import psycopg2
import datetime

def calculate_discount(old_price, new_price):
    if old_price == 0:
        return 0
    else:
        return (old_price - new_price) / old_price * 100

def calculate_price(product_id, old_price, db):
    now = datetime.datetime.now()
    current_month = now.month
    current_year = now.year
    
    query = """
        SELECT COUNT(*)
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        WHERE oi.product_id = %s
            AND EXTRACT(MONTH FROM o.order_date) = %s
            AND EXTRACT(YEAR FROM o.order_date) = %s
    """
    conn = db.get_connection()
    if conn is None:
        return int(old_price)
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, (product_id, current_month, current_year))
        result = cursor.fetchone()
        order_count = result[0] if result else 0
    except Exception as e:
        print(f"Ошибка при расчете скидки: {e}")
        order_count = 1
    finally:
        db.release_connection(conn)
    
    if order_count == 0:
        new_price = int(float(old_price) * 0.75)
    else:
        new_price = int(old_price)
        
    return new_price