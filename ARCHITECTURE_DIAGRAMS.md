# Dark Pattern Detector - Architecture Diagrams

## System Architecture Overview

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                    STREAMLIT WEB APPLICATION (app.py)                     ║
║                          Main Orchestrator                                ║
╚═══════════════════════════════════════════════════════════════════════════╝
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│  Configuration    │   │  UI Components    │   │  Utility          │
│  Module           │   │  Module           │   │  Functions        │
│  (config.py)      │   │(ui_components.py) │   │  (utils.py)       │
├───────────────────┤   ├───────────────────┤   ├───────────────────┤
│ • API Keys        │   │ • Navigation      │   │ • Gemini API      │
│ • Default Prompts │   │ • Search UI       │   │ • URL Parsing     │
│ • Session State   │   │ • Results Display │   │ • Formatting      │
│ • Env Variables   │   │ • History View    │   │ • Airtable Fetch  │
└───────────────────┘   └───────────────────┘   └───────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│  YouTube Module   │   │  TikTok Module    │   │  Firebase Module  │
│(youtube_module.py)│   │(tiktok_module.py) │   │(firebase_module.py)│
├───────────────────┤   ├───────────────────┤   ├───────────────────┤
│ • Video Search    │   │ • yt-dlp Download │   │ • Firestore CRUD  │
│ • Metadata Fetch  │   │ • Whisper Trans.  │   │ • Session Mgmt    │
│ • Transcript API  │   │ • Web Scraping    │   │ • Data Persist    │
│ • Dark Pattern    │   │ • Multi-Method    │   │ • Query/Filter    │
│   Analysis        │   │   Fallback        │   │                   │
└───────────────────┘   └───────────────────┘   └───────────────────┘
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│  YouTube Data     │   │  Google Gemini    │   │  Firebase         │
│  API v3           │   │  2.0 Flash API    │   │  Firestore        │
│                   │   │                   │   │                   │
│  • Search Videos  │   │  • AI Analysis    │   │  • NoSQL Database │
│  • Get Metadata   │   │  • JSON Schema    │   │  • Real-time Sync │
│  • Channel Info   │   │  • Structured Out │   │  • Cloud Storage  │
└───────────────────┘   └───────────────────┘   └───────────────────┘
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│  YouTube          │   │  Airtable API     │   │  OpenAI Whisper   │
│  Transcript API   │   │                   │   │                   │
│                   │   │  • Dark Patterns  │   │  • Audio→Text     │
│  • Auto Captions  │   │  • Law/Guidance   │   │  • Multi-language │
│  • Manual Subs    │   │  • Reference Data │   │  • Local Model    │
└───────────────────┘   └───────────────────┘   └───────────────────┘
```

---

## Video Analysis Workflow

```
                            ┌─────────────────────┐
                            │   USER INPUT        │
                            │  (URL or Keywords)  │
                            └──────────┬──────────┘
                                       │
                                       ▼
                            ┌─────────────────────┐
                            │  Platform Selection │
                            └──────────┬──────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    │                                     │
                    ▼                                     ▼
        ┌───────────────────────┐           ┌───────────────────────┐
        │   YOUTUBE PROCESSING  │           │   TIKTOK PROCESSING   │
        └───────────┬───────────┘           └───────────┬───────────┘
                    │                                   │
                    ▼                                   ▼
        ┌───────────────────────┐           ┌───────────────────────┐
        │ YouTube Data API      │           │ Method 1: yt-dlp      │
        │ • Search/Get Video    │           │ • Download Video      │
        │ • Fetch Metadata      │           │ • Extract Audio       │
        └───────────┬───────────┘           │ • Whisper Transcribe  │
                    │                       └───────────┬───────────┘
                    ▼                                   │
        ┌───────────────────────┐                       │ Success?
        │ YouTube Transcript    │                       │
        │ API                   │                       ▼ No
        │ • Get Auto Captions   │           ┌───────────────────────┐
        │ • Get Manual Subs     │           │ Method 2: yt-dlp      │
        └───────────┬───────────┘           │ • Metadata Only       │
                    │                       │ • No Download         │
                    │                       └───────────┬───────────┘
                    │                                   │
                    │                                   │ Success?
                    │                                   │
                    │                                   ▼ No
                    │                       ┌───────────────────────┐
                    │                       │ Method 3: Web Scrape  │
                    │                       │ • Fetch HTML          │
                    │                       │ • Parse SIGI_STATE    │
                    │                       │ • Extract Meta Tags   │
                    │                       └───────────┬───────────┘
                    │                                   │
                    └──────────────┬────────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │   VIDEO DATA OBJECT          │
                    │                              │
                    │ • Platform                   │
                    │ • Video ID                   │
                    │ • Title                      │
                    │ • Channel/Creator            │
                    │ • Description                │
                    │ • Transcript                 │
                    │ • Metadata (views, likes)    │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │   COMBINE CONTENT            │
                    │                              │
                    │ Title + Description +        │
                    │ Transcript                   │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │   GEMINI 2.0 FLASH API       │
                    │   ANALYSIS                   │
                    │                              │
                    │ Input: Combined Text +       │
                    │        Analysis Prompt       │
                    │                              │
                    │ Process:                     │
                    │ • Detect Dark Patterns       │
                    │ • Extract Excerpts           │
                    │ • Calculate Confidence       │
                    │ • Map Regulatory Violations  │
                    │ • Extract Product Names      │
                    │                              │
                    │ Output: Structured JSON      │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │   STRUCTURED ANALYSIS        │
                    │   RESULTS                    │
                    │                              │
                    │ {                            │
                    │   darkPatternAnalysis: [...],│
                    │   overallConfidenceScore: 85,│
                    │   productNames: [...]        │
                    │ }                            │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │   FORMAT FOR DISPLAY         │
                    │                              │
                    │ • Summary Table View         │
                    │ • Detailed Analysis View     │
                    │ • Regulatory Mapping         │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────┴───────────────┐
                    │                              │
                    ▼                              ▼
        ┌───────────────────────┐    ┌───────────────────────┐
        │   STORE IN SESSION    │    │   SAVE TO FIREBASE    │
        │   STATE               │    │   (If Connected)      │
        │                       │    │                       │
        │ • analyzed_results    │    │ Collection:           │
        │ • Temporary storage   │    │ influencer-marketing  │
        └───────────┬───────────┘    └───────────┬───────────┘
                    │                            │
                    └──────────────┬─────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │   DISPLAY RESULTS IN UI      │
                    │                              │
                    │ Tab 1: Summary Table         │
                    │ Tab 2: Detailed Analysis     │
                    └──────────────────────────────┘
