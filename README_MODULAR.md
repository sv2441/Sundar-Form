# Dark Pattern Detector - Modular Version

A comprehensive application for detecting dark patterns and deceptive practices in video content from YouTube and TikTok platforms.

## 🚀 Features

### Core Functionality
- **Multi-Platform Analysis**: Support for YouTube and TikTok video analysis
- **Dark Pattern Detection**: AI-powered analysis using Gemini API
- **Session Management**: Save and retrieve analysis sessions with Firebase
- **History Tracking**: View and manage previous analysis sessions
- **Transcript Extraction**: Automatic transcript extraction for comprehensive analysis

### Platform Support
- **YouTube**: Full API integration with search and URL analysis
- **TikTok**: Enhanced extraction using yt-dlp and web scraping methods
- **Mixed Analysis**: Analyze both platforms simultaneously

### Data Storage
- **Firebase Integration**: Automatic session storage and retrieval
- **History Management**: View, filter, and delete analysis sessions
- **Session Naming**: Custom session names for organization

## 📋 Requirements

### Dependencies
```bash
pip install -r requirements.txt
```

### External Tools
- **yt-dlp**: For TikTok video extraction
- **Whisper**: For transcript extraction
- **Firebase**: For data storage (optional)

### API Keys
- **YouTube Data API**: For YouTube video analysis
- **Gemini API**: For dark pattern detection
- **Firebase Service Account**: For data storage

## 🛠️ Setup

### 1. Environment Configuration
```bash
# Set Firebase service account path
export FIREBASE_SERVICE_ACCOUNT_PATH="/path/to/firebase-service-account.json"

# Windows (PowerShell)
$env:FIREBASE_SERVICE_ACCOUNT_PATH="C:\path\to\firebase-service-account.json"
```

### 2. Firebase Setup
1. Create Firebase project
2. Enable Firestore Database
3. Create `influencer-marketing` collection
4. Generate service account key
5. Set environment variable

### 3. API Keys Configuration
Create `.streamlit/secrets.toml`:
```toml
[api_keys]
youtube_api_key = "your_youtube_api_key"
gemini_api_key = "your_gemini_api_key"
airtable_api_key = "your_airtable_api_key"

[airtable]
base_id = "your_airtable_base_id"
```

## 🎯 Usage

### 1. Application Page
- **Session Name**: Enter unique session name
- **Search Mode**: Choose keywords or URL analysis
- **Platform Selection**: Select YouTube, TikTok, or both
- **Analysis**: Automatic dark pattern detection and storage

### 2. History Page
- **Session Selection**: Choose from saved sessions
- **Results View**: Summary and detailed analysis views
- **Session Management**: Delete sessions as needed

### 3. Settings Page
- **Prompt Customization**: Modify analysis prompts
- **Configuration**: View current settings

### 4. Dark Pattern Reference
- **Reference Tables**: View regulatory guidelines
- **Pattern Types**: Comprehensive dark pattern catalog

## 📊 Analysis Features

### Dark Pattern Categories
- **Implied Scarcity**: False urgency and limited availability
- **Lack of Disclosure**: Missing sponsorship information
- **Vague Language**: Ambiguous promotional terms
- **Inconsistent Disclosures**: Incomplete transparency
- **Blurring Content**: Mixed editorial and advertising

### Regulatory Compliance
- **French Consumer Code**: Art. L121-1 and L121-1-1
- **Influencer Marketing Law**: Loi n° 2023-451
- **ARPP Guidelines**: Digital advertising standards

### Output Format
```json
{
  "darkPatternAnalysis": [
    {
      "category": "Lack of Clear Disclosure",
      "excerpt": "sponsored content without disclosure",
      "sectionType": "transcript",
      "reasoning": "No clear sponsorship disclosure",
      "confidenceScore": 95,
      "regulatoryViolationReference": [...]
    }
  ],
  "overallConfidenceScore": 92,
  "productNames": ["Product1", "Product2"]
}
```

## 🔧 TikTok Integration

### Extraction Methods
1. **yt-dlp**: Primary metadata extraction
2. **Video Download**: Full video with transcript extraction
3. **Web Scraping**: Fallback HTML parsing
4. **Whisper**: Audio transcript extraction

### Supported URL Formats
- `https://www.tiktok.com/@username/video/1234567890`
- `https://tiktok.com/@user/video/0987654321`
- `https://vm.tiktok.com/abc123/`
- `https://tiktok.com/t/xyz789/`

### Example Usage
```python
# Test specific TikTok URLs
urls = """
https://www.tiktok.com/@ule.beauty/video/7493819825798679830
https://www.tiktok.com/@ule.beauty/video/7501000294772264214
https://www.tiktok.com/@ule.beauty/video/7499885193466055958
"""

analyzer = create_tiktok_analyzer()
results = analyzer.analyze_video_urls(urls, "")
```

## 📈 Firebase Integration

### Session Storage
- **Collection**: `influencer-marketing`
- **Document Structure**: Session-based organization
- **Metadata**: Platform, search type, video count, timestamps

### Session Data Format
```json
{
  "session_name": "influencer-marketing-analysis-2024",
  "search_type": "urls",
  "platform": "TikTok",
  "analysis_data": {
    "videos": [...],
    "overall_confidence_score": "N/A",
    "total_videos": 5,
    "platforms_analyzed": ["TikTok"]
  },
  "created_at": "2024-01-15T10:30:00",
  "video_count": 5
}
```

## 🧪 Testing

### Test TikTok URLs
```bash
python test_tiktok_urls.py
```

### Test Firebase Integration
```bash
python test_firebase_integration.py
```

### Test Full Workflow
```bash
streamlit run app_modular.py
```

## 📁 Project Structure

```
Sundar-Form/
├── app_modular.py          # Main application
├── config.py              # Configuration and session state
├── firebase_module.py     # Firebase integration
├── tiktok_module.py       # TikTok analysis
├── youtube_module.py      # YouTube analysis
├── ui_components.py       # UI components
├── utils.py              # Utility functions
├── requirements.txt       # Dependencies
├── ENVIRONMENT_SETUP.md  # Setup guide
└── test_tiktok_urls.py   # TikTok URL testing
```

## 🚨 Troubleshooting

### Common Issues
1. **Firebase Connection**: Check service account path and permissions
2. **TikTok Extraction**: Update yt-dlp and check video availability
3. **Whisper Installation**: Install ffmpeg for audio processing
4. **API Limits**: Monitor YouTube and Gemini API quotas

### Error Handling
- **Graceful Degradation**: App continues without Firebase
- **Fallback Methods**: Multiple TikTok extraction approaches
- **User Feedback**: Clear error messages and suggestions

## 🔮 Future Enhancements

### Planned Features
- **Real-time Monitoring**: Live video analysis
- **Advanced AI**: GPT-4 integration for better analysis
- **Multi-language Support**: Non-English content analysis
- **Batch Processing**: Large-scale analysis capabilities

### Technical Improvements
- **Caching**: Performance optimization
- **Parallel Processing**: Concurrent analysis
- **Advanced Filtering**: Enhanced search capabilities
- **Export Features**: Data export in multiple formats

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review error logs
3. Test with sample URLs
4. Verify environment setup

---

**Note**: This application respects platform Terms of Service and implements appropriate rate limiting for production use.