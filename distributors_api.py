from flask import Flask, jsonify, request
from functools import wraps
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

# Simulated data
orders = [
    {"id": 1, "customer_id": 1, "products": [{"id": 1, "name": "Coffee A", "quantity": 2}]},
    {"id": 2, "customer_id": 2, "products": [{"id": 2, "name": "Coffee B", "quantity": 1}]}
]

API_KEYS = {"distributor_1_key", "distributor_2_key"}

# Authentication decorator
def require_api_key(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        key = request.headers.get('x-api-key')
        if key and key in API_KEYS:
            return func(*args, **kwargs)
        else:
            return jsonify({"message": "Unauthorized"}), 401
    return decorated_function

@app.route('/orders', methods=['GET'])
@require_api_key
def get_orders():
    """
    Get all orders
    ---
    responses:
      200:
        description: A list of orders
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              customer_id:
                type: integer
              products:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: integer
                    name:
                      type: string
                    quantity:
                      type: integer
    """
    return jsonify(orders)

@app.route('/orders/<int:order_id>/products', methods=['GET'])
@require_api_key
def get_order_products(order_id):
    """
    Get products of an order
    ---
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: The order ID
    responses:
      200:
        description: A list of products in an order
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              quantity:
                type: integer
      404:
        description: Order not found
    """
    order = next((o for o in orders if o['id'] == order_id), None)
    if order:
        return jsonify(order['products'])
    else:
        return jsonify({"message": "Order not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
