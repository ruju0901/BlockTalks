// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DiscussionForum {
    // Post structure
    struct Post {
        uint256 id;
        address author;
        string title;
        string contentHash; // IPFS hash instead of full content
        uint256 timestamp;
        uint256 upvotes;
        uint256 downvotes;
        bool isNews;
    }
    
    // User reputation structure
    struct UserReputation {
        uint256 totalPosts;
        uint256 totalUpvotesReceived;
        uint256 totalDownvotesReceived;
        uint256 totalUpvotesGiven;
        uint256 totalDownvotesGiven;
        uint256 reputationScore;
        string sentimentTag;
    }
    
    // Events
    event PostCreated(uint256 indexed postId, address indexed author, string title, bool isNews, string contentHash);
    event PostVoted(uint256 indexed postId, address indexed voter, bool isUpvote);
    event UserSentimentUpdated(address indexed user, string sentimentTag);
    
    // Contract state variables
    uint256 public postCount;
    mapping(uint256 => Post) public posts;
    mapping(address => UserReputation) public userReputations;
    mapping(uint256 => mapping(address => bool)) public hasVoted;
    mapping(uint256 => mapping(address => bool)) public upvoted;
    mapping(uint256 => mapping(address => bool)) public downvoted;
    
    // Create a new post
    function createPost(string memory _title, string memory _contentHash, bool _isNews) public {
        // Increment post count
        postCount++;
        
        // Create post
        posts[postCount] = Post(
            postCount,
            msg.sender,
            _title,
            _contentHash,
            block.timestamp,
            0,
            0,
            _isNews
        );
        
        // Update user's post count
        userReputations[msg.sender].totalPosts++;
        
        // Calculate reputation score (simple version)
        calculateReputationScore(msg.sender);
        
        // Emit event
        emit PostCreated(postCount, msg.sender, _title, _isNews, _contentHash);
    }
    
    // Vote on a post
    function votePost(uint256 _postId, bool _isUpvote) public {
        // Require valid post
        require(_postId > 0 && _postId <= postCount, "Invalid post ID");
        
        // Require user has not voted on this post
        require(!hasVoted[_postId][msg.sender], "User has already voted on this post");
        
        // Get post
        Post storage post = posts[_postId];
        
        // Update post votes
        if (_isUpvote) {
            post.upvotes++;
            upvoted[_postId][msg.sender] = true;
            userReputations[msg.sender].totalUpvotesGiven++;
            userReputations[post.author].totalUpvotesReceived++;
        } else {
            post.downvotes++;
            downvoted[_postId][msg.sender] = true;
            userReputations[msg.sender].totalDownvotesGiven++;
            userReputations[post.author].totalDownvotesReceived++;
        }
        
        // Mark user as having voted
        hasVoted[_postId][msg.sender] = true;
        
        // Calculate reputation scores
        calculateReputationScore(post.author);
        calculateReputationScore(msg.sender);
        
        // Emit event
        emit PostVoted(_postId, msg.sender, _isUpvote);
    }
    
    // Calculate reputation score
    function calculateReputationScore(address _user) internal {
        // Get user reputation
        UserReputation storage rep = userReputations[_user];
        
        // Calculate reputation score (out of 1000, to avoid floating point)
        // Base score: 500 (5.0 out of 10)
        uint256 score = 500;
        
        // Adjust based on votes received (more weight)
        if (rep.totalUpvotesReceived + rep.totalDownvotesReceived > 0) {
            uint256 voteRatio = (rep.totalUpvotesReceived * 1000) / (rep.totalUpvotesReceived + rep.totalDownvotesReceived);
            // Weighted adjustment (60% of total score)
            score = score + ((voteRatio - 500) * 6 / 10);
        }
        
        // Adjust based on post count (less weight)
        if (rep.totalPosts > 0) {
            // Max bonus for posts: 100 (1.0 out of 10)
            uint256 postBonus = rep.totalPosts * 10;
            if (postBonus > 100) postBonus = 100;
            score += postBonus;
        }
        
        // Cap score between 0 and 1000
        if (score > 1000) score = 1000;
        if (score < 0) score = 0;
        
        // Update reputation score
        rep.reputationScore = score;
    }
    
    // Update user sentiment tag
    function updateUserSentiment(address _user, string memory _sentimentTag) public {
        userReputations[_user].sentimentTag = _sentimentTag;
        emit UserSentimentUpdated(_user, _sentimentTag);
    }
    
    // Get user reputation data
    function getUserReputation(address _user) public view returns (
        uint256 totalPosts,
        uint256 totalUpvotesReceived,
        uint256 totalDownvotesReceived,
        uint256 reputationScore,
        string memory sentimentTag
    ) {
        UserReputation storage rep = userReputations[_user];
        return (
            rep.totalPosts,
            rep.totalUpvotesReceived,
            rep.totalDownvotesReceived,
            rep.reputationScore,
            rep.sentimentTag
        );
    }
    
    // Check if user has voted on a post
    function hasUserVoted(uint256 _postId, address _user) public view returns (bool voted, bool isUpvote) {
        if (hasVoted[_postId][_user]) {
            return (true, upvoted[_postId][_user]);
        }
        return (false, false);
    }
}