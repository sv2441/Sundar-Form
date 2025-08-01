# TikTok Integration Guide

## 🎯 **Overview**

This guide provides comprehensive information about integrating TikTok functionality into the Dark Pattern Detector application using third-party tools and methods.

## 🛠️ **Third-Party Tools & Solutions**

### **1. yt-dlp (Recommended Primary Tool)**

**What it does:**
- Downloads TikTok videos and extracts metadata
- Supports multiple platforms including TikTok
- Extracts video information without downloading the full video
- Provides structured JSON output

**Installation:**
```bash
pip install yt-dlp
```

**Usage Example:**
```bash
# Extract metadata only (no download)
yt-dlp --dump-json --no-download "https://www.tiktok.com/@username/video/1234567890"

# Download video with metadata
yt-dlp "https://www.tiktok.com/@username/video/1234567890"
```

**Features:**
- ✅ Video metadata extraction
- ✅ Description and caption extraction
- ✅ Creator information
- ✅ View/like/comment counts
- ✅ Upload date and duration
- ✅ Tags and categories
- ❌ Transcript extraction (requires additional tools)

### **2. OpenAI Whisper (For Transcript Extraction)**

**What it does:**
- Converts speech to text from video audio
- Supports multiple languages
- High accuracy for short-form videos

**Installation:**
```bash
pip install openai-whisper
```

**Usage Example:**
```python
import whisper

# Load model
model = whisper.load_model("base")

# Transcribe audio file
result = model.transcribe("audio.wav")
print(result["text"])
```

### **3. Selenium (For Advanced Web Scraping)**

**What it does:**
- Browser automation for dynamic content
- Can handle JavaScript-rendered content
- Useful when simple requests fail

**Installation:**
```bash
pip install selenium
```

**Usage Example:**
```python
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://www.tiktok.com/@username/video/1234567890")
title = driver.find_element(By.CSS_SELECTOR, "h1").text
driver.quit()
```

## 📋 **Installation Instructions**

### **Step 1: Install Dependencies**
```bash
# Core dependencies
pip install yt-dlp openai-whisper selenium beautifulsoup4

# For browser automation (choose one)
pip install webdriver-manager  # Automatic driver management
# OR download ChromeDriver manually
```

### **Step 2: Verify Installation**
```bash
# Test yt-dlp
yt-dlp --version

# Test Whisper
python -c "import whisper; print('Whisper installed successfully')"
```

## 🔧 **Implementation Strategy**

### **Method 1: yt-dlp + Whisper (Recommended)**

```python
import subprocess
import json
import whisper
import tempfile

def extract_tiktok_data(url):
    """Extract TikTok video data using yt-dlp and Whisper."""
    
    # Step 1: Extract metadata
    cmd = ['yt-dlp', '--dump-json', '--no-download', url]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        metadata = json.loads(result.stdout)
        
        # Step 2: Download audio for transcription
        with tempfile.TemporaryDirectory() as temp_dir:
            download_cmd = [
                'yt-dlp',
                '--extract-audio',
                '--audio-format', 'wav',
                '--output', f'{temp_dir}/video.%(ext)s',
                url
            ]
            
            subprocess.run(download_cmd)
            
            # Step 3: Transcribe audio
            model = whisper.load_model("base")
            audio_file = f"{temp_dir}/video.wav"
            transcript = model.transcribe(audio_file)
            
            return {
                "title": metadata.get('title', ''),
                "description": metadata.get('description', ''),
                "uploader": metadata.get('uploader', ''),
                "transcript": transcript['text'],
                "duration": metadata.get('duration', 0),
                "view_count": metadata.get('view_count', 0),
                "like_count": metadata.get('like_count', 0),
                "comment_count": metadata.get('comment_count', 0)
            }
    
    return None
```

### **Method 2: Web Scraping Fallback**

```python
import requests
import re
import json

def scrape_tiktok_data(url):
    """Scrape TikTok data when yt-dlp fails."""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        html = response.text
        
        # Extract JSON data from TikTok's internal structure
        json_pattern = r'<script id="SIGI_STATE" type="application/json">(.*?)</script>'
        match = re.search(json_pattern, html, re.DOTALL)
        
        if match:
            data = json.loads(match.group(1))
            # Parse TikTok's complex JSON structure
            return parse_tiktok_json(data)
    
    return None
```

