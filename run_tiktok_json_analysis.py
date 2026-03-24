#!/usr/bin/env python3
"""
TikTok JSON Transcript Analysis Runner

- Merges multiple JSON transcript export files
- Maps fields: `url` -> video URL, `transcriptContent` -> transcript
- Uses existing TikTokCSVAnalyzer to perform dark pattern analysis
- Saves results to Firebase in the same structure as CSV workflow

Usage:
  python run_tiktok_json_analysis.py path1.json path2.json path3.json [--max 50] [--all]

Environment:
  - GEMINI_API_KEY (required)
  - FIREBASE_SERVICE_ACCOUNT_PATH (optional)
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

from dotenv import load_dotenv

# Make project modules importable
sys.path.append(os.path.dirname(__file__))

# Reuse the existing analyzer
from analyze_tiktok_csv import TikTokCSVAnalyzer

load_dotenv()


def read_json_file(file_path: str) -> List[Dict[str, Any]]:
    """Read a JSON file containing a list of transcript items.

    Each item is expected to contain at least `url` and `transcriptContent` keys.
    Returns an empty list on error.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        return data
    except Exception:
        return []


def merge_transcript_items(file_paths: List[str]) -> List[Dict[str, Any]]:
    """Merge items from multiple JSON files, deduplicate by URL, and normalize fields.

    Normalized item shape:
      {
        "url": str,
        "transcript": str,   # from transcriptContent
        "available": str,    # "yes" if transcript present and not placeholder; else "no"
        "raw": dict          # original item for traceability
      }
    """
    merged: Dict[str, Dict[str, Any]] = {}

    def is_transcript_available(text: str) -> bool:
        if not text:
            return False
        # Consider WEBVTT payloads as available content
        placeholder_markers = ["No transcript available"]
        lowered = text.strip().lower()
        return all(marker.lower() not in lowered for marker in placeholder_markers)

    for path in file_paths:
        for item in read_json_file(path):
            url = (item.get("url") or "").strip()
            transcript_content = item.get("transcriptContent") or ""
            if not url:
                continue

            normalized = {
                "url": url,
                "transcript": transcript_content,
                "available": "yes" if is_transcript_available(transcript_content) else "no",
                "raw": item,
            }
            # Last-in-wins for duplicates by URL
            merged[url] = normalized

    return list(merged.values())


def run_analysis_on_items(items: List[Dict[str, Any]], max_videos: int | None, save_to_firebase: bool) -> Dict[str, Any]:
    """Run dark pattern analysis on normalized items using TikTokCSVAnalyzer internals.

    Builds a session compatible with the Firebase schema used in CSV workflow.
    """
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    firebase_service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")

    if not gemini_api_key:
        return {"success": False, "error": "GEMINI_API_KEY environment variable not set"}

    analyzer = TikTokCSVAnalyzer(
        gemini_api_key=gemini_api_key,
        firebase_service_account_path=firebase_service_account_path,
    )

    # Filter to available items
    filtered = [it for it in items if it.get("available") == "yes" and it.get("transcript")]

    # Apply max_videos cap if provided
    if isinstance(max_videos, int) and max_videos > 0:
        filtered = filtered[:max_videos]

    analysis_results: List[Dict[str, Any]] = []
    successful = 0
    failed = 0

    for idx, it in enumerate(filtered, start=1):
        url = it["url"]
        transcript = it["transcript"]
        print(f"🔍 Analyzing {idx}/{len(filtered)}: {url}")
        result = analyzer.analyze_video_content(url, transcript)

        # Ensure required fields for Firebase
        result["video_id"] = url.split("/")[-1] if "/" in url else url
        result["platform"] = "TikTok"
        result["analysis_timestamp"] = datetime.now().isoformat()

        if result.get("success"):
            successful += 1
        else:
            failed += 1
            if "dark_pattern_analysis" not in result:
                result["dark_pattern_analysis"] = result.get("error", "Analysis failed")
            result.setdefault("raw_analysis", [])
            result.setdefault("overall_confidence_score", "N/A")
            result.setdefault("product_names", "N/A")

        analysis_results.append(result)

    # Create failed entries for non-available items to keep parity with CSV structure
    non_available = [it for it in items if it.get("available") != "yes" or not it.get("transcript")]
    for it in non_available:
        url = it["url"]
        analysis_results.append({
            "success": False,
            "url": url,
            "transcript": it.get("transcript", ""),
            "error": "No transcript available",
            "video_id": url.split("/")[-1] if "/" in url else url,
            "platform": "TikTok",
            "analysis_timestamp": datetime.now().isoformat(),
            "dark_pattern_analysis": "No analysis performed - no transcript available",
            "raw_analysis": [],
            "overall_confidence_score": "N/A",
            "product_names": "N/A",
        })
        failed += 1

    session_data = {
        "sessionName": f"TikTok_JSON_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "search_type": "json_urls",
        "platform": "TikTok",
        "analysis_data": {
            "videos": analysis_results,
            "total_videos": len(items),
            "successful_analyses": successful,
            "failed_analyses": failed,
            "csv_file": None,
            "analysis_timestamp": datetime.now().isoformat(),
            "overall_confidence_score": "N/A",
        },
    }

    document_id = None
    if save_to_firebase and analyzer.firebase_manager.is_connected():
        document_id = analyzer.save_to_firebase(session_data)

    return {
        "success": True,
        "session_data": session_data,
        "document_id": document_id,
        "summary": {
            "total_videos": session_data["analysis_data"]["total_videos"],
            "successful_analyses": session_data["analysis_data"]["successful_analyses"],
            "failed_analyses": session_data["analysis_data"]["failed_analyses"],
            "saved_to_firebase": document_id is not None,
        },
    }


