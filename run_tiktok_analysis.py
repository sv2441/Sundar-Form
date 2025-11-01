#!/usr/bin/env python3
"""
Simple runner script for TikTok CSV analysis
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()   

# Add the Utility directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Utility'))

from analyze_tiktok_csv import TikTokCSVAnalyzer

def main():
    """Run TikTok CSV analysis"""
    
    # Configuration
    CSV_FILE_PATH = "tiktok-transcripts.csv"
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
    
    # Validate configuration
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY environment variable not set")
        return
    
    if not os.path.exists(CSV_FILE_PATH):
        print(f"❌ CSV file not found: {CSV_FILE_PATH}")
        return
    
    # Create analyzer and run analysis
    analyzer = TikTokCSVAnalyzer(
        gemini_api_key=GEMINI_API_KEY,
        firebase_service_account_path=FIREBASE_SERVICE_ACCOUNT_PATH
    )
    
    print("🚀 Starting TikTok CSV Analysis...")
    print("=" * 50)
    
    results = analyzer.run_analysis(
        csv_file_path=CSV_FILE_PATH,
        max_videos=50,  # Limit to 10 videos
        only_available=True,
        save_to_firebase=True
    )
    
    if results.get("success"):
        print("🎉 Analysis completed successfully!")
        print(f"📊 Document ID: {results.get('document_id')}")
        print(f"📊 Total videos: {results['summary']['total_videos']}")
        print(f"📊 Successful analyses: {results['summary']['successful_analyses']}")
        print(f"📊 Failed analyses: {results['summary']['failed_analyses']}")
    else:
        print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main() 