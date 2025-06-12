import os
import sys
import json
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
        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=max_results,
            type="video"
        ).execute()

        video_ids = []
        videos_metadata = []

        # Extract video IDs and basic info from the search results
        for item in search_response.get("items", []):
            video_ids.append(item["id"]["videoId"])

        if not video_ids:
            print(f"No videos found for the query: {query}")
            return []

        # 2. Fetch detailed video metadata using the collected IDs
        video_response = youtube.videos().list(
            id=",".join(video_ids),
            part="snippet,statistics"
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
    if len(sys.argv) != 2:
        print('Usage: python get_results_from_youtube.py \'["query1", "query2"]\'')
        sys.exit(1)
    
    try:
        # Parse the JSON string of queries
        queries = json.loads(sys.argv[1])
        if not isinstance(queries, list):
            raise ValueError("Input must be a list of search queries")
        
        # Process each query
        for query in queries:
            results = youtube_search(query)
            
            if results:
                print(f"\n=== Results for query: '{query}' ===\n")
                # Loop through the results and print the metadata
                for i, video in enumerate(results, 1):
                    print(f"--- Result {i} ---")
                    print(f"Title: {video['title']}")
                    print(f"URL: {video['video_url']}")
                    print(f"Channel: {video['channel_title']}")
                    print(f"Views: {video.get('view_count', 'N/A')}")
                    print(f"Likes: {video.get('like_count', 'N/A')}")
                    print(f"Published Date: {video['published_at']}")
                    print(f"Description: {video['description'][:150]}...")
                    print("-" * 20)
            else:
                print(f"\nNo results found for query: '{query}'")
            
            print("\n" + "="*50 + "\n")  # Separator between queries

    except json.JSONDecodeError:
        print("Error: Invalid JSON format. Please provide queries in the format: [\"query1\", \"query2\"]")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

