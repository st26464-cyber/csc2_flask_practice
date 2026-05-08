import json 

from flask import Flask, render_template, request, redirect, url_for, session, flash 

app = Flask (__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index() :
   flowers = load_data()
   return render_template('index.html', flowers=flowers)

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
    
if __name__=='__main__':
    app.run(debug=True)


