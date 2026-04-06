import time
from tradingagents.dataflows.yfinance_news import get_global_news_yfinance

start = time.time()
# setting limit large enough so it queries all 4
res = get_global_news_yfinance("2023-10-10", look_back_days=7, limit=40)
end = time.time()
print(f"Time taken: {end - start:.2f} seconds")
