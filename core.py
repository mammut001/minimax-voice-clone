import os
import json
import requests

# Constants
# Try to get API_KEY from environment variable, fallback to "xxxx" placeholders
API_KEY = os.getenv("MINIMAX_API_KEY", "fallback")
BASE_URL = "https://api.minimax.io"

def get_headers(is_multipart=False):
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    if not is_multipart:
        headers["Content-Type"] = "application/json"
    return headers

def upload_audio_file(file_path):
    """
    Step 1: Upload audio file to MiniMax, return file_id
    """
    url = f"{BASE_URL}/v1/files/upload"
    params = {"GroupId": None} # Add group id if needed
    
    file_name = os.path.basename(file_path)
    mime_type = "audio/wav"
    if file_name.endswith(".mp3"): mime_type = "audio/mpeg"
    elif file_name.endswith(".m4a"): mime_type = "audio/mp4"

    files = {
        "file": (file_name, open(file_path, "rb"), mime_type)
    }
    data = {
        "purpose": "voice_clone"
    }
    
    response = requests.post(url, headers=get_headers(is_multipart=True), files=files, data=data)
    res_json = response.json()
    
    if res_json.get("base_resp", {}).get("status_code") == 0:
        return res_json["file"]["file_id"]
    else:
        print(f"Upload failed: {res_json}")
        return None

def register_voice_clone(file_id, voice_id):
    """
    Step 2: Register the cloned voice with MiniMax
    """
    url = f"{BASE_URL}/v1/voice_clone"
    payload = {
        "file_id": file_id,
        "voice_id": voice_id,
        "model": "voice-clone-p0",
        "need_noise_reduction": False,
        "need_volume_normalization": True
    }
    
    response = requests.post(url, headers=get_headers(), json=payload)
    res_json = response.json()
    
    if res_json.get("base_resp", {}).get("status_code") == 0:
        print(f"Successfully registered voice: {voice_id}")
        return True
    else:
        print(f"Clone registration failed: {res_json}")
        return False

def list_voices():
    """
    Fetch all cloned voices
    """
    url = f"{BASE_URL}/v1/get_voice"
    payload = {"voice_type": "voice_cloning"}
    
    response = requests.post(url, headers=get_headers(), json=payload)
    res_json = response.json()
    
    if res_json.get("base_resp", {}).get("status_code") == 0:
        voices = res_json.get("voice_cloning") or res_json.get("voices") or []
        return voices
    else:
        print(f"Failed to fetch voices: {res_json}")
        return []

def delete_voice(voice_id):
    """
    Delete a cloned voice
    """
    url = f"{BASE_URL}/v1/delete_voice"
    payload = {
        "voice_type": "voice_cloning",
        "voice_id": voice_id
    }
    
    response = requests.post(url, headers=get_headers(), json=payload)
    res_json = response.json()
    
    if res_json.get("base_resp", {}).get("status_code") == 0:
        print(f"Deleted voice: {voice_id}")
        return True
    else:
        print(f"Failed to delete voice {voice_id}: {res_json}")
        return False

def text_to_speech(text, voice_id, output_path="output.mp3", emotion="happy"):
    """
    Play/Generate voice from text (TTS)
    """
    url = f"{BASE_URL}/v1/t2a_v2"
    payload = {
        "model": "speech-01-turbo-240224",
        "text": text,
        "voice_setting": {
            "voice_id": voice_id,
            "speed": 1.0,
            "vol": 1.0,
            "pitch": 0,
            "emotion": emotion
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3",
            "channel": 1
        }
    }
    
    response = requests.post(url, headers=get_headers(), json=payload)
    res_json = response.json()
    
    if res_json.get("base_resp", {}).get("status_code") == 0:
        hex_audio = res_json["data"]["audio"]
        audio_bytes = bytes.fromhex(hex_audio)
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        print(f"TTS generated and saved to {output_path}")
        return output_path
    else:
        print(f"TTS failed: {res_json}")
        return None

if __name__ == "__main__":
    import sys
    # Simple CLI for testing
    if len(sys.argv) < 2:
        print("Usage: python core.py [list|delete|clone|tts]")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "list":
        voices = list_voices()
        print(json.dumps(voices, indent=2, ensure_ascii=False))
    elif cmd == "delete" and len(sys.argv) > 2:
        delete_voice(sys.argv[2])
    elif cmd == "clone" and len(sys.argv) > 3:
        # python core.py clone sample.wav my_new_voice_id
        fid = upload_audio_file(sys.argv[2])
        if fid:
            register_voice_clone(fid, sys.argv[3])
    elif cmd == "tts" and len(sys.argv) > 3:
        # python core.py tts "Hello world" voice_id
        text_to_speech(sys.argv[2], sys.argv[3])
