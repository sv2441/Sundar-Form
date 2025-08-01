import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
import re
import os
from urllib.parse import urlparse, parse_qs
import json # Import json for handling structured responses
import requests # Import requests for API calls
from pyairtable import Table

# Function to fetch all records from Airtable with pagination
def fetch_all_records(base_id, table_id, api_key):
    """Helper function to fetch all records with pagination"""
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

# Function to extract video ID from YouTube URL
def extract_video_id(url):
    """
    Extracts the YouTube video ID from a given URL.
    Supports standard YouTube URLs (watch?v=), short URLs (youtu.be/), and Shorts URLs.
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

# Function to call Gemini API for dark pattern detection and product extraction
def analyze_with_gemini(text_content, prompt, api_key):
    """
    Sends text content to Gemini 2.5 Flash API for dark pattern analysis and product name extraction.
    Expects a structured JSON response.
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


# --- Streamlit UI Setup ---
st.set_page_config(layout="wide", page_title="Dark Pattern Detector")

st.title("Dark Pattern Detector for Video Content")

# Initialize session state for prompt if not already set
if 'gemini_prompt' not in st.session_state:
    st.session_state.gemini_prompt = """Here is your revised detailed analysis prompt, structured for rigorous evaluation and formatted to yield a JSON object output. This version incorporates all your requirements — including detailed issue flags, excerpts, timestamps/visual cues, explanations, confidence scoring, and product name extraction:
🔍 Prompt: Detailed Analysis for Dark Patterns and Deceptive Practices
Analyze the provided text, transcript, and/or video content for the presence of dark patterns, manipulative language, or deceptive advertising practices.
For each of the following categories, identify and extract specific excerpts from the description, transcript, or captions that demonstrate the issue. Explain why each excerpt qualifies as a dark pattern or deceptive technique.

🔎 Categories to Evaluate:
Implied Scarcity / Sale Mention
Look for language that creates urgency, such as "limited time," "almost gone," "backup stock," or countdowns.
Provide quote(s) and describe how urgency is being manufactured.
Lack of Clear Disclosure
Determine if any form of sponsorship, advertising, or paid partnership is disclosed.
If disclosed, assess whether it is clear, prominent, and upfront — or buried/ambiguous (e.g., in hashtags or at the end).
Vague or Ambiguous Language
Flag any unclear promotional terms like "collab," "sp," "ambassador," or "partner" when used without also stating "Ad," "Sponsored," or "Paid Promotion."
Explain why the term may mislead viewers.
Inconsistent or Incomplete Disclosures
Evaluate whether disclosures are missing in certain formats (e.g., not repeated in long-form videos, livestreams, or multi-part stories).
Identify omissions or lack of reinforcement.
Blurring Editorial and Advertising Content
Identify sections where product promotion is presented as a personal review, opinion, or recommendation without clearly differentiating it from paid promotion.
Look for emotional appeals or personal anecdotes used to mask advertising intent.

📌 Output Requirements:
For each issue, include:
- Excerpt (quoted from transcript/description/caption)
- Section Type (transcript, caption, or description)
- Reasoning (why this qualifies as a dark pattern)
- (Optional) Timestamps or visual cues if from video
- Confidence Score (0–100) — estimate how likely it is this is a deceptive tactic

Additionally, for each identified dark pattern, identify any relevant regulatory violations from the 'Law / Guidance' section provided below. For each applicable violation, include the 'Law / Guidance', 'Article / Clause', and 'High-Level Synthesis' from the regulatory text. If no specific violation applies, indicate 'N/A' for the violation details.

Extract and list all product names mentioned.

Regulatory Violations Reference:
Law / Guidance | Article / Clause | Verbatim Text | High-Level Synthesis
---|---|---|---
Code de la consommation | Art. L121‑1 | "Les pratiques commerciales déloyales sont interdites. Une pratique commerciale est déloyale lorsqu'elle est contraire aux exigences de la diligence professionnelle et qu'elle altère ou est susceptible d'altérer de manière substantielle le comportement économique du consommateur normalement informé et raisonnablement attentif et avisé, à l'égard d'un bien ou d'un service." | • Prohibits unfair or misleading practices<br>• Applies to actions that materially affect consumer decisions, including deceptive urgency or omissions
Code de la consommation | Art. L121‑1‑1 | "Sont réputées trompeuses au sens de l'article L. 121‑1 les pratiques commerciales qui ont pour objet : (...) 5° De proposer l'achat de produits… à un prix indiqué sans révéler les raisons plausibles… quantités… raisonnables compte tenu du produit… de l'ampleur de la publicité… et du prix proposé" | • Defines specific deceptive practices<br>• Clause 5 prohibits false scarcity or misrepresenting price/availability without reasonable basis
Loi n° 2023‑451 (9 juin 2023) | Art. 1 | Defines "influence commerciale" as: "les personnes physiques ou morales qui, à titre onéreux, mobilisent leur notoriété… pour communiquer… des contenus visant à faire la promotion, directement ou indirectement, de biens… par voie électronique." | • Establishes legal definition of influencer marketing<br>• Covers paid promotions via social media
Loi n° 2023‑451 (9 juin 2023) | Art. 4 & 5 (via ordonnance 6 nov 2024) | Requires influencers to use clear labels such as "publicité" or "collaboration commerciale", visible and adapted to the format. | • Mandates explicit disclosure of commercial intent<br>• Labels must be visible, understandable, and persistent across formats
Sanctions | Non-compliance | Non-compliance may result in penalties enforced by DGCCRF (fines, injunctions), covering any format or platform. | • Provides enforcement mechanisms<br>• Applies across all influencer content formats
ARPP "Communication Publicitaire Numérique" | Art. b2, §1‑2 | "Identification of Advertiser:… must be easily identifiable… advertising presentations… should avoid confusion… conditions… must be clearly specified… notes must be immediately visible… legible… intelligible… not immersed under other information." | • Demands clear advertiser identification<br>• Requires disclosures to be visible, legible, and not obscured by other content
ARPP "Communication Publicitaire Numérique" | Section 5 – Comfort of use | "Digital advertising communication must respect… comfort… not be overlaying… autoplay videos… should not have audio… enabled by default." | • Ensures ads don't disrupt user experience (UX)<br>• Prevents deceptive integration of ads into user interface

Output as a valid JSON object with the following keys:
{
  "darkPatternAnalysis": [
    {
      "category": "Implied Scarcity / Sale Mention",
      "excerpt": "...",
      "sectionType": "transcript",
      "reasoning": "...",
      "confidenceScore": 85,
      "regulatoryViolationReference": [
        {
          "lawGuidance": "Code de la consommation",
          "articleClause": "Art. L121‑1",
          "highLevelSynthesis": "Prohibits unfair or misleading practices; Applies to actions that materially affect consumer decisions, including deceptive urgency or omissions"
        }
      ]
    },
    {
      "category": "Lack of Clear Disclosure",
      "excerpt": "...",
      "sectionType": "description",
      "reasoning": "...",
      "confidenceScore": 95,
      "regulatoryViolationReference": [
        {
          "lawGuidance": "Loi n° 2023‑451 (9 juin 2023)",
          "articleClause": "Art. 4 & 5 (via ordonnance 6 nov 2024)",
          "highLevelSynthesis": "Mandates explicit disclosure of commercial intent; Labels must be visible, understandable, and persistent across formats"
        },
        {
          "lawGuidance": "ARPP "Communication Publicitaire Numérique"",
          "articleClause": "Art. b2, §1‑2",
          "highLevelSynthesis": "Demands clear advertiser identification; Requires disclosures to be visible, legible, and not obscured by other content"
        }
      ]
    },
    ...
  ],
  "overallConfidenceScore": 92, # Changed to avoid conflict with individual confidenceScore
  "productNames": [
    "Elixir Brightening UV Protector",
    "Chaseedo Elixir",
    "Loxitan Illuminating",
    "La Roche-Posay",
    "Skin Aqua Tone Up UV Essence"
  ]
}
"""
# Initialize analyzed_youtube_results in session state if it doesn't exist
if 'analyzed_youtube_results' not in st.session_state:
    st.session_state['analyzed_youtube_results'] = []

