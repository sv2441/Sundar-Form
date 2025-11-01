# TikTok Analysis Firebase Structure Documentation

## 📊 **Firebase Database Structure Overview**

The TikTok analysis system stores data in Firebase Firestore with a well-organized structure designed for scalability and easy querying.

---

## 🗂️ **Collection Structure**

### **Main Collection: `influencer-marketing`**

All TikTok analysis sessions are stored in the `influencer-marketing` collection. Each document represents a complete analysis session.

---

## 📄 **Document Structure**

### **Document ID Format**
```
TikTok_CSV_Analysis_YYYYMMDD_HHMMSS
```
Example: `TikTok_CSV_Analysis_20241201_143022`

### **Document Fields**

```json
{
  "sessionName": "TikTok_CSV_Analysis_20241201_143022",
  "search_type": "csv_urls",
  "platform": "TikTok",
  "analysis_data": {
    "videos": [...],
    "total_videos": 10,
    "successful_analyses": 8,
    "failed_analyses": 2,
    "csv_file": "tiktok-transcripts.csv",
    "analysis_timestamp": "2024-12-01T14:30:22",
    "overall_confidence_score": "N/A"
  },
  "created_at": "2024-12-01T14:30:22",
  "created_by": "tiktok_csv_analyzer",
  "video_count": 10,
  "overall_confidence_score": "N/A"
}
```

---

## 🎯 **Field Descriptions**

### **Top-Level Fields**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `sessionName` | String | Unique session identifier | `"TikTok_CSV_Analysis_20241201_143022"` |
| `search_type` | String | Type of analysis performed | `"csv_urls"` |
| `platform` | String | Platform being analyzed | `"TikTok"` |
| `analysis_data` | Object | Complete analysis results | See below |
| `created_at` | String | ISO timestamp of creation | `"2024-12-01T14:30:22"` |
| `created_by` | String | User/system that created session | `"tiktok_csv_analyzer"` |
| `video_count` | Number | Total number of videos analyzed | `10` |
| `overall_confidence_score` | String/Number | Overall confidence score | `"N/A"` or `85` |

### **Analysis Data Structure**

```json
{
  "videos": [
    {
      "success": true,
      "url": "https://www.tiktok.com/@user/video/1234567890",
      "transcript": "Video transcript content...",
      "dark_pattern_analysis": "Formatted analysis text",
      "raw_analysis": [...],
      "overall_confidence_score": 85,
      "product_names": "Product A, Product B",
      "video_id": "1234567890",
      "platform": "TikTok",
      "analysis_timestamp": "2024-12-01T14:30:22"
    }
  ],
  "total_videos": 10,
  "successful_analyses": 8,
  "failed_analyses": 2,
  "csv_file": "tiktok-transcripts.csv",
  "analysis_timestamp": "2024-12-01T14:30:22",
  "overall_confidence_score": "N/A"
}
```

---

## 🎬 **Individual Video Analysis Structure**

### **Successful Analysis Result**

```json
{
  "success": true,
  "url": "https://www.tiktok.com/@ule.beauty/video/7450181837403507990",
  "transcript": "Have you heard of ulle? This new skincare brand...",
  "dark_pattern_analysis": "🔍 Dark Pattern Analysis:\n\n1. **Hidden Costs Pattern**\n   - Excerpt: 'Free trial but hidden fees'\n   - Confidence: 85%\n   - Reasoning: Misleading pricing information...",
  "raw_analysis": [
    {
      "category": "Hidden Costs",
      "excerpt": "Free trial but hidden fees",
      "sectionType": "transcript",
      "reasoning": "Misleading pricing information that doesn't clearly disclose all costs",
      "confidenceScore": 85,
      "regulatoryViolationReference": [
        {
          "lawGuidance": "FTC Guidelines",
          "articleClause": "Section 5",
          "highLevelSynthesis": "Deceptive pricing practices"
        }
      ]
    }
  ],
  "overall_confidence_score": 85,
  "product_names": "ulle, skincare, botanical extract",
  "video_id": "7450181837403507990",
  "platform": "TikTok",
  "analysis_timestamp": "2024-12-01T14:30:22"
}
```

### **Failed Analysis Result**

```json
{
  "success": false,
  "url": "https://www.tiktok.com/@user/video/1234567890",
  "transcript": "No transcript available",
  "error": "No transcript available",
  "video_id": "1234567890",
  "platform": "TikTok",
  "analysis_timestamp": "2024-12-01T14:30:22",
  "dark_pattern_analysis": "No analysis performed - no transcript available",
  "raw_analysis": [],
  "overall_confidence_score": "N/A",
  "product_names": "N/A"
}
```

---

## 🔍 **Dark Pattern Analysis Structure**

