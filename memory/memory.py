import json
import os
import datetime


CACHE_FILE = "memory/command_cache.json"
FAILURE_FILE = "memory/failure_log.json"


def load_cache():
    """Load command cache from file"""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading cache: {e}")
    
    return {}


def save_cache(cache):
    """Save command cache to file"""
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"Error saving cache: {e}")


def cache_command(user_input, action, response, target=None):
    """
    Cache a successful command using intent-based keys (action:target).
    
    This improves learning by grouping similar commands together:
    - "open chrome" → open_app:chrome
    - "launch chrome" → open_app:chrome
    - "start chrome" → open_app:chrome
    
    All three variants share the same cache entry and increment the same count,
    leading to faster retrieval and better learning of user patterns.
    Without intent-based keys, each phrasing would be a separate cache entry.
    """
    try:
        cache = load_cache()
        
        # Use intent-based key: action:target (much better than raw user input)
        # This groups different phrasings of the same command together
        if target:
            key = f"{action}:{target}".lower().strip()
        else:
            # For actions without targets (like "get_time"), use just the action
            key = action.lower().strip()
        
        # Update or create entry
        if key in cache:
            cache[key]["count"] = cache[key].get("count", 0) + 1
        else:
            cache[key] = {
                "action": action,
                "target": target,
                "response": response,
                "count": 1,
                "last_used": datetime.datetime.now().isoformat()
            }
        
        cache[key]["last_used"] = datetime.datetime.now().isoformat()
        save_cache(cache)
    except Exception as e:
        print(f"Error caching command: {e}")


def get_cached_command(action, target=None):
    """
    Get cached command by intent-based key (action:target).
    
    First checks for exact intent-based match, then falls back to old format
    for backwards compatibility with legacy cache entries.
    
    Intent-based retrieval is much faster than text similarity matching
    and ensures we always get the most relevant cached response.
    """
    try:
        cache = load_cache()
        
        # Priority 1: Check new intent-based format (action:target)
        # This is the primary lookup method and should be very fast
        if target:
            intent_key = f"{action}:{target}".lower().strip()
            if intent_key in cache:
                return cache[intent_key]
        else:
            # For actions without targets, use just the action
            intent_key = action.lower().strip()
            if intent_key in cache:
                return cache[intent_key]
        
        # Priority 2: Fallback for legacy cache entries (old format)
        # Scans old text-based keys for backwards compatibility
        # This allows learning to continue even with old cache data
        for cached_key in cache:
            # Skip new intent-based format keys (they contain ":")
            if ":" not in cached_key:
                cached_entry = cache[cached_key]
                # Check if action matches the cached entry
                if cached_entry.get("action") == action:
                    # If target is provided, check if it matches
                    if target is None or cached_entry.get("target") == target:
                        return cached_entry
        
        return None
    except Exception as e:
        print(f"Error getting cached command: {e}")
        return None


def load_failures():
    """Load failure log from file"""
    try:
        if os.path.exists(FAILURE_FILE):
            with open(FAILURE_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading failures: {e}")
    
    return []


def save_failures(failures):
    """Save failure log to file"""
    try:
        os.makedirs(os.path.dirname(FAILURE_FILE), exist_ok=True)
        with open(FAILURE_FILE, 'w') as f:
            json.dump(failures, f, indent=2)
    except Exception as e:
        print(f"Error saving failures: {e}")


def log_failure(user_input, action, error):
    """Log a failed command"""
    try:
        failures = load_failures()
        
        # Append failure entry
        failure_entry = {
            "input": user_input,
            "action": action,
            "error": str(error),
            "time": datetime.datetime.now().isoformat()
        }
        failures.append(failure_entry)
        
        # Keep only last 50 failures
        if len(failures) > 50:
            failures = failures[-50:]
        
        save_failures(failures)
    except Exception as e:
        print(f"Error logging failure: {e}")


def get_failure_count(action):
    """Count failures for a specific action"""
    try:
        failures = load_failures()
        count = sum(1 for failure in failures if failure.get("action") == action)
        return count
    except Exception as e:
        print(f"Error getting failure count: {e}")
        return 0


def get_most_used_commands(limit=5):
    """Get most frequently used commands sorted by usage count"""
    try:
        cache = load_cache()
        
        # Sort by count descending
        sorted_commands = sorted(
            cache.items(),
            key=lambda x: x[1].get("count", 0),
            reverse=True
        )
        
        # Return top {limit} as list of dicts with readable format
        result = []
        for key, value in sorted_commands[:limit]:
            # Format the key nicely for display
            # New format: "action:target" or just "action"
            action = value.get("action", key)
            target = value.get("target")
            
            if target:
                display_name = f"{action}: {target}"
            else:
                display_name = action
            
            result.append({
                "key": key,
                "display": display_name,
                "action": action,
                "target": target,
                "count": value.get("count", 0),
                "last_used": value.get("last_used")
            })
        
        return result
    except Exception as e:
        print(f"Error getting most used commands: {e}")
        return []


FACTS_FILE = "memory/facts.json"


def load_facts():
    """Load stored facts from file"""
    try:
        if os.path.exists(FACTS_FILE):
            with open(FACTS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading facts: {e}")
    
    return {}


def save_facts(facts):
    """Save facts to file"""
    try:
        os.makedirs(os.path.dirname(FACTS_FILE), exist_ok=True)
        with open(FACTS_FILE, 'w') as f:
            json.dump(facts, f, indent=2)
    except Exception as e:
        print(f"Error saving facts: {e}")


def remember_fact(fact_text):
    """Store a fact for later recall, avoiding duplicates"""
    try:
        facts = load_facts()
        # Convert to lowercase for case-insensitive comparison and storage
        fact_key = fact_text.lower().strip()
        
        # Check if fact already exists (case-insensitive duplicate prevention)
        if fact_key in facts:
            print(f"Fact already in memory: {fact_text}")
            return True  # Return True since it's already stored
        
        # Store new fact with original casing preserved in "text" field
        facts[fact_key] = {
            "text": fact_text,
            "stored_at": datetime.datetime.now().isoformat(),
            "recall_count": 0
        }
        
        save_facts(facts)
        return True
    except Exception as e:
        print(f"Error remembering fact: {e}")
        return False


def recall_facts():
    """Retrieve all stored facts"""
    try:
        facts = load_facts()
        if not facts:
            return None
        
        # Return list of facts in a formatted way
        fact_list = []
        for key, value in facts.items():
            fact_list.append(value.get("text", key))
        
        return fact_list
    except Exception as e:
        print(f"Error recalling facts: {e}")
        return None


def clear_memory():
    """Clear all memory (cache, failures, and facts)"""
    try:
        files_to_clear = [CACHE_FILE, FAILURE_FILE, FACTS_FILE]
        
        for file_path in files_to_clear:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        return True
    except Exception as e:
        print(f"Error clearing memory: {e}")
        return False


def get_all_facts():
    """Get all stored facts as a list"""
    try:
        facts = load_facts()
        return [v.get("text", k) for k, v in facts.items()]
    except:
        return []


def load_memory():
    """Load complete memory state including user info and conversation data"""
    cache = load_cache()
    return {
        "user": {
            "name": None,
            "city": None,
            "preferences": [],
            "facts": get_all_facts()
        },
        "conversation_count": len(cache)
    }
