import json 

from flask import Flask, render_template, request, redirect, url_for, session, flash 

app = Flask (__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index() :
   flowers, addons = load_data()
   return render_template('index1.html', flowers=flowers , addons=addons)

@app.route('/about')
def about() :
   return render_template('about.html')

@app.route('/checkout')
def checkout() :
   return render_template('invoice.html')

@app.route('/order')
def order_history() :
   return render_template('order_history.html')

def load_data():
   with open('data/flowers.json') as file:
      flowers = json.load(file)  

   with open('data/addons.json') as file:
      addons = json.load(file)

   return flowers, addons

flowers = {
    "Rose": {"price": 10, "stock": 50},
    "Tulip": {"price": 10, "stock": 40},
    "Lily": {"price": 10, "stock": 30},
    "Daisy": {"price": 10, "stock": 100},
}
addons = {
    "Ribbon": {"price": 2},
    "Specialty Wrapping Paper": {"price": 5},
    "Personalised Note": {"price": 3},
    "Delivery": {"price": 10}
}

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
