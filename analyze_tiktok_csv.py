#!/usr/bin/env python3
"""
TikTok CSV Analysis Script
Analyzes TikTok URLs from CSV file and performs dark pattern analysis.
Saves results to Firebase with session management.
"""

import pandas as pd
import streamlit as st
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional
import json
from pydantic import BaseModel, Field
from typing import List, Optional

# Add the Utility directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Utility'))

from Utility.firebase_module import FirebaseManager
from Utility.utils import format_dark_pattern_analysis
from Utility.tiktok_module import TikTokAnalyzer
from dotenv import load_dotenv

from Utility.config import get_default_gemini_prompt

# Import langchain components
from langchain.chat_models import init_chat_model
from langchain.schema import HumanMessage

load_dotenv()

class RegulatoryViolationReference(BaseModel):
    """Regulatory violation reference details."""
    law_name: str = Field(description="The law or guidance reference")
    clause_name: str = Field(description="The specific article or clause")
    highLevelSynthesis: str = Field(description="High-level synthesis of the violation")


class DarkPatternAnalysis(BaseModel):
    """Individual dark pattern analysis result."""
    dark_pattern: str = Field(description="The category of dark pattern identified")
    excerpt: str = Field(description="Specific excerpt from the content")
    sectionType: str = Field(description="Type of section (transcript, caption, or description)")
    reasoning: str = Field(description="Explanation of why this qualifies as a dark pattern")
    confidenceScore: int = Field(description="Confidence score (0-100)")
    regulatoryViolationReference: List[RegulatoryViolationReference] = Field(
        description="List of regulatory violations that apply to this dark pattern"
    )


class DarkPatternAnalysisResult(BaseModel):
    """Complete dark pattern analysis result."""
    darkPatternAnalysis: List[DarkPatternAnalysis] = Field(
        description="List of dark patterns identified in the content"
    )
    overallConfidenceScore: int = Field(
        description="Overall confidence score (0-100) of the dark pattern detection"
    )
    productNames: List[str] = Field(
        description="List of product names mentioned in the text"
    )


