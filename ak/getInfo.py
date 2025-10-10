import akshare as ak
from typing import Dict, Any

def get_stock_info(symbol="002837") -> Dict[str, Any]:
  try:
    # 3. 公司基本信息
    stock_info = ak.stock_individual_info_em(symbol)
    print("\n公司信息:")
    print(stock_info)

    # 5. 公司新闻/公告
    news = ak.stock_news_em(symbol)
    news_dict = {
      'columns': news.columns.tolist(),
      'data': news.values.tolist()
    }
    # print(news_dict)

    return {
        "success": True,
        "stock_info": stock_info,
        "news": news_dict
    }

  except Exception as e:
    return {
        "success": False,
        "error": str(e)
    }