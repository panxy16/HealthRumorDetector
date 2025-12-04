# 尝试以下调整
from duckduckgo_search import DDGS

# 1. 更换区域参数
results = DDGS().text("新冠病毒", region='zh-cn', max_results=5)  # 注意 region 格式
print(results)
# 2. 尝试英文关键词
results = DDGS().text("COVID-19", region='cn', max_results=5)
print(results)
