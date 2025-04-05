import ipfshttpclient
import requests
import json
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# IPFS Configuration
# Use local node or Infura/Pinata
IPFS_API = os.getenv("IPFS_API", "/ip4/127.0.0.1/tcp/5001")
IPFS_GATEWAY = os.getenv("IPFS_GATEWAY", "https://ipfs.io/ipfs/")

# Pinata API (optional)
PINATA_API_KEY = os.getenv("PINATA_API_KEY", "")
PINATA_SECRET_API_KEY = os.getenv("PINATA_SECRET_API_KEY", "")


def connect_to_ipfs():
    """Connect to IPFS node."""
    try:
        # Try to connect to local node
        return ipfshttpclient.connect(IPFS_API)
    except Exception as e:
        print(f"Error connecting to IPFS: {str(e)}")
        return None


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
        client = connect_to_ipfs()
        if client:
            # Add the content to IPFS
            result = client.add_str(content)
            content_hash = result
            
            # Pin the content if requested
            if pin:
                client.pin.add(content_hash)
            
            client.close()
            
            # If Pinata credentials are available, pin there too for persistence
            if PINATA_API_KEY and PINATA_SECRET_API_KEY:
                pin_to_pinata(content_hash)
                
            return content_hash
        else:
            print("Failed to connect to IPFS")
            return None
    except Exception as e:
        print(f"Error adding content to IPFS: {str(e)}")
        return None


def pin_to_pinata(content_hash):
    """
    Pin content to Pinata cloud service.
    
    Args:
        content_hash (str): IPFS content hash to pin
    """
    try:
        url = "https://api.pinata.cloud/pinning/pinByHash"
        payload = {
            "hashToPin": content_hash
        }
        headers = {
            'Content-Type': 'application/json',
            'pinata_api_key': PINATA_API_KEY,
            'pinata_secret_api_key': PINATA_SECRET_API_KEY
        }
        
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print(f"Successfully pinned {content_hash} to Pinata")
        else:
            print(f"Failed to pin to Pinata: {response.text}")
    except Exception as e:
        print(f"Error pinning to Pinata: {str(e)}")


def get_from_ipfs(content_hash):
    """
    Retrieve content from IPFS using the content hash.
    
    Args:
        content_hash (str): IPFS content hash (CID)
        
    Returns:
        str: Content retrieved from IPFS
    """
    try:
        client = connect_to_ipfs()
        if client:
            # Get the content from IPFS
            content = client.cat(content_hash).decode('utf-8')
            client.close()
            return content
        else:
            # Fallback to HTTP gateway
            response = requests.get(f"{IPFS_GATEWAY}{content_hash}")
            if response.status_code == 200:
                return response.text
            else:
                print(f"Failed to get content from IPFS gateway: {response.status_code}")
                return None
    except Exception as e:
        print(f"Error getting content from IPFS: {str(e)}")
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