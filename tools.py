from crewai_tools import YoutubeChannelSearchTool
from dotenv import load_dotenv
load_dotenv()
import os
import google.generativeai as genai
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

tool = YoutubeChannelSearchTool(youtube_channel_handle='@RenaissancePeriodization',
    config=dict(
        llm=dict(
            provider="ollama",
            config=dict(
                model="llama3.1",
            ),
        ),
        embedder=dict(
            provider="google",
            config=dict(
                model="models/embedding-001",
                task_type="retrieval_document",
            ),
        ),
    )
)

# print(tool.run("squats hurt my knees ?"))