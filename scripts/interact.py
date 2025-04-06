from web3 import Web3
import json
import os
from dotenv import load_dotenv
from ipfs_requests import store_post_content, retrieve_post_content

# Load environment variables
load_dotenv()

def is_valid_eth_address(address, w3):
    """Check if an address is a valid Ethereum address and convert to checksum format if needed."""
    if not address:
        return False
        
    try:
        # Try to convert to checksum address (will raise exception if invalid)
        checksum_address = w3.to_checksum_address(address)
        return True
    except:
        return False

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
    if user_address and is_valid_eth_address(user_address, w3):
        from_account = w3.to_checksum_address(user_address)
    elif account_index is not None and account_index < len(w3.eth.accounts):
        from_account = w3.eth.accounts[account_index]
    else:
        from_account = default_account
    
    try:
        # Store content on IPFS and get content hash
        content_hash = "direct_content"  # Fallback if IPFS fails
        try:
            ipfs_hash = store_post_content(title, content, from_account)
            if ipfs_hash:
                content_hash = ipfs_hash
                print(f"Content stored on IPFS with hash: {content_hash}")
            else:
                print("IPFS storage failed, using direct content")
        except Exception as e:
            print(f"IPFS error: {str(e)}, using direct content")
        
        # Log which account we're using
        print(f"Creating post from account: {from_account}")
        
        # Create post transaction with IPFS hash
        tx_hash = contract.functions.createPost(title, content_hash, is_news).transact({'from': from_account})
        
        # Wait for confirmation
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Get the post ID from the event logs
        post_id = None
        for log in contract.events.PostCreated().process_receipt(tx_receipt):
            post_id = log['args']['postId']
        
        print(f"Post created successfully, ID: {post_id}")
        return post_id, tx_receipt
    
    except Exception as e:
        error_msg = str(e)
        print(f"Error creating post: {error_msg}")
        
        # Check for common errors
        if "sender account not recognized" in error_msg:
            error_msg = "Wallet address not recognized. Please make sure you're connected to the correct network."
        elif "insufficient funds" in error_msg:
            error_msg = "Insufficient funds to complete transaction."
        elif "nonce too low" in error_msg:
            error_msg = "Transaction failed. Please try again (nonce issue)."
        
        return None, error_msg

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
    if user_address and is_valid_eth_address(user_address, w3):
        from_account = w3.to_checksum_address(user_address)
    elif account_index is not None and account_index < len(w3.eth.accounts):
        from_account = w3.eth.accounts[account_index]
    else:
        from_account = default_account
    
    try:
        # Check if user has already voted
        has_voted, _ = contract.functions.hasUserVoted(post_id, from_account).call()
        if has_voted:
            return False, "You have already voted on this post"
        
        # Create vote transaction
        tx_hash = contract.functions.votePost(post_id, is_upvote).transact({'from': from_account})
        
        # Wait for confirmation
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Vote recorded successfully from account: {from_account}")
        
        return True, tx_receipt
    
    except Exception as e:
        error_msg = str(e)
        print(f"Error voting on post: {error_msg}")
        
        # Check for common errors
        if "sender account not recognized" in error_msg:
            error_msg = "Wallet address not recognized. Please make sure you're connected to the correct network."
        elif "insufficient funds" in error_msg:
            error_msg = "Insufficient funds to complete transaction."
        elif "nonce too low" in error_msg:
            error_msg = "Transaction failed. Please try again (nonce issue)."
        
        return False, error_msg

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
    if from_address and is_valid_eth_address(from_address, w3):
        from_account = w3.to_checksum_address(from_address)
    elif account_index is not None and account_index < len(w3.eth.accounts):
        from_account = w3.eth.accounts[account_index]
    else:
        from_account = default_account
    
    # Convert user_address to checksum format
    if user_address and is_valid_eth_address(user_address, w3):
        user_address = w3.to_checksum_address(user_address)
    
    try:
        # Create update sentiment transaction
        tx_hash = contract.functions.updateUserSentiment(user_address, sentiment_tag).transact({'from': from_account})
        
        # Wait for confirmation
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"User sentiment updated successfully from account: {from_account}")
        
        return tx_receipt
    
    except Exception as e:
        error_msg = str(e)
        print(f"Error updating user sentiment: {error_msg}")
        
        # Check for common errors
        if "sender account not recognized" in error_msg:
            error_msg = "Wallet address not recognized. Please make sure you're connected to the correct network."
        elif "nonce too low" in error_msg:
            error_msg = "Transaction failed. Please try again (nonce issue)."
        
        return error_msg