def parse_args(argv: List[str]) -> Dict[str, Any]:
    """Minimal CLI parser for three JSON paths, optional --max and --all.

    --max N   Limit number of available items to analyze
    --all     Analyze even when transcript is unavailable (we still record failures)
    """
    json_paths: List[str] = []
    max_videos: int | None = None
    analyze_all: bool = True  # we always include non-available as failed entries

    i = 0
    while i < len(argv):
        token = argv[i]
        if token == "--max" and i + 1 < len(argv):
            try:
                max_videos = int(argv[i + 1])
            except ValueError:
                max_videos = None
            i += 2
            continue
        elif token == "--all":
            analyze_all = True
            i += 1
            continue
        else:
            json_paths.append(token)
            i += 1

    return {
        "json_paths": json_paths,
        "max_videos": max_videos,
        "analyze_all": analyze_all,
    }


def save_results_to_json_file(results: Dict[str, Any], output_filename: str) -> bool:
    """Save analysis results to a local JSON file.
    
    Args:
        results: The complete results dictionary from run_analysis_on_items
        output_filename: Name of the output JSON file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create output directory if it doesn't exist
        output_dir = "analysis_results"
        os.makedirs(output_dir, exist_ok=True)
        
        # Full output path
        output_path = os.path.join(output_dir, output_filename)
        
        # Save to JSON file with pretty formatting
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Results saved to: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving results to JSON file: {str(e)}")
        return False


def main() -> None:
    args = parse_args(sys.argv[1:])
    json_paths = args["json_paths"]
    max_videos = args["max_videos"]

    if len(json_paths) < 1:
        print("❌ Please provide at least one JSON transcript file path")
        print("   Example: python run_tiktok_json_analysis.py transcripts1.json transcripts2.json transcripts3.json --max 50")
        sys.exit(1)

    print("🚀 Merging JSON transcript files...")
    items = merge_transcript_items(json_paths)
    print(f"📦 Merged items: {len(items)}")

    results = run_analysis_on_items(items, max_videos=max_videos, save_to_firebase=True)

    if results.get("success"):
        print("🎉 JSON transcript analysis completed successfully!")
        print(f"📊 Document ID: {results.get('document_id')}")
        print(f"📊 Total videos: {results['summary']['total_videos']}")
        print(f"📊 Successful analyses: {results['summary']['successful_analyses']}")
        print(f"📊 Failed analyses: {results['summary']['failed_analyses']}")
        
        # Save results to local JSON file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"tiktok_analysis_results_{timestamp}.json"
        save_results_to_json_file(results, output_filename)
    else:
        print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
