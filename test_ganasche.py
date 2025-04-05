from web3 import Web3

# Connect to the correct Ganache port
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

# Check connection
if w3.is_connected():
    print("✅ Successfully connected to Ganache!")
    print(f"Chain ID: {w3.eth.chain_id}")
    print("\nAccounts:")
    for i, account in enumerate(w3.eth.accounts[:3]):
        print(f"  Account {i}: {account}")
else:
    print("❌ Failed to connect to Ganache!")