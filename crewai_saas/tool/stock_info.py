from crewai_tools import tool
import yfinance as yf

class StockInfoTools:

    @tool("Stock Price")
    def stock_price(ticker: str) -> str:
        """Retrieve the stock price data for a given ticker symbol.

        This tool is useful when you need to obtain the historical stock price data over the last month
        for any publicly traded company. The input should be the company's stock ticker symbol, such as 'AAPL' for Apple
        or 'MSFT' for Microsoft.

        Parameters:
        - ticker (str): The stock ticker symbol. This must be a string representing the company's symbol on the stock market.

        Returns:
        - A string summarizing the stock's price history over the last month, including dates, opening and closing prices, highs, lows, and volumes.

        Example Input:
        {'ticker': 'AAPL'}
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
        """Fetch the income statement of a company based on its stock ticker.

        This tool is designed to provide a detailed income statement for a company, which includes key financial metrics
        such as revenue, gross profit, operating income, and net income. The income statement is a crucial document
        for analyzing a company's financial health and profitability over a specific period.

        Parameters:
        - ticker (str): The stock ticker symbol. This must be a string representing the company's symbol on the stock market.

        Returns:
        - A string summarizing the company's income statement, including revenue, gross profit, operating income, and net income.

        Example Input:
        {'ticker': 'AAPL'}
        """
        ticker_info = yf.Ticker(ticker)
        financials = ticker_info.financials.T  # Transpose to get rows as periods and columns as metrics

        result = "Period | Revenue | Gross Profit | Operating Income | Net Income\n"
        result += "\n".join(
            f"{index} | {row['Total Revenue']} | {row['Gross Profit']} | {row['Operating Income']} | {row['Net Income']}"
            for index, row in financials.iterrows()
        )
        return result

    @tool("Balance Sheet")
    def balance_sheet(ticker: str) -> str:
        """Retrieve the balance sheet of a company for the specified stock ticker.

        The balance sheet provides a snapshot of a company's financial position at a specific point in time,
        showing what it owns (assets), what it owes (liabilities), and the value of shareholders' equity.
        This tool is essential for understanding the financial stability and capital structure of a company.

        Parameters:
        - ticker (str): The stock ticker symbol. This must be a string representing the company's symbol on the stock market.

        Returns:
        - A string summarizing the company's balance sheet, including total assets, total liabilities, and shareholders' equity.

        Example Input:
        {'ticker': 'AAPL'}
        """
        ticker_info = yf.Ticker(ticker)
        balance_sheet = ticker_info.balance_sheet.T  # Transpose to get rows as periods and columns as metrics

        result = "Period | Total Assets | Total Liabilities | Shareholders' Equity\n"
        result += "\n".join(
            f"{index} | {row['Total Assets']} | {row['Total Liab']} | {row['Total Stockholder Equity']}"
            for index, row in balance_sheet.iterrows()
        )
        return result

    @tool("Insider Transactions")
    def insider_transactions(self, ticker: str) -> str:
        """Obtain insider transaction data for a given stock ticker.

        Insider transactions refer to the buying and selling of a company's stock by its executives, directors, or employees.
        Tracking insider transactions can provide insights into how those closest to the company view its future prospects.

        Parameters:
        - ticker (str): The stock ticker symbol. This must be a string representing the company's symbol on the stock market.

        Returns:
        - A string summarizing the insider transactions for the specified stock, including the date, insider name, shares traded, transaction type, and price.

        Example Input:
        {'ticker': 'AAPL'}
        """
        ticker_info = yf.Ticker(ticker)
        insider = ticker_info.insider_transactions

        result = "Date | Insider Name | Shares Traded | Transaction Type | Price\n"
        result += "\n".join(
            f"{row['Date'].date()} | {row['Insider Name']} | {row['Shares']} | {row['Transaction']} | {row['Value ($)']}"
            for index, row in insider.iterrows()
        )
        return result
