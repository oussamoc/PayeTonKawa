from flask import Flask, jsonify, request
from functools import wraps
from flasgger import Swagger, swag_from
from marshmallow import Schema, fields, ValidationError

app = Flask(__name__)
swagger = Swagger(app)

# Simulated data
products = [
    {"id": 1, "name": "Coffee A", "price": 10.0},
    {"id": 2, "name": "Coffee B", "price": 12.0},
    {"id": 3, "name": "Coffee C", "price": 15.0}
]

API_KEY = "webshop_api_key"

# Authentication decorator
def require_api_key(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        key = request.headers.get('x-api-key')
        if key and key == API_KEY:
            return func(*args, **kwargs)
        else:
            return jsonify({"message": "Unauthorized"}), 401
    return decorated_function

# Marshmallow schema for product validation
class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

@app.errorhandler(ValidationError)
def handle_validation_error(error):
    response = jsonify(error.messages)
    response.status_code = 400
    return response

@app.route('/products', methods=['GET'])
@require_api_key
@swag_from({
    'responses': {
        200: {
            'description': 'A list of products',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'integer'
                        },
                        'name': {
                            'type': 'string'
                        },
                        'price': {
                            'type': 'number'
                        }
                    }
                }
            }
        }
    },
    'parameters': [
        {
            'name': 'x-api-key',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'API key for authentication'
        }
    ]
})
def get_products():
    return jsonify(products_schema.dump(products))

@app.route('/products/<int:product_id>', methods=['GET'])
@require_api_key
@swag_from({
    'responses': {
        200: {
            'description': 'A single product',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'name': {
                        'type': 'string'
                    },
                    'price': {
                        'type': 'number'
                    }
                }
            }
        },
        404: {
            'description': 'Product not found'
        }
    },
    'parameters': [
        {
            'name': 'product_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The product ID'
        },
        {
            'name': 'x-api-key',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'API key for authentication'
        }
    ]
})
def get_product(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        return jsonify(product_schema.dump(product))
    else:
        return jsonify({"message": "Product not found"}), 404

@app.route('/products', methods=['POST'])
@require_api_key
@swag_from({
    'responses': {
        201: {
            'description': 'Product created',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'name': {
                        'type': 'string'
                    },
                    'price': {
                        'type': 'number'
                    }
                }
            }
        },
        400: {
            'description': 'Invalid input'
        }
    },
    'parameters': [
        {
            'name': 'x-api-key',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'API key for authentication'
        },
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'required': ['id', 'name', 'price'],
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'name': {
                        'type': 'string'
                    },
                    'price': {
                        'type': 'number'
                    }
                }
            }
        }
    ]
})
def add_product():
    data = request.get_json()
    try:
        product_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_product = {
        "id": data['id'],
        "name": data['name'],
        "price": data['price']
    }
    products.append(new_product)
    return jsonify(product_schema.dump(new_product)), 201

@app.route('/products/<int:product_id>', methods=['PUT'])
@require_api_key
@swag_from({
    'responses': {
        200: {
            'description': 'Product updated',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'name': {
                        'type': 'string'
                    },
                    'price': {
                        'type': 'number'
                    }
                }
            }
        },
        400: {
            'description': 'Invalid input'
        },
        404: {
            'description': 'Product not found'
        }
    },
    'parameters': [
        {
            'name': 'product_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The product ID'
        },
        {
            'name': 'x-api-key',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'API key for authentication'
        },
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'required': ['name', 'price'],
                'properties': {
                    'name': {
                        'type': 'string'
                    },
                    'price': {
                        'type': 'number'
                    }
                }
            }
        }
    ]
})
def update_product(product_id):
    data = request.get_json()
    try:
        product_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    if data.get('name') is None or data['name'] == '':
        return jsonify({"message": "Invalid input, name is required"}), 400

    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        product['name'] = data['name']
        product['price'] = data['price']
        return jsonify(product_schema.dump(product))
    else:
        return jsonify({"message": "Product not found"}), 404

@app.route('/products/<int:product_id>', methods=['DELETE'])
@require_api_key
@swag_from({
    'responses': {
        204: {
            'description': 'Product deleted'
        },
        404: {
            'description': 'Product not found'
        }
    },
    'parameters': [
        {
            'name': 'product_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'The product ID'
        },
        {
            'name': 'x-api-key',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'API key for authentication'
        }
    ]
})
def delete_product(product_id):
    global products
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        products = [p for p in products if p['id'] != product_id]
        return '', 204
    else:
        return jsonify({"message": "Product not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