# Sidebar for navigation
st.sidebar.title("Navigation")
selected_page = st.sidebar.radio("Go to", ["Application", "Settings", "Dark Pattern Reference"])

if selected_page == "Dark Pattern Reference":
    st.header("Dark Pattern Reference Tables")
    
    try:
        airtable_api_key = st.secrets["api_keys"]["airtable_api_key"]
        airtable_base_id = st.secrets["airtable"]["base_id"]
        
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
            
    except KeyError as e:
        st.error(f"❌ Missing Airtable configuration in secrets.toml: {e}")
        st.info("Please ensure your .streamlit/secrets.toml file contains the required Airtable API key and base ID under [api_keys] and [airtable] sections.")
        st.stop()
    except Exception as e:
        st.error(f"Error fetching data from Airtable: {e}")
        st.stop()

elif selected_page == "Settings":
    st.header("Application Settings")
    st.write("Configure the prompt for dark pattern detection here.")
    
    st.info("🔐 API keys are configured in the secrets.toml file and cannot be edited from this interface for security reasons.")
    
    st.session_state.gemini_prompt = st.text_area(
        "Prompt for Dark Pattern Detection:",
        value=st.session_state.gemini_prompt,
        height=400,
        key="settings_gemini_prompt",
        help="Customize the analysis prompt that will be sent to the Gemini AI model for dark pattern detection."
    )
    
    st.info("✅ Prompt settings are saved automatically. Switch to 'Application' to use them.")

