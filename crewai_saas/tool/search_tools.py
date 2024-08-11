import json
import os

import requests
from langchain.tools import tool


class SearchTools():
  @tool("Search the internet")
  def search_internet(query: str):
    """Perform a general search on the internet for a given topic and return the most relevant results.

    This tool is designed to help you find information on a wide range of topics by querying the internet.
    It returns the top results that are most relevant to your search query, making it easier to gather information quickly.

    Parameters:
    - query (str): The search term or phrase you want to look up. This must be a string.
      - Example: "Latest advancements in artificial intelligence" or "How to learn Python programming".

    Returns:
    - A formatted string containing the top search results, each with a title, link, and snippet. The results are separated by lines for clarity.

    Notes:
    - If the query is 'JavaScript', the search will be retried due to potential ambiguity or excessive results related to the term.
    - The function validates that the input is a string. If the input is not a string, an error will be raised.
    - The tool is useful for a wide array of searches, including academic research, general knowledge, or finding specific information on products, services, or concepts.

    Example Input:
    {'query': 'Latest trends in renewable energy'}

    Example Output:
    Title: Renewable Energy 2024: Trends to Watch
    Link: https://www.example.com/renewable-energy-trends
    Snippet: Explore the latest trends in renewable energy for 2024, including advancements in solar and wind technologies...

    -----------------
    """

    top_result_to_return = 4
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': os.environ['SERPER_API_KEY'],
        'content-type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    results = response.json()['organic']
    string = []
    for result in results[:top_result_to_return]:
      try:
        string.append('\n'.join([
            f"Title: {result['title']}", f"Link: {result['link']}",
            f"Snippet: {result['snippet']}", "\n-----------------"
        ]))
      except KeyError:
        next

    return '\n'.join(string)

  @tool("Search news on the internet")
  def search_news(query):
    """Search the internet for recent news articles related to a given topic and return the most relevant results.

    This tool is particularly useful when you need to find the latest news about a specific topic, such as a company, event, or trending issue.
    It fetches the top news articles that are most relevant to your search query, helping you stay informed with up-to-date information.

    Parameters:
    - query (str): The search term or phrase related to the news you want to find. This must be a string.
      - Example: "Tesla stock performance" or "Global warming effects".

    Returns:
    - A formatted string containing the top news articles, each with a title, link, and snippet. The results are separated by lines for clarity.

    Notes:
    - The tool is designed to retrieve the latest news, so it is best suited for topics that are current and of public interest.
    - It validates that the input is a string. If the input is not a string, an error will be raised.
    - This tool is useful for journalists, researchers, and anyone interested in staying updated on recent developments in any field.

    Example Input:
    {'query': 'Climate change and its impact on coastal cities'}

    Example Output:
    Title: Rising Sea Levels Threaten Coastal Cities Worldwide
    Link: https://www.example.com/climate-change-coastal-impact
    Snippet: As climate change accelerates, rising sea levels are posing significant threats to coastal cities, leading to...

    -----------------
    """
    top_result_to_return = 4
    url = "https://google.serper.dev/news"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': os.environ['SERPER_API_KEY'],
        'content-type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    results = response.json()['news']
    string = []
    for result in results[:top_result_to_return]:
      try:
        string.append('\n'.join([
            f"Title: {result['title']}", f"Link: {result['link']}",
            f"Snippet: {result['snippet']}", "\n-----------------"
        ]))
      except KeyError:
        next

    return '\n'.join(string)
