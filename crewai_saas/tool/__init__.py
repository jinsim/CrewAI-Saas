from .calculator_tools import CalculatorTools
from .scrape_web import scrape_tool
from .search_tools import SearchTools
from .sec_tools import SECTools
from .stock_info import StockInfoTools, stock_price
from .stock_news import stock_news

function_map = {
    "calculate": CalculatorTools.calculate,
    "search_news": SearchTools.search_news,
    "search_internet": SearchTools.search_internet,
    "scrape_web": scrape_tool,
    "stock_news": stock_news,
    "stock_price": stock_price,
    "income_stmt": StockInfoTools.income_stmt,
    "balance_sheet": StockInfoTools.balance_sheet,
    "insider_transactions": StockInfoTools.insider_transactions,
    "search_10q": SECTools.search_10q,
    "search_10k": SECTools.search_10k
}

def execute_function_by_string(func_name, *args, **kwargs):
    if func_name in function_map:
        # Call the function and pass any additional arguments
        return function_map[func_name](*args, **kwargs)
    else:
        raise ValueError(f"Function '{func_name}' not found in the tool package!")

# Handling unknown functions
# try:
#     print(execute_function_by_string("unknown_function", "some_param"))
# except ValueError as e:
#     print(e)  # Output: Function 'unknown_function' not found in the tool package!

