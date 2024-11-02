from crewai import Task
from agents import Scraper,Writer
from tools import tool

Content_scraping = Task(
    description='scrape the channel for the requested information.',
    expected_output='A detailed context.',
    agent=Scraper,
    tools=[tool]
)

Writing_task=Task(
    description='Summarize the provided context in a very informative and detailed manner.',
    expected_output='',
    agent=Writer,
    context=[Scraper],
)