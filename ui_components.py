"""
UI Components for the Dark Pattern Detector application.
Contains all Streamlit interface elements and display logic.
"""

import streamlit as st
import pandas as pd
from utils import fetch_all_records
import os


def setup_page_config():
    """Configure the main page settings."""
    st.set_page_config(layout="wide", page_title="Dark Pattern Detector")
    st.title("Dark Pattern Detector for Video Content")


def create_navigation():
    """Create the sidebar navigation."""
    st.sidebar.title("Navigation")
    return st.sidebar.radio("Go to", ["Application", "History", "Settings", "Dark Pattern Reference"])


def render_dark_pattern_reference():
    """Render the Dark Pattern Reference page with Airtable data."""
    st.header("Dark Pattern Reference Tables")
    
    try:
        # Get Airtable configuration from environment variables
        airtable_api_key = os.getenv('AIRTABLE_API_KEY')
        airtable_base_id = os.getenv('AIRTABLE_BASE_ID')
        
        if not airtable_api_key or not airtable_base_id:
            st.error("❌ Airtable configuration not found in environment variables.")
            st.info("Please set AIRTABLE_API_KEY and AIRTABLE_BASE_ID environment variables.")
            st.stop()
        
        # Create tabs for the two tables
        tab1, tab2 = st.tabs(["Influencer Dark Patterns", "Law/Guidance Clauses"])
        
        with tab1:
            st.subheader("Influencer Dark Pattern Types")
            
            # Fetch dark pattern records using direct API
            dark_pattern_records = fetch_all_records(
                airtable_base_id,
                "tblOqL0mtNyY74Z2d",  # Dark Pattern table ID
                airtable_api_key
            )
            
            # Convert to DataFrame
            dark_pattern_df = pd.DataFrame([
                {
                    "Issues": record["fields"].get("Issues", ""),
                    "Description": record["fields"].get("Description", ""),
                    "Classification": record["fields"].get("Classification", ""),
                    "Remarks": record["fields"].get("Remarks", "")
                }
                for record in dark_pattern_records
            ])
            
            # Display the DataFrame
            st.dataframe(
                dark_pattern_df,
                column_config={
                    "Issues": "Dark Pattern Type",
                    "Description": "Description",
                    "Classification": "Detection Status",
                    "Remarks": "Additional Notes"
                },
                use_container_width=True
            )
        
        with tab2:
            st.subheader("Law and Guidance Reference")
            
            # Fetch law/guidance records using direct API
            law_guidance_records = fetch_all_records(
                airtable_base_id,
                "tblk0vHIm00L5P1ME",  # Law/Guidance table ID
                airtable_api_key
            )
            
            # Convert to DataFrame
            law_guidance_df = pd.DataFrame([
                {
                    "Law/Guidance": record["fields"].get("Law/Guidance Name", ""),
                    "Clause/Article": record["fields"].get("Clause or Article Reference", ""),
                    "Verbatim": record["fields"].get("Verbatim of Clause or Article", ""),
                    "High Level Synthesis": record["fields"].get("High Level Synthesis (Bullets)", "")
                }
                for record in law_guidance_records
            ])
            
            # Display the DataFrame
            st.dataframe(
                law_guidance_df,
                column_config={
                    "Law/Guidance": "Law/Guidance Name",
                    "Clause/Article": "Article Reference",
                    "Verbatim": "Full Text",
                    "High Level Synthesis": "Summary"
                },
                use_container_width=True
            )
            
    except Exception as e:
        st.error(f"Error fetching data from Airtable: {e}")
        st.stop()


