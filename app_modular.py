"""
Main application for the Dark Pattern Detector - Modular Version.
Orchestrates all modules and handles the main application flow.
"""

import streamlit as st
from config import initialize_session_state, get_api_keys, get_airtable_config
from ui_components import (
    setup_page_config, create_navigation, render_dark_pattern_reference,
    render_settings_page, render_history_page, create_search_interface, 
    render_tiktok_placeholder, render_results_tabs, render_data_storage_placeholder
)
from youtube_module import create_youtube_analyzer
from tiktok_module import create_tiktok_analyzer
from firebase_module import create_firebase_manager
from utils import extract_video_id


def main():
    """
    Main application function that orchestrates all modules.
    """
    # Setup page configuration
    setup_page_config()
    
    # Initialize session state
    initialize_session_state()
    
    # Create navigation and get selected page
    selected_page = create_navigation()
    
    # Route to appropriate page
    if selected_page == "Dark Pattern Reference":
        render_dark_pattern_reference()
        
    elif selected_page == "History":
        render_history_page()
        
    elif selected_page == "Settings":
        render_settings_page()
        
    elif selected_page == "Application":
        # Get API keys
        youtube_api_key, gemini_api_key = get_api_keys()
        gemini_prompt = st.session_state.gemini_prompt
        
        # Create search interface and get parameters
        search_params = create_search_interface()
        
        if not search_params:
            st.stop()
        
        # Process search when button is clicked
        if st.button("Start Search and Analysis"):
            all_results = []
            
            # Initialize Firebase manager
            firebase_manager = create_firebase_manager()
            
            # Process YouTube videos if selected
            if "YouTube" in search_params["platform_options"]:
                st.subheader("🔍 YouTube Analysis")
                
                if youtube_api_key:
                    youtube_analyzer = create_youtube_analyzer(youtube_api_key)
                    
                    if search_params["search_mode"] == "Search by Keywords/Hashtags":
                        youtube_results = youtube_analyzer.search_videos_by_keywords(
                            search_params["keywords_hashtags"],
                            search_params["max_results_to_fetch"],
                            search_params["channels_to_exclude"]
                        )
                    else:  # Analyze Video URLs
                        # Filter YouTube URLs from the input
                        urls = [url.strip() for url in search_params["video_urls_input"].split('\n') if url.strip()]
                        youtube_urls = []
                        
                        for url in urls:
                            if "youtube.com" in url or "youtu.be" in url:
                                youtube_urls.append(url)
                        
                        if youtube_urls:
                            youtube_urls_text = '\n'.join(youtube_urls)
                            youtube_results = youtube_analyzer.analyze_video_urls(
                                youtube_urls_text,
                                search_params["channels_to_exclude"]
                            )
                        else:
                            st.warning("No YouTube URLs found in the provided URLs.")
                            youtube_results = []
                    
                    # Perform dark pattern analysis on YouTube results
                    if youtube_results:
                        st.write("Performing dark pattern analysis on YouTube videos...")
                        analyzed_youtube_results = youtube_analyzer.analyze_dark_patterns(
                            youtube_results, gemini_prompt, gemini_api_key
                        )
                        all_results.extend(analyzed_youtube_results)
                    else:
                        st.info("No YouTube videos found or analyzed.")
                else:
                    st.error("YouTube API key not found. Please add it to your secrets.")
            
            # Process TikTok videos if selected
            if "TikTok" in search_params["platform_options"]:
                st.subheader("🎵 TikTok Analysis")
                
                # Create TikTok analyzer (no API key required for third-party tools)
                tiktok_analyzer = create_tiktok_analyzer()
                
                if search_params["search_mode"] == "Search by Keywords/Hashtags":
                    st.info("⚠️ TikTok keyword search is limited due to API restrictions.")
                    st.info("💡 Consider using specific TikTok URLs for analysis instead.")
                    
                    tiktok_results = tiktok_analyzer.search_videos_by_keywords(
                        search_params["keywords_hashtags"],
                        search_params["max_results_to_fetch"],
                        search_params["channels_to_exclude"]
                    )
                else:  # Analyze Video URLs
                    st.info("🔧 Using enhanced TikTok extraction with multiple fallback methods...")
                    st.info("📋 This may take longer as it tries multiple extraction methods.")
                    
                    # Filter TikTok URLs from the input
                    urls = [url.strip() for url in search_params["video_urls_input"].split('\n') if url.strip()]
                    tiktok_urls = []
                    
                    for url in urls:
                        if "tiktok.com" in url:
                            tiktok_urls.append(url)
                    
                    if tiktok_urls:
                        tiktok_urls_text = '\n'.join(tiktok_urls)
                        tiktok_results = tiktok_analyzer.analyze_video_urls(
                            tiktok_urls_text,
                            search_params["channels_to_exclude"]
                        )
                    else:
                        st.warning("No TikTok URLs found in the provided URLs.")
                        tiktok_results = []
                
                # Perform dark pattern analysis on TikTok results
                if tiktok_results:
                    st.write("Performing dark pattern analysis on TikTok videos...")
                    analyzed_tiktok_results = tiktok_analyzer.analyze_dark_patterns(
                        tiktok_results, gemini_prompt, gemini_api_key
                    )
                    all_results.extend(analyzed_tiktok_results)
                else:
                    st.info("No TikTok videos found or analyzed.")
            
            # Store results in session state
            st.session_state['analyzed_results'] = all_results
            
            # Save to Firebase if connected
            if all_results and firebase_manager.is_connected():
                st.subheader("💾 Saving to Firebase")
                
                # Prepare analysis data for Firebase
                analysis_data = {
                    "videos": all_results,
                    "overall_confidence_score": "N/A",  # Could be calculated from individual scores
                    "total_videos": len(all_results),
                    "platforms_analyzed": search_params["platform_options"]
                }
                
                # Determine search type
                search_type = "keywords" if search_params["search_mode"] == "Search by Keywords/Hashtags" else "urls"
                
                # Determine platform
                platform = "Mixed" if len(search_params["platform_options"]) > 1 else search_params["platform_options"][0]
                
                # Save to Firebase
                success = firebase_manager.save_analysis_session(
                    search_params["session_name"],
                    analysis_data,
                    search_type,
                    platform
                )
                
                if success:
                    st.success("✅ Analysis session saved to Firebase successfully!")
                else:
                    st.warning("⚠️ Failed to save to Firebase, but analysis completed successfully.")
            
            # Display results
            if st.session_state['analyzed_results']:
                st.success(f"✅ Analysis complete! Found {len(all_results)} videos to analyze.")
                render_results_tabs(st.session_state['analyzed_results'])
            else:
                st.info("No videos found or analyzed based on your input.")
            
            # Render data storage placeholder
            render_data_storage_placeholder()


if __name__ == "__main__":
    main()