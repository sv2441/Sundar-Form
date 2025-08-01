"""
Configuration module for the Dark Pattern Detector application.
Handles default prompts, session state initialization, and API key management.
"""

import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()


def get_default_gemini_prompt():
    """
    Get the default Gemini analysis prompt.
    
    Returns:
        str: Default prompt for dark pattern analysis
    """
    return """Here is your revised detailed analysis prompt, structured for rigorous evaluation and formatted to yield a JSON object output. This version incorporates all your requirements — including detailed issue flags, excerpts, timestamps/visual cues, explanations, confidence scoring, and product name extraction:
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


def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if 'gemini_prompt' not in st.session_state:
        st.session_state.gemini_prompt = get_default_gemini_prompt()
    
    if 'analyzed_results' not in st.session_state:
        st.session_state['analyzed_results'] = []


def get_api_keys():
    """
    Retrieve API keys from environment variables.
    
    Returns:
        tuple: (youtube_api_key, gemini_api_key) or (None, None) if missing
    """
    try:
        # Get API keys from environment variables
        youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if not youtube_api_key:
            st.warning("⚠️ YouTube API key not found in environment variables.")
            st.info("Please set YOUTUBE_API_KEY environment variable.")
        
        if not gemini_api_key:
            st.warning("⚠️ Gemini API key not found in environment variables.")
            st.info("Please set GEMINI_API_KEY environment variable.")
        
        return youtube_api_key, gemini_api_key
        
    except Exception as e:
        st.error(f"❌ Error retrieving API keys from environment: {e}")
        return None, None


def get_airtable_config():
    """
    Retrieve Airtable configuration from environment variables.
    
    Returns:
        tuple: (airtable_api_key, airtable_base_id) or (None, None) if missing
    """
    try:
        airtable_api_key = os.getenv('AIRTABLE_API_KEY')
        airtable_base_id = os.getenv('AIRTABLE_BASE_ID')
        
        if not airtable_api_key:
            st.warning("⚠️ Airtable API key not found in environment variables.")
            st.info("Please set AIRTABLE_API_KEY environment variable.")
        
        if not airtable_base_id:
            st.warning("⚠️ Airtable Base ID not found in environment variables.")
            st.info("Please set AIRTABLE_BASE_ID environment variable.")
        
        return airtable_api_key, airtable_base_id
        
    except Exception as e:
        st.error(f"❌ Error retrieving Airtable configuration from environment: {e}")
        return None, None