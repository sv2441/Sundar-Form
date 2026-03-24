# Dark Pattern Detector - Complete Documentation

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Application Architecture](#application-architecture)
3. [Application Flow](#application-flow)
4. [Module Analysis](#module-analysis)
5. [Data Flow Diagrams](#data-flow-diagrams)
6. [Prompts and AI Integration](#prompts-and-ai-integration)
7. [API Integrations](#api-integrations)
8. [Database Schema](#database-schema)
9. [User Workflows](#user-workflows)
10. [Technical Stack](#technical-stack)

---

## Executive Summary

The **Dark Pattern Detector** is a comprehensive Streamlit-based application designed to identify and analyze dark patterns and deceptive advertising practices in video content from YouTube and TikTok platforms. The application leverages AI-powered analysis using Google's Gemini 2.0 Flash model to detect manipulative marketing tactics used by influencers, with a specific focus on French consumer protection regulations.

### Key Features
- **Multi-Platform Support**: Analyzes content from YouTube and TikTok
- **Dual Search Modes**: Keyword/hashtag search or direct URL analysis
- **AI-Powered Analysis**: Uses Gemini 2.0 Flash for dark pattern detection
- **Regulatory Compliance**: Maps violations to French consumer protection laws
- **Persistent Storage**: Firebase integration for session management
- **Reference Database**: Airtable integration for dark pattern taxonomy
- **Transcript Extraction**: Automatic transcript generation for comprehensive analysis

---

## Application Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     STREAMLIT APPLICATION                    │
│                         (app.py)                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ├─────────────────────────────────┐
                              │                                 │
                    ┌─────────▼─────────┐           ┌──────────▼──────────┐
                    │  Configuration    │           │   UI Components     │
                    │   (config.py)     │           │ (ui_components.py)  │
                    └───────────────────┘           └─────────────────────┘
                              │                                 │
        ┌─────────────────────┼─────────────────────────────────┤
        │                     │                                 │
┌───────▼────────┐  ┌────────▼────────┐  ┌──────────▼─────────┐
│ YouTube Module │  │  TikTok Module  │  │  Firebase Module   │
│(youtube_module)│  │ (tiktok_module) │  │ (firebase_module)  │
└────────────────┘  └─────────────────┘  └────────────────────┘
        │                     │                      │
        └─────────────────────┼──────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Utility Functions│
                    │    (utils.py)     │
                    └───────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐  ┌────────▼────────┐  ┌────────▼────────┐
│  YouTube API   │  │   Gemini API    │  │  Airtable API   │
└────────────────┘  └─────────────────┘  └─────────────────┘
```

### Modular Architecture

The application follows a **modular architecture** with clear separation of concerns:

#### 1. **Core Application Layer** (`app.py`)
- Orchestrates all modules
- Manages application lifecycle
- Handles routing between pages
- Coordinates data flow between modules

#### 2. **Configuration Layer** (`config.py`)
- Manages environment variables
- Stores default prompts
- Initializes session state
- Handles API key retrieval

#### 3. **Presentation Layer** (`ui_components.py`)
- Renders all UI elements
- Manages user interactions
- Displays analysis results
- Handles navigation

#### 4. **Business Logic Layer**
- **YouTube Module** (`youtube_module.py`): YouTube-specific operations
- **TikTok Module** (`tiktok_module.py`): TikTok-specific operations
- **Utils** (`utils.py`): Shared utility functions

#### 5. **Data Persistence Layer** (`firebase_module.py`)
- Firebase Firestore integration
- CRUD operations for sessions
- Data serialization/deserialization

---

## Application Flow

### Main Application Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION START                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Setup Page Configuration (setup_page_config)            │
│     - Set page layout to wide                               │
│     - Set page title                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Initialize Session State (initialize_session_state)     │
│     - Load default Gemini prompt                            │
│     - Initialize analyzed_results list                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Create Navigation (create_navigation)                   │
│     - Display sidebar with page options                     │
│     - Return selected page                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Route to Selected Page                                  │
│     ├─ Dark Pattern Reference                               │
│     ├─ History                                              │
│     ├─ Settings                                             │
│     └─ Application (Main Analysis Page)                     │
└─────────────────────────────────────────────────────────────┘
```

### Analysis Workflow (Application Page)

```
┌─────────────────────────────────────────────────────────────┐
│  1. Get API Keys                                            │
│     - Retrieve YouTube API Key from environment             │
│     - Retrieve Gemini API Key from environment              │
│     - Display warnings if missing                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Create Search Interface                                 │
│     - Session Name Input                                    │
│     - Search Mode Selection (Keywords vs URLs)              │
│     - Platform Selection (YouTube/TikTok)                   │
│     - Exclusion Filters                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  3. User Clicks "Start Search and Analysis"                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Initialize Firebase Manager                             │
│     - Connect to Firestore                                  │
│     - Prepare for data persistence                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Platform-Specific Processing                            │
│     ┌──────────────────┐         ┌──────────────────┐       │
│     │  YouTube Selected│         │  TikTok Selected │       │
│     └────────┬─────────┘         └────────┬─────────┘       │
│              │                            │                 │
│              ▼                            ▼                 │
│     ┌────────────────────┐      ┌────────────────────┐     │
│     │ Create YouTube     │      │ Create TikTok      │     │
│     │ Analyzer           │      │ Analyzer           │     │
│     └────────┬───────────┘      └────────┬───────────┘     │
│              │                            │                 │
│              ▼                            ▼                 │
│     ┌────────────────────┐      ┌────────────────────┐     │
│     │ Search/Analyze     │      │ Search/Analyze     │     │
│     │ Videos             │      │ Videos             │     │
│     └────────┬───────────┘      └────────┬───────────┘     │
│              │                            │                 │
│              ▼                            ▼                 │
│     ┌────────────────────┐      ┌────────────────────┐     │
│     │ Extract Metadata   │      │ Extract Metadata   │     │
│     │ & Transcripts      │      │ & Transcripts      │     │
│     └────────┬───────────┘      └────────┬───────────┘     │
│              │                            │                 │
│              └────────────┬───────────────┘                 │
│                           │                                 │
└───────────────────────────┼─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  6. Dark Pattern Analysis (For Each Video)                  │
│     - Combine title, description, transcript                │
│     - Send to Gemini API with analysis prompt               │
│     - Parse structured JSON response                        │
│     - Extract dark patterns, confidence scores, products    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  7. Store Results in Session State                          │
│     - Update analyzed_results list                          │
│     - Format analysis for display                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  8. Save to Firebase (If Connected)                         │
│     - Prepare analysis data                                 │
│     - Save to 'influencer-marketing' collection             │
│     - Store session metadata                                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  9. Display Results                                         │
│     - Summary Table Tab                                     │
│     - Detailed Analysis Tab                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Module Analysis

### 1. `app.py` - Main Application Orchestrator

**Purpose**: Central orchestration point for the entire application.

**Key Functions**:
- `main()`: Entry point that coordinates all operations

**Flow**:
1. Sets up page configuration
2. Initializes session state
3. Creates navigation
4. Routes to appropriate page based on user selection
5. For Application page:
   - Retrieves API keys
   - Creates search interface
   - Processes user input
   - Orchestrates platform-specific analyzers
   - Manages Firebase operations
   - Displays results

**Dependencies**:
- All utility modules
- Streamlit framework
- Environment variables

---

### 2. `config.py` - Configuration Management

**Purpose**: Centralized configuration and environment management.

**Key Functions**:

#### `get_default_gemini_prompt()`
Returns the comprehensive dark pattern analysis prompt with:
- Category definitions (Implied Scarcity, Lack of Clear Disclosure, etc.)
- Output requirements (excerpts, timestamps, confidence scores)
- Regulatory violation mapping
- Structured JSON schema

#### `initialize_session_state()`
Initializes Streamlit session state with:
- `gemini_prompt`: Default analysis prompt
- `analyzed_results`: Empty list for storing results

#### `get_api_keys()`
Retrieves API keys from environment:
- `YOUTUBE_API_KEY`
- `GEMINI_API_KEY`
- Displays warnings if missing

#### `get_airtable_config()`
Retrieves Airtable configuration:
- `AIRTABLE_API_KEY`
- `AIRTABLE_BASE_ID`

**Environment Variables Required**:
```
YOUTUBE_API_KEY=your_youtube_api_key
GEMINI_API_KEY=your_gemini_api_key
AIRTABLE_API_KEY=your_airtable_api_key
AIRTABLE_BASE_ID=your_airtable_base_id
FIREBASE_SERVICE_ACCOUNT_PATH=path/to/firebase/credentials.json
```

---

### 3. `ui_components.py` - User Interface Layer

**Purpose**: All UI rendering and user interaction handling.

**Key Functions**:

#### `setup_page_config()`
- Sets page layout to wide
- Sets page title

#### `create_navigation()`
- Creates sidebar navigation
- Returns selected page

#### `render_dark_pattern_reference()`
- Fetches data from Airtable
- Displays two tabs:
  - **Influencer Dark Patterns**: Classification of dark pattern types
  - **Law/Guidance Clauses**: French regulatory framework

#### `render_history_page()`
- Fetches all sessions from Firebase
- Displays session selector
- Shows session metadata (platform, search type, video count, date)
- Renders analysis results
- Provides session deletion functionality

#### `render_settings_page()`
- Allows customization of Gemini analysis prompt
- Displays API key information

#### `create_search_interface()`
Returns search parameters:
- `session_name`: User-defined session identifier
- `search_mode`: "Search by Keywords/Hashtags" or "Analyze Video URLs"
- `keywords_hashtags`: Search terms
- `max_results_to_fetch`: Number of videos to retrieve
- `video_urls_input`: Direct URLs for analysis
- `platform_options`: Selected platforms (YouTube/TikTok)
- `channels_to_exclude`: Channels to filter out

#### `render_results_tabs()`
Displays analysis results in two tabs:
- **Summary Table**: Overview of all analyzed videos
- **Detailed Analysis**: Expandable sections for each dark pattern

---

### 4. `youtube_module.py` - YouTube Operations

**Purpose**: Handle all YouTube-specific operations.

**Class**: `YouTubeAnalyzer`

**Key Methods**:

#### `__init__(api_key)`
- Initializes YouTube Data API client
- Stores API key

#### `search_videos_by_keywords(keywords_hashtags, max_results, exclude_channels)`
**Flow**:
1. Parse keywords/hashtags
2. For each search query:
   - Call YouTube Search API
   - Retrieve video metadata (title, channel, description)
   - Extract transcript using YouTubeTranscriptApi
   - Filter excluded channels
   - Compile results

**Returns**: List of video data dictionaries

#### `analyze_video_urls(youtube_video_urls_input, exclude_channels)`
**Flow**:
1. Parse and validate URLs
2. Extract video IDs
3. For each video:
   - Call YouTube Videos API
   - Retrieve metadata
   - Extract transcript
   - Filter excluded channels
   - Compile results

**Returns**: List of video data dictionaries

#### `_extract_transcript(video_id)`
**Flow**:
1. Attempt to fetch transcript using YouTubeTranscriptApi
2. Handle exceptions:
   - NoTranscriptFound
   - TranscriptsDisabled
   - General errors

**Returns**: Transcript text or error message

#### `analyze_dark_patterns(video_results, gemini_prompt, gemini_api_key)`
**Flow**:
1. For each video:
   - Combine title, description, transcript
   - Call `analyze_with_gemini()`
   - Parse JSON response
   - Store raw analysis
   - Format for display
   - Update video data

**Returns**: Updated video results with analysis

---

### 5. `tiktok_module.py` - TikTok Operations

**Purpose**: Handle all TikTok-specific operations with multiple fallback methods.

**Class**: `TikTokAnalyzer`

**Key Features**:
- Multiple extraction methods with fallback
- Whisper-based transcript extraction
- yt-dlp integration
- Web scraping capabilities

**Key Methods**:

#### `__init__(api_key=None)`
- Initializes HTTP session
- Loads Whisper model for transcript extraction
- Sets up user agent headers

#### `_extract_tiktok_video_id(url)`
Handles various TikTok URL formats:
- `tiktok.com/@username/video/123456`
- `tiktok.com/v/123456`
- `vm.tiktok.com/abc123`
- `tiktok.com/t/abc123`

#### `_download_and_extract_video_data(url)`
**Comprehensive extraction method**:
1. Downloads video using yt-dlp
2. Extracts metadata from JSON
3. Extracts audio in WAV format
4. Transcribes audio using Whisper
5. Reads description file
6. Compiles comprehensive data

**Returns**: Complete video data including transcript

#### `_try_yt_dlp_extraction(url)`
**Metadata-only extraction**:
1. Checks yt-dlp availability
2. Runs `yt-dlp --dump-json --no-download`
3. Parses JSON output

**Returns**: Video metadata without downloading

#### `_try_web_scraping(url)`
**Web scraping fallback**:
1. Fetches HTML content
2. Searches for SIGI_STATE JSON data
3. Parses TikTok's internal data structure
4. Falls back to basic HTML parsing

**Returns**: Extracted video data

#### `_parse_tiktok_json(json_data, url)`
Navigates TikTok's complex JSON structure:
- Looks for ItemModule
- Extracts video data, stats, author info

#### `_extract_basic_info_from_html(html_content, url)`
**Robust HTML parsing**:
- Extracts title from multiple sources (meta tags, title tag, headings)
- Extracts description from og:description
- Extracts creator from URL or HTML
- Attempts to extract view/like/comment counts

#### `analyze_video_urls(tiktok_video_urls_input, exclude_creators)`
**Multi-method extraction flow**:
1. Parse URLs
2. For each URL:
   - **Method 1**: Try comprehensive download + Whisper transcription
   - **Method 2**: Try yt-dlp metadata extraction
   - **Method 3**: Try web scraping
   - Filter excluded creators
   - Compile results with extraction method info

**Returns**: List of video data with transcripts

#### `analyze_dark_patterns(video_results, gemini_prompt, gemini_api_key)`
Similar to YouTube module, analyzes TikTok videos for dark patterns.

---

### 6. `firebase_module.py` - Data Persistence

**Purpose**: Manage Firebase Firestore operations for session persistence.

**Class**: `FirebaseManager`

**Key Methods**:

#### `__init__()`
- Initializes Firebase Admin SDK
- Connects to Firestore

#### `_initialize_firebase()`
**Flow**:
1. Check if Firebase already initialized
2. Retrieve service account path from environment
3. Validate file existence
4. Initialize Firebase Admin SDK
5. Get Firestore client

#### `save_analysis_session(sessionName, analysis_data, search_type, platform, created_by)`
**Flow**:
1. Prepare session data:
   - sessionName
   - search_type (keywords/urls)
   - platform (YouTube/TikTok/Mixed)
   - analysis_data (videos, scores, etc.)
   - created_at (ISO timestamp)
   - video_count
   - overall_confidence_score
2. Save to 'influencer-marketing' collection
3. Use sessionName as document ID

**Returns**: Document ID or None

#### `get_all_sessions()`
**Flow**:
1. Query 'influencer-marketing' collection
2. Order by created_at descending
3. Convert documents to dictionaries
4. Add document ID to each session

**Returns**: List of session dictionaries

#### `get_session_by_name(sessionName)`
**Flow**:
1. Query specific document by sessionName
2. Check if exists
3. Convert to dictionary

**Returns**: Session data or None

#### `delete_session(sessionName)`
**Flow**:
1. Get document reference
2. Delete document
3. Display success message

**Returns**: Boolean success status

#### `is_connected()`
Checks if Firestore client is initialized.

**Returns**: Boolean

---

### 7. `utils.py` - Shared Utilities

**Purpose**: Common utility functions used across modules.

**Key Functions**:

#### `fetch_all_records(base_id, table_id, api_key)`
**Purpose**: Fetch all records from Airtable with pagination.

**Flow**:
1. Set up authorization headers
2. Make initial request
3. Collect records
4. Handle pagination with offset
5. Continue until no more records

**Returns**: List of all records

#### `extract_video_id(url)`
**Purpose**: Extract YouTube video ID from various URL formats.

**Supported Formats**:
- YouTube Shorts: `youtube.com/shorts/VIDEO_ID`
- Standard: `youtube.com/watch?v=VIDEO_ID`
- Short URL: `youtu.be/VIDEO_ID`

**Returns**: Video ID or None

#### `analyze_with_gemini(text_content, prompt, api_key)`
**Purpose**: Send content to Gemini 2.0 Flash API for analysis.

**Flow**:
1. Define structured response schema
2. Prepare chat history with user prompt
3. Create payload with:
   - contents (chat history)
   - generationConfig (JSON response with schema)
4. Send POST request to Gemini API
5. Parse JSON response
6. Extract structured data

**Response Schema**:
```json
{
  "darkPatternAnalysis": [
    {
      "category": "string",
      "excerpt": "string",
      "sectionType": "string",
      "reasoning": "string",
      "confidenceScore": integer,
      "regulatoryViolationReference": [
        {
          "lawGuidance": "string",
          "articleClause": "string",
          "highLevelSynthesis": "string"
        }
      ]
    }
  ],
  "overallConfidenceScore": integer,
  "productNames": ["string"]
}
```

**Returns**: Structured analysis dictionary

#### `format_dark_pattern_analysis(dark_pattern_analysis_details)`
**Purpose**: Format analysis results for DataFrame display.

**Flow**:
1. Iterate through dark pattern items
2. Extract category, excerpt, reasoning, confidence
3. Format regulatory violations
4. Compile into readable string

**Returns**: Formatted analysis string

---

## Data Flow Diagrams

### Video Analysis Data Flow

```
┌─────────────┐
│ User Input  │
│ (URL/Query) │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│         Platform Analyzer                   │
│  (YouTube/TikTok Module)                    │
│                                             │
│  1. Validate Input                          │
│  2. Extract Video ID                        │
│  3. Fetch Metadata (API/Scraping)           │
│  4. Extract Transcript                      │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│         Video Data Object                   │
│  {                                          │
│    "Platform": "YouTube/TikTok",            │
│    "Video ID": "...",                       │
│    "Title": "...",                          │
│    "Channel": "...",                        │
│    "URL": "...",                            │
│    "Description": "...",                    │
│    "Transcript": "..."                      │
│  }                                          │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│         Gemini Analysis                     │
│  (analyze_with_gemini)                      │
│                                             │
│  Input: Combined text (title + desc +      │
│         transcript) + analysis prompt       │
│                                             │
│  Process: Gemini 2.0 Flash API call         │
│                                             │
│  Output: Structured JSON with:             │
│    - Dark pattern categories                │
│    - Excerpts & reasoning                   │
│    - Confidence scores                      │
│    - Regulatory violations                  │
│    - Product names                          │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│         Enhanced Video Data                 │
│  {                                          │
│    ...previous fields...,                   │
│    "Dark Pattern Analysis": "formatted",    │
│    "Raw Dark Pattern Analysis": [...],      │
│    "Overall Confidence Score": 85,          │
│    "Product Names": "Product A, B, C"       │
│  }                                          │
└──────┬──────────────────────────────────────┘
       │
       ├─────────────────┬────────────────────┐
       │                 │                    │
       ▼                 ▼                    ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────────┐
│  Session    │  │  Firebase   │  │  UI Display     │
│  State      │  │  Storage    │  │  (Results Tabs) │
└─────────────┘  └─────────────┘  └─────────────────┘
```

### Firebase Data Flow

```
┌─────────────────────────────────────────────┐
│         Analysis Complete                   │
│  all_results = [video1, video2, ...]        │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│         Prepare Analysis Data               │
│  {                                          │
│    "videos": all_results,                   │
│    "overall_confidence_score": "N/A",       │
│    "total_videos": count,                   │
│    "platforms_analyzed": [...]              │
│  }                                          │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│         Firebase Manager                    │
│  save_analysis_session()                    │
│                                             │
│  Saves to Firestore:                        │
│  Collection: 'influencer-marketing'         │
│  Document ID: session_name                  │
│                                             │
│  Document Structure:                        │
│  {                                          │
│    "sessionName": "...",                    │
│    "search_type": "keywords/urls",          │
│    "platform": "YouTube/TikTok/Mixed",      │
│    "analysis_data": {...},                  │
│    "created_at": "2024-12-01T...",          │
│    "created_by": "unknown",                 │
│    "video_count": 10,                       │
│    "overall_confidence_score": "N/A"        │
│  }                                          │
└─────────────────────────────────────────────┘
```

---

## Prompts and AI Integration

### Default Gemini Analysis Prompt

The application uses a comprehensive, structured prompt for dark pattern detection:

#### Prompt Structure

**1. Introduction & Objective**
```
Analyze the provided text, transcript, and/or video content for the presence 
of dark patterns, manipulative language, or deceptive advertising practices.
```

**2. Categories to Evaluate**

##### a) Implied Scarcity / Sale Mention
- Look for: "limited time", "almost gone", "backup stock", countdowns
- Requirement: Provide quotes and explain urgency manufacturing

##### b) Lack of Clear Disclosure
- Determine: Sponsorship/advertising disclosure presence
- Assess: Clarity, prominence, placement (upfront vs buried)

##### c) Vague or Ambiguous Language
- Flag: "collab", "sp", "ambassador", "partner" without "Ad"/"Sponsored"
- Explain: How terms may mislead viewers

##### d) Inconsistent or Incomplete Disclosures
- Evaluate: Missing disclosures in different formats
- Identify: Omissions in long-form videos, livestreams, stories

##### e) Blurring Editorial and Advertising Content
- Identify: Product promotion as personal review
- Look for: Emotional appeals masking advertising intent

**3. Output Requirements**

For each issue:
- **Excerpt**: Quoted from transcript/description/caption
- **Section Type**: transcript, caption, or description
- **Reasoning**: Why this qualifies as a dark pattern
- **Timestamps/Visual Cues**: If from video (optional)
- **Confidence Score**: 0-100 likelihood estimate

**4. Regulatory Violations Mapping**

The prompt includes a comprehensive table of French consumer protection laws:

| Law / Guidance | Article / Clause | High-Level Synthesis |
|----------------|------------------|----------------------|
| Code de la consommation | Art. L121-1 | Prohibits unfair or misleading practices |
| Code de la consommation | Art. L121-1-1 | Defines specific deceptive practices (false scarcity) |
| Loi n° 2023-451 | Art. 1 | Defines "influence commerciale" |
| Loi n° 2023-451 | Art. 4 & 5 | Requires clear labels ("publicité", "collaboration commerciale") |
| ARPP | Art. b2, §1-2 | Demands clear advertiser identification |
| ARPP | Section 5 | Ensures ads don't disrupt user experience |

**5. Structured JSON Output**

```json
{
  "darkPatternAnalysis": [
    {
      "category": "Implied Scarcity / Sale Mention",
      "excerpt": "Only 3 left in stock! Limited time offer!",
      "sectionType": "transcript",
      "reasoning": "Creates artificial urgency without evidence",
      "confidenceScore": 85,
      "regulatoryViolationReference": [
        {
          "lawGuidance": "Code de la consommation",
          "articleClause": "Art. L121-1",
          "highLevelSynthesis": "Prohibits unfair or misleading practices..."
        }
      ]
    }
  ],
  "overallConfidenceScore": 92,
  "productNames": ["Product A", "Product B"]
}
```

### Gemini API Integration

**API Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent`

**Request Configuration**:
```json
{
  "contents": [
    {
      "role": "user",
      "parts": [
        {
          "text": "[PROMPT]\n\nContent to analyze:\n[VIDEO_CONTENT]"
        }
      ]
    }
  ],
  "generationConfig": {
    "responseMimeType": "application/json",
    "responseSchema": {
      "type": "OBJECT",
      "properties": {
        "darkPatternAnalysis": {...},
        "overallConfidenceScore": {...},
        "productNames": {...}
      }
    }
  }
}
```

**Key Features**:
- **Structured Output**: Enforces JSON schema compliance
- **Type Safety**: Defines expected data types for each field
- **Validation**: Ensures all required fields are present

---

## API Integrations

### 1. YouTube Data API v3

**Purpose**: Fetch video metadata and search results

**Endpoints Used**:

#### Search Endpoint
```
GET https://www.googleapis.com/youtube/v3/search
Parameters:
  - q: Search query
  - part: snippet
  - type: video
  - maxResults: Number of results
  - key: API key
```

#### Videos Endpoint
```
GET https://www.googleapis.com/youtube/v3/videos
Parameters:
  - part: snippet
  - id: Video ID
  - key: API key
```

**Data Retrieved**:
- Video ID
- Title
- Channel title
- Description
- Thumbnails
- Publication date

### 2. YouTube Transcript API

**Library**: `youtube-transcript-api`

**Purpose**: Extract video transcripts

**Usage**:
```python
from youtube_transcript_api import YouTubeTranscriptApi

transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
transcript_text = " ".join([t['text'] for t in transcript_list])
```

**Error Handling**:
- `NoTranscriptFound`: Transcript not available
- `TranscriptsDisabled`: Transcripts disabled by uploader

### 3. Google Gemini 2.0 Flash API

**Purpose**: AI-powered dark pattern analysis

**Model**: `gemini-2.0-flash`

**Features**:
- Structured JSON output
- Schema validation
- High-speed processing
- Multi-modal understanding

**Rate Limits**: (Check Google AI documentation)

### 4. Airtable API

**Purpose**: Fetch dark pattern reference data

**Endpoints Used**:
```
GET https://api.airtable.com/v0/{base_id}/{table_id}
Headers:
  Authorization: Bearer {api_key}
```

**Tables**:
1. **Dark Pattern Table** (`tblOqL0mtNyY74Z2d`)
   - Issues
   - Description
   - Classification
   - Remarks

2. **Law/Guidance Table** (`tblk0vHIm00L5P1ME`)
   - Law/Guidance Name
   - Clause or Article Reference
   - Verbatim of Clause or Article
   - High Level Synthesis (Bullets)

**Pagination**: Handled automatically with offset parameter

### 5. Firebase Firestore

**Purpose**: Persistent storage for analysis sessions

**Collection**: `influencer-marketing`

**Document Structure**:
```javascript
{
  sessionName: string,
  search_type: "keywords" | "urls",
  platform: "YouTube" | "TikTok" | "Mixed",
  analysis_data: {
    videos: [...],
    overall_confidence_score: string,
    total_videos: number,
    platforms_analyzed: [...]
  },
  created_at: string (ISO timestamp),
  created_by: string,
  video_count: number,
  overall_confidence_score: string
}
```

**Operations**:
- `set()`: Create/update session
- `get()`: Retrieve session
- `stream()`: List all sessions
- `delete()`: Remove session

### 6. TikTok Data Extraction

**Methods** (in order of preference):

#### a) yt-dlp
**Command**: `yt-dlp --dump-json --no-download [URL]`

**Capabilities**:
- Metadata extraction
- Video download
- Audio extraction
- Subtitle extraction

#### b) Whisper (OpenAI)
**Purpose**: Audio transcription

**Model**: `base` (configurable)

**Usage**:
```python
import whisper
model = whisper.load_model("base")
result = model.transcribe(audio_file)
transcript = result['text']
```

#### c) Web Scraping
**Target**: TikTok's SIGI_STATE JSON

**Pattern**: `<script id="SIGI_STATE" type="application/json">...</script>`

**Fallback**: HTML meta tags and content parsing

---

## Database Schema

### Firebase Firestore Schema

#### Collection: `influencer-marketing`

**Document ID**: `{sessionName}` (user-defined)

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `sessionName` | string | Unique session identifier |
| `search_type` | string | "keywords" or "urls" |
| `platform` | string | "YouTube", "TikTok", or "Mixed" |
| `analysis_data` | object | Complete analysis results |
| `created_at` | string | ISO 8601 timestamp |
| `created_by` | string | User identifier (default: "unknown") |
| `video_count` | number | Number of videos analyzed |
| `overall_confidence_score` | string | Aggregate confidence score |

**analysis_data Structure**:
```javascript
{
  videos: [
    {
      Platform: string,
      "Video ID": string,
      Title: string,
      Channel: string,
      URL: string,
      Description: string,
      Transcript: string,
      "Dark Pattern Analysis": string,
      "Raw Dark Pattern Analysis": [
        {
          category: string,
          excerpt: string,
          sectionType: string,
          reasoning: string,
          confidenceScore: number,
          regulatoryViolationReference: [
            {
              lawGuidance: string,
              articleClause: string,
              highLevelSynthesis: string
            }
          ]
        }
      ],
      "Overall Confidence Score": number,
      "Product Names": string
    }
  ],
  overall_confidence_score: string,
  total_videos: number,
  platforms_analyzed: [string]
}
```

### Airtable Schema

#### Table 1: Dark Patterns (`tblOqL0mtNyY74Z2d`)

| Field | Type | Description |
|-------|------|-------------|
| Issues | Single line text | Dark pattern type |
| Description | Long text | Detailed description |
| Classification | Single select | Detection status |
| Remarks | Long text | Additional notes |

#### Table 2: Law/Guidance (`tblk0vHIm00L5P1ME`)

| Field | Type | Description |
|-------|------|-------------|
| Law/Guidance Name | Single line text | Name of law/regulation |
| Clause or Article Reference | Single line text | Specific article |
| Verbatim of Clause or Article | Long text | Full legal text |
| High Level Synthesis (Bullets) | Long text | Summary in bullet points |

---

## User Workflows

### Workflow 1: Keyword-Based Analysis

```
1. User navigates to "Application" page
2. User enters session name (e.g., "shiseido-campaign-2024")
3. User selects "Search by Keywords/Hashtags"
4. User enters keywords (e.g., "shiseido, skincare, #shiseidopartner")
5. User sets max results (e.g., 20)
6. User selects platform (e.g., YouTube)
7. User enters channels to exclude (e.g., "@shiseido, @shiseidousa")
8. User clicks "Start Search and Analysis"
9. System searches YouTube for matching videos
10. System extracts metadata and transcripts
11. System analyzes each video with Gemini
12. System displays results in Summary and Detailed tabs
13. System saves session to Firebase
14. User reviews dark pattern findings
15. User can navigate to "History" to view saved session
```

### Workflow 2: URL-Based Analysis

```
1. User navigates to "Application" page
2. User enters session name
3. User selects "Analyze Video URLs"
4. User pastes video URLs (one per line, max 10)
   Example:
   https://www.youtube.com/watch?v=abc123
   https://www.tiktok.com/@user/video/123456
5. User selects platforms (YouTube and/or TikTok)
6. User enters channels to exclude
7. User clicks "Start Search and Analysis"
8. System processes each URL:
   - YouTube: Fetches metadata + transcript
   - TikTok: Tries download → yt-dlp → web scraping
9. System analyzes each video with Gemini
10. System displays results
11. System saves to Firebase
```

### Workflow 3: Viewing History

```
1. User navigates to "History" page
2. System fetches all sessions from Firebase
3. User selects session from dropdown
4. System displays session metadata:
   - Platform
   - Search type
   - Video count
   - Creation date
5. User views results in two tabs:
   - Summary Table: All videos at a glance
   - Detailed Analysis: Expandable dark pattern details
6. User can delete session if needed
```

### Workflow 4: Customizing Analysis Prompt

```
1. User navigates to "Settings" page
2. User views current Gemini prompt
3. User modifies prompt (e.g., adds new dark pattern category)
4. Changes auto-save to session state
5. User returns to "Application" page
6. New analyses use updated prompt
```

### Workflow 5: Viewing Dark Pattern Reference

```
1. User navigates to "Dark Pattern Reference" page
2. System fetches data from Airtable
3. User views two tabs:
   - Tab 1: Influencer Dark Patterns
     * Issues, Description, Classification, Remarks
   - Tab 2: Law/Guidance Clauses
     * Law name, Article, Full text, Summary
4. User can reference this while reviewing analysis results
```

---

## Technical Stack

### Frontend Framework
- **Streamlit**: Python-based web framework for data applications
  - Version: Latest stable
  - Features used:
    - Session state management
    - Multi-page navigation
    - Tabs and expandable sections
    - Data tables (DataFrames)
    - File upload/download
    - Custom styling

### Backend Libraries

#### API Clients
- **google-api-python-client**: YouTube Data API integration
- **youtube-transcript-api**: Transcript extraction
- **requests**: HTTP requests for Gemini and Airtable APIs
- **firebase-admin**: Firebase Admin SDK for Firestore

#### Data Processing
- **pandas**: Data manipulation and display
- **json**: JSON parsing and serialization
- **re**: Regular expressions for URL parsing

#### AI/ML
- **openai-whisper**: Audio transcription for TikTok videos
- **Google Gemini 2.0 Flash**: Dark pattern analysis

#### Video Processing
- **yt-dlp**: Video download and metadata extraction
- **subprocess**: Execute external commands (yt-dlp)
- **tempfile**: Temporary file management

### External Services

#### APIs
1. **YouTube Data API v3**
   - Quota: 10,000 units/day (default)
   - Cost: Free tier available

2. **Google Gemini API**
   - Model: gemini-2.0-flash
   - Pricing: Pay-per-use

3. **Airtable API**
   - Rate limit: 5 requests/second
   - Pricing: Free tier available

4. **Firebase Firestore**
   - Free tier: 1 GB storage, 50K reads/day
   - Pricing: Pay-as-you-go

### Development Tools
- **Python**: 3.8+
- **dotenv**: Environment variable management
- **Git**: Version control

### Deployment Options
- **Streamlit Cloud**: Native Streamlit hosting
- **Heroku**: Container-based deployment
- **Google Cloud Run**: Serverless containers
- **AWS EC2**: Traditional server deployment

### Environment Configuration

**Required Environment Variables**:
```bash
# API Keys
YOUTUBE_API_KEY=your_youtube_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
AIRTABLE_API_KEY=your_airtable_api_key_here

# Configuration
AIRTABLE_BASE_ID=your_airtable_base_id_here
FIREBASE_SERVICE_ACCOUNT_PATH=/path/to/firebase-credentials.json
```

**Optional Configuration**:
```bash
# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

---

## Security Considerations

### API Key Management
- All API keys stored in environment variables
- Never committed to version control
- `.env` file in `.gitignore`
- Streamlit secrets for cloud deployment

### Firebase Security
- Service account credentials file protected
- Firestore security rules configured
- Read/write permissions managed

### Data Privacy
- No personal user data collected
- Video URLs and metadata only
- Session names user-defined
- Optional Firebase storage

### Rate Limiting
- YouTube API: Respects quota limits
- Gemini API: Error handling for rate limits
- Airtable API: Pagination and retry logic
- TikTok: Multiple fallback methods to avoid blocking

---

## Error Handling

### API Errors

#### YouTube API
```python
try:
    response = youtube.search().list(...).execute()
except Exception as e:
    st.error(f"Error during YouTube search: {e}")
    return []
```

#### Gemini API
```python
try:
    response = requests.post(apiUrl, ...)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    st.error(f"Error calling Gemini API: {e}")
    return default_response
```

#### Firebase
```python
try:
    doc_ref.set(session_data)
    st.success("Session saved successfully!")
except Exception as e:
    st.error(f"Error saving to Firebase: {e}")
    return None
```

### Transcript Errors
```python
try:
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
except NoTranscriptFound:
    return "No transcript found for this video."
except TranscriptsDisabled:
    return "Transcripts are disabled for this video."
```

### TikTok Extraction Errors
- **Method 1 Fails**: Falls back to Method 2
- **Method 2 Fails**: Falls back to Method 3
- **All Methods Fail**: Displays detailed error message with troubleshooting tips

---

## Performance Optimization

### Caching
- Streamlit session state for results
- Whisper model loaded once per session
- Firebase connection reused

### Batch Processing
- Multiple videos processed in sequence
- Progress indicators for user feedback

### Async Considerations
- YouTube API: Synchronous requests
- Gemini API: Synchronous with timeout
- Future: Could implement async processing for parallel video analysis

---

## Future Enhancements

### Planned Features
1. **Batch URL Upload**: CSV file upload for bulk analysis
2. **Export Functionality**: Download results as CSV/JSON/PDF
3. **Advanced Filtering**: Filter results by confidence score, dark pattern type
4. **Visualization**: Charts and graphs for pattern distribution
5. **User Authentication**: Multi-user support with Firebase Auth
6. **Scheduled Analysis**: Periodic monitoring of channels/keywords
7. **Email Notifications**: Alerts for high-confidence violations
8. **API Endpoint**: RESTful API for programmatic access

### Technical Improvements
1. **Async Processing**: Parallel video analysis
2. **Caching Layer**: Redis for API response caching
3. **Queue System**: Celery for background tasks
4. **Database Migration**: PostgreSQL for relational data
5. **Monitoring**: Application performance monitoring (APM)
6. **Testing**: Unit tests, integration tests, E2E tests

---

## Troubleshooting Guide

### Common Issues

#### 1. YouTube API Quota Exceeded
**Error**: `quotaExceeded`
**Solution**: 
- Wait for quota reset (daily)
- Request quota increase from Google
- Use URL-based analysis instead of keyword search

#### 2. Gemini API Rate Limit
**Error**: `429 Too Many Requests`
**Solution**:
- Add delay between requests
- Reduce batch size
- Upgrade API tier

#### 3. Firebase Connection Failed
**Error**: `Firebase initialization failed`
**Solution**:
- Verify service account file path
- Check file permissions
- Validate JSON format

#### 4. TikTok Extraction Failed
**Error**: `Failed to extract data from: [URL]`
**Solution**:
- Verify URL is valid and public
- Check yt-dlp installation: `yt-dlp --version`
- Update yt-dlp: `pip install -U yt-dlp`
- Check disk space for video downloads

#### 5. Whisper Model Loading Failed
**Error**: `Whisper model not available`
**Solution**:
- Install Whisper: `pip install openai-whisper`
- Install ffmpeg (required by Whisper)
- Check available disk space

---

## Conclusion

The **Dark Pattern Detector** is a sophisticated, modular application that combines multiple APIs, AI analysis, and robust data extraction methods to identify deceptive marketing practices in video content. Its architecture prioritizes:

- **Modularity**: Clear separation of concerns
- **Extensibility**: Easy to add new platforms or analysis methods
- **Reliability**: Multiple fallback mechanisms
- **User Experience**: Intuitive interface with comprehensive feedback
- **Compliance**: Mapping to regulatory frameworks

This documentation provides a complete reference for understanding, maintaining, and extending the application.

---

**Document Version**: 1.0  
**Last Updated**: December 1, 2024  
**Author**: Dark Pattern Detector Development Team
