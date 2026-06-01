import json 
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash 

app = Flask (__name__)
app.secret_key = 'your_secret_key'
def load_data():
    with open('data/flowers.json') as file:
        flowers = json.load(file)
    with open('data/addons.json') as file:
        addons = json.load(file)
    return flowers, addons

def calculate_total(cart, selected_addons):
    flower_total = sum(
        item['price'] * item['quantity']
        for item in cart.values()
    )

    addon_total = sum(selected_addons.values())

    return flower_total + addon_total
    
@app.route('/')
def index1():
    cart = session.get('cart', {})
    selected_addons = session.get('selected_addons', {})

    flowers, addons = load_data()

    total = calculate_total(cart, selected_addons)

    return render_template(
        'index1.html',
        flowers=flowers,
        addons=addons,
        cart=cart,
        total=total,
        selected_addons=selected_addons
    )
@app.route('/about')
def about() :
   return render_template('about.html')
@app.route('/checkout', methods=['POST'])
def checkout():

    customer_name = request.form['customer_name'].strip().title()

    if not customer_name:
        flash("Customer name is required.")
        return redirect(url_for('index1'))

    cart = session.get('cart', {})
    selected_addons = session.get('selected_addons', {})

    if not cart:
        flash("Your cart is empty.")
        return redirect(url_for('index1'))

    total = calculate_total(cart, selected_addons)

    invoice_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    invoice_number = f"INV_{customer_name.replace(' ', '_')}"

    return render_template(
        'invoice.html',
        customer_name=customer_name,
        cart=cart,
        selected_addons=selected_addons,
        total=total,
        invoice_number=invoice_number,
        invoice_date=invoice_date
    )

@app.route('/order')
def order_history() :
   return render_template('order_history.html')

@app.route('/page1')
def page1():
    return render_template('index1.html')

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():

    flower = request.form['flower']
    quantity = int(request.form['quantity'])

    flowers, addons = load_data()

    cart = session.get('cart', {})

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

    session['cart'] = cart
    session.modified = True

    flash(f"{quantity} {flower}(s) added to cart.")

    return redirect(url_for('index1'))

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

@app.route('/cancel_order', methods=['POST'])
def cancel_order():
    session.pop('cart', None)
    session.pop('selected_addons', None)

    flash("Order cancelled successfully. Cart has been cleared.")

    return redirect(url_for('index1'))

if __name__=='__main__':
    app.run(debug=True)