```

---

## Data Flow: User Journey Through Application

```
┌─────────────────────────────────────────────────────────────────────┐
│                        APPLICATION START                            │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Page Configuration    │
                    │  • Set layout: wide    │
                    │  • Set title           │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Initialize Session    │
                    │  State                 │
                    │  • gemini_prompt       │
                    │  • analyzed_results[]  │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Create Navigation     │
                    │  Sidebar               │
                    └────────────┬───────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
                ▼                ▼                ▼
    ┌──────────────────┐ ┌──────────────┐ ┌──────────────┐
    │  Dark Pattern    │ │   History    │ │   Settings   │
    │  Reference       │ │              │ │              │
    └──────────────────┘ └──────────────┘ └──────────────┘
                │                │                │
                ▼                ▼                ▼
    ┌──────────────────┐ ┌──────────────┐ ┌──────────────┐
    │ Fetch Airtable   │ │ Fetch        │ │ Edit Gemini  │
    │ • Dark Patterns  │ │ Firebase     │ │ Prompt       │
    │ • Law/Guidance   │ │ Sessions     │ │              │
    └──────────────────┘ └──────────────┘ └──────────────┘
                │                │                │
                ▼                ▼                ▼
    ┌──────────────────┐ ┌──────────────┐ ┌──────────────┐
    │ Display in Tabs  │ │ Display      │ │ Auto-save to │
    │ • Reference Data │ │ Session List │ │ Session State│
    └──────────────────┘ └──────────────┘ └──────────────┘

                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  APPLICATION PAGE      │
                    │  (Main Analysis)       │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Get API Keys          │
                    │  • YOUTUBE_API_KEY     │
                    │  • GEMINI_API_KEY      │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Create Search         │
                    │  Interface             │
                    │                        │
                    │  Inputs:               │
                    │  • Session Name        │
                    │  • Search Mode         │
                    │  • Keywords/URLs       │
                    │  • Platform Selection  │
                    │  • Exclusion Filters   │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  User Clicks           │
                    │  "Start Search and     │
                    │   Analysis"            │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Initialize Firebase   │
                    │  Manager               │
                    └────────────┬───────────┘
                                 │
                ┌────────────────┴────────────────┐
                │                                 │
                ▼                                 ▼
    ┌───────────────────────┐       ┌───────────────────────┐
    │  YouTube Selected     │       │  TikTok Selected      │
    └───────────┬───────────┘       └───────────┬───────────┘
                │                               │
                ▼                               ▼
    ┌───────────────────────┐       ┌───────────────────────┐
    │  Create YouTube       │       │  Create TikTok        │
    │  Analyzer             │       │  Analyzer             │
    └───────────┬───────────┘       └───────────┬───────────┘
                │                               │
                ▼                               ▼
    ┌───────────────────────┐       ┌───────────────────────┐
    │  Search/Analyze       │       │  Search/Analyze       │
    │  Videos               │       │  Videos               │
    │  • By Keywords        │       │  • By Keywords        │
    │  • By URLs            │       │  • By URLs            │
    └───────────┬───────────┘       └───────────┬───────────┘
                │                               │
                ▼                               ▼
    ┌───────────────────────┐       ┌───────────────────────┐
    │  Extract Metadata     │       │  Extract Metadata     │
    │  & Transcripts        │       │  & Transcripts        │
    │  • YouTube API        │       │  • yt-dlp + Whisper   │
    │  • Transcript API     │       │  • Web Scraping       │
    └───────────┬───────────┘       └───────────┬───────────┘
                │                               │
                └───────────────┬───────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │  Analyze Dark Patterns │
                    │  (For Each Video)      │
                    │                        │
                    │  • Combine Content     │
                    │  • Call Gemini API     │
                    │  • Parse JSON Response │
                    │  • Format Results      │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Store Results         │
                    │  • Session State       │
                    │  • analyzed_results    │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Save to Firebase      │
                    │  (If Connected)        │
                    │                        │
                    │  Collection:           │
                    │  influencer-marketing  │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Display Results       │
                    │                        │
                    │  Tab 1: Summary Table  │
                    │  Tab 2: Detailed View  │
                    └────────────────────────┘
