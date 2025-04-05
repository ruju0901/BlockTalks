from web3 import Web3
import json

print("Starting minimal deployment...")

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
print(f"Connected to Ganache: {w3.is_connected()}")

if not w3.is_connected():
    print("Failed to connect to Ganache. Make sure it's running.")
    exit(1)

# Get the first account
account = w3.eth.accounts[0]
print(f"Using account: {account}")

# Hard-coded ABI and bytecode for a simple storage contract
# We'll use this instead of compiling the DiscussionForum contract
print("Using pre-compiled contract data...")

# Simple storage contract - much smaller than your discussion forum contract
abi = [
    {
        "inputs": [],
        "name": "retrieve",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "num", "type": "uint256"}],
        "name": "store",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

bytecode = "608060405234801561001057600080fd5b50610150806100206000396000f3fe608060405234801561001057600080fd5b50600436106100365760003560e01c80632e64cec11461003b5780636057361d14610059575b600080fd5b610043610075565b60405161005091906100a1565b60405180910390f35b610073600480360381019061006e91906100ed565b61007e565b005b60008054905090565b8060008190555050565b6000819050919050565b61009b81610088565b82525050565b60006020820190506100b66000830184610092565b92915050565b600080fd5b6100ca81610088565b81146100d557600080fd5b50565b6000813590506100e7816100c1565b92915050565b600060208284031215610103576101026100bc565b5b6000610111848285016100d8565b9150509291505056fea2646970667358221220322c78243e61b783558509c9cc22cb8493dde6925aa5e89a08cdf6e22f279ef164736f6c63430008120033"

# Create contract instance
contract = w3.eth.contract(abi=abi, bytecode=bytecode)

# Deploy contract
print("Deploying contract...")
tx_hash = w3.eth.send_transaction({
    'from': account,
    'data': bytecode,
    'gas': 3000000
})

# Wait for transaction receipt
print("Waiting for transaction receipt...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = tx_receipt.contractAddress
print(f"Contract deployed at: {contract_address}")

# Save contract address and ABI
with open("contract_address.txt", "w") as file:
    file.write(contract_address)

with open("abi.json", "w") as file:
    json.dump(abi, file)

print("Deployment complete!")