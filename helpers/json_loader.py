import json
from pathlib import Path

def load_json(relative_path):
    project_root=Path(__file__).resolve().parent.parent
    file_path=project_root/relative_path
    with open(file_path,"r",encoding="utf-8") as file:
        return json.load(file)

def load_chapter(chapter_number):
    return load_json(f"data/chapter_{chapter_number}.json")