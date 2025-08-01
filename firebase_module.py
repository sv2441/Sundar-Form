"""
Firebase integration module for the Dark Pattern Detector application.
Handles database operations for storing and retrieving analysis sessions.
"""

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os
from typing import List, Dict, Optional
import json


class FirebaseManager:
    """
    Firebase manager class for handling database operations.
    """
    
    def __init__(self):
        """
        Initialize Firebase connection using environment variables.
        """
        self.db = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """
        Initialize Firebase connection using service account credentials from environment.
        """
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # Get service account path from environment variable
                service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
                
                if not service_account_path:
                    st.warning("⚠️ Firebase service account path not found in environment variables.")
                    st.info("Please set FIREBASE_SERVICE_ACCOUNT_PATH environment variable.")
                    return
                
                if not os.path.exists(service_account_path):
                    st.error(f"❌ Firebase service account file not found: {service_account_path}")
                    return
                
                # Initialize Firebase with service account
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
                st.success("✅ Firebase initialized successfully")
            
            # Get Firestore client
            self.db = firestore.client()
            
        except Exception as e:
            st.error(f"❌ Firebase initialization failed: {str(e)}")
            self.db = None
    
    def save_analysis_session(self, session_name: str, analysis_data: Dict, search_type: str, platform: str) -> bool:
        """
        Save analysis session data to Firebase.
        
        Args:
            session_name (str): Name of the analysis session
            analysis_data (dict): Analysis results data
            search_type (str): Type of search (keywords/urls)
            platform (str): Platform analyzed (YouTube/TikTok)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.db:
            st.error("❌ Firebase not initialized. Cannot save data.")
            return False
        
        try:
            # Prepare session data
            session_data = {
                "session_name": session_name,
                "search_type": search_type,
                "platform": platform,
                "analysis_data": analysis_data,
                "created_at": datetime.now().isoformat(),
                "video_count": len(analysis_data.get('videos', [])),
                "overall_confidence_score": analysis_data.get('overall_confidence_score', 'N/A')
            }
            
            # Save to 'influencer-marketing' collection
            doc_ref = self.db.collection('influencer-marketing').document(session_name)
            doc_ref.set(session_data)
            
            st.success(f"✅ Analysis session '{session_name}' saved to Firebase successfully!")
            return True
            
        except Exception as e:
            st.error(f"❌ Error saving to Firebase: {str(e)}")
            return False
    
    def get_all_sessions(self) -> List[Dict]:
        """
        Retrieve all analysis sessions from Firebase.
        
        Returns:
            list: List of session data dictionaries
        """
        if not self.db:
            st.error("❌ Firebase not initialized. Cannot retrieve data.")
            return []
        
        try:
            sessions = []
            docs = self.db.collection('influencer-marketing').order_by('created_at', direction=firestore.Query.DESCENDING).stream()
            
            for doc in docs:
                session_data = doc.to_dict()
                session_data['id'] = doc.id
                sessions.append(session_data)
            
            return sessions
            
        except Exception as e:
            st.error(f"❌ Error retrieving sessions from Firebase: {str(e)}")
            return []
    
    def get_session_by_name(self, session_name: str) -> Optional[Dict]:
        """
        Retrieve a specific session by name.
        
        Args:
            session_name (str): Name of the session to retrieve
            
        Returns:
            dict or None: Session data if found, None otherwise
        """
        if not self.db:
            st.error("❌ Firebase not initialized. Cannot retrieve data.")
            return None
        
        try:
            doc_ref = self.db.collection('influencer-marketing').document(session_name)
            doc = doc_ref.get()
            
            if doc.exists:
                session_data = doc.to_dict()
                session_data['id'] = doc.id
                return session_data
            else:
                return None
                
        except Exception as e:
            st.error(f"❌ Error retrieving session from Firebase: {str(e)}")
            return None
    
    def delete_session(self, session_name: str) -> bool:
        """
        Delete a session from Firebase.
        
        Args:
            session_name (str): Name of the session to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.db:
            st.error("❌ Firebase not initialized. Cannot delete data.")
            return False
        
        try:
            doc_ref = self.db.collection('influencer-marketing').document(session_name)
            doc_ref.delete()
            st.success(f"✅ Session '{session_name}' deleted successfully!")
            return True
            
        except Exception as e:
            st.error(f"❌ Error deleting session from Firebase: {str(e)}")
            return False
    
    def is_connected(self) -> bool:
        """
        Check if Firebase is properly connected.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self.db is not None


def create_firebase_manager():
    """
    Factory function to create a Firebase manager instance.
    
    Returns:
        FirebaseManager: Configured Firebase manager instance
    """
    return FirebaseManager() 