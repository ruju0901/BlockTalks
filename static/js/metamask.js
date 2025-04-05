// MetaMask Connection Handling

// Global variables 
let currentAccount = null;
let web3 = null;
let isConnected = false;

// Check if MetaMask is installed
function isMetaMaskInstalled() {
    return Boolean(window.ethereum && window.ethereum.isMetaMask);
}

// Initialize the connection
async function initializeMetaMask() {
    if (!isMetaMaskInstalled()) {
        document.getElementById('connect-button').innerText = 'Install MetaMask';
        document.getElementById('connect-button').addEventListener('click', () => {
            window.open('https://metamask.io/download.html', '_blank');
        });
        return false;
    }
    
    document.getElementById('connect-button').addEventListener('click', connectMetaMask);
    
    // Check if already connected
    if (window.ethereum.selectedAddress) {
        await connectMetaMask();
    }
    
    // Listen for account changes
    window.ethereum.on('accountsChanged', handleAccountsChanged);
    
    // Listen for chain changes
    window.ethereum.on('chainChanged', () => {
        window.location.reload();
    });
    
    return true;
}

// Connect to MetaMask
async function connectMetaMask() {
    try {
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        handleAccountsChanged(accounts);
        return true;
    } catch (error) {
        if (error.code === 4001) {
            // User rejected request
            showStatus('Please connect to MetaMask to use this dApp', 'error');
        } else {
            showStatus('Error connecting to MetaMask: ' + error.message, 'error');
        }
        return false;
    }
}

// Handle account changes
function handleAccountsChanged(accounts) {
    if (accounts.length === 0) {
        // MetaMask is locked or user has no accounts
        showStatus('Please connect to MetaMask', 'warning');
        currentAccount = null;
        isConnected = false;
        updateUI(false);
    } else if (accounts[0] !== currentAccount) {
        currentAccount = accounts[0];
        isConnected = true;
        
        // Display account info
        const shortAddress = `${currentAccount.substring(0, 6)}...${currentAccount.substring(38)}`;
        document.getElementById('wallet-address').innerText = shortAddress;
        
        // Update the hidden input field for form submissions
        const addressInputs = document.querySelectorAll('input[name="user_address"]');
        addressInputs.forEach(input => {
            input.value = currentAccount;
        });
        
        // Update the UI
        updateUI(true);
        
        // Send the address to the server for session
        updateServerSession(currentAccount);
        
        showStatus('Connected: ' + shortAddress, 'success');
    }
}

// Update the UI based on connection status
function updateUI(connected) {
    if (connected) {
        document.getElementById('connect-button').innerText = 'Connected';
        document.getElementById('connect-button').classList.add('btn-success');
        document.getElementById('connect-button').classList.remove('btn-primary');
        document.getElementById('wallet-info').style.display = 'block';
        
        // Show content that requires connection
        const authRequired = document.querySelectorAll('.auth-required');
        authRequired.forEach(el => {
            el.style.display = 'block';
        });
        
        // Hide content for non-connected users
        const noAuthRequired = document.querySelectorAll('.no-auth-required');
        noAuthRequired.forEach(el => {
            el.style.display = 'none';
        });
    } else {
        document.getElementById('connect-button').innerText = 'Connect Wallet';
        document.getElementById('connect-button').classList.add('btn-primary');
        document.getElementById('connect-button').classList.remove('btn-success');
        document.getElementById('wallet-info').style.display = 'none';
        
        // Hide content that requires connection
        const authRequired = document.querySelectorAll('.auth-required');
        authRequired.forEach(el => {
            el.style.display = 'none';
        });
        
        // Show content for non-connected users
        const noAuthRequired = document.querySelectorAll('.no-auth-required');
        noAuthRequired.forEach(el => {
            el.style.display = 'block';
        });
    }
}

// Send the address to the server to update session
function updateServerSession(address) {
    fetch('/update_session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_address: address }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Session updated successfully');
        } else {
            console.error('Failed to update session');
        }
    })
    .catch(error => {
        console.error('Error updating session:', error);
    });
}

// Display status messages
function showStatus(message, type = 'info') {
    const statusDiv = document.getElementById('status-messages');
    if (!statusDiv) return;
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    statusDiv.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => {
            alertDiv.remove();
        }, 150);
    }, 5000);
}

// Get signature from user to verify ownership of address
async function signMessage(message) {
    try {
        const signature = await window.ethereum.request({
            method: 'personal_sign',
            params: [message, currentAccount]
        });
        return signature;
    } catch (error) {
        showStatus('Error signing message: ' + error.message, 'error');
        return null;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initializeMetaMask);