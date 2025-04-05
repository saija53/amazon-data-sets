from flask import Flask, render_template, request, redirect, jsonify
from utils.db import db
from models.order import Order  # Assuming Order model for sales data
from models.wishlist import Wishlist  # Assuming Wishlist model
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


@app.route('/')
def index():
    # Fetch all orders to display on the index page
    orders = Order.query.all()
    return render_template('index.html', orders=orders)

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/add_products')
def add_products():
    return render_template('add_products.html')

@app.route('/cost')
def cost():
    # Placeholder logic for calculating total cost of orders
    total_cost = db.session.query(db.func.sum(Order.total_price)).scalar()
    return render_template('cost.html', total_cost=total_cost)


@app.route('/add_orders', methods=['GET', 'POST'])
def add_orders():
    if request.method == 'POST':
        # Collect form data to add new order
        order_data = request.form.to_dict()
        order = Order(
            product_name=order_data['product_name'],
            quantity=order_data['quantity'],
            price_per_unit=order_data['price_per_unit'],
            total_price=float(order_data['quantity']) * float(order_data['price_per_unit']),
            customer_name=order_data['customer_name'],
            order_date=order_data['order_date']
        )
        db.session.add(order)
        db.session.commit()
        return redirect('/orders')
    return render_template('add_orders.html')


@app.route('/wishlist', methods=['GET', 'POST'])
def wishlist():
    if request.method == 'POST':
        wishlist_data = request.form.to_dict()
        wishlist_item = Wishlist(
            product_name=wishlist_data['product_name'],
            customer_name=wishlist_data['customer_name'],
            price=wishlist_data['price'],
        )
        db.session.add(wishlist_item)
        db.session.commit()
        return redirect('/wishlist')

    # Fetch all wishlist items to display
    items = Wishlist.query.all()
    return render_template('wishlist.html', items=items)


@app.route('/orders')
def orders():
    orders = Order.query.all()
    return render_template('orders.html', orders=orders)



@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/delete_order/<int:id>', methods=['GET', 'DELETE'])
def delete_order(id):
    order = Order.query.get(id)
    if not order:
        return jsonify({'message': 'Order not found'}), 404
    try:
        db.session.delete(order)
        db.session.commit()
        return redirect('/orders')
        return jsonify({'message': 'Order deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'An error occurred while deleting the order: {e}'}), 500


@app.route('/update_order/<int:id>', methods=['GET', 'POST'])
def update_order(id):
    order = Order.query.get_or_404(id)
    if request.method == 'POST':
        order.product_name = request.form['product_name']
        order.quantity = request.form['quantity']
        order.price_per_unit = request.form['price_per_unit']
        order.total_price = float(request.form['quantity']) * float(request.form['price_per_unit'])
        order.customer_name = request.form['customer_name']
        order.order_date = request.form['order_date']

        try:
            db.session.commit()
            return redirect('/orders')
        except Exception as e:
            db.session.rollback()
            return f"Error updating order: {e}"

    return render_template('update_order.html', order=order)


# Initialize database and create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=2021, debug=True)