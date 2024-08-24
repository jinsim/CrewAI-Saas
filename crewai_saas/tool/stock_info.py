from crewai_tools import tool
import yfinance as yf

class StockInfoTools:

    @tool("Stock Price")
    def stock_price(ticker: str) -> str:
        """Get the stock price data for a given ticker over the last month.

        Parameters:
        - ticker (str): Stock ticker symbol (e.g., 'AAPL').

        Returns:
        - A summary of the stock's daily price history, including date, open, high, low, close, and volume.
        """
        ticker_info = yf.Ticker(ticker)
        history = ticker_info.history(period="1mo")

        result = "Date | Open | High | Low | Close | Volume\n"
        result += "\n".join(
            f"{index.date()} | {row['Open']} | {row['High']} | {row['Low']} | {row['Close']} | {row['Volume']}"
            for index, row in history.iterrows()
        )
        return result

    @tool("Income Statement")
    def income_stmt(ticker: str) -> str:
        """Fetch the income statement for a company by its ticker.

        Parameters:
        - ticker (str): Stock ticker symbol (e.g., 'AAPL').

        Returns:
        - A summary of the company's income statement, including revenue, gross profit, operating income, and net income.
        """
        ticker_info = yf.Ticker(ticker)
        financials = ticker_info.financials.T

        result = "Period | Revenue | Gross Profit | Operating Income | Net Income\n"
        result += "\n".join(
            f"{index} | {row['Total Revenue']} | {row['Gross Profit']} | {row['Operating Income']} | {row['Net Income']}"
            for index, row in financials.iterrows()
        )
        return result

    @tool("Balance Sheet")
    def balance_sheet(ticker: str) -> str:
        """Retrieve the balance sheet for a company by its ticker.

        Parameters:
        - ticker (str): Stock ticker symbol (e.g., 'AAPL').

        Returns:
        - A summary of the company's balance sheet, including total assets, liabilities, and shareholders' equity.
        """
        ticker_info = yf.Ticker(ticker)
        balance_sheet = ticker_info.balance_sheet.T

        result = "Period | Total Assets | Total Liabilities | Shareholders' Equity\n"
        result += "\n".join(
            f"{index} | {row['Total Assets']} | {row['Total Liab']} | {row['Total Stockholder Equity']}"
            for index, row in balance_sheet.iterrows()
        )
        return result

    @tool("Insider Transactions")
    def insider_transactions(self, ticker: str) -> str:
        """Get insider transaction data for a given stock ticker.

        Parameters:
        - ticker (str): Stock ticker symbol (e.g., 'AAPL').

        Returns:
        - A summary of insider transactions, including date, insider name, shares traded, transaction type, and price.
        """
        ticker_info = yf.Ticker(ticker)
        insider = ticker_info.insider_transactions

        result = "Date | Insider Name | Shares Traded | Transaction Type | Price\n"
        result += "\n".join(
            f"{row['Date'].date()} | {row['Insider Name']} | {row['Shares']} | {row['Transaction']} | {row['Value ($)']}"
            for index, row in insider.iterrows()
        )
        return result
