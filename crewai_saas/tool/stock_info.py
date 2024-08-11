from crewai_tools import tool
from langchain.tools.base import StructuredTool

import yfinance as yf
from langchain_core.pydantic_v1 import BaseModel, Field

class StockInfoTools():

    @tool("Stock Price")
    def stock_price(ticker):
        """
        Useful to get stock price data.
        The input to this tool should be a ticker, for example AAPL, MSFT.
        """
        ticker = yf.Ticker(ticker)
        return ticker.history(period="1mo")

    @tool("Income Statement")
    def income_stmt(ticker):
        """
        Useful to get the income statement of a company.
        The input to this tool should be a ticker, for example AAPL, MSFT.
        """
        ticker = yf.Ticker(ticker)
        return ticker.income_stmt

    @tool("Balance Sheet")
    def balance_sheet(ticker):
        """
        Useful to get the balance sheet of a company.
        The input should be a ticker, for example AAPL, MSFT.
        """
        ticker = yf.Ticker(ticker)
        return ticker.balance_sheet

    @tool("Insider Transactions")
    def insider_transactions(ticker):
        """
        Useful to get insider transactions of a stock.
        The input should be a ticker, for example AAPL, MSFT.
        """
        ticker = yf.Ticker(ticker)
        return ticker.insider_transactions