elif selected_page == "Application":
    # Retrieve API keys from secrets and prompt from session state
    try:
        youtube_api_key = st.secrets["api_keys"]["youtube_api_key"]
        gemini_api_key = st.secrets["api_keys"]["gemini_api_key"]
    except KeyError as e:
        st.error(f"❌ Missing API key in secrets.toml: {e}")
        st.info("Please ensure your .streamlit/secrets.toml file contains the required API keys under [api_keys] section.")
        st.stop()
    
    gemini_prompt = st.session_state.gemini_prompt

    # Select search mode
    search_mode = st.radio(
        "Select Search Mode:",
        ("Search by Keywords/Hashtags", "Analyze YouTube Video URLs")
    )

    # Conditional inputs based on search mode
    keywords_hashtags = None
    max_results_to_fetch = 10 # Default value, will be overridden for keyword search
    youtube_video_urls_input = None

    if search_mode == "Search by Keywords/Hashtags":
        keywords_hashtags = st.text_area("Enter keywords/hashtags (comma-separated or multi-line):", height=100)
        max_results_to_fetch = st.number_input(
            "Number of YouTube videos to fetch (in multiples of 10):",
            min_value=10,
            value=10,
            step=10,
            help="Set the total number of videos to retrieve from YouTube search results. Must be a multiple of 10."
        )
    else: # Analyze YouTube Video URLs
        youtube_video_urls_input = st.text_area(
            "Enter YouTube Video URLs (one per line, up to 10):",
            height=200,
            help="Paste YouTube video URLs here. Each URL should be on a new line. Max 10 URLs."
        )

    # Option to select platform (still relevant for overall app, but YouTube is implied for URL mode)
    if search_mode == "Analyze YouTube Video URLs":
        platform_options = st.multiselect("Select Platform(s):", ["YouTube", "TikTok"], default=["YouTube"], disabled=True)
    else:
        platform_options = st.multiselect("Select Platform(s):", ["YouTube", "TikTok"], default=["YouTube"])

    # Input for channels to exclude - now with default values
    channels_to_exclude = st.text_area(
        "Enter channels/creators to exclude (comma-separated or multi-line):",
        height=68,
        value="@shiseido, @shiseidousa, @ShiseidoAsia, @ShiseidoKorea, @SHISEIDOofficial"
    )

    # Button to start search and analysis
    if st.button("Start Search and Analysis"):
        st.info("Starting search and analysis...")

        # --- YouTube Search & Data Extraction ---
        if "YouTube" in platform_options or search_mode == "Analyze YouTube Video URLs":
            st.subheader("YouTube Results")

            if not youtube_api_key:
                st.warning("Please provide a YouTube Data API Key in the 'Settings' page to perform YouTube operations.")
            else:
                youtube = build('youtube', 'v3', developerKey=youtube_api_key)
                all_youtube_results = []
                exclude_channels_list = [c.strip().lower() for c in re.split(r'[\n,]', channels_to_exclude) if c.strip()]

                if search_mode == "Search by Keywords/Hashtags":
                    search_queries = [q.strip() for q in re.split(r'[\n,]', keywords_hashtags) if q.strip()]
                    if not search_queries:
                        st.warning("Please enter keywords/hashtags for search mode.")
                    else:
                        for query_term in search_queries:
                            if not query_term:
                                continue

                            st.write(f"Searching YouTube for: '{query_term}' (fetching {max_results_to_fetch} results)")
                            try:
                                request = youtube.search().list(
                                    q=query_term,
                                    part='snippet',
                                    type='video',
                                    maxResults=max_results_to_fetch
                                )
                                response = request.execute()

                                for item in response['items']:
                                    video_id = item['id']['videoId']
                                    title = item['snippet']['title']
                                    channel_title = item['snippet']['channelTitle']
                                    description = item['snippet']['description']
                                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                                    transcript_text = ""

                                    # Filter out excluded channels
                                    if channel_title.lower() in exclude_channels_list:
                                        st.info(f"Skipping video '{title}' from excluded channel '{channel_title}'.")
                                        continue

                                    # Extract transcripts (which includes captions)
                                    try:
                                        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                                        transcript_text = " ".join([t['text'] for t in transcript_list])
                                    except NoTranscriptFound:
                                        transcript_text = "No transcript found for this video."
                                    except TranscriptsDisabled:
                                        transcript_text = "Transcripts are disabled for this video."
                                    except Exception as e:
                                        transcript_text = f"Error fetching transcript: {e}"

                                    all_youtube_results.append({
                                        "Platform": "YouTube",
                                        "Video ID": video_id,
                                        "Title": title,
                                        "Channel": channel_title,
                                        "URL": video_url,
                                        "Description": description,
                                        "Transcript": transcript_text,
                                        "Dark Pattern Analysis": "N/A", # Placeholder for Gemini API
                                        "Overall Confidence Score": "N/A", # Placeholder for Gemini API
                                        "Product Names": "N/A" # Placeholder for extracted product names
                                    })
                            except Exception as e:
                                st.error(f"Error during YouTube search for '{query_term}': {e}")

                elif search_mode == "Analyze YouTube Video URLs":
                    if youtube_video_urls_input:
                        youtube_urls = [url.strip() for url in youtube_video_urls_input.split('\n') if url.strip()][:10]

                        if not youtube_urls:
                            st.warning("No valid YouTube URLs entered for analysis.")
                        else:
                            for url in youtube_urls:
                                video_id = extract_video_id(url)
                                standardized_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else url

                                if video_id:
                                    st.write(f"Analyzing YouTube video: '{standardized_url}'")
                                    try:
                                        videos_request = youtube.videos().list(
                                            part="snippet",
                                            id=video_id
                                        )
                                        videos_response = videos_request.execute()

                                        if videos_response['items']:
                                            item = videos_response['items'][0]
                                            title = item['snippet']['title']
                                            channel_title = item['snippet']['channelTitle']
                                            description = item['snippet']['description']
                                            
                                            transcript_text = ""

                                            if channel_title.lower() in exclude_channels_list:
                                                st.info(f"Skipping video '{title}' from excluded channel '{channel_title}'.")
                                            else:
                                                try:
                                                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                                                    transcript_text = " ".join([t['text'] for t in transcript_list])
                                                except NoTranscriptFound:
                                                    transcript_text = "No transcript found for this video."
                                                except TranscriptsDisabled:
                                                    transcript_text = "Transcripts are disabled for this video."
                                                except Exception as e:
                                                    transcript_text = f"Error fetching transcript: {e}"

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

            # --- Dark Pattern Detection (Gemini API Integration) ---
            if all_youtube_results and gemini_api_key:
                st.subheader("Performing Dark Pattern Analysis with Gemini...")
                for i, video_data in enumerate(all_youtube_results):
                    st.write(f"Analyzing video: {video_data['Title']}")
                    combined_text = f"Title: {video_data['Title']}\nDescription: {video_data['Description']}\nTranscript: {video_data['Transcript']}"

                    analysis_result = analyze_with_gemini(combined_text, gemini_prompt, gemini_api_key)

                    # Store the raw analysis result for detailed view
                    video_data["Raw Dark Pattern Analysis"] = analysis_result.get("darkPatternAnalysis", [])
                    video_data["Overall Confidence Score"] = analysis_result.get("overallConfidenceScore", "N/A")
                    video_data["Product Names"] = ", ".join(analysis_result.get("productNames", [])) if analysis_result.get("productNames") else "N/A"

                    # Format the detailed analysis for direct display in the DataFrame
                    formatted_analysis = ""
                    dark_pattern_analysis_details = video_data["Raw Dark Pattern Analysis"]
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
                        formatted_analysis = "Analysis data not in expected format." # Fallback if not list

                    video_data["Dark Pattern Analysis"] = formatted_analysis # This will now hold the detailed string for the table

                    all_youtube_results[i] = video_data
                st.success("Dark Pattern Analysis complete!")
            elif all_youtube_results and not gemini_api_key:
                st.warning("Gemini API Key not provided. Skipping Dark Pattern Analysis.")
            elif not all_youtube_results:
                st.info("No YouTube videos to analyze for dark patterns.")

            # Store results in session state for detailed view
            st.session_state['analyzed_youtube_results'] = all_youtube_results

            if st.session_state['analyzed_youtube_results']: # Use session state for displaying results
                # Create tabs for displaying results
                tab1, tab2 = st.tabs(["Summary Table", "Detailed Analysis"])

                with tab1:
                    st.subheader("Summary of Analyzed Videos")
                    summary_df = pd.DataFrame(st.session_state['analyzed_youtube_results'])
                    # Display all relevant columns, including the detailed analysis
                    display_cols = ["Title", "Channel", "URL", "Dark Pattern Analysis", "Overall Confidence Score", "Product Names"]
                    st.dataframe(summary_df[display_cols], use_container_width=True)

                with tab2:
                    st.subheader("Detailed Dark Pattern Analysis (Collapsible View)")
                    
                    # Ensure the list is not empty before creating selectbox
                    if st.session_state['analyzed_youtube_results']:
                        video_titles = [f"{idx+1}. {video['Title']} ({video['Channel']})" for idx, video in enumerate(st.session_state['analyzed_youtube_results'])]
                        selected_video_index = st.selectbox("Select a video for detailed dark pattern analysis:", options=range(len(video_titles)), format_func=lambda x: video_titles[x])

                        if selected_video_index is not None:
                            # Access data from session state
                            selected_video_data = st.session_state['analyzed_youtube_results'][selected_video_index]
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
            else:
                st.info("No YouTube videos found or analyzed based on your input.")

        # --- TikTok Search & Data Extraction (Placeholder) ---
        if "TikTok" in platform_options:
            st.subheader("TikTok Search Results (Coming Soon!)")
            st.info("TikTok search and data extraction functionality is not yet implemented.")
            st.write("Due to the complexities of TikTok's API and scraping, this will require further development.")

        # --- Filtering (already integrated into YouTube search for channels) ---
        # Further filtering options will be added when displaying the final table.

        # --- Compile & Store JSON (Firebase/Supabase - Placeholder) ---
        st.subheader("Data Storage (Firebase/Supabase - Optional)")
        st.info("Data storage to Firebase and Supabase will be implemented after dark pattern detection. The application will function without these credentials if not provided.")

        st.success("Search and initial data extraction complete! Proceeding with next steps...")
