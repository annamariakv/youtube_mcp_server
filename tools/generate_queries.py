import openai
import os
import asyncio
import argparse
from typing import List
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment variables from .env file
load_dotenv()

# Constants
MAX_RETRIES = 3
SEMAPHORE_LIMIT = 5

async def generate_youtube_queries(user_query: str) -> List[str]:
    """
    Generate 5 YouTube search queries based on the user's input query using OpenAI.
    
    Args:
        user_query (str): The original query from the user
        
    Returns:
        List[str]: List of 5 generated YouTube search queries
    """
    # Get API key from environment variable
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    # Initialize AsyncOpenAI client
    async_client = AsyncOpenAI()
    
    # Create semaphore for rate limiting
    semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)
    
    # Create the prompt for the LLM
    system_prompt = "You are a helpful assistant that generates YouTube search queries. Return the queries in a JSON array format."
    user_prompt = f"""Given the following query, generate 5 different YouTube search queries that would help find relevant videos.
    Make the queries diverse and specific, including different aspects of the topic.
    Original query: {user_query}
    
    Return the queries in a JSON array format like this:
    {{"queries": ["query1", "query2", "query3", "query4", "query5"]}}"""
    
    for retries in range(MAX_RETRIES):
        async with semaphore:
            print(f"Attempt {retries + 1}/{MAX_RETRIES}: Generating queries...")
            try:
                # Call OpenAI API using the latest format
                response = await async_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.7,
                    max_tokens=150
                )
                
                # Extract and process the generated queries
                generated_text = response.choices[0].message.content.strip()
                try:
                    import json
                    result = json.loads(generated_text)
                    queries = result.get("queries", [])
                    if len(queries) > 0:
                        return queries[:5]  # Ensure we have at most 5 queries
                except json.JSONDecodeError:
                    # Fallback to line-based parsing if JSON parsing fails
                    queries = [query.strip() for query in generated_text.split('\n') if query.strip()]
                    return queries[:5]
                
            except Exception as e:
                print(f"Error on attempt {retries + 1}: {str(e)}")
                if retries == MAX_RETRIES - 1:
                    print("Max retries reached. Could not generate queries.")
                    return []
                await asyncio.sleep(1)  # Wait before retrying
    
    return []

async def main_async(search_query: str):
    try:
        # Generate queries
        queries = await generate_youtube_queries(search_query)
        
        # Display results
        print("\nGenerated YouTube search queries:")
        for i, query in enumerate(queries, 1):
            print(f"{i}. {query}")
            
    except ValueError as e:
        print(f"Error: {str(e)}")
        print("Please make sure you have created a .env file with your OPENAI_API_KEY")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Generate YouTube search queries using OpenAI')
    parser.add_argument('search_query', type=str, help='The search query to generate variations for')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the async main function
    asyncio.run(main_async(args.search_query))

if __name__ == "__main__":
    main()
