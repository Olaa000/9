from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# MongoDB connection
client = MongoClient(os.getenv('MONGODB_URI'))
db = client.product_catalog

# Collections
products = db.products
orders = db.orders
clients = db.clients

@app.route('/')
def index():
    return render_template('index.html')

# Products CRUD
@app.route('/products')
def list_products():
    all_products = list(products.find())
    return render_template('products/list.html', products=all_products)

@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product = {
            'name': request.form['name'],
            'price': float(request.form['price']),
            'quantity': int(request.form['quantity']),
            'description': request.form['description']
        }
        products.insert_one(product)
        return redirect(url_for('list_products'))
    return render_template('products/add.html')

@app.route('/products/edit/<id>', methods=['GET', 'POST'])
def edit_product(id):
    if request.method == 'POST':
        products.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'name': request.form['name'],
                'price': float(request.form['price']),
                'quantity': int(request.form['quantity']),
                'description': request.form['description']
            }}
        )
        return redirect(url_for('list_products'))
    product = products.find_one({'_id': ObjectId(id)})
    return render_template('products/edit.html', product=product)

@app.route('/products/delete/<id>')
def delete_product(id):
    products.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('list_products'))

# Orders CRUD
@app.route('/orders')
def list_orders():
    all_orders = list(orders.find())
    # Add client name to orders
    for order in all_orders:
        client = clients.find_one({'_id': order['client_id']}) 
        product = products.find_one({'_id': order['product_id']}) 
        order['client_name'] = client['name'] if client else 'Unknown'
        order['product_name'] = product['name'] if product else 'Unknown'
    return render_template('orders/list.html', orders=all_orders)

@app.route('/orders/add', methods=['GET', 'POST'])
def add_order():
    if request.method == 'POST':
        order = {
            'product_id': ObjectId(request.form['product_id']),
            'client_id': ObjectId(request.form['client_id']),
            'quantity': int(request.form['quantity']),
            'order_date': datetime.strptime(request.form['order_date'], '%Y-%m-%d'),
            'status': request.form['status']
        }
        orders.insert_one(order)
        return redirect(url_for('list_orders'))
    all_products = list(products.find())
    all_clients = list(clients.find())
    return render_template('orders/add.html', products=all_products, clients=all_clients)

@app.route('/orders/edit/<id>', methods=['GET', 'POST'])
def edit_order(id):
    if request.method == 'POST':
        orders.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'product_id': ObjectId(request.form['product_id']),
                'client_id': ObjectId(request.form['client_id']),
                'quantity': int(request.form['quantity']),
                'order_date': datetime.strptime(request.form['order_date'], '%Y-%m-%d'),
                'status': request.form['status']
            }}
        )
        return redirect(url_for('list_orders'))
    order = orders.find_one({'_id': ObjectId(id)})
    all_products = list(products.find())
    all_clients = list(clients.find())
    return render_template('orders/edit.html', order=order, products=all_products, clients=all_clients)

@app.route('/orders/delete/<id>')
def delete_order(id):
    orders.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('list_orders'))

# Clients CRUD
@app.route('/clients')
def list_clients():
    all_clients = list(clients.find())
    return render_template('clients/list.html', clients=all_clients)

@app.route('/clients/add', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        client = {
            'name': request.form['name'],
            'email': request.form['email'],
            'phone': request.form['phone']
        }
        clients.insert_one(client)
        return redirect(url_for('list_clients'))
    return render_template('clients/add.html')

@app.route('/clients/edit/<id>', methods=['GET', 'POST'])
def edit_client(id):
    if request.method == 'POST':
        clients.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'name': request.form['name'],
                'email': request.form['email'],
                'phone': request.form['phone']
            }}
        )
        return redirect(url_for('list_clients'))
    client = clients.find_one({'_id': ObjectId(id)})
    return render_template('clients/edit.html', client=client)

@app.route('/clients/delete/<id>')
def delete_client(id):
    clients.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('list_clients'))


if __name__ == '__main__':
    app.run(debug=True)