```

---

## Module Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                            app.py                                   │
│                      (Main Orchestrator)                            │
│                                                                     │
│  main()                                                             │
│   ├─ setup_page_config()          ────────────┐                    │
│   ├─ initialize_session_state()   ────────────┼───────┐            │
│   ├─ create_navigation()          ────────────┼───────┼────┐       │
│   └─ Route to page                            │       │    │       │
└─────────────────────────────────────────────────┼───────┼────┼───────┘
                                                  │       │    │
                        ┌─────────────────────────┘       │    │
                        │                                 │    │
                        ▼                                 ▼    ▼
        ┌───────────────────────────┐       ┌────────────────────────┐
        │     config.py             │       │   ui_components.py     │
        │                           │       │                        │
        │  get_default_gemini_      │       │  setup_page_config()   │
        │    prompt()               │       │  create_navigation()   │
        │  initialize_session_      │       │  render_dark_pattern_  │
        │    state()                │       │    reference()         │
        │  get_api_keys()           │       │  render_history_page() │
        │  get_airtable_config()    │       │  render_settings_page()│
        └───────────────────────────┘       │  create_search_        │
                        │                   │    interface()         │
                        │                   │  render_results_tabs() │
                        │                   └────────────────────────┘
                        │                               │
                        │                               │
                        ▼                               ▼
        ┌───────────────────────────┐       ┌────────────────────────┐
        │     utils.py              │       │  firebase_module.py    │
        │                           │       │                        │
        │  fetch_all_records()      │       │  FirebaseManager       │
        │  extract_video_id()       │       │   ├─ save_analysis_    │
        │  analyze_with_gemini()    │       │   │    session()       │
        │  format_dark_pattern_     │       │   ├─ get_all_sessions()│
        │    analysis()             │       │   ├─ get_session_by_   │
        └───────────────────────────┘       │   │    name()          │
                        │                   │   └─ delete_session()  │
                        │                   └────────────────────────┘
                        │                               │
        ┌───────────────┼───────────────┐               │
        │               │               │               │
        ▼               ▼               ▼               ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│youtube_module │ │tiktok_module  │ │  Gemini API   │ │  Firestore    │
│               │ │               │ │               │ │               │
│YouTubeAnalyzer│ │TikTokAnalyzer │ │  POST /       │ │  Collection:  │
│ ├─ search_    │ │ ├─ search_    │ │  generate     │ │  influencer-  │
│ │   videos_by_│ │ │   videos_by_│ │  Content      │ │  marketing    │
│ │   keywords()│ │ │   keywords()│ │               │ │               │
│ ├─ analyze_   │ │ ├─ analyze_   │ │  Response:    │ │  Documents:   │
│ │   video_    │ │ │   video_    │ │  Structured   │ │  {sessionName}│
│ │   urls()    │ │ │   urls()    │ │  JSON         │ │               │
│ ├─ _extract_  │ │ ├─ _download_ │ └───────────────┘ └───────────────┘
│ │   transcript│ │ │   and_      │
│ │   ()        │ │ │   extract_  │
│ └─ analyze_   │ │ │   video_    │
│     dark_     │ │ │   data()    │
│     patterns()│ │ ├─ _try_yt_   │
└───────────────┘ │ │   dlp_      │
        │         │ │   extraction│
        │         │ │   ()        │
        │         │ └─ analyze_   │
        │         │     dark_     │
        │         │     patterns()│
        │         └───────────────┘
        │                 │
        ▼                 ▼
┌───────────────┐ ┌───────────────┐
│  YouTube API  │ │  yt-dlp +     │
│               │ │  Whisper      │
│  • search()   │ │               │
│  • videos()   │ │  • Download   │
│               │ │  • Transcribe │
└───────────────┘ └───────────────┘
        │
        ▼
┌───────────────┐
│  Transcript   │
│  API          │
│               │
│  • get_       │
│    transcript │
└───────────────┘
```

