from crewai import Agent
from tools import tool
Scraper=Agent(
    role='Youtube content Scraper.',
    goal='Scrape the requested youtube channel and return the requested information.',
    backstory="""You are a content/web scraper for a FAANG company with 10+ years of experience.""",
    max_iter=5,
    tools=[tool],
    max_rpm=None,
    verbose=True,
    allow_delegation=False,
    cache=True,
    max_retry_limit=2,
)


Writer=agent = Agent(
    role='content transcriber',
    goal='Extract important and actionable workout information form the provide context.',
    backstory="""You are a content transcriber for a large
    fortune 500 corporation with a decade of experience.
    use your knowledge and expertise to generate a response to the provides query.""",
    max_iter=5,
    max_rpm=None,
    verbose=True,
    allow_delegation=False,
    cache=True,
    max_retry_limit=2,
)