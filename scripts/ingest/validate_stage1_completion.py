#!/usr/bin/env python3

import json
import os

def validate_stage1_completion():
    """Validate that Stage 1 completion criteria are met"""
    
    print("Validating Stage 1 completion...")
    
    # Check if required files exist and have content
    required_files = [
        "workspace/source_manifest.json",
        "workspace/processing_tasks.json", 
        "workspace/progress.json",
        "workspace/README_STATE.md"
    ]
    
    all_valid = True
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"ERROR: Required file missing - {file_path}")
            all_valid = False
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if not content.strip():
            print(f"ERROR: File is empty - {file_path}")
            all_valid = False
        else:
            print(f"✓ {file_path} exists and has content")
    
    # Check source manifest
    with open("workspace/source_manifest.json", 'r', encoding='utf-8') as f:
        manifest = json.load(f)
        
    if len(manifest["sources"]) == 0:
        print("ERROR: No sources found in manifest")
        all_valid = False
    else:
        print(f"✓ Source manifest contains {len(manifest['sources'])} sources")
    
    # Check processing tasks  
    with open("workspace/processing_tasks.json", 'r', encoding='utf-8') as f:
        tasks_data = json.load(f)
        
    if len(tasks_data["tasks"]) == 0:
        print("ERROR: No processing tasks found")
        all_valid = False
    else:
        print(f"✓ Processing tasks contain {len(tasks_data['tasks'])} tasks")
        
    # Check progress file indicates stage 1 is completed
    with open("workspace/progress.json", 'r', encoding='utf-8') as f:
        progress = json.load(f)
        
    if progress["current_stage"] != "Stage 1 - Source Inventory + PDF Preprocessing":
        print("ERROR: Progress file does not show Stage 1 completed")
        all_valid = False
    else:
        print("✓ Progress file correctly shows Stage 1 as completed")
    
    # Check README_STATE.md
    with open("workspace/README_STATE.md", 'r', encoding='utf-8') as f:
        readme_content = f.read()
        
    if "Stage 1 - Source Inventory + PDF Preprocessing" not in readme_content:
        print("ERROR: README does not show Stage 1 as completed")
        all_valid = False
    else:
        print("✓ README correctly shows Stage 1 as completed")
        
    if all_valid:
        print("\n✅ All validation checks passed! Stage 1 is properly completed.")
        return True
    else:
        print("\n❌ Some validation checks failed!")
        return False

if __name__ == "__main__":
    validate_stage1_completion()