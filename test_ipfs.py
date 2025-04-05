# Replace this line:
# from ipfs_storage import add_to_ipfs, get_from_ipfs
# With this:
from ipfs_requests import add_to_ipfs, get_from_ipfs

# Test adding content to IPFS
test_content = "This is a test post content for IPFS storage"
print("Adding content to IPFS...")
content_hash = add_to_ipfs(test_content)

if content_hash:
    print(f"Content added successfully with hash: {content_hash}")
    
    # Test retrieving content from IPFS
    print("Retrieving content from IPFS...")
    retrieved_content = get_from_ipfs(content_hash)
    
    if retrieved_content:
        print(f"Content retrieved successfully: {retrieved_content}")
        print(f"Content matches: {test_content == retrieved_content}")
    else:
        print("Failed to retrieve content from IPFS")
else:
    print("Failed to add content to IPFS")