### **Raw Analysis Array**

Each video's `raw_analysis` field contains an array of detected dark patterns:

```json
[
  {
    "category": "Hidden Costs",
    "excerpt": "Free trial but hidden fees",
    "sectionType": "transcript",
    "reasoning": "Misleading pricing information that doesn't clearly disclose all costs",
    "confidenceScore": 85,
    "regulatoryViolationReference": [
      {
        "lawGuidance": "FTC Guidelines",
        "articleClause": "Section 5",
        "highLevelSynthesis": "Deceptive pricing practices"
      },
      {
        "lawGuidance": "GDPR",
        "articleClause": "Article 7",
        "highLevelSynthesis": "Consent manipulation"
      }
    ]
  },
  {
    "category": "Urgency Scarcity",
    "excerpt": "Limited time offer, only 24 hours left",
    "sectionType": "transcript",
    "reasoning": "Creates false urgency to pressure users into making decisions",
    "confidenceScore": 92,
    "regulatoryViolationReference": [
      {
        "lawGuidance": "FTC Guidelines",
        "articleClause": "Section 5",
        "highLevelSynthesis": "False urgency and scarcity tactics"
      }
    ]
  }
]
```

---

## 📈 **Query Examples**

### **Get All TikTok Sessions**
```javascript
// Firestore query
db.collection('influencer-marketing')
  .where('platform', '==', 'TikTok')
  .orderBy('created_at', 'desc')
```

### **Get Sessions by Date Range**
```javascript
// Firestore query
db.collection('influencer-marketing')
  .where('platform', '==', 'TikTok')
  .where('created_at', '>=', '2024-12-01T00:00:00')
  .where('created_at', '<=', '2024-12-01T23:59:59')
```

### **Get Sessions with High Confidence Scores**
```javascript
// Firestore query
db.collection('influencer-marketing')
  .where('platform', '==', 'TikTok')
  .where('overall_confidence_score', '>', 80)
```

### **Get Failed Analysis Sessions**
```javascript
// Firestore query
db.collection('influencer-marketing')
  .where('platform', '==', 'TikTok')
  .where('analysis_data.failed_analyses', '>', 0)
```

---

## 🔧 **Firebase Operations**

### **Save Session**
```python
# Python code
document_id = firebase_manager.save_analysis_session(
    sessionName="TikTok_CSV_Analysis_20241201_143022",
    analysis_data=analysis_data,
    search_type="csv_urls",
    platform="TikTok",
    created_by="tiktok_csv_analyzer"
)
```

### **Retrieve Session**
```python
# Python code
session_data = firebase_manager.get_session_by_name("TikTok_CSV_Analysis_20241201_143022")
```

### **Get All Sessions**
```python
# Python code
all_sessions = firebase_manager.get_all_sessions()
```

### **Delete Session**
```python
# Python code
success = firebase_manager.delete_session("TikTok_CSV_Analysis_20241201_143022")
```

---

## 📊 **Data Statistics**

### **Session Metadata**
- **Total Videos**: Number of videos in the CSV file
- **Successful Analyses**: Videos successfully analyzed
- **Failed Analyses**: Videos that failed analysis
- **Success Rate**: `(successful_analyses / total_videos) * 100`

### **Analysis Quality Metrics**
- **Overall Confidence Score**: Average confidence across all patterns
- **Pattern Categories**: Types of dark patterns detected
- **Regulatory Violations**: Number of regulatory violations found

---

## 🛡️ **Security Rules**

### **Recommended Firestore Security Rules**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /influencer-marketing/{document} {
      allow read, write: if request.auth != null;
      allow read: if resource.data.created_by == request.auth.uid;
    }
  }
}
```

---

## 🔄 **Data Flow**

1. **CSV Processing** → Load TikTok URLs and transcripts
2. **Analysis** → Process each video through Gemini API
3. **Structured Output** → Parse dark pattern analysis
4. **Firebase Storage** → Save complete session data
5. **Retrieval** → Query sessions for reporting/analysis

---

## 📋 **Best Practices**

### **Data Organization**
- ✅ Use consistent session naming convention
- ✅ Include comprehensive metadata
- ✅ Store both raw and formatted analysis
- ✅ Maintain audit trail with timestamps

### **Performance Optimization**
- ✅ Index on `platform`, `created_at`, `overall_confidence_score`
- ✅ Limit video count per session (max 50)
- ✅ Use pagination for large result sets

### **Data Integrity**
- ✅ Validate all required fields before saving
- ✅ Handle failed analyses gracefully
- ✅ Maintain backward compatibility

---

**Documentation Generated**: December 1, 2024  
**Version**: 1.0  
**Status**: ✅ **Production Ready** 