#!/usr/bin/env python3

import os
import json
from datetime import datetime

# Create processing tasks for each source
def create_processing_tasks():
    # Read the source manifest 
    with open("workspace/source_manifest.json", 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    tasks = []
    
    # Create a simple extraction task for each source (this is simplified - in practice, we would extract actual text from PDFs)
    for source in manifest["sources"]:
        task_id = f"task_{len(tasks) + 1:03d}"
        
        # For demonstration purposes, I'll create a simple task structure
        # In reality, this would be based on the actual content and page breakdown of each PDF
        task = {
            "task_id": task_id,
            "source_id": source["source_id"],
            "page_start": 1,
            "page_end": 10,  # Placeholder - real implementation would determine from PDF
            "section": "main",
            "status": "pending", 
            "assigned_role": None,
            "notes": f"Extract rules from {source['source_document']}"
        }
        
        tasks.append(task)
    
    return tasks

def save_processing_tasks(tasks):
    """Save the processing tasks to a JSON file"""
    task_data = {
        "tasks": tasks,
        "last_updated": datetime.now().isoformat(),
        "total_count": len(tasks),
        "status_summary": {
            "pending": sum(1 for t in tasks if t["status"] == "pending"),
            "running": 0,
            "completed": 0,
            "failed": 0
        }
    }
    
    with open("workspace/processing_tasks.json", 'w', encoding='utf-8') as f:
        json.dump(task_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    print("Creating processing tasks...")
    tasks = create_processing_tasks()
    save_processing_tasks(tasks)
    
    print(f"Created {len(tasks)} extraction tasks")
    for task in tasks[:5]:  # Show first 5 tasks
        print(f"- {task['task_id']}: {task['source_id']} ({task['status']})")
