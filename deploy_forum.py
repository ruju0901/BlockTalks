from web3 import Web3
from solcx import compile_standard, install_solc
import json
import os

print("Starting DiscussionForum deployment...")

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
print(f"Connected to Ganache: {w3.is_connected()}")

# Use the first account
account = w3.eth.accounts[0]
print(f"Using account: {account}")

# Read the contract file
with open("./contracts/DiscussionForum.sol", "r") as file:
    contract_file = file.read()

print("Compiling contract...")
try:
    # Make sure solc is installed
    install_solc("0.8.0")
    
    # Compile the contract
    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"DiscussionForum.sol": {"content": contract_file}},
            "settings": {
                "outputSelection": {
                    "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
                }
            },
        },
        solc_version="0.8.0",
    )
    
    # Get bytecode and ABI
    bytecode = compiled_sol["contracts"]["DiscussionForum.sol"]["DiscussionForum"]["evm"]["bytecode"]["object"]
    abi = compiled_sol["contracts"]["DiscussionForum.sol"]["DiscussionForum"]["abi"]
    
    print("Contract compiled successfully")
    
    # Create contract instance
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    # Deploy contract
    print("Deploying contract...")
    tx_hash = w3.eth.send_transaction({
        'from': account,
        'data': "0x" + bytecode,
        'gas': 6000000  # Higher gas limit for a larger contract
    })
    
    # Wait for transaction receipt
    print("Waiting for transaction receipt...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    contract_address = tx_receipt.contractAddress
    print(f"Contract deployed at: {contract_address}")
    
    # Save contract address and ABI
    with open("forum_contract_address.txt", "w") as file:
        file.write(contract_address)
    
    with open("forum_abi.json", "w") as file:
        json.dump(abi, file)
    
    print("Deployment complete!")
    
except Exception as e:
    print(f"Error during deployment: {str(e)}")