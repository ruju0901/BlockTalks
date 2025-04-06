# BlockTalks: Decentralized Blockchain Discussion Forum

> Your thoughts on chain, your voice unchained

BlockTalks is a decentralized discussion forum specifically designed for blockchain enthusiasts, developers, and investors. Built using blockchain technology itself, it ensures true ownership of content, transparent reputation tracking, and censorship resistance.

## Features

- *Decentralized Storage*: Content stored on IPFS with only references on the blockchain
- *Transparent Reputation*: Community-driven upvote/downvote system recorded on-chain
- *Sentiment Analysis*: Automatic sentiment detection for news posts
- *Smart Contract Foundation*: Ethereum-based contract system for data integrity
- *Content Permanence*: Once published, content cannot be silently removed or modified

## Technology Stack

- *Blockchain*: Ethereum, Solidity smart contracts
- *Decentralized Storage*: IPFS (InterPlanetary File System)
- *Backend*: Python, Flask web framework
- *Web3 Integration*: Web3.py for blockchain interaction
- *Frontend*: HTML, CSS, JavaScript, Bootstrap
- *Natural Language Processing*: TextBlob for sentiment analysis
- *Development Environment*: Ganache for local blockchain testing

## Getting Started

### Prerequisites

- Python 3.8+
- Ganache for local blockchain
- IPFS daemon v0.34.1+
- Ethereum development environment

### Installation

1. Clone the repository

git clone https://github.com/yourusername/blocktalks.git
cd blocktalks


2. Install dependencies

pip install -r requirements.txt


3. Start IPFS daemon

ipfs daemon


4. Deploy the smart contract

python deploy_forum.py


5. Start the application

python app.py


6. Open your browser and navigate to http://127.0.0.1:5000

## Usage

### Creating a Post
1. Navigate to the Create Post page
2. Enter your post title and content
3. Toggle the "News" switch if posting news content
4. Submit your post - it will be stored on IPFS and referenced on the blockchain

### Voting on Content
1. Browse posts on the homepage
2. Use the upvote/downvote buttons to contribute to content reputation
3. All votes are recorded on-chain for full transparency

### Viewing Profiles
1. Click on any user address to view their profile
2. See reputation metrics and post history
3. All data is pulled directly from the blockchain for authenticity

## Architecture

BlockTalks uses a hybrid architecture:
- Smart contracts handle reputation, voting, and content verification
- IPFS stores the actual content in a distributed manner
- Flask web application provides the user interface
- Web3.py bridges the application with the Ethereum blockchain

## Roadmap

- [ ] MetaMask Integration for seamless wallet authentication
- [ ] Mobile application development
- [ ] Enhanced reputation mechanisms with weighted voting
- [ ] Content categories and tags for better organization
- [ ] Token-based incentive system for quality content

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Ethereum and IPFS communities for building the infrastructure that makes this possible
- All contributors and testers who have helped shape this project
