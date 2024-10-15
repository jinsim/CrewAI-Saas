from .calculator_tools import CalculatorTools
from .scrape_web import scrape_tool
from .search_tools import SearchTools
from .sec_tools import SECTools
from .stock_info import StockInfoTools
from .stock_news import stock_news

import os
from typing import Union
from urllib.parse import urljoin
from crewai_tools import DOCXSearchTool, PDFSearchTool, TXTSearchTool, CSVSearchTool, XMLSearchTool

function_map = {
    "calculate": CalculatorTools.calculate,
    "search_news": SearchTools.search_news,
    "search_internet": SearchTools.search_internet,
    "scrape_web": scrape_tool,
    "stock_news": stock_news,
    "stock_price": StockInfoTools.stock_price,
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


class UnsupportedFileTypeError(Exception):
    """파일 형식이 지원되지 않을 때 발생하는 예외"""


def get_full_file_path(file_name: str) -> str:
    """
    Supabase URL과 파일명을 조합하여 완전한 파일 경로를 생성합니다.
    SUPABASE_URL 환경 변수를 사용합니다.
    """
    print(os.getenv("SUPABASE_URL", ""), "/storage/v1/object/public/", file_name)
    return urljoin(urljoin(os.getenv("SUPABASE_URL", ""), "/storage/v1/object/public/"), file_name)


def get_search_tool(file_name: str) -> Union[
    DOCXSearchTool, PDFSearchTool, TXTSearchTool, CSVSearchTool, XMLSearchTool]:
    """
    파일명을 받아 적절한 검색 도구를 반환합니다.

    :param file_name: Supabase에 저장된 파일명
    :return: 해당 파일 유형에 맞는 검색 도구
    :raises UnsupportedFileTypeError: 지원되지 않는 파일 형식일 경우
    """
    full_file_path = get_full_file_path(file_name)
    extension = os.path.splitext(file_name)[1].lower()

    if extension == '.docx':
        return DOCXSearchTool(docx=full_file_path)
    elif extension == '.pdf':
        return PDFSearchTool(pdf=full_file_path)
    elif extension == '.txt':
        return TXTSearchTool(txt=full_file_path)
    elif extension == '.csv':
        return CSVSearchTool(csv=full_file_path)
    elif extension == '.xml':
        return XMLSearchTool(xml=full_file_path)
    else:
        raise UnsupportedFileTypeError(f"지원되지 않는 파일 형식입니다: {extension}")



