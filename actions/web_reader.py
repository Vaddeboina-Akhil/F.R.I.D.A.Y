import requests
from bs4 import BeautifulSoup


def get_google_answer(query):
    """
    Search Google and extract the featured snippet or knowledge panel answer.
    
    Args:
        query (str): The search query
        
    Returns:
        str: The answer text if found, None otherwise
    """
    try:
        # Build Google search URL
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        
        # Set headers with User-Agent to avoid blocking
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # Fetch the page with timeout
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Try to find featured snippet
        featured_classes = ["BNeawe", "IZ6rdc", "AZCkJd"]
        for class_name in featured_classes:
            snippets = soup.find_all("div", class_=class_name)
            for snippet in snippets:
                text = snippet.get_text(strip=True)
                if text and len(text) > 10:
                    return text
        
        # Try to find knowledge panel answer
        knowledge_classes = ["kno-rdesc", "SPZz6b"]
        for class_name in knowledge_classes:
            panels = soup.find_all("div", class_=class_name)
            for panel in panels:
                text = panel.get_text(strip=True)
                if text and len(text) > 10:
                    return text
        
        return None
        
    except Exception as e:
        print(f"Error fetching Google answer: {e}")
        return None


def search_and_read(query):
    """
    Search Google for a query and return a concise answer.
    
    Args:
        query (str): The search query
        
    Returns:
        str: Concise answer (up to 300 chars) if found, None otherwise
    """
    try:
        answer = get_google_answer(query)
        
        # Return truncated answer if found and substantial
        if answer and len(answer) > 10:
            return answer[:300]
        
        return None
        
    except Exception as e:
        print(f"Error in search_and_read: {e}")
        return None
