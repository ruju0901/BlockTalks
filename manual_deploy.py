from web3 import Web3
from solcx import compile_standard, install_solc
import json
import os

print("Starting deployment process...")

# Install Solidity compiler
print("Installing solc...")
install_solc("0.8.0")

# Connect to Ganache
print("Connecting to Ganache...")
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
print(f"Connected: {w3.is_connected()}")

# Get the first account from Ganache
account = w3.eth.accounts[0]
print(f"Using account: {account}")

# Read the contract file
print("Reading contract file...")
with open("./contracts/DiscussionForum.sol", "r") as file:
    contract_file = file.read()

# Compile the contract
print("Compiling contract...")
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

# Save ABI
print("Saving ABI...")
with open("abi.json", "w") as file:
    json.dump(abi, file)

# Create contract instance
contract = w3.eth.contract(abi=abi, bytecode=bytecode)

# Deploy contract
print("Deploying contract...")
tx_hash = w3.eth.send_transaction({
    'from': account,
    'data': bytecode,
    'gas': 6000000
})

# Wait for transaction receipt
print("Waiting for transaction receipt...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = tx_receipt.contractAddress
print(f"Contract deployed at: {contract_address}")

# Save contract address
with open("contract_address.txt", "w") as file:
    file.write(contract_address)

print("Deployment complete!")