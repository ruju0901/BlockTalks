from web3 import Web3
from solcx import compile_standard, install_solc
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Install specific Solidity compiler version
install_solc("0.8.0")

def deploy_contract():
    # Connect to blockchain
    w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI", "http://127.0.0.1:7545")))
    
    # Set default account
    account = w3.eth.accounts[0]
    private_key = os.getenv("PRIVATE_KEY")
    
    # Read the contract file
    with open("./contracts/DiscussionForum.sol", "r") as file:
        contract_file = file.read()
    
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
    
    # Save the compiled contract
    with open("compiled_code.json", "w") as file:
        json.dump(compiled_sol, file)
    
    # Get bytecode
    bytecode = compiled_sol["contracts"]["DiscussionForum.sol"]["DiscussionForum"]["evm"]["bytecode"]["object"]
    
    # Get ABI
    abi = compiled_sol["contracts"]["DiscussionForum.sol"]["DiscussionForum"]["abi"]
    
    # Save ABI to a file for later use
    with open("abi.json", "w") as file:
        json.dump(abi, file)
    
    # Create the contract
    Forum = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    # Get nonce
    nonce = w3.eth.get_transaction_count(account)
    
    # Create deployment transaction
    transaction = Forum.constructor().build_transaction(
        {
            "chainId": w3.eth.chain_id,
            "from": account,
            "nonce": nonce,
            "gasPrice": w3.eth.gas_price,
        }
    )
    
    # Sign the transaction
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    
    # Send the transaction
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    
    # Wait for transaction receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    print(f"Contract deployed at {tx_receipt.contractAddress}")
    
    # Save contract address for later use
    with open("contract_address.txt", "w") as file:
        file.write(tx_receipt.contractAddress)
    
    return tx_receipt.contractAddress, abi

if __name__ == "__main__":
    deploy_contract()