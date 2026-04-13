import sys
import json
from core import list_voices, delete_voice

def main():
    if len(sys.argv) < 2:
        print("Usage: python manage.py [list|delete VOICE_ID]")
        return
        
    cmd = sys.argv[1]
    
    if cmd == "list":
        voices = list_voices()
        print(f"\nFound {len(voices)} cloned voices:")
        print("-" * 50)
        for v in voices:
            name = v.get("name", "Unnamed")
            vid = v.get("voice_id", "N/A")
            print(f"Name: {name}")
            print(f"ID:   {vid}")
            print("-" * 50)
            
    elif cmd == "delete" and len(sys.argv) > 2:
        vid = sys.argv[2]
        if delete_voice(vid):
            print(f"Successfully deleted {vid}")
        else:
            print(f"Failed to delete {vid}")
    else:
        print("Invalid command or missing VOICE_ID")

if __name__ == "__main__":
    main()