class TikTokCSVAnalyzer:
    """
    Analyzer class for processing TikTok URLs from CSV file and performing dark pattern analysis.
    """
    
    def __init__(self, gemini_api_key: str, firebase_service_account_path: str = None):
        """
        Initialize the TikTok CSV analyzer.
        
        Args:
            gemini_api_key (str): Gemini API key for dark pattern analysis
            firebase_service_account_path (str): Path to Firebase service account file
        """
        self.gemini_api_key = gemini_api_key
        self.firebase_manager = FirebaseManager()
        self.tiktok_analyzer = TikTokAnalyzer()
        
        # Set Firebase service account path if provided
        if firebase_service_account_path:
            os.environ['FIREBASE_SERVICE_ACCOUNT_PATH'] = firebase_service_account_path
        
        # Set up Gemini API key for langchain
        os.environ["GOOGLE_API_KEY"] = gemini_api_key
        
        # Initialize langchain chat model with structured output
        try:
            self.llm = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
            self.structured_llm = self.llm.with_structured_output(DarkPatternAnalysisResult)
            print("✅ Langchain Gemini model initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing Langchain model: {str(e)}")
            self.structured_llm = None
        
        # Get default analysis prompt from config
        self.analysis_prompt = get_default_gemini_prompt()
    
    def load_csv_data(self, csv_file_path: str) -> pd.DataFrame:
        """
        Load and validate TikTok CSV data.
        
        Args:
            csv_file_path (str): Path to the CSV file
            
        Returns:
            pd.DataFrame: Loaded and validated data
        """
        try:
            # Load CSV file
            df = pd.read_csv(csv_file_path)
            
            # Validate required columns
            required_columns = ['TikTok Link', 'Transcript', 'Available']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Clean and validate data
            df = df.dropna(subset=['TikTok Link'])  # Remove rows without URLs
            df['Available'] = df['Available'].str.lower().str.strip()  # Normalize available column
            
            print(f"✅ Loaded {len(df)} TikTok videos from CSV")
            print(f"📊 Available transcripts: {len(df[df['Available'] == 'yes'])}")
            print(f"📊 Missing transcripts: {len(df[df['Available'] == 'no'])}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error loading CSV file: {str(e)}")
            return pd.DataFrame()
    
    def analyze_video_content(self, url: str, transcript: str) -> Dict:
        """
        Analyze a single TikTok video for dark patterns using structured output.
        
        Args:
            url (str): TikTok video URL
            transcript (str): Video transcript
            
        Returns:
            dict: Analysis results
        """
        try:
            if not self.structured_llm:
                return {
                    "success": False,
                    "url": url,
                    "transcript": transcript,
                    "error": "Langchain model not initialized"
                }
            
            # Prepare content for analysis
            content_for_analysis = f"""
            Content to analyze:
            
            TikTok Video URL: {url}
            Transcript: {transcript}
            
            Please analyze this content for dark patterns and deceptive practices.
            """
            
            # Perform structured analysis using langchain
            analysis_result = self.structured_llm.invoke(content_for_analysis)
            
            if analysis_result:
                # Convert Pydantic model to dict for processing
                result_dict = analysis_result.dict()
                
                # Format the analysis results
                formatted_analysis = format_dark_pattern_analysis(result_dict.get('darkPatternAnalysis', []))
                
                return {
                    "success": True,
                    "url": url,
                    "transcript": transcript,
                    "dark_pattern_analysis": formatted_analysis,
                    "raw_analysis": result_dict.get('darkPatternAnalysis', []),
                    "overall_confidence_score": result_dict.get('overallConfidenceScore', 'N/A'),
                    "product_names": ", ".join(result_dict.get('productNames', [])) if result_dict.get('productNames') else "N/A"
                }
            else:
                return {
                    "success": False,
                    "url": url,
                    "transcript": transcript,
                    "error": "Analysis failed - no result returned"
                }
                
        except Exception as e:
            return {
                "success": False,
                "url": url,
                "transcript": transcript,
                "error": f"Analysis error: {str(e)}"
            }
    
    def process_csv_analysis(self, csv_file_path: str, max_videos: int = None, 
                           only_available: bool = True) -> Dict:
        """
        Process TikTok CSV file and perform dark pattern analysis.
        
        Args:
            csv_file_path (str): Path to the CSV file
            max_videos (int): Maximum number of videos to analyze (None for all)
            only_available (bool): Only analyze videos with available transcripts
            
        Returns:
            dict: Analysis results and session data
        """
        print("🚀 Starting TikTok CSV analysis...")
        
        # Load CSV data
        df = self.load_csv_data(csv_file_path)
        if df.empty:
            return {"error": "Failed to load CSV data"}
        
        # Filter data based on parameters
        if only_available:
            df = df[df['Available'] == 'yes']
            print(f"📋 Analyzing {len(df)} videos with available transcripts")
        else:
            print(f"📋 Analyzing {len(df)} videos (including those without transcripts)")
        
        # Limit to 10 videos for analysis
        if len(df) > 50:
            df = df.head(10)
            print(f"📋 Limited to 10 videos for analysis")
        
        if df.empty:
            return {"error": "No videos to analyze after filtering"}
        
        # Process each video
        analysis_results = []
        successful_analyses = 0
        failed_analyses = 0
        
        for index, row in df.iterrows():
            url = row['TikTok Link']
            transcript = row['Transcript']
            available = row['Available']
            
            print(f"🔍 Analyzing video {index + 1}/{len(df)}: {url}")
            
            if available == 'yes' and transcript and transcript != "No transcript available":
                result = self.analyze_video_content(url, transcript)
                
                # Ensure the result has all required fields for Firebase
                if result['success']:
                    # Add additional fields for consistency
                    result['video_id'] = url.split('/')[-1] if '/' in url else url
                    result['platform'] = 'TikTok'
                    result['analysis_timestamp'] = datetime.now().isoformat()
                    
                    successful_analyses += 1
                    print(f"✅ Analysis completed for: {url}")
                    print(f"   📊 Confidence Score: {result.get('overall_confidence_score', 'N/A')}")
                    print(f"   📦 Products: {result.get('product_names', 'N/A')}")
                else:
                    # Add additional fields for failed analysis
                    result['video_id'] = url.split('/')[-1] if '/' in url else url
                    result['platform'] = 'TikTok'
                    result['analysis_timestamp'] = datetime.now().isoformat()
                    
                    failed_analyses += 1
                    print(f"❌ Analysis failed for: {url} - {result.get('error', 'Unknown error')}")
                
                analysis_results.append(result)
            else:
                print(f"⏭️ Skipping video without transcript: {url}")
                failed_result = {
                    "success": False,
                    "url": url,
                    "transcript": transcript,
                    "error": "No transcript available",
                    "video_id": url.split('/')[-1] if '/' in url else url,
                    "platform": 'TikTok',
                    "analysis_timestamp": datetime.now().isoformat(),
                    "dark_pattern_analysis": "No analysis performed - no transcript available",
                    "raw_analysis": [],
                    "overall_confidence_score": "N/A",
                    "product_names": "N/A"
                }
                analysis_results.append(failed_result)
                failed_analyses += 1
        
        # Prepare session data
        session_data = {
            "sessionName": f"TikTok_CSV_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "search_type": "csv_urls",
            "platform": "TikTok",
            "analysis_data": {
                "videos": analysis_results,
                "total_videos": len(df),
                "successful_analyses": successful_analyses,
                "failed_analyses": failed_analyses,
                "csv_file": os.path.basename(csv_file_path),  # Just the filename
                "analysis_timestamp": datetime.now().isoformat(),
                "overall_confidence_score": "N/A"  # Will be calculated if needed
            }
        }
        
        print(f"📊 Analysis Summary:")
        print(f"   - Total videos processed: {len(df)}")
        print(f"   - Successful analyses: {successful_analyses}")
        print(f"   - Failed analyses: {failed_analyses}")
        
        return session_data
    
    def save_to_firebase(self, session_data: Dict) -> Optional[str]:
        """
        Save analysis results to Firebase.
        
        Args:
            session_data (dict): Session data to save
            
        Returns:
            str or None: Document ID if successful, None otherwise
        """
        try:
            # Debug: Print the structure being sent to Firebase
            print(f"🔍 Debug: Sending to Firebase:")
            print(f"   - Session name: {session_data['sessionName']}")
            print(f"   - Platform: {session_data['platform']}")
            print(f"   - Total videos: {session_data['analysis_data']['total_videos']}")
            print(f"   - Videos data length: {len(session_data['analysis_data']['videos'])}")
            
            document_id = self.firebase_manager.save_analysis_session(
                sessionName=session_data["sessionName"],
                analysis_data=session_data["analysis_data"],
                search_type=session_data["search_type"],
                platform=session_data["platform"],
                created_by="tiktok_csv_analyzer"  # You can change this to user email
            )
            
            if document_id:
                print(f"✅ Analysis results saved to Firebase with document ID: {document_id}")
                return document_id
            else:
                print("❌ Failed to save analysis results to Firebase")
                return None
                
        except Exception as e:
            print(f"❌ Error saving to Firebase: {str(e)}")
            return None
    
    def run_analysis(self, csv_file_path: str, max_videos: int = None, 
                    only_available: bool = True, save_to_firebase: bool = True) -> Dict:
        """
        Run complete TikTok CSV analysis workflow.
        
        Args:
            csv_file_path (str): Path to the CSV file
            max_videos (int): Maximum number of videos to analyze
            only_available (bool): Only analyze videos with available transcripts
            save_to_firebase (bool): Whether to save results to Firebase
            
        Returns:
            dict: Complete analysis results
        """
        print("🎯 Starting TikTok CSV Analysis Workflow")
        print("=" * 50)
        
        # Step 1: Process CSV analysis
        session_data = self.process_csv_analysis(csv_file_path, max_videos, only_available)
        
        if "error" in session_data:
            print(f"❌ Analysis failed: {session_data['error']}")
            return session_data
        
        # Step 2: Save to Firebase if requested
        document_id = None
        if save_to_firebase and self.firebase_manager.is_connected():
            document_id = self.save_to_firebase(session_data)
        elif save_to_firebase and not self.firebase_manager.is_connected():
            print("⚠️ Firebase not connected. Skipping save to Firebase.")
        
        # Step 3: Prepare final results
        results = {
            "success": True,
            "session_data": session_data,
            "document_id": document_id,
            "summary": {
                "total_videos": session_data["analysis_data"]["total_videos"],
                "successful_analyses": session_data["analysis_data"]["successful_analyses"],
                "failed_analyses": session_data["analysis_data"]["failed_analyses"],
                "saved_to_firebase": document_id is not None
            }
        }
        
        print("=" * 50)
        print("✅ TikTok CSV Analysis Workflow Completed")
        print(f"📊 Document ID: {document_id}")
        print(f"📊 Total videos: {results['summary']['total_videos']}")
        print(f"📊 Successful analyses: {results['summary']['successful_analyses']}")
        print(f"📊 Failed analyses: {results['summary']['failed_analyses']}")
        
        return results


def main():
    """
    Main function to run TikTok CSV analysis.
    """
    # Configuration
    CSV_FILE_PATH = "tiktok-transcripts.csv"
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
    
    # Analysis parameters
    MAX_VIDEOS = 50  # Limit to 50 videos for testing
    ONLY_AVAILABLE = True  # Only analyze videos with transcripts
    SAVE_TO_FIREBASE = True
    
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
    
    results = analyzer.run_analysis(
        csv_file_path=CSV_FILE_PATH,
        max_videos=MAX_VIDEOS,
        only_available=ONLY_AVAILABLE,
        save_to_firebase=SAVE_TO_FIREBASE
    )
    
    if results.get("success"):
        print("🎉 Analysis completed successfully!")
    else:
        print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main() 