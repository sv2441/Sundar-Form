"""
Utility functions for the Dark Pattern Detector application.
Contains helper functions for API calls, URL parsing, and data fetching.
"""

import streamlit as st
import pandas as pd
import re
import json
import requests
from urllib.parse import urlparse, parse_qs
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled


def fetch_all_records(base_id, table_id, api_key):
    """
    Helper function to fetch all records with pagination from Airtable.
    
    Args:
        base_id (str): Airtable base ID
        table_id (str): Airtable table ID
        api_key (str): Airtable API key
        
    Returns:
        list: All records from the specified table
    """
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    url = f'https://api.airtable.com/v0/{base_id}/{table_id}'
    all_records = []
    params = {}
    
    while True:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            st.error(f"Error fetching data: {response.status_code}")
            return []
            
        response_data = response.json()
        all_records.extend(response_data.get('records', []))
        
        # Check if there are more records
        offset = response_data.get('offset')
        if not offset:
            break
        params['offset'] = offset
        
    return all_records


def extract_video_id(url):
    """
    Extracts the YouTube video ID from a given URL.
    Supports standard YouTube URLs (watch?v=), short URLs (youtu.be/), and Shorts URLs.
    
    Args:
        url (str): YouTube video URL
        
    Returns:
        str or None: Video ID if found, None otherwise
    """
    # Handle YouTube Shorts URLs first
    if "youtube.com/shorts/" in url:
        # Extract the video ID part after 'shorts/'
        video_id_part = url.split("youtube.com/shorts/")[1]
        # Remove any query parameters (like ?si=...)
        if '?' in video_id_part:
            video_id_part = video_id_part.split('?')[0]
        # The ID is directly available after 'shorts/'
        return video_id_part

    # Handle standard YouTube URLs
    elif "youtube.com/watch?v=" in url:
        query = urlparse(url).query
        return parse_qs(query).get('v', [None])[0]
    
    # Handle youtu.be short URLs
    elif "youtu.be/" in url:
        # Splits by 'youtu.be/' and then takes the part before any further query parameters
        return url.split("youtu.be/")[1].split("?")[0]
    
    return None


def analyze_with_gemini(text_content, prompt, api_key):
    """
    Sends text content to Gemini 2.5 Flash API for dark pattern analysis and product name extraction.
    Expects a structured JSON response.
    
    Args:
        text_content (str): Content to analyze
        prompt (str): Analysis prompt for Gemini
        api_key (str): Gemini API key
        
    Returns:
        dict: Structured analysis results with dark patterns and product names
    """
    if not api_key:
        return {"darkPatternAnalysis": [], "overallConfidenceScore": "N/A", "productNames": []}

    # Define the structured response schema for Gemini
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "darkPatternAnalysis": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "category": {"type": "STRING"},
                        "excerpt": {"type": "STRING"},
                        "sectionType": {"type": "STRING"},
                        "reasoning": {"type": "STRING"},
                        "confidenceScore": {"type": "INTEGER"},
                        "regulatoryViolationReference": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "lawGuidance": {"type": "STRING"},
                                    "articleClause": {"type": "STRING"},
                                    "highLevelSynthesis": {"type": "STRING"}
                                },
                                "required": ["lawGuidance", "articleClause", "highLevelSynthesis"]
                            }
                        }
                    },
                    "required": ["category", "excerpt", "sectionType", "reasoning", "confidenceScore", "regulatoryViolationReference"]
                }
            },
            "overallConfidenceScore": {"type": "INTEGER", "description": "Overall confidence score (0-100) of the dark pattern detection."},
            "productNames": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "List of product names mentioned in the text."}
        },
        "required": ["darkPatternAnalysis", "overallConfidenceScore", "productNames"]
    }

    chat_history = []
    chat_history.append({ "role": "user", "parts": [{ "text": f"{prompt}\n\nContent to analyze:\n{text_content}" }] })

    payload = {
        "contents": chat_history,
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": response_schema
        }
    }

    apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    try:
        response = requests.post(
            apiUrl,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        result = response.json()

        if result.get('candidates') and result['candidates'][0].get('content') and result['candidates'][0]['content'].get('parts'):
            json_string = result['candidates'][0]['content']['parts'][0]['text']
            parsed_json = json.loads(json_string)
            return parsed_json
        else:
            st.error(f"Gemini API response structure unexpected: {result}")
            return {"darkPatternAnalysis": [], "overallConfidenceScore": "N/A", "productNames": []}
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling Gemini API: {e}")
        return {"darkPatternAnalysis": [], "overallConfidenceScore": "N/A", "productNames": []}
    except json.JSONDecodeError as e:
        st.error(f"Error decoding Gemini API response JSON: {e}. Raw response: {response.text}")
        return {"darkPatternAnalysis": [], "overallConfidenceScore": "N/A", "productNames": []}
    except Exception as e:
        st.error(f"An unexpected error occurred during Gemini analysis: {e}")
        return {"darkPatternAnalysis": [], "overallConfidenceScore": "N/A", "productNames": []}


def format_dark_pattern_analysis(dark_pattern_analysis_details):
    """
    Formats dark pattern analysis results for display in the DataFrame.
    
    Args:
        dark_pattern_analysis_details (list): Raw dark pattern analysis results
        
    Returns:
        str: Formatted analysis string for display
    """
    formatted_analysis = ""
    if isinstance(dark_pattern_analysis_details, list):
        for dp_item in dark_pattern_analysis_details:
            category = dp_item.get("category", "N/A")
            excerpt = dp_item.get("excerpt", "N/A")
            reasoning = dp_item.get("reasoning", "N/A")
            confidence = dp_item.get("confidenceScore", "N/A")
            
            formatted_analysis += f"Category: {category}\nExcerpt: '{excerpt}'\nReasoning: {reasoning}\nConfidence: {confidence}\n"
            
            regulatory_refs = dp_item.get("regulatoryViolationReference", [])
            if regulatory_refs and isinstance(regulatory_refs, list):
                formatted_analysis += "Regulatory Violations:\n"
                for ref in regulatory_refs:
                    law = ref.get("lawGuidance", "N/A")
                    article = ref.get("articleClause", "N/A")
                    synthesis = ref.get("highLevelSynthesis", "N/A")
                    formatted_analysis += f"  - Law/Guidance: {law}, Article/Clause: {article}\n    Synthesis: {synthesis}\n"
            formatted_analysis += "\n"
        if not formatted_analysis:
            formatted_analysis = "No dark patterns detected."
    else:
        formatted_analysis = "Analysis data not in expected format."
    
    return formatted_analysis