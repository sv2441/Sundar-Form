"""
TikTok module for the Dark Pattern Detector application.
Enhanced with multiple third-party tools for TikTok data extraction.
"""

import streamlit as st
import requests
import json
import re
from urllib.parse import urlparse
import subprocess
import os
import tempfile
from typing import List, Dict, Optional, Tuple
import whisper
import time


class TikTokAnalyzer:
    """
    Enhanced TikTok analyzer class with multiple data extraction methods.
    Supports various third-party tools and fallback options.
    """
    
    def __init__(self, api_key=None):
        """
        Initialize the TikTok analyzer with API key.
        
        Args:
            api_key (str): TikTok API key (optional for third-party tools)
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        # Initialize Whisper model for transcript extraction
        try:
            self.whisper_model = whisper.load_model("base")
            st.success("✅ Whisper model loaded successfully for transcript extraction")
        except Exception as e:
            st.warning(f"⚠️ Whisper model not available: {e}")
            self.whisper_model = None
    
    def _extract_tiktok_video_id(self, url: str) -> Optional[str]:
        """
        Extract TikTok video ID from various URL formats.
        
        Args:
            url (str): TikTok video URL
            
        Returns:
            str or None: Video ID if found, None otherwise
        """
        # Handle various TikTok URL formats
        patterns = [
            r'tiktok\.com/@[\w.-]+/video/(\d+)',
            r'tiktok\.com/v/(\d+)',
            r'vm\.tiktok\.com/(\w+)',
            r'tiktok\.com/t/(\w+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _download_and_extract_video_data(self, url: str) -> Dict:
        """
        Download TikTok video and extract comprehensive data including transcript.
        
        Args:
            url (str): TikTok video URL
            
        Returns:
            dict: Comprehensive video data including transcript
        """
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                st.write("📥 Downloading TikTok video...")
                
                # Step 1: Download video with metadata
                download_cmd = [
                    'yt-dlp',
                    '--write-info-json',
                    '--write-description',
                    '--write-thumbnail',
                    '--extract-audio',
                    '--audio-format', 'wav',
                    '--output', f'{temp_dir}/video.%(ext)s',
                    '--write-info-json',
                    url
                ]
                
                result = subprocess.run(download_cmd, capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    st.success("✅ Video downloaded successfully")
                    
                    # Step 2: Extract metadata from JSON file
                    json_files = [f for f in os.listdir(temp_dir) if f.endswith('.info.json')]
                    if json_files:
                        with open(os.path.join(temp_dir, json_files[0]), 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        # Step 3: Extract transcript using Whisper
                        transcript = "No transcript available"
                        audio_files = [f for f in os.listdir(temp_dir) if f.endswith('.wav')]
                        
                        if audio_files and self.whisper_model:
                            st.write("🎤 Extracting transcript using Whisper...")
                            audio_file = os.path.join(temp_dir, audio_files[0])
                            
                            try:
                                result = self.whisper_model.transcribe(audio_file)
                                transcript = result['text']
                                st.success(f"✅ Transcript extracted: {len(transcript)} characters")
                            except Exception as e:
                                st.warning(f"⚠️ Transcript extraction failed: {e}")
                                transcript = "Transcript extraction failed"
                        elif not self.whisper_model:
                            transcript = "Whisper model not available for transcript extraction"
                        
                        # Step 4: Read description file if available
                        description = ""
                        desc_files = [f for f in os.listdir(temp_dir) if f.endswith('.description')]
                        if desc_files:
                            with open(os.path.join(temp_dir, desc_files[0]), 'r', encoding='utf-8') as f:
                                description = f.read().strip()
                        
                        return {
                            "success": True,
                            "method": "video_download",
                            "title": metadata.get('title', ''),
                            "description": description or metadata.get('description', ''),
                            "uploader": metadata.get('uploader', ''),
                            "duration": metadata.get('duration', 0),
                            "view_count": metadata.get('view_count', 0),
                            "like_count": metadata.get('like_count', 0),
                            "comment_count": metadata.get('comment_count', 0),
                            "upload_date": metadata.get('upload_date', ''),
                            "tags": metadata.get('tags', []),
                            "categories": metadata.get('categories', []),
                            "webpage_url": metadata.get('webpage_url', url),
                            "transcript": transcript
                        }
                    else:
                        st.warning("⚠️ No metadata file found after download")
                        return {"error": "No metadata file found", "method": "video_download"}
                else:
                    st.error(f"❌ Video download failed: {result.stderr}")
                    return {"error": result.stderr, "method": "video_download"}
                    
        except Exception as e:
            st.error(f"❌ Error during video download: {str(e)}")
            return {"error": str(e), "method": "video_download"}
    
    def _try_yt_dlp_extraction(self, url: str) -> Dict:
        """
        Attempt to extract TikTok video data using yt-dlp (metadata only).
        
        Args:
            url (str): TikTok video URL
            
        Returns:
            dict: Extracted video data or error information
        """
        try:
            # Check if yt-dlp is available
            result = subprocess.run(['yt-dlp', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return {"error": "yt-dlp not installed", "method": "yt-dlp"}
            
            # Extract metadata using yt-dlp
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-download',
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    "success": True,
                    "method": "yt-dlp",
                    "title": data.get('title', ''),
                    "description": data.get('description', ''),
                    "uploader": data.get('uploader', ''),
                    "duration": data.get('duration', 0),
                    "view_count": data.get('view_count', 0),
                    "like_count": data.get('like_count', 0),
                    "comment_count": data.get('comment_count', 0),
                    "upload_date": data.get('upload_date', ''),
                    "tags": data.get('tags', []),
                    "categories": data.get('categories', []),
                    "webpage_url": data.get('webpage_url', url)
                }
            else:
                return {"error": result.stderr, "method": "yt-dlp"}
                
        except Exception as e:
            return {"error": str(e), "method": "yt-dlp"}
    
    def _try_web_scraping(self, url: str) -> Dict:
        """
        Attempt to extract TikTok video data using web scraping.
        
        Args:
            url (str): TikTok video URL
            
        Returns:
            dict: Extracted video data or error information
        """
        try:
            # Add headers to mimic browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Extract basic information from HTML
                html_content = response.text
                
                # Look for JSON data in script tags
                json_pattern = r'<script id="SIGI_STATE" type="application/json">(.*?)</script>'
                match = re.search(json_pattern, html_content, re.DOTALL)
                
                if match:
                    try:
                        json_data = json.loads(match.group(1))
                        # Parse TikTok's internal data structure
                        return self._parse_tiktok_json(json_data, url)
                    except json.JSONDecodeError:
                        pass
                
                # Fallback: extract basic info from HTML
                return self._extract_basic_info_from_html(html_content, url)
            else:
                return {"error": f"HTTP {response.status_code}", "method": "web_scraping"}
                
        except Exception as e:
            return {"error": str(e), "method": "web_scraping"}
    
    def _parse_tiktok_json(self, json_data: Dict, url: str) -> Dict:
        """
        Parse TikTok's internal JSON data structure.
        
        Args:
            json_data (dict): TikTok's internal JSON data
            url (str): Original video URL
            
        Returns:
            dict: Parsed video data
        """
        try:
            # Navigate through TikTok's complex JSON structure
            video_data = {}
            
            # Look for video information in various possible locations
            if 'ItemModule' in json_data:
                for key, item in json_data['ItemModule'].items():
                    if 'video' in item:
                        video_data = {
                            "success": True,
                            "method": "web_scraping",
                            "title": item.get('desc', ''),
                            "description": item.get('desc', ''),
                            "uploader": item.get('author', {}).get('nickname', ''),
                            "duration": item.get('video', {}).get('duration', 0),
                            "view_count": item.get('stats', {}).get('playCount', 0),
                            "like_count": item.get('stats', {}).get('diggCount', 0),
                            "comment_count": item.get('stats', {}).get('commentCount', 0),
                            "webpage_url": url
                        }
                        break
            
            return video_data if video_data else {"error": "No video data found in JSON", "method": "web_scraping"}
            
        except Exception as e:
            return {"error": f"JSON parsing error: {str(e)}", "method": "web_scraping"}
    
    def _extract_basic_info_from_html(self, html_content: str, url: str) -> Dict:
        """
        Extract basic information from HTML when JSON parsing fails.
        
        Args:
            html_content (str): HTML content of the page
            url (str): Original video URL
            
        Returns:
            dict: Basic video information
        """
        try:
            # Extract title from multiple possible locations
            title = ''
            
            # Try meta tags first
            title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html_content)
            if title_match:
                title = title_match.group(1)
            
            # Try other title patterns if meta tag is empty
            if not title:
                # Look for title in various HTML patterns
                title_patterns = [
                    r'<title>([^<]+)</title>',
                    r'<h1[^>]*>([^<]+)</h1>',
                    r'<h2[^>]*>([^<]+)</h2>',
                    r'<div[^>]*class="[^"]*title[^"]*"[^>]*>([^<]+)</div>',
                    r'<span[^>]*class="[^"]*title[^"]*"[^>]*>([^<]+)</span>'
                ]
                
                for pattern in title_patterns:
                    match = re.search(pattern, html_content, re.IGNORECASE)
                    if match:
                        title = match.group(1).strip()
                        if title and len(title) > 5:  # Ensure it's a meaningful title
                            break
            
            # Extract description from meta tags
            desc_match = re.search(r'<meta property="og:description" content="([^"]+)"', html_content)
            description = desc_match.group(1) if desc_match else ''
            
            # Extract creator from various possible locations
            creator = ''
            
            # Try meta tags first
            creator_match = re.search(r'<meta property="og:site_name" content="([^"]+)"', html_content)
            if creator_match:
                creator = creator_match.group(1)
            
            # Try to extract from URL if not found in meta tags
            if not creator:
                url_match = re.search(r'tiktok\.com/@([^/]+)', url)
                if url_match:
                    creator = f"@{url_match.group(1)}"
            
            # Try to find creator in HTML content
            if not creator:
                creator_patterns = [
                    r'<meta name="author" content="([^"]+)"',
                    r'<span[^>]*class="[^"]*author[^"]*"[^>]*>([^<]+)</span>',
                    r'<div[^>]*class="[^"]*author[^"]*"[^>]*>([^<]+)</div>',
                    r'<a[^>]*class="[^"]*author[^"]*"[^>]*>([^<]+)</a>'
                ]
                
                for pattern in creator_patterns:
                    match = re.search(pattern, html_content, re.IGNORECASE)
                    if match:
                        creator = match.group(1).strip()
                        if creator:
                            break
            
            # Try to extract video stats if available
            view_count = 0
            like_count = 0
            comment_count = 0
            
            # Look for stats in HTML
            stats_patterns = [
                (r'([0-9,]+)\s*views?', 'view_count'),
                (r'([0-9,]+)\s*likes?', 'like_count'),
                (r'([0-9,]+)\s*comments?', 'comment_count')
            ]
            
            for pattern, stat_type in stats_patterns:
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    try:
                        value = int(match.group(1).replace(',', ''))
                        if stat_type == 'view_count':
                            view_count = value
                        elif stat_type == 'like_count':
                            like_count = value
                        elif stat_type == 'comment_count':
                            comment_count = value
                    except ValueError:
                        pass
            
            # If no title found, create a default one
            if not title:
                title = f"TikTok video by {creator}" if creator else "TikTok video"
            
            # If no description found, create a default one
            if not description:
                description = f"TikTok video content from {creator}" if creator else "TikTok video content"
            
            return {
                "success": True,
                "method": "web_scraping_basic",
                "title": title,
                "description": description,
                "uploader": creator,
                "view_count": view_count,
                "like_count": like_count,
                "comment_count": comment_count,
                "webpage_url": url
            }
            
        except Exception as e:
            return {"error": f"HTML parsing error: {str(e)}", "method": "web_scraping_basic"}
    
    def search_videos_by_keywords(self, keywords_hashtags: str, max_results: int, exclude_creators: str) -> List[Dict]:
        """
        Search TikTok videos by keywords/hashtags.
        
        Args:
            keywords_hashtags (str): Comma-separated or multi-line keywords
            max_results (int): Maximum number of results to fetch
            exclude_creators (str): Comma-separated creators to exclude
            
        Returns:
            list: List of video data dictionaries
        """
        st.warning("TikTok keyword search is limited due to API restrictions.")
        st.info("Consider using specific TikTok URLs for analysis instead.")
        
        # Parse keywords
        search_queries = [q.strip() for q in keywords_hashtags.replace('\n', ',').split(',') if q.strip()]
        
        results = []
        for query in search_queries[:3]:  # Limit to 3 queries to avoid rate limiting
            st.write(f"Searching TikTok for: '{query}'")
            
            # For now, return placeholder results
            # In a full implementation, you would use TikTok's search API or web scraping
            results.append({
                "Platform": "TikTok",
                "Video ID": f"placeholder_{query}",
                "Title": f"Search result for: {query}",
                "Channel": "Unknown",
                "URL": f"https://tiktok.com/search?q={query}",
                "Description": "Search functionality requires TikTok API access",
                "Transcript": "Not available for search results",
                "Dark Pattern Analysis": "N/A",
                "Overall Confidence Score": "N/A",
                "Product Names": "N/A"
            })
        
        return results
    
    def analyze_video_urls(self, tiktok_video_urls_input: str, exclude_creators: str) -> List[Dict]:
        """
        Analyze specific TikTok video URLs using comprehensive extraction methods.
        
        Args:
            tiktok_video_urls_input (str): Multi-line TikTok URLs
            exclude_creators (str): Comma-separated creators to exclude
            
        Returns:
            list: List of video data dictionaries
        """
        if not tiktok_video_urls_input.strip():
            st.warning("Please enter at least one TikTok Video URL to analyze.")
            return []
        
        # Parse URLs
        urls = [url.strip() for url in tiktok_video_urls_input.split('\n') if url.strip()]
        exclude_creators_list = [creator.strip().lower() for creator in exclude_creators.split(',') if creator.strip()]
        
        all_results = []
        
        for url in urls[:5]:  # Limit to 5 URLs for performance
            st.write(f"🎵 Analyzing TikTok video: {url}")
            
            # Extract video ID
            video_id = self._extract_tiktok_video_id(url)
            if not video_id:
                st.warning(f"Invalid TikTok URL skipped: {url}")
                continue
            
            # Try comprehensive extraction methods
            video_data = None
            
            # Method 1: Try comprehensive video download and extraction
            st.write("📥 Attempting comprehensive video download and extraction...")
            download_result = self._download_and_extract_video_data(url)
            
            if download_result.get("success"):
                video_data = download_result
                st.success("✅ Comprehensive extraction successful!")
                st.write(f"📋 Extracted: Title='{video_data.get('title', 'N/A')}', Creator='{video_data.get('uploader', 'N/A')}'")
                st.write(f"📋 Transcript: {len(video_data.get('transcript', ''))} characters")
            else:
                st.warning(f"Video download failed: {download_result.get('error', 'Unknown error')}")
                
                # Method 2: Try yt-dlp metadata extraction
                st.write("🔧 Attempting yt-dlp metadata extraction...")
                yt_dlp_result = self._try_yt_dlp_extraction(url)
                
                if yt_dlp_result.get("success"):
                    video_data = yt_dlp_result
                    st.success("✅ yt-dlp extraction successful")
                    st.write(f"📋 Extracted: Title='{video_data.get('title', 'N/A')}', Creator='{video_data.get('uploader', 'N/A')}'")
                else:
                    st.warning(f"yt-dlp failed: {yt_dlp_result.get('error', 'Unknown error')}")
                    
                    # Method 3: Try web scraping
                    st.write("🌐 Attempting web scraping...")
                    scraping_result = self._try_web_scraping(url)
                    
                    if scraping_result.get("success"):
                        video_data = scraping_result
                        st.success("✅ Web scraping successful")
                        st.write(f"📋 Extracted: Title='{video_data.get('title', 'N/A')}', Creator='{video_data.get('uploader', 'N/A')}'")
                        st.write(f"📋 Method used: {video_data.get('method', 'Unknown')}")
                    else:
                        st.warning(f"Web scraping failed: {scraping_result.get('error', 'Unknown error')}")
            
            if video_data:
                # Check if creator should be excluded
                creator = video_data.get("uploader", "Unknown")
                if creator.lower() in exclude_creators_list:
                    st.info(f"Skipping video from excluded creator: {creator}")
                    continue
                
                # Create result with detailed information
                result = {
                    "Platform": "TikTok",
                    "Video ID": video_id,
                    "Title": video_data.get("title", "Unknown"),
                    "Channel": creator,
                    "URL": url,
                    "Description": video_data.get("description", ""),
                    "Transcript": video_data.get("transcript", "No transcript available"),
                    "Duration": video_data.get("duration", 0),
                    "View Count": video_data.get("view_count", 0),
                    "Like Count": video_data.get("like_count", 0),
                    "Comment Count": video_data.get("comment_count", 0),
                    "Tags": video_data.get("tags", []),
                    "Dark Pattern Analysis": "N/A",
                    "Overall Confidence Score": "N/A",
                    "Product Names": "N/A"
                }
                
                # Add extraction method info for debugging
                result["Extraction Method"] = video_data.get("method", "Unknown")
                
                all_results.append(result)
                
                # Show detailed extraction info
                st.write("📊 Extraction Details:")
                st.write(f"   - Method: {video_data.get('method', 'Unknown')}")
                st.write(f"   - Title: {video_data.get('title', 'N/A')}")
                st.write(f"   - Creator: {creator}")
                st.write(f"   - Duration: {video_data.get('duration', 'N/A')} seconds")
                st.write(f"   - Views: {video_data.get('view_count', 'N/A')}")
                st.write(f"   - Likes: {video_data.get('like_count', 'N/A')}")
                st.write(f"   - Comments: {video_data.get('comment_count', 'N/A')}")
                st.write(f"   - Transcript Length: {len(video_data.get('transcript', ''))} characters")
                
            else:
                st.error(f"Failed to extract data from: {url}")
                st.write("💡 This might be due to:")
                st.write("   - Video being private or deleted")
                st.write("   - TikTok's anti-bot measures")
                st.write("   - Network connectivity issues")
                st.write("   - Insufficient disk space for download")
        
        return all_results
    
    def analyze_dark_patterns(self, video_results: List[Dict], gemini_prompt: str, gemini_api_key: str) -> List[Dict]:
        """
        Perform dark pattern analysis on TikTok video results using Gemini API.
        
        Args:
            video_results (list): List of video data dictionaries
            gemini_prompt (str): Analysis prompt for Gemini
            gemini_api_key (str): Gemini API key
            
        Returns:
            list: Updated video results with analysis
        """
        if not video_results:
            st.warning("No TikTok videos available for dark pattern analysis.")
            return video_results
        
        st.write("Performing dark pattern analysis on TikTok videos...")
        
        # Import here to avoid circular imports
        from Utility.utils import analyze_with_gemini, format_dark_pattern_analysis
        
        for i, video in enumerate(video_results):
            st.write(f"Analyzing video {i+1}/{len(video_results)}: {video.get('Title', 'Unknown')}")
            
            # Prepare content for analysis
            content_for_analysis = f"""
            Title: {video.get('Title', '')}
            Description: {video.get('Description', '')}
            Transcript: {video.get('Transcript', '')}
            Tags: {', '.join(video.get('Tags', []))}
            """
            
            try:
                # Analyze with Gemini
                analysis_result = analyze_with_gemini(content_for_analysis, gemini_prompt, gemini_api_key)
                
                if analysis_result:
                    # Format the analysis results
                    formatted_analysis = format_dark_pattern_analysis(analysis_result)
                    
                    video_results[i]["Dark Pattern Analysis"] = formatted_analysis
                    video_results[i]["Overall Confidence Score"] = analysis_result.get("overallConfidenceScore", "N/A")
                    video_results[i]["Product Names"] = ", ".join(analysis_result.get("productNames", []))
                    
                    st.success(f"Analysis completed for: {video.get('Title', 'Unknown')}")
                else:
                    st.warning(f"Analysis failed for: {video.get('Title', 'Unknown')}")
                    
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
                video_results[i]["Dark Pattern Analysis"] = f"Analysis error: {str(e)}"
        
        return video_results


def create_tiktok_analyzer(api_key=None):
    """
    Factory function to create a TikTok analyzer instance.
    
    Args:
        api_key (str): TikTok API key (optional)
        
    Returns:
        TikTokAnalyzer: Configured TikTok analyzer instance
    """
    return TikTokAnalyzer(api_key)


# TODO: Future implementation tasks for TikTok integration
"""
Future Implementation Tasks:

1. **Install Required Dependencies:**
   pip install yt-dlp
   pip install openai-whisper  # For transcript extraction
   pip install selenium  # For advanced web scraping

2. **Speech-to-Text Integration:**
   - Integrate OpenAI Whisper API for transcript extraction
   - Add support for multiple languages
   - Handle audio processing for better accuracy

3. **Enhanced Web Scraping:**
   - Implement Selenium-based scraping for dynamic content
   - Add proxy rotation to avoid rate limiting
   - Implement retry mechanisms with exponential backoff

4. **TikTok API Integration:**
   - Research official TikTok API access
   - Implement authentication flow
   - Handle API rate limits and quotas

5. **Data Validation:**
   - Add input validation for TikTok URLs
   - Implement data quality checks
   - Add error handling for malformed data

6. **Performance Optimization:**
   - Implement caching for repeated requests
   - Add parallel processing for multiple URLs
   - Optimize memory usage for large datasets

7. **User Experience:**
   - Add progress indicators for long operations
   - Implement cancel functionality
   - Provide detailed error messages

8. **Compliance:**
   - Ensure compliance with TikTok's Terms of Service
   - Implement rate limiting to avoid being blocked
   - Add user consent mechanisms for data collection
"""