def render_history_page():
    """Render the History page for viewing saved analysis sessions."""
    st.header("📚 Analysis History")
    
    # Import Firebase manager
    from firebase_module import create_firebase_manager
    
    firebase_manager = create_firebase_manager()
    
    if not firebase_manager.is_connected():
        st.warning("⚠️ Firebase not connected. History features are not available.")
        st.info("Please configure Firebase credentials to view analysis history.")
        return
    
    # Get all sessions
    sessions = firebase_manager.get_all_sessions()
    
    if not sessions:
        st.info("📭 No analysis sessions found in history.")
        st.info("Run an analysis from the Application page to create your first session.")
        return
    
    # Create session selector
    st.subheader("Select Session to View")
    
    # Create options for dropdown (latest first)
    session_options = []
    for session in sessions:
        session_name = session.get('session_name', 'Unknown')
        created_at = session.get('created_at', 'Unknown')
        platform = session.get('platform', 'Unknown')
        search_type = session.get('search_type', 'Unknown')
        video_count = session.get('video_count', 0)
        
        # Format the display text
        display_text = f"{session_name} ({platform}, {search_type}, {video_count} videos, {created_at[:10]})"
        session_options.append((display_text, session))
    
    if session_options:
        selected_option = st.selectbox(
            "Choose a session:",
            options=[opt[0] for opt in session_options],
            index=0
        )
        
        # Find the selected session
        selected_session = None
        for display_text, session in session_options:
            if display_text == selected_option:
                selected_session = session
                break
        
        if selected_session:
            # Display session details
            st.subheader(f"Session: {selected_session.get('session_name', 'Unknown')}")
            
            # Session metadata
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Platform", selected_session.get('platform', 'Unknown'))
            with col2:
                st.metric("Search Type", selected_session.get('search_type', 'Unknown'))
            with col3:
                st.metric("Videos Analyzed", selected_session.get('video_count', 0))
            with col4:
                st.metric("Created", selected_session.get('created_at', 'Unknown')[:10])
            
            # Display analysis results
            analysis_data = selected_session.get('analysis_data', {})
            videos = analysis_data.get('videos', [])
            
            if videos:
                st.subheader("Analysis Results")
                
                # Create tabs for different views
                tab1, tab2 = st.tabs(["Summary Table", "Detailed Analysis"])
                
                with tab1:
                    render_results_summary(videos)
                
                with tab2:
                    render_detailed_analysis(videos)
                
                # Delete session option
                st.subheader("Session Management")
                if st.button("🗑️ Delete This Session", type="secondary"):
                    if st.checkbox("I confirm I want to delete this session"):
                        session_name = selected_session.get('session_name')
                        if firebase_manager.delete_session(session_name):
                            st.success("Session deleted successfully!")
                            st.rerun()
            else:
                st.warning("No video data found in this session.")


def render_settings_page():
    """Render the Settings page for prompt customization."""
    st.header("Application Settings")
    st.write("Configure the prompt for dark pattern detection here.")
    
    st.info("🔐 API keys are configured via environment variables and cannot be edited from this interface for security reasons.")
    
    st.session_state.gemini_prompt = st.text_area(
        "Prompt for Dark Pattern Detection:",
        value=st.session_state.gemini_prompt,
        height=400,
        key="settings_gemini_prompt",
        help="Customize the analysis prompt that will be sent to the Gemini AI model for dark pattern detection."
    )
    
    st.info("✅ Prompt settings are saved automatically. Switch to 'Application' to use them.")


def create_search_interface():
    """Create the main search interface with session name input."""
    # Session name input
    st.subheader("📝 Session Configuration")
    session_name = st.text_input(
        "Enter Session Name:",
        placeholder="e.g., influencer-marketing-analysis-2024",
        help="Provide a unique name for this analysis session. This will be used to save and retrieve results from Firebase."
    )
    
    if not session_name:
        st.warning("⚠️ Please enter a session name to continue.")
        return None
    
    # Select search mode
    search_mode = st.radio(
        "Select Search Mode:",
        ("Search by Keywords/Hashtags", "Analyze Video URLs")
    )

    # Conditional inputs based on search mode
    keywords_hashtags = None
    max_results_to_fetch = 10  # Default value, will be overridden for keyword search
    video_urls_input = None

    if search_mode == "Search by Keywords/Hashtags":
        keywords_hashtags = st.text_area("Enter keywords/hashtags (comma-separated or multi-line):", height=100)
        max_results_to_fetch = st.number_input(
            "Number of videos to fetch (in multiples of 10):",
            min_value=10,
            value=10,
            step=10,
            help="Set the total number of videos to retrieve from search results. Must be a multiple of 10."
        )
    else:  # Analyze Video URLs
        video_urls_input = st.text_area(
            "Enter Video URLs (one per line, up to 10):",
            height=200,
            help="Paste video URLs here. Each URL should be on a new line. Max 10 URLs. Supports both YouTube and TikTok URLs."
        )

    # Platform selection
    platform_options = st.multiselect("Select Platform(s):", ["YouTube", "TikTok"], default=["YouTube"])

    # Input for channels to exclude - now with default values
    channels_to_exclude = st.text_area(
        "Enter channels/creators to exclude (comma-separated or multi-line):",
        height=68,
        value="@shiseido, @shiseidousa, @ShiseidoAsia, @ShiseidoKorea, @SHISEIDOofficial"
    )

    return {
        "session_name": session_name,
        "search_mode": search_mode,
        "keywords_hashtags": keywords_hashtags,
        "max_results_to_fetch": max_results_to_fetch,
        "video_urls_input": video_urls_input,
        "platform_options": platform_options,
        "channels_to_exclude": channels_to_exclude
    }


