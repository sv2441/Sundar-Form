# Dark Pattern Detector for Video Content

A production-ready Streamlit application that analyzes YouTube videos for deceptive marketing practices and regulatory compliance violations using AI-powered analysis.

## 🚀 Features

- **YouTube Video Analysis**: Search by keywords or analyze specific video URLs
- **AI-Powered Detection**: Uses Google Gemini 2.0 Flash for dark pattern identification
- **Regulatory Compliance**: Maps violations to French consumer protection laws
- **Production Security**: API keys stored securely in `secrets.toml`
- **Interactive UI**: User-friendly interface with detailed analysis results

## 🔧 Setup Instructions

### 1. Install Dependencies

```bash
# Activate virtual environment
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install required packages
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.streamlit/secrets.toml` file in your project root:

```toml
# Streamlit Secrets Configuration
# This file contains sensitive API keys
# Never commit this file to version control - add it to .gitignore

[api_keys]
youtube_api_key = "YOUR_YOUTUBE_DATA_API_KEY_HERE"
gemini_api_key = "YOUR_GEMINI_API_KEY_HERE"
```

**Important:** 
- Replace the placeholder values with your actual API keys
- This file is already in `.gitignore` to prevent accidental commits
- API keys cannot be edited from the web interface for security

### 3. Get API Keys

#### YouTube Data API Key:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Copy the API key to `secrets.toml`

#### Gemini API Key:
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy the API key to `secrets.toml`

### 4. Run the Application

```bash
streamlit run app.py
```

## 📋 Usage

### Settings Page
- **Prompt Configuration**: Customize the AI analysis prompt for dark pattern detection
- **API Keys**: Securely configured via `secrets.toml` file (not editable in UI)

### Application Page
- **Search Modes**:
  - Search by Keywords/Hashtags
  - Analyze specific YouTube video URLs
- **Analysis Features**:
  - Dark pattern detection
  - Regulatory violation mapping
  - Product name extraction
  - Confidence scoring

## 🔍 Dark Pattern Categories

The application detects:

1. **Implied Scarcity/Sale Mentions** - False urgency tactics
2. **Lack of Clear Disclosure** - Missing sponsorship labels
3. **Vague/Ambiguous Language** - Unclear promotional terms
4. **Inconsistent Disclosures** - Missing disclosures across formats
5. **Blurred Editorial/Advertising** - Disguised advertisements

## 📚 Regulatory Compliance

Maps violations to:
- **Code de la consommation** (French Consumer Code)
- **Loi n° 2023-451** (Influencer Marketing Law)
- **ARPP Guidelines** (Digital Advertising Standards)

## 🔒 Security Features

- API keys stored in `secrets.toml` (never in code)
- Automatic `.gitignore` protection
- No API key exposure in web interface
- Production-level error handling

## 🛠️ Technical Stack

- **Frontend**: Streamlit
- **AI Analysis**: Google Gemini 2.0 Flash
- **YouTube API**: Google YouTube Data API v3
- **Data Processing**: Pandas
- **Transcript Extraction**: youtube-transcript-api

## 📄 File Structure

```
Sundar-Form/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── secrets.toml         # API keys (create this file)
├── .gitignore               # Excludes sensitive files
├── README.md                # This file
└── venv/                    # Virtual environment
```

## ⚠️ Important Notes

- Keep your `secrets.toml` file secure and never share it
- API keys are loaded once at startup for security
- The application includes comprehensive error handling
- All analysis results include confidence scores and regulatory references 