## 🚀 **Quick Start Guide**

### **1. Test with a Single TikTok URL**

```python
from tiktok_module import TikTokAnalyzer

# Create analyzer
analyzer = TikTokAnalyzer()

# Test with a TikTok URL
url = "https://www.tiktok.com/@username/video/1234567890"
results = analyzer.analyze_video_urls(url, "")

print(f"Extracted {len(results)} videos")
for result in results:
    print(f"Title: {result['Title']}")
    print(f"Creator: {result['Channel']}")
    print(f"Description: {result['Description'][:100]}...")
```

### **2. Batch Process Multiple URLs**

```python
urls = """
https://www.tiktok.com/@user1/video/1234567890
https://www.tiktok.com/@user2/video/0987654321
https://www.tiktok.com/@user3/video/1122334455
"""

results = analyzer.analyze_video_urls(urls, "excluded_creator1,excluded_creator2")
```

## ⚠️ **Important Considerations**

### **Rate Limiting**
- TikTok has aggressive rate limiting
- Implement delays between requests (2-5 seconds)
- Use proxy rotation for large-scale scraping
- Respect robots.txt and Terms of Service

### **Legal Compliance**
- Check TikTok's Terms of Service
- Ensure compliance with data protection laws
- Implement user consent mechanisms
- Use data only for legitimate purposes

### **Technical Limitations**
- TikTok frequently updates their website structure
- Some videos may be private or deleted
- Transcript extraction requires audio download
- Web scraping may be blocked by anti-bot measures

## 🔄 **Fallback Strategy**

The enhanced TikTok module implements a multi-layered approach:

1. **Primary**: yt-dlp for metadata extraction
2. **Secondary**: Web scraping with requests
3. **Tertiary**: Selenium for dynamic content
4. **Final**: Basic HTML parsing

## 📊 **Expected Data Output**

```json
{
  "Platform": "TikTok",
  "Video ID": "1234567890",
  "Title": "Video Title",
  "Channel": "@username",
  "URL": "https://www.tiktok.com/@username/video/1234567890",
  "Description": "Video description...",
  "Transcript": "Extracted transcript text...",
  "Duration": 30,
  "View Count": 10000,
  "Like Count": 500,
  "Comment Count": 50,
  "Tags": ["tag1", "tag2"],
  "Dark Pattern Analysis": "Analysis results...",
  "Overall Confidence Score": 85,
  "Product Names": "Product1, Product2"
}
```

## 🛠️ **Troubleshooting**

### **Common Issues**

1. **yt-dlp fails:**
   - Update yt-dlp: `pip install --upgrade yt-dlp`
   - Check if video is private or deleted
   - Try different URL formats

2. **Whisper transcription fails:**
   - Ensure audio file is downloaded correctly
   - Check audio format compatibility
   - Verify sufficient disk space

3. **Web scraping blocked:**
   - Rotate User-Agent headers
   - Add delays between requests
   - Use proxy servers

### **Debug Mode**

Enable debug output in the TikTok module:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 **Performance Optimization**

1. **Parallel Processing**: Process multiple URLs simultaneously
2. **Caching**: Cache results to avoid re-downloading
3. **Batch Processing**: Group requests to minimize overhead
4. **Error Recovery**: Implement retry mechanisms

## 🔮 **Future Enhancements**

1. **Official TikTok API**: Monitor for official API access
2. **Advanced AI**: Use GPT-4 for better transcript analysis
3. **Real-time Monitoring**: Implement live video analysis
4. **Multi-language Support**: Add support for non-English content

## 📞 **Support**

For issues with TikTok integration:
1. Check the troubleshooting section
2. Update all dependencies
3. Test with different TikTok URLs
4. Review error logs for specific issues

---

**Note**: This implementation respects TikTok's Terms of Service and implements appropriate rate limiting and error handling for production use.