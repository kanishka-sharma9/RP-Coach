from crewai import Agent, Task, Crew, Process, LLM
from langchain.tools import tool
from googleapiclient.discovery import build
from typing import List, Dict
import json
import os
from dotenv import load_dotenv
load_dotenv()

# import google.generativeai as genai
# genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# llm = LLM(
#     model="gemini-1.5-flash",
#     temperature=0.5,
#     base_url="https://generativelanguage.googleapis.com",
#     api_key=os.getenv('GOOGLE_API_KEY')
# )

llm=LLM(model="ollama/llama3.1", base_url="http://localhost:11434")

class RPStrengthTools:
    @tool
    def scrape_video_data(self, video_id: str) -> Dict:
        """
        Scrapes detailed data from a specific RP Strength YouTube video
        Args:
            video_id: The YouTube video ID to scrape
        Returns:
            Dictionary containing video information or empty dict if video not found
        """
        try:
            youtube = build('youtube', 'v3', 
                        developerKey=os.getenv('YOUTUBE_API_KEY'))
            
            # Get video details
            request = youtube.videos().list(
                part='snippet,statistics,contentDetails,topicDetails',
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                print(f"No video found with ID: {video_id}")
                return {}
                
            video_data = response['items'][0]
            
            # Extract data with safe dictionary access
            snippet = video_data.get('snippet', {})
            statistics = video_data.get('statistics', {})
            content_details = video_data.get('contentDetails', {})
            
            # Build response dictionary with safety checks
            result = {
                'video_id': video_id,
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'published_at': snippet.get('publishedAt', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'tags': snippet.get('tags', []),
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0)),
                'duration': content_details.get('duration', ''),
                'definition': content_details.get('definition', ''),
                'caption': content_details.get('caption', 'false') == 'true',
                'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', '')
            }
            
            # Try to extract exercise-related metadata
            try:
                description_lower = result['description'].lower()
                
                # Extract common RP Strength video patterns
                result['metadata'] = {
                    'has_timestamps': ':' in description_lower and ('00:' in description_lower or '0:' in description_lower),
                    'is_form_guide': any(term in description_lower for term in ['form guide', 'how to', 'technique', 'tutorial']),
                    'is_program_related': any(term in description_lower for term in ['program', 'routine', 'workout', 'training split']),
                    'mentioned_muscles': [muscle for muscle in ['chest', 'back', 'shoulders', 'legs', 'arms', 'biceps', 'triceps', 'quads', 'hamstrings', 'calves']
                                        if muscle in description_lower]
                }
            except Exception as e:
                print(f"Error extracting metadata: {str(e)}")
                result['metadata'] = {}
            
            return result
            
        except Exception as e:
            print(f"Error scraping video data: {str(e)}")
            return {}

    @tool
    def get_channel_videos(self,max_results: int = 10) -> List[Dict]:
        """
        Retrieves latest videos from RP Strength channel with pagination and error handling
        Args:
            max_results: Number of videos to retrieve (default: 10)
        Returns:
            List of dictionaries containing video information
        """
        try:
            youtube = build('youtube', 'v3',
                        developerKey=os.getenv('YOUTUBE_API_KEY'))
            
            # RP Strength channel ID
            channel_id = 'UCfQgsKhHjSyRLOp9mnffqVg'
            
            videos = []
            next_page_token = None
            
            while len(videos) < max_results:
                # Prepare request parameters
                request_params = {
                    'part': 'snippet,statistics,contentDetails',
                    'channelId': channel_id,
                    'maxResults': min(50, max_results - len(videos)),  # YouTube API limit is 50
                    'order': 'date',
                    'type': 'video'
                }
                
                if next_page_token:
                    request_params['pageToken'] = next_page_token
                    
                # Make API request
                request = youtube.search().list(**request_params)
                response = request.execute()
                
                # Process each video
                for item in response['items']:
                    video_id = item['id']['videoId']
                    
                    # Get additional video details
                    video_details = youtube.videos().list(
                        part='contentDetails,statistics',
                        id=video_id
                    ).execute()
                    
                    # Extract duration and statistics
                    details = video_details['items'][0]
                    
                    video_data = {
                        'video_id': video_id,
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'published_at': item['snippet']['publishedAt'],
                        'duration': details['contentDetails']['duration'],
                        'view_count': details['statistics'].get('viewCount', 0),
                        'like_count': details['statistics'].get('likeCount', 0),
                    }
                    videos.append(video_data)
                
                # Check if there are more pages
                next_page_token = response.get('nextPageToken')
                if not next_page_token or len(videos) >= max_results:
                    break
                    
            return videos[:max_results]
            
        except Exception as e:
            print(f"Error fetching videos: {str(e)}")
            return []

class RPStrengthCrew:
    def __init__(self):
        self.tools = RPStrengthTools()
        
        # Create specialized agents
        self.researcher = Agent(
            llm=llm,
            role='Exercise Research Specialist',
            goal='Analyze RP Strength videos to extract accurate exercise and training information',
            backstory='Expert in exercise science with deep knowledge of RP Strength methodology',
            tools=[self.tools.scrape_video_data, self.tools.get_channel_videos],
            verbose=True,
            allow_delegation=False,
        )
        
        self.advisor = Agent(
            llm=llm,
            role='Training Program Advisor',
            goal='Provide personalized exercise recommendations based on RP Strength principles',
            backstory='Experienced strength coach specializing in hypertrophy and program design',
            verbose=True,
            allow_delegation=False,
        )
        
    def analyze_query(self, user_query: str) -> str:
        # Create tasks
        research_task = Task(
            description=f'Research RP Strength videos relevant to: {user_query}',
            expected_output="return transcripts of the top 5 relevant videos",
            agent=self.researcher,
        )
        
        advise_task = Task(
            description=f'Analyze research and provide recommendations for: {user_query}',
            expected_output="Top 10 most important points mentioned in the provided context",
            agent=self.advisor,
            # output_file="results/output.md",
            # context=[research_task],
        )
        
        # Create and run crew
        crew = Crew(
            agents=[self.researcher, self.advisor],
            tasks=[research_task, advise_task],
            process=Process.sequential,
            max_rpm=2
            # output_log_file=,
        )
        
        result = crew.kickoff()
        return result

# Example usage
def main():
    # Initialize crew
    rp_crew = RPStrengthCrew()
    
    # Example query
    query = "What are the best exercises for building bigger biceps?"
    response = rp_crew.analyze_query(query)
    print(response)

if __name__ == "__main__":
    main()