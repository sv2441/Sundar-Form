# Dark Pattern Detector - Quick Reference Guide

## 📚 Documentation Index

This project includes comprehensive documentation across multiple files:

1. **[DOCUMENTATION.md](DOCUMENTATION.md)** - Complete technical documentation
   - Application architecture
   - Module analysis
   - Data flows
   - API integrations
   - Database schema
   - User workflows

2. **[ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md)** - Visual architecture diagrams
   - System architecture
   - Video analysis workflow
   - Module interactions
   - Firebase structure
   - TikTok extraction methods
   - Error handling

3. **[PROMPTS_AND_ANALYSIS.md](PROMPTS_AND_ANALYSIS.md)** - AI analysis methodology
   - Complete Gemini prompt
   - Dark pattern categories
   - Regulatory framework
   - Analysis methodology
   - JSON schemas
   - Example analyses
   - Customization guide

---

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.8+
pip install -r requirements.txt
```

### Environment Setup
Create `.env` file:
```bash
YOUTUBE_API_KEY=your_youtube_api_key
GEMINI_API_KEY=your_gemini_api_key
AIRTABLE_API_KEY=your_airtable_api_key
AIRTABLE_BASE_ID=your_airtable_base_id
FIREBASE_SERVICE_ACCOUNT_PATH=/path/to/firebase-credentials.json
```

### Run Application
```bash
streamlit run app.py
```

---

## 📋 Application Structure

```
Sundar-Form/
├── app.py                          # Main application
├── Utility/
│   ├── config.py                   # Configuration & prompts
│   ├── ui_components.py            # UI rendering
│   ├── youtube_module.py           # YouTube operations
│   ├── tiktok_module.py            # TikTok operations
│   ├── firebase_module.py          # Firebase integration
│   └── utils.py                    # Shared utilities
├── DOCUMENTATION.md                # Complete documentation
├── ARCHITECTURE_DIAGRAMS.md        # Architecture diagrams
├── PROMPTS_AND_ANALYSIS.md         # AI analysis guide
├── QUICK_REFERENCE.md              # This file
└── requirements.txt                # Python dependencies
```

---

## 🎯 Key Features

### 1. Multi-Platform Support
- **YouTube**: Search by keywords or analyze specific URLs
- **TikTok**: Multiple extraction methods with fallback

### 2. AI-Powered Analysis
- **Model**: Google Gemini 2.0 Flash
- **Output**: Structured JSON with dark patterns, confidence scores, regulatory violations
- **Categories**: 5 main dark pattern types

### 3. Data Persistence
- **Firebase Firestore**: Session storage
- **Airtable**: Reference data (dark patterns, laws)
- **Session State**: Temporary results

### 4. User Interface
- **Navigation**: 4 pages (Application, History, Settings, Reference)
- **Results**: Summary table + detailed analysis
- **Customization**: Editable analysis prompt

---

## 🔍 Dark Pattern Categories

1. **Implied Scarcity / Sale Mention**
   - Creates artificial urgency
   - Example: "Only 3 left! Sale ends tonight!"

2. **Lack of Clear Disclosure**
   - Missing or unclear sponsorship disclosure
   - Example: Buried #ad in description

3. **Vague or Ambiguous Language**
   - Unclear promotional terms
   - Example: "collab" without "sponsored"

4. **Inconsistent or Incomplete Disclosures**
   - Disclosures missing in some formats
   - Example: Disclosure in video 1 but not video 2

5. **Blurring Editorial and Advertising Content**
   - Presenting ads as personal opinion
   - Example: "I genuinely love this!" (in sponsored content)

---

## 📊 Workflow Overview

### Keyword Search
```
1. Enter session name
2. Select "Search by Keywords/Hashtags"
3. Enter keywords (e.g., "shiseido, skincare")
4. Set max results (e.g., 20)
5. Select platform (YouTube/TikTok)
6. Enter channels to exclude
7. Click "Start Search and Analysis"
8. View results in Summary/Detailed tabs
```

### URL Analysis
```
1. Enter session name
2. Select "Analyze Video URLs"
3. Paste URLs (one per line, max 10)
4. Select platform
5. Enter channels to exclude
6. Click "Start Search and Analysis"
7. View results
```

---

## 🔧 Module Reference

### config.py
- `get_default_gemini_prompt()` - Returns analysis prompt
- `initialize_session_state()` - Initializes session variables
- `get_api_keys()` - Retrieves API keys from environment
- `get_airtable_config()` - Retrieves Airtable configuration

### ui_components.py
- `setup_page_config()` - Configures page layout
- `create_navigation()` - Creates sidebar navigation
- `render_dark_pattern_reference()` - Displays reference data
- `render_history_page()` - Shows saved sessions
- `render_settings_page()` - Prompt customization
- `create_search_interface()` - Main search UI
- `render_results_tabs()` - Displays analysis results

### youtube_module.py
- `YouTubeAnalyzer` class
  - `search_videos_by_keywords()` - Search YouTube
  - `analyze_video_urls()` - Analyze specific URLs
  - `analyze_dark_patterns()` - Run AI analysis

### tiktok_module.py
- `TikTokAnalyzer` class
  - `analyze_video_urls()` - Multi-method extraction
  - `_download_and_extract_video_data()` - yt-dlp + Whisper
  - `_try_yt_dlp_extraction()` - Metadata only
  - `_try_web_scraping()` - HTML parsing
  - `analyze_dark_patterns()` - Run AI analysis

### firebase_module.py
- `FirebaseManager` class
  - `save_analysis_session()` - Save to Firestore
  - `get_all_sessions()` - Retrieve all sessions
  - `get_session_by_name()` - Get specific session
  - `delete_session()` - Remove session
  - `is_connected()` - Check connection status

### utils.py
- `fetch_all_records()` - Airtable pagination
- `extract_video_id()` - Parse YouTube URLs
- `analyze_with_gemini()` - Call Gemini API
- `format_dark_pattern_analysis()` - Format results

---

## 🌐 API Reference

### YouTube Data API v3
**Endpoints**:
- `search().list()` - Search videos
- `videos().list()` - Get video details

**Quota**: 10,000 units/day (default)

### Google Gemini 2.0 Flash API
**Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent`

