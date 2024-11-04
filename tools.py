from crewai_tools import YoutubeChannelSearchTool
from dotenv import load_dotenv
load_dotenv()
import os
import google.generativeai as genai
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
llm=genai.GenerativeModel("gemini-1.5-flash")
# print(llm.generate_content("what is an LLM?"))


tool = YoutubeChannelSearchTool(youtube_channel_handle='@RenaissancePeriodization',
    config=dict(
        llm=dict(
            provider="google",
            config=dict(
                model="gemini-1.5-flash",
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