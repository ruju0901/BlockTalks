from textblob import TextBlob
import re

def clean_text(text):
    # Remove URLs, special characters, etc.
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = text.lower()
    return text

def analyze_sentiment(text):
    # Clean the text
    cleaned_text = clean_text(text)
    
    # Create a TextBlob object
    blob = TextBlob(cleaned_text)
    
    # Get the sentiment polarity (-1 to 1)
    polarity = blob.sentiment.polarity
    
    # Determine sentiment category
    if polarity > 0.1:
        return "positive", polarity
    elif polarity < -0.1:
        return "negative", polarity
    else:
        return "neutral", polarity

def determine_user_sentiment(posts):
    if not posts:
        return "neutral"
    
    # Analyze news posts only
    news_posts = [p for p in posts if p.get('isNews', False)]
    
    if not news_posts:
        return "neutral"
    
    # Count sentiment types
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
    
    for post in news_posts:
        sentiment, _ = analyze_sentiment(post['content'])
        sentiment_counts[sentiment] += 1
    
    # Find the dominant sentiment
    max_sentiment = max(sentiment_counts.items(), key=lambda x: x[1])
    
    # If there's a tie, return neutral
    if list(sentiment_counts.values()).count(max_sentiment[1]) > 1:
        return "neutral"
    
    return max_sentiment[0]