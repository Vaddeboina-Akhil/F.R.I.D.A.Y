import webbrowser
import subprocess
import os

WORLD_MONITOR_URL = "https://www.worldmonitor.app/?lat=20.0000&lon=0.0000&zoom=1.57&view=mena&timeRange=7d&layers=conflicts,hotspots,sanctions,weather,outages,natural,iranAttacks"


def open_url(url):
    """Open a URL in the default web browser"""
    try:
        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"Error opening URL: {e}")
        return False


def search_google(query):
    """Search Google for a query"""
    try:
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"Error searching Google: {e}")
        return False


def search_youtube(query):
    """Search YouTube for a query"""
    try:
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"Error searching YouTube: {e}")
        return False


def open_world_monitor():
    """Open the World Monitor dashboard"""
    try:
        webbrowser.open(WORLD_MONITOR_URL)
        return True
    except Exception as e:
        print(f"Error opening World Monitor: {e}")
        return False


def open_claude():
    """Open Claude AI"""
    try:
        webbrowser.open("https://claude.ai")
        return True
    except Exception as e:
        print(f"Error opening Claude: {e}")
        return False


def open_chatgpt():
    """Open ChatGPT"""
    try:
        webbrowser.open("https://chatgpt.com")
        return True
    except Exception as e:
        print(f"Error opening ChatGPT: {e}")
        return False