---

## Firebase Data Structure

```
Firestore Database
│
└─── Collection: "influencer-marketing"
     │
     ├─── Document: "session-name-1"
     │    │
     │    ├─── sessionName: "session-name-1"
     │    ├─── search_type: "keywords"
     │    ├─── platform: "YouTube"
     │    ├─── created_at: "2024-12-01T12:30:00Z"
     │    ├─── created_by: "unknown"
     │    ├─── video_count: 10
     │    ├─── overall_confidence_score: "N/A"
     │    └─── analysis_data:
     │         │
     │         ├─── videos: [
     │         │    │
     │         │    ├─── {
     │         │    │    Platform: "YouTube",
     │         │    │    "Video ID": "abc123",
     │         │    │    Title: "...",
     │         │    │    Channel: "...",
     │         │    │    URL: "...",
     │         │    │    Description: "...",
     │         │    │    Transcript: "...",
     │         │    │    "Dark Pattern Analysis": "...",
     │         │    │    "Raw Dark Pattern Analysis": [
     │         │    │        {
     │         │    │          category: "...",
     │         │    │          excerpt: "...",
     │         │    │          sectionType: "...",
     │         │    │          reasoning: "...",
     │         │    │          confidenceScore: 85,
     │         │    │          regulatoryViolationReference: [...]
     │         │    │        }
     │         │    │    ],
     │         │    │    "Overall Confidence Score": 85,
     │         │    │    "Product Names": "Product A, B"
     │         │    │    },
     │         │    └─── ...
     │         │    ]
     │         ├─── overall_confidence_score: "N/A"
     │         ├─── total_videos: 10
     │         └─── platforms_analyzed: ["YouTube"]
     │
     ├─── Document: "session-name-2"
     │    └─── ...
     │
     └─── Document: "session-name-3"
          └─── ...
```

---

## TikTok Multi-Method Extraction Flow

