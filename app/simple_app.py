from flask import Flask, render_template, request, redirect, url_for, flash
import os
import sys
from web3 import Web3
import json

app = Flask(__name__)
app.secret_key = "testing_secret_key"

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level to the project root
project_root = os.path.dirname(script_dir)

def get_contract():
    # Connect to blockchain
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    
    # Set default account
    account = w3.eth.accounts[0]
    
    # Load contract address
    contract_address_path = os.path.join(project_root, "contract_address.txt")
    with open(contract_address_path, "r") as file:
        contract_address = file.read().strip()
    
    # Load ABI
    abi_path = os.path.join(project_root, "abi.json")
    with open(abi_path, "r") as file:
        abi = json.load(file)
    
    # Create contract instance
    contract = w3.eth.contract(address=contract_address, abi=abi)
    
    return w3, contract, account

@app.route('/')
def index():
    try:
        w3, contract, account = get_contract()
        value = contract.functions.retrieve().call()
        return f"<h1>Simple Storage DApp</h1><p>Current value: {value}</p><form method='POST' action='/store'><input type='number' name='value'><button type='submit'>Store</button></form>"
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>"

@app.route('/store', methods=['POST'])
def store():
    try:
        value = int(request.form.get('value', 0))
        w3, contract, account = get_contract()
        tx_hash = contract.functions.store(value).transact({'from': account})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return redirect(url_for('index'))
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>"

if __name__ == '__main__':
    app.run(debug=True)