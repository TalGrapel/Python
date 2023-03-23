from flask import jsonify ,request, make_response
from sqlalchemy import func
from app.models import Category,Product,Customer,Order,OrderItem,Cart,CartItem
from app import flask_app, db
import jwt
import datetime
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = auth_header.split(' ')[1]
            print(token)
            print(flask_app.config['SECRET_KEY'])
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            print(jwt.decode(token, flask_app.config['SECRET_KEY'], algorithms=["HS256"]))

        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is Invalid'}), 401
        
        return f(*args, **kwargs) 
    
    return decorated  

#Login operation

@flask_app.route('/login')
def login():
    auth = request.authorization
    
    if auth and auth.password == 'tal':
        print(flask_app.config['SECRET_KEY'])
        token = jwt.encode({'user': auth.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=250)}, flask_app.config['SECRET_KEY'])
        print(token)
        return jsonify({'token': token})
    return make_response('Could not verify!',401, {'WWW-Authenticate': 'Basic realm="Login Required'})    
        

#Simple CRUD operations

@flask_app.route('/categories', methods=['POST'])
@token_required
def create_category():
    name = request.json.get('name')
    category = Category(name=name)
    db.session.add(category)
    db.session.commit()
    return jsonify(category.to_dict()), 201

@flask_app.route('/categories',methods=['GET'])
def get_categories():
    categories = Category.query.all()
    serialized_categories = [category.to_dict() for category in categories]
    return jsonify(serialized_categories)

@flask_app.route('/categories/category',methods=['GET'])
def get_category():
    id = request.args.get('category')
    category = Category.query.filter_by(id == Category.id).first()
    return jsonify(category.to_dict())

@flask_app.route('/categories/category', methods=['PUT'])
@token_required
def update_category():
    id = request.args.get('category')
    category = Category.query.get(id)
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    category.name = request.json.get('name', category.name)
    db.session.commit()
    return jsonify({'id': category.id, 'name': category.name})

@flask_app.route('/categories/category', methods=['DELETE'])
@token_required
def delete_category():
    id = request.args.get('category')
    category = Category.query.get(id)
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category deleted successfully'})


@flask_app.route('/products', methods=['POST'])
@token_required
def create_product():
    data = request.get_json()
    product = Product(**data)
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict())

@flask_app.route('/products/product', methods=['GET'])
def read_product():
    product_id = request.args.get('product')
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

@flask_app.route('/products', methods=['GET'])
def read_all_products():
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products])

@flask_app.route('/products/product', methods=['PUT'])
@token_required
def update_product():
    product_id = request.args.get('product')
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    for key, value in data.items():
        setattr(product, key, value)
    db.session.commit()
    return jsonify(product.to_dict())

@flask_app.route('/products/product', methods=['DELETE'])
@token_required
def delete_product():
    product_id = request.args.get('product')
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return '', 204

@flask_app.route('/customers', methods=['POST'])
@token_required
def create_customer():
    data = request.get_json()
    customer = Customer(**data)    
    db.session.add(customer)
    db.session.commit()
    return jsonify(customer.to_dict()), 201

@flask_app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return jsonify([customer.to_dict() for customer in customers])

