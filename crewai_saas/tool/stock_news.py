from crewai_tools import tool
import yfinance as yf

@tool("Stock News")
def stock_news(ticker):
    """
        Useful for obtaining news about a stock from Yahoo Finance. 
        The input to this tool should be a ticker, such as AAPL, MSFT or 005930. 
        This tool supports tickers from not only NASDAQ but also stock markets worldwide.
    """
    ticker = yf.Ticker(ticker)
    return ticker.news