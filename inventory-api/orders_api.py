from flask import Flask, jsonify, request
import mysql.connector
import os
import time
## logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

db_config = {
    "host": os.getenv("DB_HOST", "db"),
    "user": os.getenv("MYSQL_USER", "orders_user"),
    "password": os.getenv("MYSQL_PASSWORD", "orders_password"),
    "database": os.getenv("DB_NAME", "orders_db"),
    "port": int(os.getenv("DB_PORT", 3306))
}


def get_connection():
    return mysql.connector.connect(**db_config)


def init_db_with_retry(max_retries=10, delay=3):
    last_error = None
    for _ in range(max_retries):
        try:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    customer_name VARCHAR(100) NOT NULL,
                    product_name VARCHAR(100) NOT NULL,
                    quantity INT NOT NULL,
                    status VARCHAR(50) NOT NULL
                )
            """)
            ## add inventory table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS product_stock (
                    product_id INT PRIMARY KEY,
                    quantity INT NOT NULL DEFAULT 0
                )
            """)

            connection.commit()
            cursor.close()
            connection.close()
            return
        except Exception as e:
            last_error = e
            time.sleep(delay)
    raise last_error


@app.route("/health", methods=["GET"])
def health():
    try:
        connection = get_connection()
        connection.close()
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()

    required_fields = ["customer_name", "product_name", "quantity", "status"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO orders (customer_name, product_name, quantity, status)
            VALUES (%s, %s, %s, %s)
        """, (
            data["customer_name"],
            data["product_name"],
            data["quantity"],
            data["status"]
        ))
        connection.commit()
        order_id = cursor.lastrowid
        cursor.close()
        connection.close()

        return jsonify({
            "message": "Order created successfully",
            "order_id": order_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/orders", methods=["GET"])
def get_orders():
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM orders")
        orders = cursor.fetchall()
        cursor.close()
        connection.close()

        return jsonify(orders), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

## add inventory api
@app.route("/inventory/<int:product_id>", methods=["GET"])
def get_inventory(product_id):
    logger.info(f"Checking stock for product_id={product_id}")
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT product_id, quantity FROM product_stock WHERE product_id = %s",
            (product_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        connection.close()

        if row is None:
            return jsonify({"error": "product not found"}), 404

        return jsonify(row), 200
    except Exception as e:
        logger.error(f"Failed to fetch stock for product_id={product_id}: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    init_db_with_retry()
    app.run(host="0.0.0.0", port=5000, debug=True)