@flask_app.route('/customers/customer', methods=['GET'])
def get_customer():
    id = request.args.get('customer')
    customer = Customer.query.get(id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    return jsonify(customer.to_dict())

@flask_app.route('/customers/customer', methods=['PUT'])
@token_required
def update_customer():
    id = request.args.get('customer')
    customer = Customer.query.get_or_404(id)
    data = request.get_json()
    for key, value in data.items():
        setattr(customer, key, value)
    db.session.commit()
    return jsonify(customer.to_dict())

@flask_app.route('/customers/customer', methods=['DELETE'])
@token_required
def delete_customer():
    id = request.json.get('customer')
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer deleted successfully'})

@flask_app.route('/orders', methods=['POST'])
@token_required
def create_order():
    data = request.get_json()
    order = Order(**data)
    db.session.add(order)
    db.session.commit()
    return jsonify(order.to_dict())

@flask_app.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return jsonify([order.to_dict() for order in orders])

@flask_app.route('/orders/order' ,methods=['GET'])
def get_order():
    id = request.args.get('order')
    order = Order.query.get_or_404(id)
    return jsonify(order.to_dict())

@flask_app.route('/orders/order', methods=['PUT'])
@token_required
def update_order():
    id = request.args.get('order')
    order = Order.query.get_or_404(id)
    data = request.get_json()
    for key, value in data.items():
        setattr(order, key, value)
    db.session.commit()
    db.session.commit()
    return jsonify(order.to_dict())

@flask_app.route('/orders/order', methods=['DELETE'])
@token_required
def delete_order():
    id = request.args.get('order')
    order = Order.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({'message': 'Order deleted successfully'})
        
@flask_app.route('/order-items', methods=['POST'])
@token_required
def create_order_item():
    data = request.get_json()
    order_item = OrderItem(**data)
    db.session.add(order_item)
    db.session.commit()
    return jsonify(order_item.to_dict())        
   
@flask_app.route('/order-items', methods=['GET'])
def read_all_order_items():
    order_items = OrderItem.query.all()
    return jsonify([order_item.to_dict() for order_item in order_items])

@flask_app.route('/order-items/item', methods=['GET'])
def read_order_item():
    id = request.args.get('item')
    order_item = OrderItem.query.get_or_404(id)
    return jsonify(order_item.to_dict())

@flask_app.route('/order-items/item', methods=['PUT'])
@token_required
def update_order_item():
    id = request.args.get('item')
    order_item = OrderItem.query.get_or_404(id)
    data = request.get_json()
    for key,value in data.items():
        setattr(order_item,key,value)
    db.session.commit()
    return jsonify(order_item.to_dict())

@flask_app.route('/order-items/item', methods=['DELETE'])
@token_required
def delete_order_item():
    id = request.args.get('item')
    order_item = OrderItem.query.get_or_404(id)
    db.session.delete(order_item)
    db.session.commit()
    return jsonify({"Element deleted sucessfully"})

@flask_app.route('/cart', methods=['POST'])
@token_required
def create_cart():
    data = request.get_json()
    cart = Cart(**data)
    db.session.add(cart)
    db.session.commit()
    return jsonify(cart.to_dict())

@flask_app.route('/cart', methods=['GET'])
def read_all_carts():
    carts = Cart.query.all()
    return jsonify({[cart.to_dict() for cart in carts]})

@flask_app.route('/cart/id', methods=['GET'])
def read_cart():
    id = request.args.get('id')
    cart = Cart.query.get_or_404(id)
    return jsonify(cart.to_dict())

@flask_app.route('/cart/id', methods=['PUT'])
@token_required
def update_cart():
    id = request.args.get('id')
    cart = Cart.query.get_or_404(id)
    data = request.get_json()
    for key,value in data.items():
        setattr(cart,key,value)
    db.session.commit()
    return jsonify(cart.to_dict())

@flask_app.route('/cart/id', methods=['DELETE'])
@token_required
def delete_cart():
    id = request.args.get('id')
    cart = Cart.query.get_or_404(id)
    db.session.delete(cart)
    db.session.commit()
    return jsonify({"Element deleted sucessfully"})

@flask_app.route('/cart-items', methods=['POST'])
@token_required
def create_cart_item():
    data = request.get_json()
    cart_item = CartItem(**data)
    db.session.add(cart_item)
    db.session.commit()
    return jsonify(cart_item.to_dict())

@flask_app.route('/cart-items', methods=['GET'])
def read_all_cart_items():
    cart_items = CartItem.query.all()
    return jsonify({[cart_item.to_dict() for cart_item in cart_items]})

@flask_app.route('/cart-items/item', methods=['GET'])
def read_cart_item():
    id = request.args.get('item')
    cart_item = CartItem.query.get_or_404(id)
    return jsonify(cart_item.to_dict())

@flask_app.route('/cart-items/item', methods=['PUT'])
@token_required
def update_cart_item():
    id = request.args.get('item')
    cart_item = CartItem.query.get_or_404(id)
    data = request.get_json()
    for key, value in data.items():
        setattr(cart_item,key, value)
    db.session.commit()
    return jsonify(cart_item.to_dict())

@flask_app.route('/cart-items/item', methods=['DELETE'])
@token_required
def delete_cart_item():
    id = request.args.get('item')
    cart_item = CartItem.query.get_or_404(id)
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({"Element removed sucessfully"})        
    
#Complex queries

#returns catergory and product 

@flask_app.route('/categories-with-products',methods=['GET'])
def get_categories_with_products():
    categories = Category.query \
        .join(Product, Category.id == Product.category_id) \
        .add_columns(Category.id, Category.name, Product.id, Product.name, Product.description, Product.price, Product.image, Product.quantity) \
        .all()
    serialized_categories = []
    for category in categories:
        category_data = {
            "id": category[1],
            "name": category[2],
            "products": []
        }
        product_data = {
            "id": category[3],
            "name": category[4],
            "description": category[5],
            "price": str(category[6]),
            "image": category[7],
            "quantity": category[8]
        }
        if category_data in serialized_categories:
            category_index = serialized_categories.index(category_data)
            serialized_categories[category_index]["products"].append(product_data)
        else:
            category_data["products"].append(product_data)
            serialized_categories.append(category_data)
    return jsonify(serialized_categories)

#returns average price per category

@flask_app.route('/avg_price_by_category', methods=['GET'])
def get_avg_price_by_category():
    results = db.session.query(Category.name, func.avg(Product.price))\
        .join(Product, Category.id == Product.category_id)\
        .group_by(Category.name)\
        .all()
    serialized_results = [{
        "category_name": result[0],
        "avg_price": float(result[1])
    } for result in results]
    return jsonify(serialized_results)

#returns quantity of products per category

@flask_app.route('/products_quantity_per_category', methods=['GET'])
def get_quantity_per_category():
    results = db.session.query(Category.name, func.count(Product.id))\
        .join(Product, Category.id == Product.category_id)\
        .group_by(Category.name)\
        .all()
    serialized_results = [{
        "category_name": result[0],
        "quantity": float(result[1])
    } for result in results]
    return jsonify(serialized_results)

@flask_app.route('/products_quantity_per_category/category', methods=['GET'])
def get_quantity_per_specific_category():
    cat = request.args.get('category')
    results = db.session.query(Category.name, func.count(Product.id))\
        .join(Product, Category.id == Product.category_id)\
        .filter(Category.name == cat)\
        .group_by(Category.name)\
        .all()
    serialized_results = [{
        "category_name": result[0],
        "quantity": float(result[1])
    } for result in results]
    return jsonify(serialized_results)

#returns customers and their orders

@flask_app.route('/orders-per-customers', methods=['GET'])
def get_orders_for_all_customers():    
    elements = db.session.query(Customer.id, Customer.name, Order.id, Order.order_date)\
        .join(Order, Order.customer_id == Customer.id).all()
    
    result = []
    for element in elements:
        customer_dict = {
            'id':element[0],
            'name':element[1],
            'orders':[{
                'id':element[2],
                'order_date':str(element[3])
            }]
        }
        result.append(customer_dict)
        
    return jsonify(result)

@flask_app.route('/orders-per-customers/customer', methods=['GET'])
def get_orders_for_customer():
    id = request.args.get('id')    
    elements = db.session.query(Customer.id, Customer.name, Order.id, Order.order_date)\
        .filter(Customer.id == id)\
        .join(Order, Order.customer_id == Customer.id).all()
    
    result = []
    for element in elements:
        customer_dict = {
            'id':element[0],
            'name':element[1],
            'orders':[{
                'id':element[2],
                'order_date':str(element[3])
            }]
        }
        result.append(customer_dict)
        
    return jsonify(result)

#returns order details of customers

@flask_app.route('/order-data-of-customers', methods=['GET'])
def get_order_data_of_customers():        
    elements = db.session.query(Customer.id,Customer.name,Order.id,OrderItem.id,Product.id,Product.name)\
        .join(Order, Order.customer_id == Customer.id)\
        .join(OrderItem, Order.id == OrderItem.order_id)\
            .join(Product, OrderItem.product_id == Product.id).all()    
    
    result = []
    for element in elements:
        result.append({
            'customer_id':element[0],
            'customer_name':element[1],
            'order_id':element[2],
            'order_item_id':element[3],
            'product_id':element[4],
            'product_name':element[5]
        })
        
    return jsonify(result)

@flask_app.route('/order-data-of-customers/customer', methods=['GET'])
def get_order_data_of_customer():
    id = request.args.get('id')        
    elements = db.session.query(Customer.id,Customer.name,Order.id,OrderItem.id,Product.id,Product.name)\
        .filter(Customer.id == id)\
        .join(Order, Order.customer_id == Customer.id)\
        .join(OrderItem, Order.id == OrderItem.order_id)\
            .join(Product, OrderItem.product_id == Product.id).all()    
    
    result = []
    for element in elements:
        result.append({
            'customer_id':element[0],
            'customer_name':element[1],
            'order_id':element[2],
            'order_item_id':element[3],
            'product_id':element[4],
            'product_name':element[5]
        })
        
    return jsonify(result)

#returns amount of orders of all customers

@flask_app.route('/num-of-orders-all-customers', methods=['GET'])
def get_num_of_orders_of_all_customers():
    customers = db.session.query(Customer.id, Customer.name, func.count(Order.id))\
        .join(Order, Customer.id == Order.customer_id)\
            .group_by(Customer.id, Customer.name)
            
    result = []
    for customer in customers:
        result.append({
            'customer_id':customer[0],
            'customer_name':customer[1],
            'num_of_orders':customer[2]
        })                        

    return jsonify(result)

@flask_app.route('/num-of-orders-customers/customer', methods=['GET'])
def get_num_of_orders_of__customer():
    id = request.args.get('id')
    customers = db.session.query(Customer.id, Customer.name, func.count(Order.id))\
        .filter(Customer.id == id)\
        .join(Order, Customer.id == Order.customer_id)\
            .group_by(Customer.id, Customer.name)
            
    result = []
    for customer in customers:
        result.append({
            'customer_id':customer[0],
            'customer_name':customer[1],
            'num_of_orders':customer[2]
        })                        

    return jsonify(result)

#returns total price of an order

@flask_app.route('/total-price-of-order', methods=['GET'])
def get_total_price():
    customers = db.session.query(Customer.id, Customer.name, Order.id, func.sum(Product.price))\
        .join(Order, Customer.id == Order.customer_id)\
            .join(OrderItem, Order.id == OrderItem.order_id)\
                .join(Product, OrderItem.product_id == Product.id)\
                    .group_by(Customer.id, Customer.name, Order.id)
    
    result = []
    
    for customer in customers:                
        result.append({
            'customer_id':customer[0],
            'customer_name':customer[1],
            'order_id':customer[2],
            'total_price':customer[3]
        })
        
    return jsonify(result)

@flask_app.route('/total-price-of-order/order', methods=['GET'])
def get_total_price_of_order():
    id = request.args.get('id')
    customers = db.session.query(Customer.id, Customer.name, Order.id, func.sum(Product.price))\
        .filter(Order.id == id)\
        .join(Order, Customer.id == Order.customer_id)\
            .join(OrderItem, Order.id == OrderItem.order_id)\
                .join(Product, OrderItem.product_id == Product.id)\
                    .group_by(Customer.id, Customer.name, Order.id)
    
    result = []
    
    for customer in customers:                
        result.append({
            'customer_id':customer[0],
            'customer_name':customer[1],
            'order_id':customer[2],
            'total_price':customer[3]
        })
        
    return jsonify(result)

#returns total amount of orders of all customers

@flask_app.route('/total-count-of-order', methods=['GET'])
def get_total_count():
    customers = db.session.query(Customer.id, Customer.name, Order.id,func.count(Product.price))\
        .join(Order, Customer.id == Order.customer_id)\
            .join(OrderItem, Order.id == OrderItem.order_id)\
                .join(Product, OrderItem.product_id == Product.id)\
                    .group_by(Customer.id, Customer.name, Order.id)
    
    result = []
    
    for customer in customers:                
        result.append({
            'customer_id':customer[0],
            'customer_name':customer[1],
            'order_id':customer[2],
            'total_count':customer[3]
        })
        
    return jsonify(result)

@flask_app.route('/total-count-of-order/order', methods=['GET'])
def get_total_count_of_products():
    id = request.args.get('id')
    customers = db.session.query(Customer.id, Customer.name, Order.id,func.count(Product.price))\
        .filter(Order.id == id)\
        .join(Order, Customer.id == Order.customer_id)\
            .join(OrderItem, Order.id == OrderItem.order_id)\
                .join(Product, OrderItem.product_id == Product.id)\
                    .group_by(Customer.id, Customer.name, Order.id)
    
    result = []
    
    for customer in customers:                
        result.append({
            'customer_id':customer[0],
            'customer_name':customer[1],
            'order_id':customer[2],
            'total_count':customer[3]
        })
        
    return jsonify(result)

#returns total amount of products of all orders

@flask_app.route('/total-products-per-order/product', methods=['GET'])
def total_products_per_specific_order():
    id = request.args.get('id')
    products = db.session.query(Product.id, Product.name, Product.price, func.count(OrderItem.id))\
        .filter(Product.id == id)\
        .join(OrderItem, Product.id == OrderItem.product_id)\
            .group_by(Product.id, Product.name, Product.price)
    
    result = []
    for product in products:
        result.append({
            'product_id':product[0],
            'product_name':product[1],
            'product_price':product[2],
            'total_orders':product[3]
        })
        
    return jsonify(result)                

@flask_app.route('/products/cost', methods=['GET'])
def get_products_in_range():
    min_cost = float(request.args.get('min_cost'))
    max_cost = float(request.args.get('max_cost'))
    
    products = Product.query.filter(Product.price >= min_cost, Product.price <= max_cost).all()
    
    return jsonify([product.to_dict() for product in products])

@flask_app.route('/products/stock', methods=['GET'])
def get_products_stock():
    stock_count = request.args.get('stock')
    products = Product.query.filter(Product.quantity >= stock_count)
    
    return jsonify([product.to_dict() for product in products])