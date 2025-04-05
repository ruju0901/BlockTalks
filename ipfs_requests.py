import requests
import json
import time

# IPFS API endpoint
IPFS_API_URL = "http://127.0.0.1:5001/api/v0"

def add_to_ipfs(content, pin=True):
    """
    Add content to IPFS and return the content hash (CID).
    
    Args:
        content (str): The content to add to IPFS
        pin (bool): Whether to pin the content
        
    Returns:
        str: IPFS content hash (CID)
    """
    try:
        # Use the /add endpoint
        files = {'file': content}
        params = {'pin': 'true' if pin else 'false'}
        response = requests.post(f"{IPFS_API_URL}/add", files=files, params=params)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('Hash')
        else:
            print(f"Failed to add to IPFS: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"Error adding to IPFS: {str(e)}")
        return None

def get_from_ipfs(content_hash):
    """
    Retrieve content from IPFS using the content hash.
    
    Args:
        content_hash (str): IPFS content hash (CID)
        
    Returns:
        str: Content retrieved from IPFS
    """
    try:
        # Use the /cat endpoint
        params = {'arg': content_hash}
        response = requests.post(f"{IPFS_API_URL}/cat", params=params)
        
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to get from IPFS: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"Error getting from IPFS: {str(e)}")
        return None

def store_post_content(title, content, author):
    """
    Store post content on IPFS.
    
    Args:
        title (str): Post title
        content (str): Post content
        author (str): Author's Ethereum address
        
    Returns:
        str: IPFS content hash
    """
    # Create a JSON object with post details
    post_data = {
        "title": title,
        "content": content,
        "author": author,
        "timestamp": int(time.time())
    }
    
    # Convert to JSON string
    json_data = json.dumps(post_data)
    
    # Store on IPFS
    return add_to_ipfs(json_data)

def retrieve_post_content(content_hash):
    """
    Retrieve post content from IPFS.
    
    Args:
        content_hash (str): IPFS content hash
        
    Returns:
        dict: Post data as dictionary
    """
    json_data = get_from_ipfs(content_hash)
    if json_data:
        try:
            return json.loads(json_data)
        except json.JSONDecodeError:
            print("Error decoding JSON from IPFS")
            return None
    return None