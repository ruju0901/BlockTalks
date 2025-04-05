from web3 import Web3
import json
import os
from dotenv import load_dotenv
from ipfs_requests import store_post_content, retrieve_post_content

# Load environment variables
load_dotenv()

def get_contract():
    # Connect to blockchain
    w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI", "http://127.0.0.1:7545")))
    
    # Set default account
    default_account = w3.eth.accounts[0]
    
    # Load contract address
    try:
        with open("forum_contract_address.txt", "r") as file:
            contract_address = file.read().strip()
    except FileNotFoundError:
        # Fallback to project root
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        contract_address_path = os.path.join(project_root, "forum_contract_address.txt")
        with open(contract_address_path, "r") as file:
            contract_address = file.read().strip()
    
    # Load ABI
    try:
        with open("forum_abi.json", "r") as file:
            abi = json.load(file)
    except FileNotFoundError:
        # Fallback to project root
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        abi_path = os.path.join(project_root, "forum_abi.json")
        with open(abi_path, "r") as file:
            abi = json.load(file)
    
    # Create contract instance
    contract = w3.eth.contract(address=contract_address, abi=abi)
    
    return w3, contract, default_account

def create_post(title, content, is_news=False, user_address=None, account_index=None):
    """
    Create a new post on the forum.
    
    Args:
        title (str): Post title
        content (str): Post content
        is_news (bool): Whether this is a news post
        user_address (str): Specific user address to use (highest priority)
        account_index (int): Index of account to use (if user_address not provided)
    """
    w3, contract, default_account = get_contract()
    
    # Priority: 1. Explicit user_address, 2. account_index, 3. default_account
    if user_address and Web3.is_address(user_address):
        from_account = user_address
    elif account_index is not None and account_index < len(w3.eth.accounts):
        from_account = w3.eth.accounts[account_index]
    else:
        from_account = default_account
    
    # Store content on IPFS and get content hash
    content_hash = store_post_content(title, content, from_account)
    
    if not content_hash:
        raise Exception("Failed to store content on IPFS")
    
    # Log which account we're using
    print(f"Creating post from account: {from_account}")
    print(f"Content stored on IPFS with hash: {content_hash}")
    
    # Create post transaction with IPFS hash
    tx_hash = contract.functions.createPost(title, content_hash, is_news).transact({'from': from_account})
    
    # Wait for confirmation
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    # Get the post ID from the event logs
    post_id = None
    for log in contract.events.PostCreated().process_receipt(tx_receipt):
        post_id = log['args']['postId']
    
    return post_id, tx_receipt

def vote_post(post_id, is_upvote, user_address=None, account_index=None):
    """
    Vote on a post.
    
    Args:
        post_id (int): ID of post to vote on
        is_upvote (bool): True for upvote, False for downvote
        user_address (str): Specific user address to use
        account_index (int): Index of account to use (if user_address not provided)
    """
    w3, contract, default_account = get_contract()
    
    # Determine which account to use
    if user_address and Web3.is_address(user_address):
        from_account = user_address
    elif account_index is not None and account_index < len(w3.eth.accounts):
        from_account = w3.eth.accounts[account_index]
    else:
        from_account = default_account
    
    # Check if user has already voted
    has_voted, _ = contract.functions.hasUserVoted(post_id, from_account).call()
    if has_voted:
        return False, "User has already voted on this post"
    
    # Create vote transaction
    tx_hash = contract.functions.votePost(post_id, is_upvote).transact({'from': from_account})
    
    # Wait for confirmation
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    return True, tx_receipt

def update_user_sentiment(user_address, sentiment_tag, from_address=None, account_index=None):
    """
    Update a user's sentiment tag.
    
    Args:
        user_address (str): Address of user to update
        sentiment_tag (str): New sentiment tag
        from_address (str): Address to send transaction from
        account_index (int): Index of account to use (if from_address not provided)
    """
    w3, contract, default_account = get_contract()
    
    # Determine which account to use
    if from_address and Web3.is_address(from_address):
        from_account = from_address
    elif account_index is not None and account_index < len(w3.eth.accounts):
        from_account = w3.eth.accounts[account_index]
    else:
        from_account = default_account
    
    # Create update sentiment transaction
    tx_hash = contract.functions.updateUserSentiment(user_address, sentiment_tag).transact({'from': from_account})
    
    # Wait for confirmation
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    return tx_receipt

def get_all_posts():
    """Get all posts from the forum."""
    w3, contract, _ = get_contract()
    
    # Get post count
    post_count = contract.functions.postCount().call()
    
    posts = []
    # Get all posts
    for i in range(1, post_count + 1):
        post = contract.functions.posts(i).call()
        # Get content from IPFS
        try:
            ipfs_data = retrieve_post_content(post[3])  # post[3] is contentHash
            if ipfs_data:
                content = ipfs_data.get('content', 'Content could not be loaded from IPFS')
            else:
                content = "Content could not be loaded from IPFS"
        except Exception as e:
            print(f"Error retrieving content for post {i}: {str(e)}")
            content = "Error loading content from IPFS"
            
        # Format post data
        post_data = {
            'id': post[0],
            'author': post[1],
            'title': post[2],
            'content': content,
            'ipfs_hash': post[3],
            'timestamp': post[4],
            'upvotes': post[5],
            'downvotes': post[6],
            'isNews': post[7]
        }
        posts.append(post_data)
    
    return posts

def get_user_reputation(user_address):
    """Get reputation data for a user."""
    w3, contract, _ = get_contract()
    
    # Get user reputation
    rep_data = contract.functions.getUserReputation(user_address).call()
    
    # Format reputation data
    reputation = {
        'totalPosts': rep_data[0],
        'totalUpvotesReceived': rep_data[1],
        'totalDownvotesReceived': rep_data[2],
        'reputationScore': rep_data[3] / 100,  # Convert to a score out of 10
        'sentimentTag': rep_data[4]
    }
    
    return reputation

def get_post(post_id):
    """Get a specific post by ID."""
    w3, contract, _ = get_contract()
    
    # Get post data
    post = contract.functions.posts(post_id).call()
    
    # Get content from IPFS
    try:
        ipfs_data = retrieve_post_content(post[3])  # post[3] is contentHash
        if ipfs_data:
            content = ipfs_data.get('content', 'Content could not be loaded from IPFS')
        else:
            content = "Content could not be loaded from IPFS"
    except Exception as e:
        print(f"Error retrieving content for post {post_id}: {str(e)}")
        content = "Error loading content from IPFS"
    
    # Format post data
    post_data = {
        'id': post[0],
        'author': post[1],
        'title': post[2],
        'content': content,
        'ipfs_hash': post[3],
        'timestamp': post[4],
        'upvotes': post[5],
        'downvotes': post[6],
        'isNews': post[7]
    }
    
    return post_data

def has_user_voted(post_id, user_address):
    """Check if a user has voted on a post."""
    w3, contract, _ = get_contract()
    
    # Check if user has voted
    return contract.functions.hasUserVoted(post_id, user_address).call()