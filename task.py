from crewai import Task
from agents import Scraper,Writer
from tools import tool
# from tools import llm
Content_scraping = Task(
    description='scrape the channel for the requested information.',
    expected_output='A detailed context.',
    agent=Scraper,
    tools=[tool],
)

Writing_content=Task(
    # llm=llm,
    description='Summarize the provided context in a very informative and detailed manner.',
    expected_output='''A 100 to 150 word response, in the format of a text file, to the user's query.''',
    agent=Writer,
    context=[Scraper],


)