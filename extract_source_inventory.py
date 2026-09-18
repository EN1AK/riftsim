#!/usr/bin/env python3

import os
import json
import re
from datetime import datetime
import hashlib

# Create the source manifest for all PDF files
def create_source_manifest():
    sources = []
    
    # Process loltcg_pdfs directory
    pdf_dir = "loltcg_pdfs"
    if os.path.exists(pdf_dir):
        for filename in sorted(os.listdir(pdf_dir)):
            if filename.endswith('.pdf'):
                filepath = os.path.join(pdf_dir, filename)
                
                # Extract metadata from filename
                source_id = f"source_{len(sources) + 1:03d}"
                source_document = filename
                
                # Parse date and version information from filename
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
                effective_date = date_match.group(1) if date_match else "unknown"
                
                # Determine source type based on name pattern
                source_type = determine_source_type(filename)
                language = get_language_from_filename(filename)
                
                version = extract_version_info(filename)
                
                # Create source entry
                source_entry = {
                    "source_id": source_id,
                    "source_document": source_document,
                    "source_type": source_type,
                    "language": language,
                    "version": version,
                    "date": effective_date,
                    "effective_date": effective_date,
                    "page_count": 0,  # Will be set during processing
                    "supersedes": None,
                    "possible_counterpart": None,
                    "date_confidence": "inferred",
                    "version_confidence": "inferred",
                    "notes": ""
                }
                
                sources.append(source_entry)
    
    # Process riftbound_en_rules directory  
    pdf_dir = "riftbound_en_rules"
    if os.path.exists(pdf_dir):
        for filename in sorted(os.listdir(pdf_dir)):
            if filename.endswith('.pdf'):
                filepath = os.path.join(pdf_dir, filename)
                
                # Extract metadata from filename
                source_id = f"source_{len(sources) + 1:03d}"
                source_document = filename
                
                # Parse date and version information from filename
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
                effective_date = date_match.group(1) if date_match else "unknown"
                
                # Determine source type based on name pattern
                source_type = determine_source_type(filename)
                language = get_language_from_filename(filename)
                
                version = extract_version_info(filename)
                
                # Create source entry
                source_entry = {
                    "source_id": source_id,
                    "source_document": source_document,
                    "source_type": source_type,
                    "language": language,
                    "version": version,
                    "date": effective_date,
                    "effective_date": effective_date,
                    "page_count": 0,  # Will be set during processing
                    "supersedes": None,
                    "possible_counterpart": None,
                    "date_confidence": "inferred",
                    "version_confidence": "inferred",
                    "notes": ""
                }
                
                sources.append(source_entry)
    
    return sources

def determine_source_type(filename):
    """Determine source type based on filename pattern"""
    if 'FAQ' in filename or 'faq' in filename:
        return 'faq'
    elif 'Errata' in filename or 'errata' in filename:
        return 'errata'
    elif 'Rules' in filename or 'rules' in filename:
        return 'rule'
    elif 'Patch_Notes' in filename or 'patch_notes' in filename:
        return 'official_explanation'
    else:
        return 'other'

def get_language_from_filename(filename):
    """Determine language from filename"""
    if 'zh' in filename.lower() or '中文' in filename:
        return 'zh'
    elif 'en' in filename.lower() or 'english' in filename.lower():
        return 'en'
    else:
        return 'unknown'

def extract_version_info(filename):
    """Extract version information from filename"""
    # Look for version patterns
    version_pattern = re.search(r'(v\d+(?:\.\d+)*)', filename, re.IGNORECASE)
    if version_pattern:
        return version_pattern.group(1).lower()
    
    # Look for date-based versions (like 2025.06 or 2024.Q3)
    date_version = re.search(r'\d{4}(?:\.\d+)*', filename)
    if date_version:
        return f"v{date_version.group()}"
        
    return "unknown"

def save_source_manifest(sources):
    """Save the source manifest to file"""
    manifest_data = {
        "sources": sources,
        "last_updated": datetime.now().isoformat()
    }
    
    with open("workspace/source_manifest.json", 'w', encoding='utf-8') as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    print("Creating source manifest...")
    sources = create_source_manifest()
    save_source_manifest(sources)
    
    print(f"Created manifest with {len(sources)} sources")
    for source in sources:
        print(f"- {source['source_id']}: {source['source_document']} ({source['source_type']}, {source['language']})")
