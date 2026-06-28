import json 
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash 

import sqlite3
def initialise_database(): 
    with sqlite3.connect('flower_shop.db') as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT,
                customer_name TEXT,
                items TEXT,
                addons TEXT,
                total REAL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
 #Create the Flask application
app = Flask(__name__)
app.secret_key = 'your_secret_key'
# Load flower and add-on data from JSON files
def load_data():
    with open('data/flowers.json') as file:
        flowers = json.load(file)
    with open('data/addons.json') as file:
        addons = json.load(file)
    return flowers, addons
# Calculate the total cost of flowers and selected add-ons
def calculate_total(cart, selected_addons):
    flower_total = sum(
        item['price'] * item['quantity']
        for item in cart.values()
    )

    addon_total = sum(selected_addons.values())
    
    # Store initial sum before running the discount check
    total = flower_total + addon_total
    discount_applied = False

    # Apply 10% discount if total is greater than 180
    if total > 180:
        total *= 0.9   # Apply 10% discount
        discount_applied = True

    return round(total, 2), discount_applied   
@app.route('/')
def index1():
    cart = session.get('cart', {})
    selected_addons = session.get('selected_addons', {})

    flowers, addons = load_data()

    total, discount_applied = calculate_total(cart, selected_addons)

    return render_template(
        'index1.html',
        flowers=flowers,
        addons=addons,
        cart=cart,
        total=total,
        discount_applied=discount_applied,
        selected_addons=selected_addons
    )
# Display the About page
@app.route('/about')
def about() :
   return render_template('about.html')

# Process customer checkout and generate invoice
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', {})
    # 1. If a user tries to visit the page directly via URL link, redirect them back to the shop
    if request.method == 'GET':
        flash("Please add items to your cart and use the checkout form.")
        return redirect(url_for('index1'))
    
    customer_name = request.form['customer_name'].strip().title()

    if not customer_name:
        flash("Customer name is required.")
        return redirect(url_for('index1'))

    cart = session.get('cart', {})
    selected_addons = session.get('selected_addons', {})

    if not cart:
        flash("Your cart is empty.")
        return redirect(url_for('index1'))
# Calculate final order total
    total, discount_applied = calculate_total(cart, selected_addons)
    try:
        # Load the active stock metrics from your flowers data file
        with open('data/flowers.json', 'r') as file:
            flower_data = json.load(file)

        # Loop through each item bought in the current session cart
        for flower_name, details in cart.items():
            if flower_name in flower_data:
                # Subtract what they purchased from the inventory
                flower_data[flower_name]['stock'] -= details['quantity']
                
                # Check to prevent negative stock numbers
                if flower_data[flower_name]['stock'] < 0:
                    flower_data[flower_name]['stock'] = 0

        # Save the updated stock metrics back to your data folder
        with open('data/flowers.json', 'w') as file:
            json.dump(flower_data, file, indent=4)
            
    except Exception as stock_err:
        print(f"Error handling stock counts update: {stock_err}")
# Create invoice details
    invoice_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    invoice_number = f"INV_{customer_name.replace(' ', '_')}"
    try:
        # Convert dictionaries to strings using json.dumps()
        items_json = json.dumps(cart)
        addons_json = json.dumps(selected_addons)

        with sqlite3.connect('flower_shop.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO orders (invoice_number, customer_name, items, addons, total)
                VALUES (?, ?, ?, ?, ?)
            ''', (invoice_number, customer_name, items_json, addons_json, total))
            conn.commit()
    except Exception as e:
        print(f"Database error: {e}")
        flash("There was an error saving your order to the database.")
      
    return render_template(
        'invoice.html',
        customer_name=customer_name,
        cart=cart,
        selected_addons=selected_addons,
        total=total,
        invoice_number=invoice_number,
        discount_applied=discount_applied,
        invoice_date=invoice_date
    )

# Display order history page
@app.route('/order')
def order_history() :
    with sqlite3.connect('flower_shop.db') as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM orders ORDER BY date DESC")
        rows = cursor.fetchall()

        orders = []

        for row in rows:
            orders.append({
                'order_id': row[0],
                'invoice_number': row[1],
                'customer_name': row[2],
                'items': json.loads(row[3]),
                'addons': json.loads(row[4]),
                'total': row[5],
                'date': row[6]
                
            })

    return render_template('order_history.html',orders=orders)

# Display the home page
@app.route('/page1')
def page1():
    return render_template('index1.html')
# Add selected flowers to the shopping cart
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():

    flower = request.form['flower']
    quantity = int(request.form['quantity'])

    flowers, addons = load_data()

    cart = session.get('cart', {})
# Check that the flower exists
    if flower not in flowers:

        flash("Invalid flower selected.")

        return redirect(url_for('index1'))

    if flower in cart:

        cart[flower]['quantity'] += quantity

    else:

        cart[flower] = {
            'price': flowers[flower]['price'],
            'quantity': quantity
        }
 # Save updated cart to session
    session['cart'] = cart
    session.modified = True

    flash(f"{quantity} {flower}(s) added to cart.")

    return redirect(url_for('index1'))

# Remove an item completely from the cart
@app.route('/remove_from_cart/<item>')
def remove_from_cart(item):
    cart = session.get('cart', {})

    if item in cart:
        del cart[item]
        session['cart'] = cart
        session.modified = True
        flash(f"Removed all {item} from the cart.")
    else:
        flash("Item not found in cart")


    return redirect(url_for('index1'))
# Save selected add-ons to the session
@app.route('/select_addon', methods=['POST'])
def select_addon():

    selected_addons = {}

    _, addons = load_data()

    selected_keys = request.form.getlist('addons')

    for addon in selected_keys:
        if addon in addons:
            selected_addons[addon] = float(addons[addon]['price'])

    session['selected_addons'] = selected_addons
    session.modified = True

    flash("Add-ons selected successfully!")

    return redirect(url_for('index1'))
# Clear the cart and cancel the order
@app.route('/cancel_order', methods=['POST'])
def cancel_order():
    session.pop('cart', None)
    session.pop('selected_addons', None)
    session.modified = True
    flash("Order cancelled successfully. Cart has been cleared.")

    return redirect(url_for('index1'))

@app.route('/cancel_saved_order/<order_id>', methods=['POST'])
def cancel_saved_order(order_id):
    with sqlite3.connect('flower_shop.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT items FROM orders WHERE invoice_number = ?", (order_id,))
        row = cursor.fetchone()
            
        if row:
                # Convert the saved database items string back into a Python dictionary
                order_items = json.loads(row[0])
                
                # 2. Open up the original flowers active storage metrics file
                with open('data/flowers.json', 'r') as file:
                    flower_data = json.load(file)
                
                # 3. Add the canceled quantities right back into the active stock counts
                for flower_name, details in order_items.items():
                    if flower_name in flower_data:
                        flower_data[flower_name]['stock'] += details['quantity']
                
                # 4. Save the updated layout safely back into the JSON file
                with open('data/flowers.json', 'w') as file:
                    json.dump(flower_data, file, indent=4)
        # Change 'id = ?' to match your invoice column name (e.g., invoice_number)
        cursor.execute("DELETE FROM orders WHERE invoice_number = ?", (order_id,))
        conn.commit()
        
    flash("Order cancelled successfully.")
    return redirect(url_for('order_history'))
# Run the application
if __name__ == '__main__':
    initialise_database()
    app.run(debug=True)
 