```
                    ┌────────────────────────┐
                    │  TikTok URL Input      │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Extract Video ID      │
                    │  • Parse URL patterns  │
                    └────────────┬───────────┘
                                 │
                                 ▼
        ┌────────────────────────────────────────────┐
        │         METHOD 1: COMPREHENSIVE            │
        │         yt-dlp + Whisper                   │
        └────────────────────┬───────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────────┐
        │  1. Download video with yt-dlp             │
        │     • --write-info-json                    │
        │     • --extract-audio                      │
        │     • --audio-format wav                   │
        └────────────────────┬───────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────────┐
        │  2. Extract metadata from .info.json       │
        │     • Title, description, uploader         │
        │     • View count, likes, comments          │
        │     • Upload date, tags                    │
        └────────────────────┬───────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────────┐
        │  3. Transcribe audio with Whisper          │
        │     • Load base model                      │
        │     • model.transcribe(audio_file)         │
        │     • Extract text from result             │
        └────────────────────┬───────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────────┐
        │  4. Read description file                  │
        │     • .description file                    │
        └────────────────────┬───────────────────────┘
                             │
                             ▼
                    ┌────────────────────┐
                    │  Success?          │
                    └─────────┬──────────┘
                              │
                    ┌─────────┴─────────┐
                    │ Yes               │ No
                    ▼                   ▼
        ┌───────────────────┐  ┌────────────────────────┐
        │  Return Complete  │  │  METHOD 2: METADATA    │
        │  Data with        │  │  yt-dlp Only           │
        │  Transcript       │  └────────────┬───────────┘
        └───────────────────┘               │
                                            ▼
                            ┌───────────────────────────┐
                            │  Run yt-dlp --dump-json   │
                            │  --no-download            │
                            └───────────┬───────────────┘
                                        │
                                        ▼
                            ┌───────────────────────────┐
                            │  Parse JSON output        │
                            │  • Extract metadata       │
                            │  • No transcript          │
                            └───────────┬───────────────┘
                                        │
                                        ▼
                            ┌───────────────────────────┐
                            │  Success?                 │
                            └───────────┬───────────────┘
                                        │
                            ┌───────────┴───────────┐
                            │ Yes                   │ No
                            ▼                       ▼
                ┌───────────────────┐  ┌────────────────────────┐
                │  Return Metadata  │  │  METHOD 3: WEB SCRAPE  │
                │  (No Transcript)  │  └────────────┬───────────┘
                └───────────────────┘               │
                                                    ▼
                                    ┌───────────────────────────┐
                                    │  Fetch HTML with requests │
                                    │  • User-Agent headers     │
                                    └───────────┬───────────────┘
                                                │
                                                ▼
                                    ┌───────────────────────────┐
                                    │  Search for SIGI_STATE    │
                                    │  JSON in <script> tag     │
                                    └───────────┬───────────────┘
                                                │
                                    ┌───────────┴───────────┐
                                    │ Found?                │
                                    └───────────┬───────────┘
                                                │
                                    ┌───────────┴───────────┐
                                    │ Yes                   │ No
                                    ▼                       ▼
                        ┌───────────────────┐  ┌────────────────────┐
                        │  Parse TikTok     │  │  Extract from HTML │
                        │  JSON Structure   │  │  • Meta tags       │
                        │  • ItemModule     │  │  • Title patterns  │
                        │  • Video data     │  │  • Creator from URL│
                        │  • Stats          │  │  • Basic info      │
                        └───────────────────┘  └────────────────────┘
                                    │                       │
                                    └───────────┬───────────┘
                                                │
                                                ▼
                                    ┌───────────────────────────┐
                                    │  Return Scraped Data      │
                                    │  (Limited info, no        │
                                    │   transcript)             │
                                    └───────────────────────────┘
```

---