def render_tiktok_placeholder():
    """Render TikTok placeholder section."""
    st.subheader("TikTok Search Results (Coming Soon!)")
    st.info("TikTok search and data extraction functionality is not yet implemented.")
    st.write("Due to the complexities of TikTok's API and scraping, this will require further development.")


def render_results_summary(video_results):
    """Render the summary table of analyzed videos."""
    st.subheader("Summary of Analyzed Videos")
    summary_df = pd.DataFrame(video_results)
    # Display all relevant columns, including the detailed analysis
    display_cols = ["Title", "Channel", "URL", "Dark Pattern Analysis", "Overall Confidence Score", "Product Names"]
    st.dataframe(summary_df[display_cols], use_container_width=True)


def render_detailed_analysis(video_results):
    """Render the detailed analysis view with expandable sections."""
    st.subheader("Detailed Dark Pattern Analysis (Collapsible View)")
    
    # Ensure the list is not empty before creating selectbox
    if video_results:
        video_titles = [f"{idx+1}. {video['Title']} ({video['Channel']})" for idx, video in enumerate(video_results)]
        selected_video_index = st.selectbox("Select a video for detailed dark pattern analysis:", options=range(len(video_titles)), format_func=lambda x: video_titles[x])

        if selected_video_index is not None:
            # Access data from session state
            selected_video_data = video_results[selected_video_index]
            st.markdown(f"### Details for: {selected_video_data['Title']}")
            st.write(f"**URL:** {selected_video_data['URL']}")
            st.write(f"**Overall Confidence Score:** {selected_video_data['Overall Confidence Score']}")
            st.write(f"**Product Names:** {selected_video_data['Product Names']}")

            dark_pattern_details = selected_video_data.get("Raw Dark Pattern Analysis", [])
            if dark_pattern_details:
                for dp_item in dark_pattern_details:
                    category = dp_item.get("category", "N/A")
                    excerpt = dp_item.get("excerpt", "N/A")
                    section_type = dp_item.get("sectionType", "N/A")
                    reasoning = dp_item.get("reasoning", "N/A")
                    confidence = dp_item.get("confidenceScore", "N/A")
                    regulatory_refs = dp_item.get("regulatoryViolationReference", [])

                    with st.expander(f"Category: {category} (Confidence: {confidence})"):
                        st.write(f"**Excerpt:** '{excerpt}'")
                        st.write(f"**Section Type:** {section_type}")
                        st.write(f"**Reasoning:** {reasoning}")
                        
                        if regulatory_refs:
                            st.write("**Regulatory Violations:**")
                            for ref in regulatory_refs:
                                law = ref.get("lawGuidance", "N/A")
                                article = ref.get("articleClause", "N/A")
                                synthesis = ref.get("highLevelSynthesis", "N/A")
                                st.markdown(f"- **Law/Guidance:** {law}, **Article/Clause:** {article}")
                                st.markdown(f"  **Synthesis:** {synthesis}")
                        else:
                            st.write("No specific regulatory violations identified for this pattern.")
            else:
                st.info("No dark patterns detected for this video.")
    else:
        st.info("No videos available for detailed analysis. Run a search first.")


def render_results_tabs(video_results):
    """Render results in tabs (Summary and Detailed Analysis)."""
    if video_results:
        # Create tabs for displaying results
        tab1, tab2 = st.tabs(["Summary Table", "Detailed Analysis"])

        with tab1:
            render_results_summary(video_results)

        with tab2:
            render_detailed_analysis(video_results)
    else:
        st.info("No videos found or analyzed based on your input.")


def render_data_storage_placeholder():
    """Render the data storage placeholder section."""
    st.subheader("Data Storage (Firebase - Optional)")
    st.info("Data storage to Firebase will be implemented after dark pattern detection. The application will function without these credentials if not provided.")
    st.success("Search and initial data extraction complete! Proceeding with next steps...")