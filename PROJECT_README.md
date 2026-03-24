# Dark Pattern Detector for Video Content

A comprehensive Streamlit application for detecting and analyzing dark patterns and deceptive advertising practices in YouTube and TikTok influencer content, with AI-powered analysis using Google Gemini 2.0 Flash.

![Version](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Documentation](#documentation)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Architecture](#architecture)
- [Dark Pattern Categories](#dark-pattern-categories)
- [Regulatory Framework](#regulatory-framework)
- [API Integrations](#api-integrations)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

The **Dark Pattern Detector** is a sophisticated tool designed to identify manipulative marketing tactics in influencer video content. It combines multiple data extraction methods, AI-powered analysis, and regulatory compliance mapping to provide comprehensive insights into deceptive advertising practices.

### Key Capabilities

- **Multi-Platform Analysis**: YouTube and TikTok support
- **Dual Search Modes**: Keyword-based search or direct URL analysis
- **AI-Powered Detection**: Gemini 2.0 Flash for pattern recognition
- **Regulatory Mapping**: Automatic mapping to French consumer protection laws
- **Persistent Storage**: Firebase integration for session management
- **Reference Database**: Airtable integration for dark pattern taxonomy
- **Comprehensive Reporting**: Detailed analysis with confidence scores and evidence

---

## ✨ Features

### 🔍 Analysis Features

- **5 Dark Pattern Categories**:
  - Implied Scarcity / Sale Mention
  - Lack of Clear Disclosure
  - Vague or Ambiguous Language
  - Inconsistent or Incomplete Disclosures
  - Blurring Editorial and Advertising Content

- **Multi-Source Data Extraction**:
  - Video titles and descriptions
  - Automatic transcript extraction (YouTube)
  - Audio transcription with Whisper (TikTok)
  - Metadata (views, likes, comments)

- **Confidence Scoring**:
  - Individual pattern confidence (0-100)
  - Overall analysis confidence
  - Evidence-based reasoning

- **Regulatory Compliance**:
  - Mapping to French consumer protection laws
  - Article-level violation references
  - Plain language summaries

### 🎨 User Interface

- **4 Main Pages**:
  - **Application**: Main analysis interface
  - **History**: View saved analysis sessions
  - **Settings**: Customize analysis prompts
  - **Dark Pattern Reference**: View taxonomy and regulations

- **Results Display**:
  - Summary table view
  - Detailed analysis with expandable sections
  - Product name extraction
  - Regulatory violation mapping

### 💾 Data Management

- **Session Persistence**: Save and retrieve analysis sessions
- **Firebase Integration**: Cloud storage for results
- **Airtable Reference**: Live reference data
- **Export Ready**: Structured JSON output

---

## 📚 Documentation

This project includes comprehensive documentation:

| Document | Description |
|----------|-------------|
| **[DOCUMENTATION.md](DOCUMENTATION.md)** | Complete technical documentation covering architecture, modules, data flows, APIs, and workflows |
| **[ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md)** | Visual diagrams showing system architecture, workflows, and data structures |
| **[PROMPTS_AND_ANALYSIS.md](PROMPTS_AND_ANALYSIS.md)** | Detailed guide to AI prompts, dark pattern categories, and analysis methodology |
| **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** | Quick reference guide with common tasks and troubleshooting |

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (optional, for cloning)

### Step 1: Clone or Download

```bash
git clone <repository-url>
cd Sundar-Form
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Key Dependencies**:
- `streamlit` - Web application framework
- `google-api-python-client` - YouTube Data API
- `youtube-transcript-api` - Transcript extraction
- `firebase-admin` - Firebase integration
- `openai-whisper` - Audio transcription
- `requests` - HTTP client
- `pandas` - Data manipulation
- `python-dotenv` - Environment variable management

### Step 3: Install System Dependencies

**For TikTok Support**:

1. **yt-dlp** (video download):
```bash
pip install yt-dlp
```

2. **ffmpeg** (required by Whisper):
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg`

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# YouTube Data API
YOUTUBE_API_KEY=your_youtube_api_key_here

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Airtable API
AIRTABLE_API_KEY=your_airtable_api_key_here
AIRTABLE_BASE_ID=your_airtable_base_id_here

# Firebase
FIREBASE_SERVICE_ACCOUNT_PATH=/path/to/firebase-credentials.json
```

### Obtaining API Keys

#### YouTube Data API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Copy the API key

#### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an API key
3. Copy the API key

#### Airtable API Key
1. Go to [Airtable Account](https://airtable.com/account)
2. Generate a personal access token
3. Copy the token
4. Get your Base ID from the Airtable base URL

#### Firebase Setup
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project
3. Go to Project Settings > Service Accounts
4. Generate new private key
5. Download JSON file
6. Update `FIREBASE_SERVICE_ACCOUNT_PATH` with file path

---

## 🎮 Usage

### Starting the Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### Workflow 1: Keyword Search

1. Navigate to **Application** page
2. Enter a session name (e.g., `shiseido-campaign-2024`)
3. Select **"Search by Keywords/Hashtags"**
4. Enter keywords (e.g., `shiseido, skincare, #sponsored`)
5. Set max results (e.g., `20`)
6. Select platform (**YouTube** or **TikTok**)
7. Enter channels to exclude (optional)
8. Click **"Start Search and Analysis"**
9. View results in **Summary Table** and **Detailed Analysis** tabs

### Workflow 2: URL Analysis

1. Navigate to **Application** page
2. Enter a session name
3. Select **"Analyze Video URLs"**
4. Paste video URLs (one per line, max 10):
   ```
   https://www.youtube.com/watch?v=abc123
   https://www.tiktok.com/@user/video/123456
   ```
5. Select platform
6. Click **"Start Search and Analysis"**
7. View results

### Workflow 3: View History

1. Navigate to **History** page
2. Select a saved session from dropdown
3. View session metadata and results
4. Optionally delete session

### Workflow 4: Customize Prompt

1. Navigate to **Settings** page
2. Edit the Gemini analysis prompt
3. Changes auto-save
4. Return to **Application** to use updated prompt

### Workflow 5: View Reference Data

1. Navigate to **Dark Pattern Reference** page
2. View two tabs:
   - **Influencer Dark Patterns**: Taxonomy of dark pattern types
   - **Law/Guidance Clauses**: French regulatory framework

---

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────┐
│     Streamlit Web Application           │
│            (app.py)                     │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│YouTube │ │TikTok  │ │Firebase│
│Module  │ │Module  │ │Module  │
└────────┘ └────────┘ └────────┘
    │          │          │
    └──────────┼──────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│YouTube │ │Gemini  │ │Airtable│
│API     │ │API     │ │API     │
└────────┘ └────────┘ └────────┘
```

### Module Structure

- **app.py**: Main orchestrator
- **config.py**: Configuration and prompts
- **ui_components.py**: User interface
- **youtube_module.py**: YouTube operations
- **tiktok_module.py**: TikTok operations (multi-method)
- **firebase_module.py**: Data persistence
- **utils.py**: Shared utilities

For detailed architecture diagrams, see [ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md)

---

## 🎭 Dark Pattern Categories

### 1. Implied Scarcity / Sale Mention
Creates artificial urgency through scarcity claims.

**Examples**:
- "Only 3 left in stock!"
- "Sale ends at midnight!"
- "Limited time offer!"

**Regulatory Violation**: Code de la consommation, Art. L121-1-1

---

### 2. Lack of Clear Disclosure
Failure to clearly disclose commercial relationships.

**Examples**:
- No sponsorship disclosure
- Disclosure buried in description
- Disclosure only in hashtags

**Regulatory Violation**: Loi n° 2023-451, Art. 4 & 5

---

### 3. Vague or Ambiguous Language
Using unclear terms that obscure commercial relationships.

**Examples**:
- "Collab" (without "ad")
- "SP" (abbreviation)
- "Ambassador"

**Regulatory Violation**: Loi n° 2023-451, Art. 4 & 5

---

### 4. Inconsistent or Incomplete Disclosures
Disclosures that vary across formats or are missing in some contexts.

**Examples**:
- Disclosure in video but not description
- Disclosure in first video but not subsequent ones

**Regulatory Violation**: Loi n° 2023-451, Art. 4 & 5

---

### 5. Blurring Editorial and Advertising Content
Presenting advertising as personal opinion or editorial content.

**Examples**:
- "I genuinely love this product" (in sponsored content)
- Personal anecdotes masking paid promotion

**Regulatory Violation**: Code de la consommation, Art. L121-1

For detailed category definitions and examples, see [PROMPTS_AND_ANALYSIS.md](PROMPTS_AND_ANALYSIS.md)

---

## ⚖️ Regulatory Framework

### French Consumer Protection Laws

The application maps detected dark patterns to specific French regulations:

1. **Code de la consommation - Art. L121-1**
   - Prohibits unfair commercial practices

2. **Code de la consommation - Art. L121-1-1**
   - Prohibits false scarcity and misleading availability claims

3. **Loi n° 2023-451 (9 juin 2023) - Art. 1**
   - Defines "influence commerciale" (influencer marketing)

4. **Loi n° 2023-451 - Art. 4 & 5**
   - Requires clear disclosure labels ("publicité", "collaboration commerciale")

5. **ARPP "Communication Publicitaire Numérique" - Art. b2**
   - Demands clear advertiser identification

6. **ARPP - Section 5**
   - Ensures ads don't disrupt user experience

For complete regulatory text and analysis, see [PROMPTS_AND_ANALYSIS.md](PROMPTS_AND_ANALYSIS.md)

---

## 🔌 API Integrations

### YouTube Data API v3
- **Purpose**: Video search and metadata
- **Quota**: 10,000 units/day (default)
- **Endpoints**: `search().list()`, `videos().list()`

### YouTube Transcript API
- **Purpose**: Automatic transcript extraction
- **Library**: `youtube-transcript-api`
- **Supports**: Auto-captions and manual subtitles

### Google Gemini 2.0 Flash API
- **Purpose**: AI-powered dark pattern analysis
- **Features**: Structured JSON output, schema validation
- **Model**: `gemini-2.0-flash`

### Airtable API
- **Purpose**: Reference data (dark patterns, regulations)
- **Tables**: Dark Patterns, Law/Guidance
- **Rate Limit**: 5 requests/second

### Firebase Firestore
- **Purpose**: Session persistence
- **Collection**: `influencer-marketing`
- **Operations**: CRUD for analysis sessions

### OpenAI Whisper
- **Purpose**: Audio transcription (TikTok)
- **Model**: `base` (configurable)
- **Local**: Runs on your machine

For detailed API documentation, see [DOCUMENTATION.md](DOCUMENTATION.md)

---

## 🔧 Troubleshooting

### Common Issues

#### YouTube API Quota Exceeded
**Error**: `quotaExceeded`

**Solutions**:
- Wait for daily quota reset
- Request quota increase from Google
- Use URL-based analysis instead of keyword search

---

#### Gemini API Rate Limit
**Error**: `429 Too Many Requests`

**Solutions**:
- Add delays between requests
- Reduce batch size
- Upgrade API tier

---

#### Firebase Connection Failed
**Error**: `Firebase initialization failed`

**Solutions**:
- Verify `FIREBASE_SERVICE_ACCOUNT_PATH` is correct
- Check file permissions
- Validate JSON format of credentials file

---

#### TikTok Extraction Failed
**Error**: `Failed to extract data from: [URL]`

**Solutions**:
- Verify URL is valid and public
- Update yt-dlp: `pip install -U yt-dlp`
- Install ffmpeg (required by Whisper)
- Check available disk space

---

#### Whisper Model Not Loading
**Error**: `Whisper model not available`

**Solutions**:
- Install Whisper: `pip install openai-whisper`
- Install ffmpeg
- Check disk space (model requires ~1GB)

For more troubleshooting tips, see [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Reporting Issues
- Use GitHub Issues to report bugs
- Include error messages and steps to reproduce
- Specify your environment (OS, Python version)

### Suggesting Features
- Open a GitHub Issue with feature request
- Describe use case and expected behavior
- Consider regulatory implications

### Code Contributions
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Documentation
- Improve existing documentation
- Add examples and use cases
- Translate to other languages

---

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

---

## 🙏 Acknowledgments

- **Google**: YouTube Data API, Gemini API
- **OpenAI**: Whisper model
- **Airtable**: Reference database
- **Firebase**: Cloud storage
- **Streamlit**: Web framework

---

## 📞 Support

### Documentation
- [Complete Documentation](DOCUMENTATION.md)
- [Architecture Diagrams](ARCHITECTURE_DIAGRAMS.md)
- [Prompts & Analysis](PROMPTS_AND_ANALYSIS.md)
- [Quick Reference](QUICK_REFERENCE.md)

### External Resources
- [Streamlit Docs](https://docs.streamlit.io/)
- [YouTube API Docs](https://developers.google.com/youtube/v3)
- [Gemini API Docs](https://ai.google.dev/docs)
- [Firebase Docs](https://firebase.google.com/docs)

---

## 🔄 Version History

### Version 1.0 (December 2024)
- Initial release
- YouTube and TikTok support
- Gemini 2.0 Flash integration
- Firebase persistence
- Airtable reference data
- 5 dark pattern categories
- French regulatory framework
- Comprehensive documentation

---

## 🎓 Citation

If you use this tool in your research or work, please cite:

```
Dark Pattern Detector for Video Content (2024)
A Streamlit application for detecting deceptive advertising practices
in influencer marketing content.
```

---

## 📊 Project Status

- ✅ **Stable**: Core functionality complete
- 🔄 **Active Development**: Regular updates and improvements
- 📚 **Well Documented**: Comprehensive documentation available
- 🧪 **Tested**: Validated with real-world influencer content

---

**Built with ❤️ for transparency in influencer marketing**

**Last Updated**: December 1, 2024  
**Version**: 1.0
