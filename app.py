import json 

from flask import Flask, render_template, request, redirect, url_for, session, flash 

app = Flask (__name__)
app.secret_key = 'your_secret_key'
def load_data():
    with open('data/flowers.json') as file:
        flowers = json.load(file)
    with open('data/addons.json') as file:
        addons = json.load(file)
    return flowers, addons

def calculate_total(cart):
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return total
    
@app.route('/')
def index1():
    cart = session.get('cart', {})
    flowers, addons = load_data()

    total = calculate_total(cart)

    return render_template(
        'index1.html',
        flowers=flowers,
        addons=addons,
        cart=cart,
        total=total
    )
@app.route('/about')
def about() :
   return render_template('about.html')

@app.route('/checkout')
def checkout() :
   return render_template('invoice.html')

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

        return redirect(url_for('index'))

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

    return redirect(url_for('index'))

@app.route('/remove_from_cart/<item>')
def remove_from_cart(item):
    cart = session.get('cart', {})

    if item in cart:
        del cart[item]
        session['cart'] = cart
        session.modified = True
        flash(f"{item} removed from cart.")
    else:
        flash("Item not found in cart")

    return redirect(url_for('index'))
if __name__=='__main__':
    app.run(debug=True)
