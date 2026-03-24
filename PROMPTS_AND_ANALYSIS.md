# Dark Pattern Detector - Prompts & Analysis Methodology

## Table of Contents
1. [Gemini Analysis Prompt](#gemini-analysis-prompt)
2. [Prompt Structure Breakdown](#prompt-structure-breakdown)
3. [Dark Pattern Categories](#dark-pattern-categories)
4. [Regulatory Framework](#regulatory-framework)
5. [Analysis Methodology](#analysis-methodology)
6. [JSON Response Schema](#json-response-schema)
7. [Example Analysis](#example-analysis)
8. [Prompt Customization Guide](#prompt-customization-guide)

---

## Gemini Analysis Prompt

### Complete Default Prompt

The application uses the following comprehensive prompt for dark pattern detection:

```
Here is your revised detailed analysis prompt, structured for rigorous evaluation 
and formatted to yield a JSON object output. This version incorporates all your 
requirements — including detailed issue flags, excerpts, timestamps/visual cues, 
explanations, confidence scoring, and product name extraction:

🔍 Prompt: Detailed Analysis for Dark Patterns and Deceptive Practices

Analyze the provided text, transcript, and/or video content for the presence of 
dark patterns, manipulative language, or deceptive advertising practices.

For each of the following categories, identify and extract specific excerpts from 
the description, transcript, or captions that demonstrate the issue. Explain why 
each excerpt qualifies as a dark pattern or deceptive technique.

🔎 Categories to Evaluate:

1. Implied Scarcity / Sale Mention
   Look for language that creates urgency, such as "limited time," "almost gone," 
   "backup stock," or countdowns.
   Provide quote(s) and describe how urgency is being manufactured.

2. Lack of Clear Disclosure
   Determine if any form of sponsorship, advertising, or paid partnership is disclosed.
   If disclosed, assess whether it is clear, prominent, and upfront — or buried/
   ambiguous (e.g., in hashtags or at the end).

3. Vague or Ambiguous Language
   Flag any unclear promotional terms like "collab," "sp," "ambassador," or "partner" 
   when used without also stating "Ad," "Sponsored," or "Paid Promotion."
   Explain why the term may mislead viewers.

4. Inconsistent or Incomplete Disclosures
   Evaluate whether disclosures are missing in certain formats (e.g., not repeated 
   in long-form videos, livestreams, or multi-part stories).
   Identify omissions or lack of reinforcement.

5. Blurring Editorial and Advertising Content
   Identify sections where product promotion is presented as a personal review, 
   opinion, or recommendation without clearly differentiating it from paid promotion.
   Look for emotional appeals or personal anecdotes used to mask advertising intent.

📌 Output Requirements:

For each issue, include:
- Excerpt (quoted from transcript/description/caption)
- Section Type (transcript, caption, or description)
- Reasoning (why this qualifies as a dark pattern)
- (Optional) Timestamps or visual cues if from video
- Confidence Score (0–100) — estimate how likely it is this is a deceptive tactic

Additionally, for each identified dark pattern, identify any relevant regulatory 
violations from the 'Law / Guidance' section provided below. For each applicable 
violation, include the 'Law / Guidance', 'Article / Clause', and 'High-Level 
Synthesis' from the regulatory text. If no specific violation applies, indicate 
'N/A' for the violation details.

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
          "lawGuidance": "ARPP \"Communication Publicitaire Numérique\"",
          "articleClause": "Art. b2, §1‑2",
          "highLevelSynthesis": "Demands clear advertiser identification; Requires disclosures to be visible, legible, and not obscured by other content"
        }
      ]
    },
    ...
  ],
  "overallConfidenceScore": 92,
  "productNames": [
    "Elixir Brightening UV Protector",
    "Chaseedo Elixir",
    "Loxitan Illuminating",
    "La Roche-Posay",
    "Skin Aqua Tone Up UV Essence"
  ]
}
```

---

## Prompt Structure Breakdown

### 1. Introduction & Objective
**Purpose**: Set the context and task for the AI model

```
Analyze the provided text, transcript, and/or video content for the presence of 
dark patterns, manipulative language, or deceptive advertising practices.
```

**Key Elements**:
- Clear task definition
- Scope: text, transcript, video content
- Focus: dark patterns, manipulation, deception

### 2. Category Definitions
**Purpose**: Provide specific criteria for each dark pattern type

Each category includes:
- **Name**: Clear identifier (e.g., "Implied Scarcity")
- **Description**: What to look for
- **Examples**: Specific phrases or patterns
- **Instructions**: How to analyze and report

### 3. Output Requirements
**Purpose**: Specify the format and detail level for responses

Required for each finding:
- **Excerpt**: Direct quote from content
- **Section Type**: Where it was found (transcript/description/caption)
- **Reasoning**: Why it qualifies as a dark pattern
- **Timestamps**: Optional, for video content
- **Confidence Score**: 0-100 likelihood estimate

### 4. Regulatory Mapping
**Purpose**: Connect dark patterns to legal violations

Includes:
- **Law/Guidance Name**: Legal framework
- **Article/Clause**: Specific provision
- **Verbatim Text**: Original legal language
- **High-Level Synthesis**: Plain language summary

### 5. Product Extraction
**Purpose**: Identify all mentioned products for tracking

**Instruction**: "Extract and list all product names mentioned."

### 6. JSON Schema
**Purpose**: Enforce structured, parseable output

**Benefits**:
- Consistent format
- Easy to parse programmatically
- Type safety
- Validation

---

## Dark Pattern Categories

### Category 1: Implied Scarcity / Sale Mention

**Definition**: Creating artificial urgency through scarcity claims

**What to Look For**:
- "Limited time offer"
- "Only X left in stock"
- "Almost gone"
- "Backup stock"
- Countdown timers
- "While supplies last"
- "Exclusive deal ending soon"

**Why It's Deceptive**:
- May not reflect actual inventory
- Creates pressure to purchase without research
- Exploits FOMO (Fear of Missing Out)

**Regulatory Violations**:
- Code de la consommation, Art. L121-1-1, Clause 5
- Prohibits false scarcity without reasonable basis

**Example Analysis**:
```json
{
  "category": "Implied Scarcity / Sale Mention",
  "excerpt": "Only 3 bottles left! This deal ends at midnight!",
  "sectionType": "transcript",
  "reasoning": "Creates artificial urgency with specific scarcity claim and time pressure without evidence of actual limited availability",
  "confidenceScore": 90,
  "regulatoryViolationReference": [
    {
      "lawGuidance": "Code de la consommation",
      "articleClause": "Art. L121-1-1",
      "highLevelSynthesis": "Defines specific deceptive practices; Clause 5 prohibits false scarcity or misrepresenting price/availability without reasonable basis"
    }
  ]
}
```

---

### Category 2: Lack of Clear Disclosure

**Definition**: Failure to clearly disclose commercial relationships

**What to Look For**:
- No mention of sponsorship/partnership
- Disclosure buried in description
- Disclosure only in hashtags
- Disclosure at end of long video
- Unclear terms ("collab" without "ad")

**Why It's Deceptive**:
- Viewers may not realize content is advertising
- Violates trust between influencer and audience
- Misleads about objectivity of review

**Regulatory Violations**:
- Loi n° 2023-451, Art. 4 & 5
- ARPP "Communication Publicitaire Numérique", Art. b2

**Example Analysis**:
```json
{
  "category": "Lack of Clear Disclosure",
  "excerpt": "Thanks to my friends at BrandX for sending this over! #partner",
  "sectionType": "description",
  "reasoning": "Uses vague term 'friends' and buries partnership disclosure in hashtag rather than clear upfront statement like 'Sponsored' or 'Paid Partnership'",
  "confidenceScore": 95,
  "regulatoryViolationReference": [
    {
      "lawGuidance": "Loi n° 2023-451 (9 juin 2023)",
      "articleClause": "Art. 4 & 5 (via ordonnance 6 nov 2024)",
      "highLevelSynthesis": "Mandates explicit disclosure of commercial intent; Labels must be visible, understandable, and persistent across formats"
    }
  ]
}
```

---

### Category 3: Vague or Ambiguous Language

**Definition**: Using unclear terms that obscure commercial relationships

**What to Look For**:
- "Collab" (without "ad")
- "SP" (abbreviation for sponsored)
- "Ambassador"
- "Partner"
- "Gifted"
- "PR package"

**Why It's Deceptive**:
- Terms may not be understood by all viewers
- Obscures paid nature of promotion
- Creates plausible deniability

**Regulatory Violations**:
- Loi n° 2023-451, Art. 4 & 5
- Requires clear labels like "publicité"

**Example Analysis**:
```json
{
  "category": "Vague or Ambiguous Language",
  "excerpt": "Excited to share this collab with BrandY!",
  "sectionType": "transcript",
  "reasoning": "Uses term 'collab' which could mean creative partnership, gifted product, or paid promotion. Does not clearly state if this is advertising.",
  "confidenceScore": 80,
  "regulatoryViolationReference": [
    {
      "lawGuidance": "Loi n° 2023-451 (9 juin 2023)",
      "articleClause": "Art. 4 & 5 (via ordonnance 6 nov 2024)",
      "highLevelSynthesis": "Mandates explicit disclosure of commercial intent; Labels must be visible, understandable, and persistent across formats"
    }
  ]
}
```

---

### Category 4: Inconsistent or Incomplete Disclosures

**Definition**: Disclosures that vary across formats or are missing in some contexts

**What to Look For**:
- Disclosure in video but not description
- Disclosure in first video of series but not subsequent ones
- Disclosure in static post but not in Stories
- Disclosure removed after initial posting

**Why It's Deceptive**:
- Not all viewers see all formats
- Viewers joining mid-series miss disclosure
- Creates confusion about commercial nature

**Regulatory Violations**:
- Loi n° 2023-451, Art. 4 & 5
- Labels must be "persistent across formats"

**Example Analysis**:
```json
{
  "category": "Inconsistent or Incomplete Disclosures",
  "excerpt": "As I mentioned in my last video, I'm using this amazing product...",
  "sectionType": "transcript",
  "reasoning": "References disclosure in previous video but does not repeat it in current video. Viewers watching standalone may not know this is sponsored content.",
  "confidenceScore": 75,
  "regulatoryViolationReference": [
    {
      "lawGuidance": "Loi n° 2023-451 (9 juin 2023)",
      "articleClause": "Art. 4 & 5 (via ordonnance 6 nov 2024)",
      "highLevelSynthesis": "Mandates explicit disclosure of commercial intent; Labels must be visible, understandable, and persistent across formats"
    }
  ]
}
```

---

### Category 5: Blurring Editorial and Advertising Content

**Definition**: Presenting advertising as personal opinion or editorial content

**What to Look For**:
- "I genuinely love this product" (in sponsored content)
- Personal anecdotes about product use
- Emotional storytelling around product
- Review format for sponsored content
- "This changed my life" claims

**Why It's Deceptive**:
- Exploits trust in influencer's authenticity
- Viewers may not realize opinions are paid for
- Blurs line between genuine recommendation and advertisement

**Regulatory Violations**:
- Code de la consommation, Art. L121-1
- ARPP, Art. b2 (avoid confusion)

**Example Analysis**:
```json
{
  "category": "Blurring Editorial and Advertising Content",
  "excerpt": "I've been using this serum for months and it's honestly transformed my skin. I can't imagine my routine without it!",
  "sectionType": "transcript",
  "reasoning": "Uses personal testimony and emotional language ('honestly', 'transformed', 'can't imagine') in sponsored content, presenting paid promotion as genuine personal experience",
  "confidenceScore": 85,
  "regulatoryViolationReference": [
    {
      "lawGuidance": "Code de la consommation",
      "articleClause": "Art. L121-1",
      "highLevelSynthesis": "Prohibits unfair or misleading practices; Applies to actions that materially affect consumer decisions, including deceptive urgency or omissions"
    },
    {
      "lawGuidance": "ARPP \"Communication Publicitaire Numérique\"",
      "articleClause": "Art. b2, §1-2",
      "highLevelSynthesis": "Demands clear advertiser identification; Requires disclosures to be visible, legible, and not obscured by other content"
    }
  ]
}
```

---

## Regulatory Framework

### French Consumer Protection Laws

#### 1. Code de la consommation - Art. L121-1

**Full Text**:
> "Les pratiques commerciales déloyales sont interdites. Une pratique commerciale est déloyale lorsqu'elle est contraire aux exigences de la diligence professionnelle et qu'elle altère ou est susceptible d'altérer de manière substantielle le comportement économique du consommateur normalement informé et raisonnablement attentif et avisé, à l'égard d'un bien ou d'un service."

**Translation**:
Unfair commercial practices are prohibited. A commercial practice is unfair when it is contrary to the requirements of professional diligence and it alters or is likely to substantially alter the economic behavior of the normally informed and reasonably attentive and circumspect consumer, with regard to a good or service.

**Application to Dark Patterns**:
- Broad prohibition on unfair practices
- Applies to practices that materially affect consumer decisions
- Includes deceptive urgency, omissions, misleading presentations

---

#### 2. Code de la consommation - Art. L121-1-1

**Full Text (Clause 5)**:
> "Sont réputées trompeuses au sens de l'article L. 121‑1 les pratiques commerciales qui ont pour objet : (...) 5° De proposer l'achat de produits… à un prix indiqué sans révéler les raisons plausibles… quantités… raisonnables compte tenu du produit… de l'ampleur de la publicité… et du prix proposé"

**Translation**:
Practices are deemed deceptive within the meaning of Article L. 121-1 which have the purpose of: (...) 5° Proposing the purchase of products... at an indicated price without revealing plausible reasons... quantities... reasonable given the product... the scale of advertising... and the proposed price

**Application to Dark Patterns**:
- Specifically prohibits false scarcity
- Requires reasonable basis for availability claims
- Applies to "limited stock" and "limited time" claims

---

#### 3. Loi n° 2023-451 (9 juin 2023) - Art. 1

**Full Text**:
> Defines "influence commerciale" as: "les personnes physiques ou morales qui, à titre onéreux, mobilisent leur notoriété… pour communiquer… des contenus visant à faire la promotion, directement ou indirectement, de biens… par voie électronique."

**Translation**:
Defines "commercial influence" as: "natural or legal persons who, for a fee, mobilize their notoriety... to communicate... content aimed at promoting, directly or indirectly, goods... by electronic means."

**Application to Dark Patterns**:
- Establishes legal definition of influencer marketing
- Covers all paid promotions via social media
- Applies to direct and indirect promotion

---

#### 4. Loi n° 2023-451 (9 juin 2023) - Art. 4 & 5

**Full Text**:
> Requires influencers to use clear labels such as "publicité" or "collaboration commerciale", visible and adapted to the format.

**Translation**:
Requires influencers to use clear labels such as "advertising" or "commercial collaboration", visible and adapted to the format.

**Application to Dark Patterns**:
- Mandates explicit disclosure of commercial intent
- Labels must be:
  - Visible (not hidden or buried)
  - Understandable (clear language)
  - Persistent (across all formats)
  - Adapted (appropriate for platform)

**Acceptable Labels**:
- "Publicité" (Advertising)
- "Collaboration commerciale" (Commercial collaboration)
- "Partenariat rémunéré" (Paid partnership)

**Unacceptable Labels**:
- "Collab" (too vague)
- "SP" (abbreviation, not clear)
- "#ad" (may be missed, not prominent)
- Disclosure only in description (not visible in video)

---

#### 5. ARPP "Communication Publicitaire Numérique" - Art. b2, §1-2

**Full Text**:
> "Identification of Advertiser:… must be easily identifiable… advertising presentations… should avoid confusion… conditions… must be clearly specified… notes must be immediately visible… legible… intelligible… not immersed under other information."

**Application to Dark Patterns**:
- Demands clear advertiser identification
- Requires disclosures to be:
  - Immediately visible
  - Legible (readable font/size)
  - Intelligible (understandable language)
  - Not obscured by other content

---

#### 6. ARPP "Communication Publicitaire Numérique" - Section 5

**Full Text**:
> "Digital advertising communication must respect… comfort… not be overlaying… autoplay videos… should not have audio… enabled by default."

**Application to Dark Patterns**:
- Ensures ads don't disrupt user experience
- Prevents deceptive integration of ads into UI
- Protects user comfort and control

---

### Enforcement

**Authority**: DGCCRF (Direction Générale de la Concurrence, de la Consommation et de la Répression des Fraudes)

**Penalties**:
- Fines
- Injunctions
- Public disclosure of violations
- Criminal prosecution for serious violations

**Scope**:
- Applies to all platforms (YouTube, TikTok, Instagram, etc.)
- Applies to all formats (videos, posts, stories, livestreams)
- Applies to all influencers (regardless of follower count)

---

## Analysis Methodology

### Step 1: Content Preparation

**Input Sources**:
1. **Video Title**: First impression, often contains key claims
2. **Video Description**: Detailed information, may contain disclosure
3. **Video Transcript**: Spoken content, primary source for analysis

**Combination**:
```python
combined_text = f"""
Title: {video['Title']}
Description: {video['Description']}
Transcript: {video['Transcript']}
"""
```

---

### Step 2: Gemini API Analysis

**API Configuration**:
- **Model**: gemini-2.0-flash
- **Response Format**: JSON
- **Schema Enforcement**: Enabled

**Request Structure**:
```json
{
  "contents": [
    {
      "role": "user",
      "parts": [
        {
          "text": "[PROMPT]\n\nContent to analyze:\n[COMBINED_TEXT]"
        }
      ]
    }
  ],
  "generationConfig": {
    "responseMimeType": "application/json",
    "responseSchema": {
      "type": "OBJECT",
      "properties": {...}
    }
  }
}
```

---

### Step 3: Response Parsing

**Extraction Process**:
1. Get response from API
2. Navigate to `candidates[0].content.parts[0].text`
3. Parse JSON string to Python dict
4. Validate structure
5. Extract key fields

**Validation**:
- Check for required fields
- Validate data types
- Handle missing or malformed data

---

### Step 4: Result Formatting

**Two Formats**:

1. **Raw Analysis** (for detailed view):
```python
video_data["Raw Dark Pattern Analysis"] = analysis["darkPatternAnalysis"]
```

2. **Formatted Analysis** (for summary table):
```python
formatted = format_dark_pattern_analysis(analysis["darkPatternAnalysis"])
video_data["Dark Pattern Analysis"] = formatted
```

**Formatted Example**:
```
Category: Implied Scarcity / Sale Mention
Excerpt: 'Only 3 left in stock!'
Reasoning: Creates artificial urgency without evidence
Confidence: 90
Regulatory Violations:
  - Law/Guidance: Code de la consommation, Article/Clause: Art. L121-1-1
    Synthesis: Prohibits false scarcity...
```

---

### Step 5: Confidence Scoring

**Confidence Score Guidelines**:

- **90-100**: Very High Confidence
  - Clear, unambiguous violation
  - Multiple indicators present
  - Strong evidence in transcript

- **70-89**: High Confidence
  - Clear violation with some context
  - Most indicators present
  - Good evidence

- **50-69**: Moderate Confidence
  - Possible violation
  - Some indicators present
  - Requires interpretation

- **30-49**: Low Confidence
  - Weak indicators
  - Ambiguous language
  - May be legitimate

- **0-29**: Very Low Confidence
  - Minimal evidence
  - Likely false positive
  - Requires human review

---

## JSON Response Schema

### Complete Schema Definition

```json
{
  "type": "OBJECT",
  "properties": {
    "darkPatternAnalysis": {
      "type": "ARRAY",
      "description": "List of identified dark patterns",
      "items": {
        "type": "OBJECT",
        "properties": {
          "category": {
            "type": "STRING",
            "description": "Dark pattern category name",
            "enum": [
              "Implied Scarcity / Sale Mention",
              "Lack of Clear Disclosure",
              "Vague or Ambiguous Language",
              "Inconsistent or Incomplete Disclosures",
              "Blurring Editorial and Advertising Content"
            ]
          },
          "excerpt": {
            "type": "STRING",
            "description": "Direct quote from content demonstrating the dark pattern"
          },
          "sectionType": {
            "type": "STRING",
            "description": "Where the excerpt was found",
            "enum": ["transcript", "description", "caption", "title"]
          },
          "reasoning": {
            "type": "STRING",
            "description": "Explanation of why this qualifies as a dark pattern"
          },
          "confidenceScore": {
            "type": "INTEGER",
            "description": "Confidence level (0-100) that this is a dark pattern",
            "minimum": 0,
            "maximum": 100
          },
          "regulatoryViolationReference": {
            "type": "ARRAY",
            "description": "List of applicable regulatory violations",
            "items": {
              "type": "OBJECT",
              "properties": {
                "lawGuidance": {
                  "type": "STRING",
                  "description": "Name of the law or guidance document"
                },
                "articleClause": {
                  "type": "STRING",
                  "description": "Specific article or clause reference"
                },
                "highLevelSynthesis": {
                  "type": "STRING",
                  "description": "Plain language summary of the violation"
                }
              },
              "required": ["lawGuidance", "articleClause", "highLevelSynthesis"]
            }
          }
        },
        "required": [
          "category",
          "excerpt",
          "sectionType",
          "reasoning",
          "confidenceScore",
          "regulatoryViolationReference"
        ]
      }
    },
    "overallConfidenceScore": {
      "type": "INTEGER",
      "description": "Overall confidence score (0-100) for the entire analysis",
      "minimum": 0,
      "maximum": 100
    },
    "productNames": {
      "type": "ARRAY",
      "description": "List of all product names mentioned in the content",
      "items": {
        "type": "STRING"
      }
    }
  },
  "required": ["darkPatternAnalysis", "overallConfidenceScore", "productNames"]
}
```

---

## Example Analysis

### Input Content

**Video Title**: "My Skincare Routine 2024 ✨"

**Video Description**:
```
Hey everyone! Today I'm sharing my updated skincare routine. 
These products have been game-changers for me!

Products mentioned:
- Shiseido Elixir Brightening UV Protector
- La Roche-Posay Effaclar Duo
- Skin Aqua Tone Up UV Essence

Thanks to my friends at Shiseido for the support! #skincare #beauty #partner
```

**Video Transcript**:
```
Hey guys! So I've been using the Shiseido Elixir for about three months now 
and honestly, it's transformed my skin. I know I say this a lot, but this 
one is genuinely different. 

And the best part? There's a special sale happening right now - only until 
midnight tonight! I think they said there's only a few bottles left, so if 
you want to try it, now's the time.

I also love the La Roche-Posay Effaclar. It's been a staple in my routine 
for years. And the Skin Aqua - oh my god, this is my holy grail sunscreen.

Link in the description if you want to check them out!
```

---

### Expected Analysis Output

```json
{
  "darkPatternAnalysis": [
    {
      "category": "Implied Scarcity / Sale Mention",
      "excerpt": "There's a special sale happening right now - only until midnight tonight! I think they said there's only a few bottles left",
      "sectionType": "transcript",
      "reasoning": "Creates artificial urgency with time pressure ('only until midnight') and scarcity claim ('only a few bottles left') without providing evidence or source for these claims. The phrase 'I think they said' suggests uncertainty, making the scarcity claim even more questionable.",
      "confidenceScore": 92,
      "regulatoryViolationReference": [
        {
          "lawGuidance": "Code de la consommation",
          "articleClause": "Art. L121-1-1",
          "highLevelSynthesis": "Defines specific deceptive practices; Clause 5 prohibits false scarcity or misrepresenting price/availability without reasonable basis"
        },
        {
          "lawGuidance": "Code de la consommation",
          "articleClause": "Art. L121-1",
          "highLevelSynthesis": "Prohibits unfair or misleading practices; Applies to actions that materially affect consumer decisions, including deceptive urgency or omissions"
        }
      ]
    },
    {
      "category": "Lack of Clear Disclosure",
      "excerpt": "Thanks to my friends at Shiseido for the support! #skincare #beauty #partner",
      "sectionType": "description",
      "reasoning": "Uses vague term 'friends' and 'support' instead of clear disclosure language. The #partner hashtag is buried at the end of the description and may not be seen by all viewers. Does not use required clear labels like 'Publicité' or 'Collaboration commerciale'. Disclosure is not repeated in the video itself.",
      "confidenceScore": 95,
      "regulatoryViolationReference": [
        {
          "lawGuidance": "Loi n° 2023-451 (9 juin 2023)",
          "articleClause": "Art. 4 & 5 (via ordonnance 6 nov 2024)",
          "highLevelSynthesis": "Mandates explicit disclosure of commercial intent; Labels must be visible, understandable, and persistent across formats"
        },
        {
          "lawGuidance": "ARPP \"Communication Publicitaire Numérique\"",
          "articleClause": "Art. b2, §1-2",
          "highLevelSynthesis": "Demands clear advertiser identification; Requires disclosures to be visible, legible, and not obscured by other content"
        }
      ]
    },
    {
      "category": "Vague or Ambiguous Language",
      "excerpt": "#partner",
      "sectionType": "description",
      "reasoning": "Uses hashtag #partner which is ambiguous - could mean brand partner, affiliate partner, or paid partnership. Does not clearly state the commercial nature of the relationship. French regulations require explicit terms like 'publicité' or 'collaboration commerciale'.",
      "confidenceScore": 88,
      "regulatoryViolationReference": [
        {
          "lawGuidance": "Loi n° 2023-451 (9 juin 2023)",
          "articleClause": "Art. 4 & 5 (via ordonnance 6 nov 2024)",
          "highLevelSynthesis": "Mandates explicit disclosure of commercial intent; Labels must be visible, understandable, and persistent across formats"
        }
      ]
    },
    {
      "category": "Inconsistent or Incomplete Disclosures",
      "excerpt": "Thanks to my friends at Shiseido for the support!",
      "sectionType": "description",
      "reasoning": "Disclosure appears only in the description, not in the video transcript. Viewers watching the video without reading the description will not know this is sponsored content. Violates requirement for disclosures to be persistent across formats.",
      "confidenceScore": 90,
      "regulatoryViolationReference": [
        {
          "lawGuidance": "Loi n° 2023-451 (9 juin 2023)",
          "articleClause": "Art. 4 & 5 (via ordonnance 6 nov 2024)",
          "highLevelSynthesis": "Mandates explicit disclosure of commercial intent; Labels must be visible, understandable, and persistent across formats"
        }
      ]
    },
    {
      "category": "Blurring Editorial and Advertising Content",
      "excerpt": "I've been using the Shiseido Elixir for about three months now and honestly, it's transformed my skin. I know I say this a lot, but this one is genuinely different.",
      "sectionType": "transcript",
      "reasoning": "Presents paid promotion as personal testimony using emotional language ('honestly', 'transformed', 'genuinely different'). The personal narrative and emphasis on authenticity ('I know I say this a lot, but...') masks the commercial nature of the content. Without clear upfront disclosure, viewers may believe this is an unpaid, objective review.",
      "confidenceScore": 87,
      "regulatoryViolationReference": [
        {
          "lawGuidance": "Code de la consommation",
          "articleClause": "Art. L121-1",
          "highLevelSynthesis": "Prohibits unfair or misleading practices; Applies to actions that materially affect consumer decisions, including deceptive urgency or omissions"
        },
        {
          "lawGuidance": "ARPP \"Communication Publicitaire Numérique\"",
          "articleClause": "Art. b2, §1-2",
          "highLevelSynthesis": "Demands clear advertiser identification; Requires disclosures to be visible, legible, and not obscured by other content"
        }
      ]
    }
  ],
  "overallConfidenceScore": 90,
  "productNames": [
    "Shiseido Elixir Brightening UV Protector",
    "La Roche-Posay Effaclar Duo",
    "Skin Aqua Tone Up UV Essence"
  ]
}
```

---

## Prompt Customization Guide

### When to Customize

**Scenarios**:
1. **Different Jurisdiction**: Adapting for non-French regulations
2. **Additional Categories**: Adding new dark pattern types
3. **Industry-Specific**: Focusing on specific product categories
4. **Severity Levels**: Adding priority/severity ratings
5. **Language**: Translating for non-French content

---

### How to Customize

#### 1. Access Settings Page

Navigate to **Settings** in the sidebar navigation.

#### 2. Edit Prompt

The prompt is displayed in a large text area. You can:
- Add new categories
- Modify existing category descriptions
- Update regulatory references
- Change output requirements
- Adjust JSON schema

#### 3. Auto-Save

Changes are automatically saved to session state.

#### 4. Test

Return to **Application** page and run an analysis to test your changes.

---

### Customization Examples

#### Example 1: Add New Category

**New Category**: "Fake Reviews"

```
6. Fake Reviews or Testimonials
   Look for reviews that appear fabricated, use stock photos, or lack 
   verifiable details.
   Identify language patterns common in fake reviews (excessive praise, 
   generic statements, no specific details).
```

**Update JSON Schema**:
```json
"category": {
  "type": "STRING",
  "enum": [
    "Implied Scarcity / Sale Mention",
    "Lack of Clear Disclosure",
    "Vague or Ambiguous Language",
    "Inconsistent or Incomplete Disclosures",
    "Blurring Editorial and Advertising Content",
    "Fake Reviews or Testimonials"  // NEW
  ]
}
```

---

#### Example 2: Add Severity Rating

**Modify Output Requirements**:
```
For each issue, include:
- Excerpt (quoted from transcript/description/caption)
- Section Type (transcript, caption, or description)
- Reasoning (why this qualifies as a dark pattern)
- Confidence Score (0–100)
- Severity Level (Low, Medium, High, Critical)  // NEW
```

**Update JSON Schema**:
```json
"severityLevel": {
  "type": "STRING",
  "description": "Severity of the violation",
  "enum": ["Low", "Medium", "High", "Critical"]
}
```

---

#### Example 3: Industry-Specific Focus

**For Financial Products**:

Add category:
```
6. Misleading Financial Claims
   Look for claims about returns, guarantees, or risk levels that are 
   misleading or not properly qualified.
   Identify missing disclaimers or risk warnings.
```

Add regulatory reference:
```
Financial Conduct Authority (FCA) | PRIN 2.1.1 | "A firm must conduct its 
business with integrity." | Requires honest, fair, and professional conduct 
in financial promotions
```

---

### Best Practices for Customization

1. **Maintain Structure**: Keep the overall format consistent
2. **Clear Definitions**: Ensure each category has clear criteria
3. **Regulatory Accuracy**: Verify legal references are correct
4. **Test Thoroughly**: Run multiple analyses to validate changes
5. **Document Changes**: Keep notes on customizations made
6. **Version Control**: Save different prompt versions for different use cases

---

## Conclusion

The Dark Pattern Detector's prompt system is designed to be:
- **Comprehensive**: Covers major dark pattern categories
- **Legally Grounded**: Maps to specific regulations
- **Structured**: Produces parseable, consistent output
- **Customizable**: Adaptable to different needs
- **Transparent**: Clear reasoning for each finding

This methodology ensures reliable, actionable insights for identifying deceptive practices in influencer marketing content.

---

**Document Version**: 1.0  
**Last Updated**: December 1, 2024  
**Companion to**: DOCUMENTATION.md, ARCHITECTURE_DIAGRAMS.md