## Gemini API Request/Response Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     VIDEO CONTENT PREPARATION                       │
│                                                                     │
│  combined_text = f"""                                               │
│    Title: {video['Title']}                                          │
│    Description: {video['Description']}                              │
│    Transcript: {video['Transcript']}                                │
│  """                                                                │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     GEMINI API REQUEST                              │
│                                                                     │
│  POST https://generativelanguage.googleapis.com/v1beta/models/     │
│       gemini-2.0-flash:generateContent?key={API_KEY}                │
│                                                                     │
│  Headers:                                                           │
│    Content-Type: application/json                                  │
│                                                                     │
│  Body:                                                              │
│  {                                                                  │
│    "contents": [                                                    │
│      {                                                              │
│        "role": "user",                                              │
│        "parts": [                                                   │
│          {                                                          │
│            "text": "{prompt}\n\nContent to analyze:\n{combined}"    │
│          }                                                          │
│        ]                                                            │
│      }                                                              │
│    ],                                                               │
│    "generationConfig": {                                            │
│      "responseMimeType": "application/json",                        │
│      "responseSchema": {                                            │
│        "type": "OBJECT",                                            │
│        "properties": {                                              │
│          "darkPatternAnalysis": {                                   │
│            "type": "ARRAY",                                         │
│            "items": {                                               │
│              "type": "OBJECT",                                      │
│              "properties": {                                        │
│                "category": {"type": "STRING"},                      │
│                "excerpt": {"type": "STRING"},                       │
│                "sectionType": {"type": "STRING"},                   │
│                "reasoning": {"type": "STRING"},                     │
│                "confidenceScore": {"type": "INTEGER"},              │
│                "regulatoryViolationReference": {                    │
│                  "type": "ARRAY",                                   │
│                  "items": {...}                                     │
│                }                                                    │
│              }                                                      │
│            }                                                        │
│          },                                                         │
│          "overallConfidenceScore": {"type": "INTEGER"},             │
│          "productNames": {"type": "ARRAY", "items": {...}}          │
│        }                                                            │
│      }                                                              │
│    }                                                                │
│  }                                                                  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     GEMINI API RESPONSE                             │
│                                                                     │
│  {                                                                  │
│    "candidates": [                                                  │
│      {                                                              │
│        "content": {                                                 │
│          "parts": [                                                 │
│            {                                                        │
│              "text": "{                                             │
│                \"darkPatternAnalysis\": [                           │
│                  {                                                  │
│                    \"category\": \"Implied Scarcity\",              │
│                    \"excerpt\": \"Only 3 left!\",                   │
│                    \"sectionType\": \"transcript\",                 │
│                    \"reasoning\": \"Creates urgency...\",           │
│                    \"confidenceScore\": 85,                         │
│                    \"regulatoryViolationReference\": [              │
│                      {                                              │
│                        \"lawGuidance\": \"Code de la consommation\",│
│                        \"articleClause\": \"Art. L121-1\",          │
│                        \"highLevelSynthesis\": \"Prohibits...\"     │
│                      }                                              │
│                    ]                                                │
│                  }                                                  │
│                ],                                                   │
│                \"overallConfidenceScore\": 85,                      │
│                \"productNames\": [\"Product A\", \"Product B\"]     │
│              }"                                                     │
│            }                                                        │
│          ]                                                          │
│        }                                                            │
│      }                                                              │
│    ]                                                                │
│  }                                                                  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     RESPONSE PARSING                                │
│                                                                     │
│  1. Extract JSON string from response['candidates'][0]['content']  │
│     ['parts'][0]['text']                                            │
│                                                                     │
│  2. Parse JSON string to Python dict                                │
│                                                                     │
│  3. Extract:                                                        │
│     • darkPatternAnalysis (list)                                    │
│     • overallConfidenceScore (int)                                  │
│     • productNames (list)                                           │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     UPDATE VIDEO DATA                               │
│                                                                     │
│  video_data["Raw Dark Pattern Analysis"] = analysis["darkPattern   │
│    Analysis"]                                                       │
│  video_data["Overall Confidence Score"] = analysis["overall        │
│    ConfidenceScore"]                                                │
│  video_data["Product Names"] = ", ".join(analysis["productNames"]) │
│  video_data["Dark Pattern Analysis"] = format_dark_pattern_        │
│    analysis(...)                                                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Session State Management

```
┌─────────────────────────────────────────────────────────────────────┐
│                     STREAMLIT SESSION STATE                         │
│                                                                     │
│  st.session_state = {                                               │
│                                                                     │
│    'gemini_prompt': """                                             │
│      [Default comprehensive dark pattern analysis prompt]          │
│      • Categories to evaluate                                       │
│      • Output requirements                                          │
│      • Regulatory violations table                                  │
│      • JSON schema                                                  │
│    """,                                                             │
│                                                                     │
│    'analyzed_results': [                                            │
│      {                                                              │
│        "Platform": "YouTube",                                       │
│        "Video ID": "abc123",                                        │
│        "Title": "Product Review",                                   │
│        "Channel": "Influencer Name",                                │
│        "URL": "https://youtube.com/watch?v=abc123",                 │
│        "Description": "...",                                        │
│        "Transcript": "...",                                         │
│        "Dark Pattern Analysis": "Category: Implied Scarcity...",    │
│        "Raw Dark Pattern Analysis": [                               │
│          {                                                          │
│            "category": "Implied Scarcity",                          │
│            "excerpt": "Only 3 left!",                               │
│            "sectionType": "transcript",                             │
│            "reasoning": "Creates artificial urgency",               │
│            "confidenceScore": 85,                                   │
│            "regulatoryViolationReference": [...]                    │
│          }                                                          │
│        ],                                                           │
│        "Overall Confidence Score": 85,                              │
│        "Product Names": "Product A, Product B"                      │
│      },                                                             │
│      ...                                                            │
│    ]                                                                │
│  }                                                                  │
│                                                                     │
│  Lifecycle:                                                         │
│  • Initialized on app start                                         │
│  • Persists across reruns                                           │
│  • Cleared on browser refresh                                       │
│  • Separate from Firebase (temporary vs persistent)                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     ERROR HANDLING STRATEGY                         │
└─────────────────────────────────────────────────────────────────────┘

YouTube API Errors:
┌────────────────────────────────────────────────────────────────┐
│  try:                                                          │
│    response = youtube.search().list(...).execute()            │
│  except Exception as e:                                        │
│    st.error(f"Error during YouTube search: {e}")              │
│    return []  # Return empty list, continue with other videos │
└────────────────────────────────────────────────────────────────┘

Transcript Errors:
┌────────────────────────────────────────────────────────────────┐
│  try:                                                          │
│    transcript = YouTubeTranscriptApi.get_transcript(video_id) │
│  except NoTranscriptFound:                                     │
│    return "No transcript found for this video."               │
│  except TranscriptsDisabled:                                   │
│    return "Transcripts are disabled for this video."          │
│  except Exception as e:                                        │
│    return f"Error fetching transcript: {e}"                   │
└────────────────────────────────────────────────────────────────┘

Gemini API Errors:
┌────────────────────────────────────────────────────────────────┐
│  try:                                                          │
│    response = requests.post(apiUrl, ...)                      │
│    response.raise_for_status()                                │
│    result = response.json()                                   │
│    # Parse and return                                         │
│  except requests.exceptions.RequestException as e:            │
│    st.error(f"Error calling Gemini API: {e}")                 │
│    return {"darkPatternAnalysis": [], ...}                    │
│  except json.JSONDecodeError as e:                            │
│    st.error(f"Error decoding JSON: {e}")                      │
│    return {"darkPatternAnalysis": [], ...}                    │
└────────────────────────────────────────────────────────────────┘

Firebase Errors:
┌────────────────────────────────────────────────────────────────┐
│  try:                                                          │
│    doc_ref.set(session_data)                                  │
│    st.success("Session saved successfully!")                  │
│  except Exception as e:                                        │
│    st.error(f"Error saving to Firebase: {e}")                 │
│    return None  # Analysis still displayed, just not saved    │
└────────────────────────────────────────────────────────────────┘

TikTok Multi-Method Fallback:
┌────────────────────────────────────────────────────────────────┐
│  Method 1: yt-dlp + Whisper                                    │
│    ├─ Success? → Return complete data                         │
│    └─ Failure → Try Method 2                                  │
│                                                                │
│  Method 2: yt-dlp metadata only                                │
│    ├─ Success? → Return metadata (no transcript)              │
│    └─ Failure → Try Method 3                                  │
│                                                                │
│  Method 3: Web scraping                                        │
│    ├─ Success? → Return scraped data                          │
│    └─ Failure → Display error with troubleshooting tips       │
└────────────────────────────────────────────────────────────────┘
```

---

**Document Version**: 1.0  
**Last Updated**: December 1, 2024  
**Companion to**: DOCUMENTATION.md
