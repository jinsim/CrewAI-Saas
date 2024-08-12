from crewai_tools import tool
import yfinance as yf

@tool("Stock News")
def stock_news(ticker):
    """
    Retrieve the latest news articles related to a specific stock ticker from Yahoo Finance.

    This tool is useful for obtaining the most recent news about a particular stock, providing insights into the company's
    latest developments, market sentiment, and other relevant information. It can be used to stay informed about the stock's
    performance and the factors influencing it.

    Parameters:
    - ticker (str): The stock ticker symbol. This must be a string representing the company's symbol on the stock market.
      - Example: 'AAPL' for Apple Inc., 'MSFT' for Microsoft Corporation, or '005930' for Samsung Electronics.

    Returns:
    - A formatted string containing the latest news articles related to the specified stock. Each article includes the title, link, and a brief snippet.
      - The articles are presented in chronological order, with the most recent articles first.

    Notes:
    - This tool supports ticker symbols from global stock markets, not just NASDAQ.
    - Ensure the ticker symbol is correct and represents a valid, publicly traded company. Incorrect symbols may result in no news being retrieved.

    Example Input:
    {'ticker': 'AAPL'}

    Example Output:
    Title: Apple Unveils New Products at Annual Event
    Link: https://www.example.com/apple-event-news
    Snippet: Apple Inc. has introduced a range of new products at its annual event, including the latest iPhone model...

    -----------------
    """
    ticker = yf.Ticker(ticker)
    return ticker.news