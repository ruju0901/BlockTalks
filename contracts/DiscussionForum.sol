
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DiscussionForum {
    // Struct for a post
    struct Post {
        uint256 id;
        address author;
        string title;
        string content;
        uint256 timestamp;
        uint256 upvotes;
        uint256 downvotes;
        bool isNews; // Flag to indicate if this post is news content
    }

    // Struct for user reputation
    struct UserReputation {
        uint256 totalPosts;
        uint256 totalUpvotesReceived;
        uint256 totalDownvotesReceived;
        uint256 totalUpvotesGiven;
        uint256 totalDownvotesGiven;
        uint256 reputationScore; // Out of 1000 (divide by 100 for a score out of 10)
        string sentimentTag; // "positive", "negative", or "neutral"
    }

    // Post counter
    uint256 public postCount;

    // Mappings
    mapping(uint256 => Post) public posts;
    mapping(address => UserReputation) public userReputations;
    mapping(uint256 => mapping(address => bool)) public hasVoted; // Track if a user has voted on a post
    mapping(uint256 => mapping(address => bool)) public upvoted; // Track if a user upvoted a post
    mapping(uint256 => mapping(address => bool)) public downvoted; // Track if a user downvoted a post

    // Events
    event PostCreated(uint256 indexed postId, address indexed author, string title, bool isNews);
    event PostVoted(uint256 indexed postId, address indexed voter, bool isUpvote);
    event UserSentimentUpdated(address indexed user, string sentimentTag);

    // Modifier to check if a post exists
    modifier postExists(uint256 _postId) {
        require(_postId > 0 && _postId <= postCount, "Post does not exist");
        _;
    }

    // Initialize user reputation if not already
    function initUserIfNeeded(address _user) internal {
        if (userReputations[_user].reputationScore == 0) {
            // Default reputation score is 500 (5.0 out of 10)
            userReputations[_user].reputationScore = 500;
            userReputations[_user].sentimentTag = "neutral";
        }
    }

    // Create a new post
    function createPost(string memory _title, string memory _content, bool _isNews) public {
        initUserIfNeeded(msg.sender);
        
        postCount++;
        posts[postCount] = Post({
            id: postCount,
            author: msg.sender,
            title: _title,
            content: _content,
            timestamp: block.timestamp,
            upvotes: 0,
            downvotes: 0,
            isNews: _isNews
        });
        
        // Update user reputation
        userReputations[msg.sender].totalPosts++;
        
        emit PostCreated(postCount, msg.sender, _title, _isNews);
    }

    // Vote on a post
    function votePost(uint256 _postId, bool _isUpvote) public postExists(_postId) {
        initUserIfNeeded(msg.sender);
        
        // Check if the user has already voted on this post
        require(!hasVoted[_postId][msg.sender], "You have already voted on this post");
        
        // Update post votes
        if (_isUpvote) {
            posts[_postId].upvotes++;
            upvoted[_postId][msg.sender] = true;
            userReputations[msg.sender].totalUpvotesGiven++;
            
            // Update author's reputation
            address author = posts[_postId].author;
            userReputations[author].totalUpvotesReceived++;
            
            // Increase reputation score (max 1000)
            if (userReputations[author].reputationScore < 1000) {
                uint256 increase = 10; // +0.1 per upvote
                userReputations[author].reputationScore = min(1000, userReputations[author].reputationScore + increase);
            }
        } else {
            posts[_postId].downvotes++;
            downvoted[_postId][msg.sender] = true;
            userReputations[msg.sender].totalDownvotesGiven++;
            
            // Update author's reputation
            address author = posts[_postId].author;
            userReputations[author].totalDownvotesReceived++;
            
            // Decrease reputation score (min 0)
            if (userReputations[author].reputationScore > 0) {
                uint256 decrease = 15; // -0.15 per downvote
                userReputations[author].reputationScore = userReputations[author].reputationScore > decrease ? 
                    userReputations[author].reputationScore - decrease : 0;
            }
        }
        
        // Mark user as having voted on this post
        hasVoted[_postId][msg.sender] = true;
        
        emit PostVoted(_postId, msg.sender, _isUpvote);
    }

    // Update user sentiment tag (called from backend)
    function updateUserSentiment(address _user, string memory _sentimentTag) public {
        initUserIfNeeded(_user);
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
        UserReputation memory rep = userReputations[_user];
        return (
            rep.totalPosts,
            rep.totalUpvotesReceived,
            rep.totalDownvotesReceived,
            rep.reputationScore,
            rep.sentimentTag
        );
    }

    // Check if a user has voted on a specific post
    function hasUserVoted(uint256 _postId, address _user) public view returns (bool voted, bool isUpvote) {
        voted = hasVoted[_postId][_user];
        isUpvote = upvoted[_postId][_user];
        return (voted, isUpvote);
    }
    
    // Helper function for min value
    function min(uint256 a, uint256 b) internal pure returns (uint256) {
        return a < b ? a : b;
    }
}
