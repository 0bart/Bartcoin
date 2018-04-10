from flask import Flask, jsonify, request, render_template, flash, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from argparse import ArgumentParser
import requests
from forms import NewTransactionForm, CheckWalletForm, GenerateForm

moment = Moment()
bootstrap = Bootstrap()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

moment.init_app(app)
bootstrap.init_app(app)

node_address = '127.0.0.1:5000'

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/chain', methods=['GET'])
def chain():
    try:
        response = requests.get(f'http://{node_address}/chain', timeout=5)
    except requests.exceptions.Timeout:
        print(f'Timeout in chain requests - {node_address}')

    if response.status_code == 200:
        length = response.json()['length']
        chain_ = response.json()['chain']

        return render_template("chain.html", length=length, chain=chain_)

    return redirect("404.html"), 404

@app.route('/transactions', defaults={'wallet_address': None}, methods=['GET', 'POST'])
@app.route('/transactions/<wallet_address>', methods=['GET'])
def transactions(wallet_address):
    form = CheckWalletForm()
    if form.validate_on_submit(): #request.method == 'POST':
        wallet_address = form.wallet_add.data #request.form['wallet_add']
        return redirect(url_for('transactions', wallet_address=wallet_address))
    elif wallet_address:
        try:
            response = requests.get(f'http://{node_address}/wallet/transactions/{wallet_address}', timeout=5)
            response2 = requests.get(f'http://{node_address}/wallet/saldo/{wallet_address}', timeout=5)

        except requests.exceptions.Timeout:
            print(f'Timeout in chain requests - {node_address}')

        if response.status_code == 200 and response2.status_code == 200:
            transactions = response.json()['transactions']
            saldo = response2.json()['saldo']
            return render_template("transactions.html", transactions=transactions, saldo=saldo, wallet_address=wallet_address)
    else:
        return render_template("transactions.html", form=form)

@app.route('/transactions/new', methods=['GET', 'POST'])
def new_transaction():
    form = NewTransactionForm()
    if form.validate_on_submit(): #request.method == 'POST':
        transaction_dict = {
            'sender': form.wallet_add.data,
            'recipient': form.recipient.data,
            'amount': form.amount.data,
            'sign': form.sign.data,
        }
        try:
            response = requests.post(f'http://{node_address}/transaction/new', json=transaction_dict, timeout=3)
            print("ODP")
            print(response.text)
        except requests.exceptions.Timeout:
            print("Sth went wrong")

        return render_template("new_transaction.html", response=response.text, transaction_dict=transaction_dict)
    else:
        return render_template("new_transaction.html", form=form)


@app.route('/wallet', methods=['GET', 'POST'])
def wallet():
    form = GenerateForm()
    if form.validate_on_submit():
        try:
            response = requests.get(f'http://{node_address}/wallet/generate', timeout=5)
        except requests.exceptions.Timeout:
            print(f'Timeout in chain requests - {node_address}')

        if response.status_code == 200:
            wallet_address = response.json()['wallet_address']
            private_key = response.json()['private_key']
            #flash("Wallet succesfully generated!")
            return render_template("wallet.html", wallet_address=wallet_address, private_key=private_key)
    else:
        return render_template("wallet.html", form=form)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=7000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
