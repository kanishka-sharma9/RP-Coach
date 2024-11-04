from crewai import Crew,Process
from task import Content_scraping,Writing_content
from agents import Scraper,Writer
from tools import llm

crew = Crew(
    agents=[Scraper, Writer],
    tasks=[Content_scraping,Writing_content],
    verbose=True,
    # output_log_file=True,
    process=Process.sequential,
    output_file="results/output.txt",

)

crew_output = crew.kickoff("what is the best exercise to build big biceps? ")
print(crew_output)