**Features**:
- Structured JSON output
- Schema validation
- High-speed processing

### Airtable API
**Base**: Dark Pattern Reference
**Tables**:
- `tblOqL0mtNyY74Z2d` - Dark Patterns
- `tblk0vHIm00L5P1ME` - Law/Guidance

### Firebase Firestore
**Collection**: `influencer-marketing`
**Operations**: Create, Read, Update, Delete sessions

---

## 📝 JSON Response Schema

```json
{
  "darkPatternAnalysis": [
    {
      "category": "string",
      "excerpt": "string",
      "sectionType": "string",
      "reasoning": "string",
      "confidenceScore": 0-100,
      "regulatoryViolationReference": [
        {
          "lawGuidance": "string",
          "articleClause": "string",
          "highLevelSynthesis": "string"
        }
      ]
    }
  ],
  "overallConfidenceScore": 0-100,
  "productNames": ["string"]
}
```

---

## ⚖️ Regulatory Framework

### French Consumer Protection Laws

1. **Code de la consommation - Art. L121-1**
   - Prohibits unfair commercial practices

2. **Code de la consommation - Art. L121-1-1**
   - Prohibits false scarcity

3. **Loi n° 2023-451 - Art. 1**
   - Defines influencer marketing

4. **Loi n° 2023-451 - Art. 4 & 5**
   - Requires clear disclosure labels

5. **ARPP - Art. b2, §1-2**
   - Demands clear advertiser identification

6. **ARPP - Section 5**
   - Ensures ads don't disrupt UX

---

## 🛠️ Troubleshooting

### YouTube API Quota Exceeded
**Solution**: Wait for daily reset or use URL-based analysis

### Gemini API Rate Limit
**Solution**: Add delays between requests or upgrade tier

### Firebase Connection Failed
**Solution**: Verify service account file path and permissions

### TikTok Extraction Failed
**Solutions**:
- Verify URL is valid and public
- Update yt-dlp: `pip install -U yt-dlp`
- Check disk space
- Install ffmpeg (required by Whisper)

### Whisper Model Not Loading
**Solutions**:
- Install: `pip install openai-whisper`
- Install ffmpeg
- Check disk space

---

## 📈 Performance Tips

1. **Batch Processing**: Process multiple videos in one session
2. **URL Mode**: Faster than keyword search (no search API calls)
3. **Exclude Channels**: Filter out unwanted results early
4. **Limit Results**: Start with smaller batches for testing
5. **Session State**: Results persist across reruns (until browser refresh)

---

## 🔐 Security Best Practices

1. **API Keys**: Store in `.env`, never commit to Git
2. **Firebase**: Use service account with minimal permissions
3. **Airtable**: Use read-only API key if possible
4. **Environment**: Use separate keys for dev/prod
5. **Secrets**: Use Streamlit secrets for cloud deployment

---

## 📚 Additional Resources

### Documentation Files
- **DOCUMENTATION.md**: Complete technical reference
- **ARCHITECTURE_DIAGRAMS.md**: Visual system diagrams
- **PROMPTS_AND_ANALYSIS.md**: AI analysis methodology

### External Links
- [Streamlit Documentation](https://docs.streamlit.io/)
- [YouTube Data API](https://developers.google.com/youtube/v3)
- [Google Gemini API](https://ai.google.dev/docs)
- [Firebase Documentation](https://firebase.google.com/docs)
- [Airtable API](https://airtable.com/developers/web/api/introduction)

---

## 🤝 Support

### Common Questions

**Q: How do I add a new dark pattern category?**
A: Edit the prompt in Settings page, add category definition and update JSON schema

**Q: Can I analyze videos in languages other than French?**
A: Yes, but regulatory references are French-specific. Customize prompt for other jurisdictions.

**Q: How many videos can I analyze at once?**
A: Keyword search: configurable (default 10). URL mode: max 10 URLs.

**Q: Where are results stored?**
A: Session state (temporary) and Firebase (persistent, if connected)

**Q: Can I export results?**
A: Currently displayed in UI. Export functionality is a planned feature.

---

## 🔄 Version History

**Version 1.0** (December 2024)
- Initial release
- YouTube and TikTok support
- Gemini 2.0 Flash integration
- Firebase persistence
- Airtable reference data
- 5 dark pattern categories
- French regulatory framework

---

## 📞 Contact

For questions, issues, or contributions, please refer to the project repository.

---

**Last Updated**: December 1, 2024  
**Version**: 1.0
