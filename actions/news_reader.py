import feedparser
import requests
import datetime


NEWS_FEEDS = {
    "world": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "technology": "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "sports": "https://feeds.bbci.co.uk/news/sport/rss.xml",
    "india": "https://feeds.bbci.co.uk/news/world/south_asia/rss.xml",
    "business": "https://feeds.bbci.co.uk/news/business/rss.xml"
}


def get_news(category="world", limit=5):
    """
    Fetch news headlines from a specific category.
    
    Args:
        category (str): News category (world, technology, sports, india, business)
        limit (int): Number of headlines to fetch
        
    Returns:
        list: List of headline strings
    """
    try:
        if category not in NEWS_FEEDS:
            category = "world"
        
        feed = feedparser.parse(NEWS_FEEDS[category])
        headlines = []
        
        for entry in feed.entries[:limit]:
            headlines.append(entry.title)
        
        return headlines
    
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []


def get_trending_news(category="world", limit=5):
    """
    Fetch trending news headlines from a specific category.
    Maps 'global' to 'world' for convenience.
    
    Args:
        category (str): News category (global/world, technology, sports, india, business)
        limit (int): Number of headlines to fetch
        
    Returns:
        list: List of headline strings
    """
    # Map 'global' to 'world' for consistency
    if category == "global":
        category = "world"
    
    return get_news(category, limit)


def get_world_briefing():
    """
    Get a world news briefing with global and India news combined.
    
    Returns:
        str: Combined response with global and India headlines
    """
    try:
        global_news = get_trending_news("global", 3)
        india_news = get_trending_news("india", 3)
        
        if not global_news:
            return "Couldn't fetch news boss."
        
        global_text = ". ".join(global_news)
        
        if india_news:
            india_text = ". ".join(india_news)
            response = f"Here's the global situation boss. {global_text}. And here's what's happening in India boss. {india_text}."
        else:
            response = f"Here's the global situation boss. {global_text}. The India news feed is currently unavailable, but you can check BBC India online boss."
        
        return response
    
    except Exception as e:
        print(f"Error in world briefing: {e}")
        return "Couldn't fetch news boss."


def get_news_by_topic(topic):
    """
    Get news headlines filtered by topic.
    
    Args:
        topic (str): News topic to search for
        
    Returns:
        list: List of headline strings for the topic
    """
    try:
        topic = topic.lower()
        
        # Technology news
        if "tech" in topic or "technology" in topic:
            return get_news("technology", 3)
        
        # Sports news
        if "sport" in topic or "cricket" in topic or "football" in topic:
            return get_news("sports", 3)
        
        # India news
        if "india" in topic:
            return get_news("india", 3)
        
        # Business news
        if "business" in topic or "market" in topic:
            return get_news("business", 3)
        
        # Default to world news
        return get_news("world", 3)
    
    except Exception as e:
        print(f"Error fetching news by topic: {e}")
        return []


def get_greeting():
    """
    Get time-based greeting message.
    
    Returns:
        str: Greeting based on current hour
    """
    try:
        hour = datetime.datetime.now().hour
        
        if 5 <= hour < 12:
            return "Good morning"
        elif 12 <= hour < 17:
            return "Good afternoon"
        elif 17 <= hour < 21:
            return "Good evening"
        else:
            return "You're up late"
    
    except Exception as e:
        print(f"Error getting greeting: {e}")
        return "Hello"


def get_india_briefing():
    """
    Get an India news briefing.
    
    Returns:
        str: India news headlines formatted as response
    """
    try:
        headlines = get_trending_news("india", 5)
        
        if not headlines:
            return "Couldn't fetch India news boss."
        
        response = "Here's what's happening in India boss. " + ". ".join(headlines) + "."
        
        return response
    
    except Exception as e:
        print(f"Error in India briefing: {e}")
        return "Couldn't fetch India news boss."
