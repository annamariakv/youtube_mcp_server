import os
import sys
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
API_KEY = os.getenv('YOUTUBE_API_KEY')
if not API_KEY:
    print("ERROR: Please set the YOUTUBE_API_KEY environment variable.")
    sys.exit(1)

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtube_search(query, max_results=3):
    """
    Searches YouTube for videos based on a query and fetches their metadata.

    Args:
        query (str): The search term.
        max_results (int): The maximum number of results to return.

    Returns:
        list: A list of dictionaries, where each dictionary contains metadata 
              for a video. Returns None if an error occurs.
    """
    if API_KEY == "YOUR_API_KEY":
        print("ERROR: Please replace 'YOUR_API_KEY' with your actual YouTube Data API key.")
        return None

    try:
        # Build the YouTube service object
        youtube = build(
            YOUTUBE_API_SERVICE_NAME, 
            YOUTUBE_API_VERSION, 
            developerKey=API_KEY
        )

        # 1. Search for videos to get their IDs
        # This part calls the search.list endpoint of the API.
        search_response = youtube.search().list(
            q=query,
            part="id,snippet", # We need the id and basic snippet info
            maxResults=max_results,
            type="video" # We are only interested in videos
        ).execute()

        video_ids = []
        videos_metadata = []

        # Extract video IDs and basic info from the search results
        for item in search_response.get("items", []):
            video_ids.append(item["id"]["videoId"])

        if not video_ids:
            print("No videos found for the query.")
            return []

        # 2. Fetch detailed video metadata using the collected IDs
        # This part calls the videos.list endpoint for more details.
        # Calling this endpoint is more efficient than getting all details from search,
        # and it provides richer information like statistics.
        video_response = youtube.videos().list(
            id=",".join(video_ids),
            part="snippet,statistics" # Get snippet and statistics
        ).execute()

        # Process the detailed response
        for item in video_response.get("items", []):
            metadata = {
                "title": item["snippet"]["title"],
                "video_id": item["id"],
                "video_url": f"https://www.youtube.com/watch?v={item['id']}",
                "description": item["snippet"]["description"],
                "channel_title": item["snippet"]["channelTitle"],
                "published_at": item["snippet"]["publishedAt"],
                "view_count": item["statistics"].get("viewCount", 0),
                "like_count": item["statistics"].get("likeCount", 0),
                "comment_count": item["statistics"].get("commentCount", 0)
            }
            videos_metadata.append(metadata)

        return videos_metadata

    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred: {e.content}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_results_from_youtube.py <search_query> [max_results]")
        sys.exit(1)
    
    search_query = sys.argv[1]
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    
    results = youtube_search(search_query, max_results=max_results)

    if results:
        print(f"--- Found {len(results)} videos for '{search_query}' ---\n")
        # Loop through the results and print the metadata
        for i, video in enumerate(results, 1):
            print(f"--- Result {i} ---")
            print(f"Title: {video['title']}")
            print(f"URL: {video['video_url']}")
            print(f"Channel: {video['channel_title']}")
            print(f"Views: {video.get('view_count', 'N/A')}")
            print(f"Likes: {video.get('like_count', 'N/A')}")
            print(f"Published Date: {video['published_at']}")
            print(f"Description: {video['description'][:150]}...") # Uncomment to see description
            print("-" * 20 + "\n")

