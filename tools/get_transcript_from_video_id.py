import asyncio
import aiohttp
import ssl
import json
from typing import Dict, List

async def fetch_transcript(session: aiohttp.ClientSession, video_id: str) -> tuple[str, str]:
    url = f"https://ytb2mp4.com/api/fetch-transcript?url=https://www.youtube.com/watch?v={video_id}"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                try:
                    data = await response.json()
                    if isinstance(data, dict) and "transcript" in data:
                        if isinstance(data["transcript"], list):
                            transcript = " ".join([item["text"] for item in data["transcript"]])
                        elif isinstance(data["transcript"], str):
                            transcript = data["transcript"]
                        else:
                            transcript = "Unexpected transcript format."
                    else:
                        transcript = "Transcript key not found in API response."
                except Exception as e:
                    transcript = f"Error decoding JSON: {str(e)}"
            else:
                transcript = f"Error fetching transcript: {response.status}"
    except Exception as e:
        transcript = f"Request failed: {str(e)}"
    
    return video_id, transcript

async def get_transcripts(video_ids: List[str]) -> Dict[str, str]:
    transcripts = {}
    
    # Create SSL context that doesn't verify certificates
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_transcript(session, video_id) for video_id in video_ids]
        results = await asyncio.gather(*tasks)
        
        for video_id, transcript in results:
            transcripts[video_id] = transcript
    
    return transcripts

async def transcripts():
    import sys
    if len(sys.argv) != 2:
        print('Usage: python get_transcript_from_video_id.py ["videoid1", "videoid2"]')
        return
    
    try:
        # Parse the JSON string of video IDs
        video_ids = json.loads(sys.argv[1])
        if not isinstance(video_ids, list):
            raise ValueError("Input must be a list of video IDs")
        
        transcripts = await get_transcripts(video_ids)
        
        # Print results in a more readable format
        print("\n=== Transcripts ===\n")
        for video_id, transcript in transcripts.items():
            print(f"Video ID: {video_id}")
            print(f"Transcript: {transcript[:200]}...")  # Show first 200 characters
            print("-" * 50 + "\n")

    except json.JSONDecodeError:
        print("Error: Invalid JSON format. Please provide video IDs in the format: [\"videoid1\", \"videoid2\"]")
    except ValueError as e:
        print(f"Error: {str(e)}")

