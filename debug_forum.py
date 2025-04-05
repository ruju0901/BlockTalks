from web3 import Web3
import json
import os

print("=== Post Author Verification Script ===")

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
print(f"Connected to blockchain: {w3.is_connected()}")

# Load contract info
with open("forum_contract_address.txt", "r") as file:
    contract_address = file.read().strip()

with open("forum_abi.json", "r") as file:
    abi = json.load(file)

# Create contract instance
contract = w3.eth.contract(address=contract_address, abi=abi)

# Get post count
post_count = contract.functions.postCount().call()
print(f"Total posts on forum: {post_count}")

# Check each post's author
print("\nPosts and authors:")
print("-" * 50)
for i in range(1, post_count + 1):
    post = contract.functions.posts(i).call()
    post_id = post[0]
    author = post[1]
    title = post[2]
    content = post[3]
    
    print(f"Post #{post_id}: '{title}'")
    print(f"Author: {author}")
    print(f"Content: {content[:30]}..." if len(content) > 30 else f"Content: {content}")
    print("-" * 50)

# Show available accounts
print("\nAvailable accounts:")
for i, account in enumerate(w3.eth.accounts[:5]):
    print(f"Account {i}: {account}")

# Function to create a post with explicit account
def create_post_with_account(title, content, is_news, from_account, account_index=None):
    print(f"\nCreating post as {from_account}")
    print(f"Account index: {account_index}" if account_index is not None else "Using explicit address")
    
    try:
        # Create post transaction
        tx_hash = contract.functions.createPost(title, content, is_news).transact({'from': from_account})
        
        # Wait for confirmation
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        tx_hash_hex = tx_hash.hex()
        
        print(f"Transaction successful: {tx_hash_hex[:10]}...")
        print(f"Block: {tx_receipt.blockNumber}")
        
        # Get post ID from events
        post_id = None
        for log in contract.events.PostCreated().process_receipt(tx_receipt):
            post_id = log['args']['postId']
            print(f"New post ID: {post_id}")
            
        return post_id, tx_receipt
    except Exception as e:
        print(f"Error creating post: {str(e)}")
        return None, None

# Test function
def test_post_creation():
    print("\n=== Testing post creation with specific accounts ===")
    
    # Get two different accounts
    account1 = w3.eth.accounts[0]
    account2 = w3.eth.accounts[1]
    
    print(f"Account 1: {account1}")
    print(f"Account 2: {account2}")
    
    # Create a post with account 1
    post_id1, _ = create_post_with_account(
        f"Test post from account 1", 
        "This is a test post to verify the sender", 
        False,  # not news
        account1
    )
    
    # Create a post with account 2
    post_id2, _ = create_post_with_account(
        f"Test post from account 2", 
        "This is another test post from a different account", 
        False,  # not news
        account2
    )
    
    # Verify the posts
    if post_id1 and post_id2:
        post1 = contract.functions.posts(post_id1).call()
        post2 = contract.functions.posts(post_id2).call()
        
        print("\n=== Verification ===")
        print(f"Post 1 author: {post1[1]}")
        print(f"Should match account 1: {account1}")
        print(f"Match: {post1[1].lower() == account1.lower()}")
        
        print(f"Post 2 author: {post2[1]}")
        print(f"Should match account 2: {account2}")
        print(f"Match: {post2[1].lower() == account2.lower()}")

# Run the test
if __name__ == "__main__":
    test_post_creation()