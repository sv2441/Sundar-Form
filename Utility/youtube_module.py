"""
YouTube module for the Dark Pattern Detector application.
Handles YouTube video search, data extraction, and analysis functionality.
"""

import streamlit as st
import pandas as pd
import re
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from Utility.utils import extract_video_id, analyze_with_gemini, format_dark_pattern_analysis


class YouTubeAnalyzer:
    """
    YouTube analyzer class that handles video search, data extraction, and dark pattern analysis.
    """
    
    def __init__(self, api_key):
        """
        Initialize the YouTube analyzer with API key.
        
        Args:
            api_key (str): YouTube Data API key
        """
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key) if api_key else None
    
    def search_videos_by_keywords(self, keywords_hashtags, max_results, exclude_channels):
        """
        Search YouTube videos by keywords/hashtags.
        
        Args:
            keywords_hashtags (str): Comma-separated or multi-line keywords
            max_results (int): Maximum number of results to fetch
            exclude_channels (str): Comma-separated channels to exclude
            
        Returns:
            list: List of video data dictionaries
        """
        if not self.youtube:
            st.warning("YouTube API key not provided. Cannot perform search.")
            return []
        
        all_youtube_results = []
        exclude_channels_list = [c.strip().lower() for c in re.split(r'[\n,]', exclude_channels) if c.strip()]
        search_queries = [q.strip() for q in re.split(r'[\n,]', keywords_hashtags) if q.strip()]
        
        if not search_queries:
            st.warning("Please enter keywords/hashtags for search mode.")
            return []
        
        for query_term in search_queries:
            if not query_term:
                continue

            st.write(f"Searching YouTube for: '{query_term}' (fetching {max_results} results)")
            try:
                request = self.youtube.search().list(
                    q=query_term,
                    part='snippet',
                    type='video',
                    maxResults=max_results
                )
                response = request.execute()

                for item in response['items']:
                    video_id = item['id']['videoId']
                    title = item['snippet']['title']
                    channel_title = item['snippet']['channelTitle']
                    description = item['snippet']['description']
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    
                    # Filter out excluded channels
                    if channel_title.lower() in exclude_channels_list:
                        st.info(f"Skipping video '{title}' from excluded channel '{channel_title}'.")
                        continue

                    # Extract transcript
                    transcript_text = self._extract_transcript(video_id)

                    all_youtube_results.append({
                        "Platform": "YouTube",
                        "Video ID": video_id,
                        "Title": title,
                        "Channel": channel_title,
                        "URL": video_url,
                        "Description": description,
                        "Transcript": transcript_text,
                        "Dark Pattern Analysis": "N/A",
                        "Overall Confidence Score": "N/A",
                        "Product Names": "N/A"
                    })
            except Exception as e:
                st.error(f"Error during YouTube search for '{query_term}': {e}")
        
        return all_youtube_results
    
    def analyze_video_urls(self, youtube_video_urls_input, exclude_channels):
        """
        Analyze specific YouTube video URLs.
        
        Args:
            youtube_video_urls_input (str): Multi-line YouTube URLs
            exclude_channels (str): Comma-separated channels to exclude
            
        Returns:
            list: List of video data dictionaries
        """
        if not self.youtube:
            st.warning("YouTube API key not provided. Cannot analyze videos.")
            return []
        
        all_youtube_results = []
        exclude_channels_list = [c.strip().lower() for c in re.split(r'[\n,]', exclude_channels) if c.strip()]
        
        if youtube_video_urls_input:
            youtube_urls = [url.strip() for url in youtube_video_urls_input.split('\n') if url.strip()][:10]

            if not youtube_urls:
                st.warning("No valid YouTube URLs entered for analysis.")
                return []

            for url in youtube_urls:
                video_id = extract_video_id(url)
                standardized_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else url

                if video_id:
                    st.write(f"Analyzing YouTube video: '{standardized_url}'")
                    try:
                        videos_request = self.youtube.videos().list(
                            part="snippet",
                            id=video_id
                        )
                        videos_response = videos_request.execute()

                        if videos_response['items']:
                            item = videos_response['items'][0]
                            title = item['snippet']['title']
                            channel_title = item['snippet']['channelTitle']
                            description = item['snippet']['description']
                            
                            if channel_title.lower() in exclude_channels_list:
                                st.info(f"Skipping video '{title}' from excluded channel '{channel_title}'.")
                            else:
                                transcript_text = self._extract_transcript(video_id)

                                all_youtube_results.append({
                                    "Platform": "YouTube",
                                    "Video ID": video_id,
                                    "Title": title,
                                    "Channel": channel_title,
                                    "URL": standardized_url,
                                    "Description": description,
                                    "Transcript": transcript_text,
                                    "Dark Pattern Analysis": "N/A",
                                    "Overall Confidence Score": "N/A",
                                    "Product Names": "N/A"
                                })
                        else:
                            st.warning(f"No video found for the URL: {url}. Please check the URL or video ID.")
                    except Exception as e:
                        st.error(f"Error analyzing video from URL '{url}': {e}")
                else:
                    st.warning(f"Invalid YouTube URL skipped: {url}. Please ensure it's a valid YouTube video URL.")
        else:
            st.warning("Please enter at least one YouTube Video URL to analyze.")
        
        return all_youtube_results
    
    def _extract_transcript(self, video_id):
        """
        Extract transcript from YouTube video.
        
        Args:
            video_id (str): YouTube video ID
            
        Returns:
            str: Transcript text or error message
        """
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join([t['text'] for t in transcript_list])
        except NoTranscriptFound:
            return "No transcript found for this video."
        except TranscriptsDisabled:
            return "Transcripts are disabled for this video."
        except Exception as e:
            return f"Error fetching transcript: {e}"
    
    def analyze_dark_patterns(self, video_results, gemini_prompt, gemini_api_key):
        """
        Perform dark pattern analysis on video results using Gemini API.
        
        Args:
            video_results (list): List of video data dictionaries
            gemini_prompt (str): Analysis prompt for Gemini
            gemini_api_key (str): Gemini API key
            
        Returns:
            list: Updated video results with analysis
        """
        if not video_results:
            st.info("No YouTube videos to analyze for dark patterns.")
            return []
        
        if not gemini_api_key:
            st.warning("Gemini API Key not provided. Skipping Dark Pattern Analysis.")
            return video_results
        
        st.subheader("Performing Dark Pattern Analysis with Gemini...")
        
        for i, video_data in enumerate(video_results):
            st.write(f"Analyzing video: {video_data['Title']}")
            combined_text = f"Title: {video_data['Title']}\nDescription: {video_data['Description']}\nTranscript: {video_data['Transcript']}"

            analysis_result = analyze_with_gemini(combined_text, gemini_prompt, gemini_api_key)

            # Store the raw analysis result for detailed view
            video_data["Raw Dark Pattern Analysis"] = analysis_result.get("darkPatternAnalysis", [])
            video_data["Overall Confidence Score"] = analysis_result.get("overallConfidenceScore", "N/A")
            video_data["Product Names"] = ", ".join(analysis_result.get("productNames", [])) if analysis_result.get("productNames") else "N/A"

            # Format the detailed analysis for direct display in the DataFrame
            dark_pattern_analysis_details = video_data["Raw Dark Pattern Analysis"]
            formatted_analysis = format_dark_pattern_analysis(dark_pattern_analysis_details)
            video_data["Dark Pattern Analysis"] = formatted_analysis

            video_results[i] = video_data
        
        st.success("Dark Pattern Analysis complete!")
        return video_results


def create_youtube_analyzer(api_key):
    """
    Factory function to create a YouTube analyzer instance.
    
    Args:
        api_key (str): YouTube Data API key
        
    Returns:
        YouTubeAnalyzer: Configured YouTube analyzer instance
    """
    return YouTubeAnalyzer(api_key)