from web3 import Web3
import json
import time
from pprint import pprint

def main():
    print("=== Decentralized Forum Tester ===")
    
    # Connect to blockchain
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
    print(f"Connected to blockchain: {w3.is_connected()}")
    
    # Load contract info
    try:
        with open("forum_contract_address.txt", "r") as file:
            contract_address = file.read().strip()
    except FileNotFoundError:
        print("Error: forum_contract_address.txt not found")
        return
    
    try:
        with open("forum_abi.json", "r") as file:
            abi = json.load(file)
    except FileNotFoundError:
        print("Error: forum_abi.json not found")
        return
    
    # Create contract instance
    contract = w3.eth.contract(address=contract_address, abi=abi)
    print(f"Contract loaded at address: {contract_address}")
    
    # Get available accounts
    accounts = w3.eth.accounts[:5]
    print(f"\nAvailable accounts:")
    for i, acct in enumerate(accounts):
        print(f"Account {i}: {acct}")
    
    # Get current post count
    current_post_count = contract.functions.postCount().call()
    print(f"\nCurrent post count: {current_post_count}")
    
    # Test creating posts from two different accounts
    print("\n=== Testing post creation from different accounts ===")
    
    # Create a post from account 0
    title1 = "Test Post from Account 0"
    content1 = "This is a test post created from account 0 to verify transaction sender"
    is_news1 = True
    
    print(f"\nCreating post 1 from account 0 ({accounts[0]})")
    tx_hash1 = contract.functions.createPost(title1, content1, is_news1).transact({'from': accounts[0]})
    tx_receipt1 = w3.eth.wait_for_transaction_receipt(tx_hash1)
    print(f"Transaction successful: {tx_hash1.hex()[:10]}...")
    
    # Create a post from account 1
    title2 = "Test Post from Account 1"
    content2 = "This is a test post created from account 1 to verify transaction sender"
    is_news2 = True
    
    print(f"\nCreating post 2 from account 1 ({accounts[1]})")
    tx_hash2 = contract.functions.createPost(title2, content2, is_news2).transact({'from': accounts[1]})
    tx_receipt2 = w3.eth.wait_for_transaction_receipt(tx_hash2)
    print(f"Transaction successful: {tx_hash2.hex()[:10]}...")
    
    # Wait for block confirmations
    print("\nWaiting for block confirmations...")
    time.sleep(2)
    
    # Get updated post count
    new_post_count = contract.functions.postCount().call()
    print(f"New post count: {new_post_count}")
    print(f"Posts created: {new_post_count - current_post_count}")
    
    # Check the latest posts
    print("\n=== Verifying post authors ===")
    
    # Get the latest two posts
    post1 = contract.functions.posts(new_post_count - 1).call()
    post2 = contract.functions.posts(new_post_count).call()
    
    # Verify post 1
    print("\nPost 1:")
    print(f"Title: {post1[2]}")
    print(f"Author: {post1[1]}")
    print(f"Expected Author: {accounts[0]}")
    print(f"Author match: {post1[1].lower() == accounts[0].lower()}")
    
    # Verify post 2
    print("\nPost 2:")
    print(f"Title: {post2[2]}")
    print(f"Author: {post2[1]}")
    print(f"Expected Author: {accounts[1]}")
    print(f"Author match: {post2[1].lower() == accounts[1].lower()}")
    
    # Test voting
    print("\n=== Testing voting ===")
    
    # Vote on post 1 from account 2
    print(f"Voting on post {new_post_count - 1} from account 2 ({accounts[2]})")
    tx_hash3 = contract.functions.votePost(new_post_count - 1, True).transact({'from': accounts[2]})
    tx_receipt3 = w3.eth.wait_for_transaction_receipt(tx_hash3)
    print(f"Vote transaction successful: {tx_hash3.hex()[:10]}...")
    
    # Get updated post 1
    updated_post1 = contract.functions.posts(new_post_count - 1).call()
    print(f"Post 1 upvotes: {updated_post1[5]}")
    
    # Check reputation
    print("\n=== Checking User Reputation ===")
    
    # Get reputation for account 0
    rep0 = contract.functions.getUserReputation(accounts[0]).call()
    print(f"Account 0 reputation:")
    print(f"Total Posts: {rep0[0]}")
    print(f"Upvotes Received: {rep0[1]}")
    print(f"Downvotes Received: {rep0[2]}")
    print(f"Reputation Score: {rep0[3]/100}/10")
    print(f"Sentiment Tag: {rep0[4]}")
    
    # Get reputation for account 1
    rep1 = contract.functions.getUserReputation(accounts[1]).call()
    print(f"\nAccount 1 reputation:")
    print(f"Total Posts: {rep1[0]}")
    print(f"Upvotes Received: {rep1[1]}")
    print(f"Downvotes Received: {rep1[2]}")
    print(f"Reputation Score: {rep1[3]/100}/10")
    print(f"Sentiment Tag: {rep1[4]}")
    
    print("\n=== Test Complete ===")
    print("If all tests pass, your forum contract is working correctly!")
    print("Make sure your web app is using the correct user addresses for transactions.")

if __name__ == "__main__":
    main()