def get_all_posts():
    """Get all posts from the forum."""
    w3, contract, _ = get_contract()
    
    try:
        # Get post count
        post_count = contract.functions.postCount().call()
        
        posts = []
        # Get all posts
        for i in range(1, post_count + 1):
            post = contract.functions.posts(i).call()
            # Get content from IPFS
            try:
                content = post[3]  # Default to using hash as content
                if post[3].startswith("Qm"):  # Looks like an IPFS hash
                    ipfs_data = retrieve_post_content(post[3])
                    if ipfs_data and isinstance(ipfs_data, dict):
                        content = ipfs_data.get('content', post[3])
                    else:
                        content = f"Content with IPFS hash: {post[3]}"
                elif post[3] == "direct_content":
                    content = post[2]  # Use title as content if IPFS failed
            except Exception as e:
                print(f"Error retrieving content for post {i}: {str(e)}")
                content = f"Error loading content: {post[3]}"
                
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
            
            # Add sentiment for news posts
            if post_data['isNews']:
                try:
                    from sentiment import analyze_sentiment
                    sentiment, polarity = analyze_sentiment(content)
                    post_data['sentiment'] = sentiment
                    post_data['sentiment_score'] = polarity
                except Exception as e:
                    print(f"Error analyzing sentiment: {str(e)}")
            
            posts.append(post_data)
        
        return posts
    
    except Exception as e:
        print(f"Error getting posts: {str(e)}")
        return []

def get_user_reputation(user_address):
    """Get reputation data for a user."""
    w3, contract, _ = get_contract()
    
    try:
        # Validate address format
        if not is_valid_eth_address(user_address, w3):
            print(f"Invalid address format: {user_address}")
            raise ValueError("Invalid Ethereum address format")
        
        # Convert to checksum address
        checksum_address = w3.to_checksum_address(user_address)
            
        # Get user reputation
        rep_data = contract.functions.getUserReputation(checksum_address).call()
        
        # Format reputation data
        reputation = {
            'totalPosts': rep_data[0],
            'totalUpvotesReceived': rep_data[1],
            'totalDownvotesReceived': rep_data[2],
            'reputationScore': rep_data[3] / 100,  # Convert to a score out of 10
            'sentimentTag': rep_data[4]
        }
        
        return reputation
    
    except Exception as e:
        print(f"Error getting user reputation: {str(e)}")
        return {
            'totalPosts': 0,
            'totalUpvotesReceived': 0,
            'totalDownvotesReceived': 0,
            'reputationScore': 5.0,  # Default score
            'sentimentTag': 'neutral'
        }

def get_post(post_id):
    """Get a specific post by ID."""
    w3, contract, _ = get_contract()
    
    try:
        # Get post data
        post = contract.functions.posts(post_id).call()
        
        # Get content from IPFS
        try:
            content = post[3]  # Default to using hash as content
            if post[3].startswith("Qm"):  # Looks like an IPFS hash
                ipfs_data = retrieve_post_content(post[3])
                if ipfs_data and isinstance(ipfs_data, dict):
                    content = ipfs_data.get('content', post[3])
                else:
                    content = f"Content with IPFS hash: {post[3]}"
            elif post[3] == "direct_content":
                content = post[2]  # Use title as content if IPFS failed
        except Exception as e:
            print(f"Error retrieving content for post {post_id}: {str(e)}")
            content = f"Error loading content: {post[3]}"
        
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
        
        # Add sentiment for news posts
        if post_data['isNews']:
            try:
                from sentiment import analyze_sentiment
                sentiment, polarity = analyze_sentiment(content)
                post_data['sentiment'] = sentiment
                post_data['sentiment_score'] = polarity
            except Exception as e:
                print(f"Error analyzing sentiment: {str(e)}")
        
        return post_data
    
    except Exception as e:
        print(f"Error getting post {post_id}: {str(e)}")
        return None

def has_user_voted(post_id, user_address):
    """Check if a user has voted on a post."""
    w3, contract, _ = get_contract()
    
    try:
        # Validate inputs
        if not user_address or not is_valid_eth_address(user_address, w3):
            print(f"Invalid address format for voting check: {user_address}")
            return False, False
        
        # Convert to checksum address
        checksum_address = w3.to_checksum_address(user_address)
            
        # Check if user has voted
        return contract.functions.hasUserVoted(post_id, checksum_address).call()
    except Exception as e:
        print(f"Error checking if user voted: {str(e)}")
        return False, False