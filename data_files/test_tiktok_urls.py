"""
Test script for the specific TikTok URLs provided by the user.
"""

import sys
import os
from Utility.tiktok_module import TikTokAnalyzer

# The specific TikTok URLs provided by the user
TEST_URLS = [
    "https://www.tiktok.com/@ule.beauty/video/7493819825798679830",
    "https://www.tiktok.com/@ule.beauty/video/7501000294772264214",
    "https://www.tiktok.com/@ule.beauty/video/7499885193466055958",
    "https://www.tiktok.com/@ule.beauty/video/7532802852427697430",
    "https://www.tiktok.com/@ule.beauty/video/7531744411474988310"
]

def test_tiktok_url_parsing():
    """Test TikTok URL parsing for the specific URLs."""
    analyzer = TikTokAnalyzer()
    
    print("🔍 Testing TikTok URL parsing for specific URLs:")
    for url in TEST_URLS:
        video_id = analyzer._extract_tiktok_video_id(url)
        if video_id:
            print(f"✅ {url}")
            print(f"   Video ID: {video_id}")
        else:
            print(f"❌ {url}")
            print(f"   No video ID found")

def test_tiktok_extraction_methods():
    """Test different extraction methods for the first URL."""
    analyzer = TikTokAnalyzer()
    
    test_url = TEST_URLS[0]  # Use the first URL for testing
    
    print(f"\n🎯 Testing extraction methods for: {test_url}")
    
    # Test yt-dlp extraction
    print("\n🔧 Testing yt-dlp extraction...")
    yt_dlp_result = analyzer._try_yt_dlp_extraction(test_url)
    if yt_dlp_result.get("success"):
        print("✅ yt-dlp extraction successful")
        print(f"   Title: {yt_dlp_result.get('title', 'N/A')}")
        print(f"   Uploader: {yt_dlp_result.get('uploader', 'N/A')}")
        print(f"   Duration: {yt_dlp_result.get('duration', 'N/A')}")
    else:
        print(f"❌ yt-dlp extraction failed: {yt_dlp_result.get('error', 'Unknown error')}")
    
    # Test web scraping
    print("\n🌐 Testing web scraping...")
    scraping_result = analyzer._try_web_scraping(test_url)
    if scraping_result.get("success"):
        print("✅ Web scraping successful")
        print(f"   Method: {scraping_result.get('method', 'N/A')}")
        print(f"   Title: {scraping_result.get('title', 'N/A')}")
        print(f"   Uploader: {scraping_result.get('uploader', 'N/A')}")
        print(f"   Description: {scraping_result.get('description', 'N/A')[:100]}...")
    else:
        print(f"❌ Web scraping failed: {scraping_result.get('error', 'Unknown error')}")

def test_full_analysis_workflow():
    """Test the full analysis workflow with the provided URLs."""
    analyzer = TikTokAnalyzer()
    
    print(f"\n🎯 Testing full analysis workflow with {len(TEST_URLS)} URLs:")
    
    # Convert URLs to text format
    urls_text = '\n'.join(TEST_URLS)
    
    try:
        results = analyzer.analyze_video_urls(urls_text, "")
        
        if results:
            print(f"✅ Analysis completed successfully")
            print(f"   Found {len(results)} videos")
            
            for i, result in enumerate(results, 1):
                print(f"   Video {i}: {result.get('Title', 'Unknown')}")
                print(f"     Channel: {result.get('Channel', 'Unknown')}")
                print(f"     Duration: {result.get('Duration', 'N/A')}")
                print(f"     View Count: {result.get('View Count', 'N/A')}")
                print(f"     Transcript Length: {len(result.get('Transcript', ''))} characters")
        else:
            print("❌ No results from analysis")
            
    except Exception as e:
        print(f"❌ Error during full analysis: {e}")

def main():
    """Run all tests."""
    print("🧪 TikTok URL Test Suite")
    print("=" * 50)
    
    # Test 1: URL parsing
    test_tiktok_url_parsing()
    
    # Test 2: Extraction methods
    test_tiktok_extraction_methods()
    
    # Test 3: Full analysis workflow
    test_full_analysis_workflow()
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print("✅ URL parsing tests completed")
    print("✅ Extraction method tests completed")
    print("✅ Full analysis workflow tests completed")
    print("\n💡 To use these URLs in the main application:")
    print("1. Go to the Application page")
    print("2. Enter a session name")
    print("3. Select 'Analyze Video URLs'")
    print("4. Paste the TikTok URLs")
    print("5. Select 'TikTok' platform")
    print("6. Click 'Start Search and Analysis'")

if __name__ == "__main__":
    main() 