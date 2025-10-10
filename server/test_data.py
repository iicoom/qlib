import sys
import os
# 添加父目录到Python路径，以便导入qlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import qlib
from qlib.data import D

# ==============================
# 1. 初始化 Qlib
# ==============================
provider_uri = "~/.qlib/qlib_data/my_data"
qlib.init(provider_uri=provider_uri)

print(f"\n✅ Qlib 初始化成功，数据目录: {provider_uri}")

# ==============================
# 2. 检查交易日历
# ==============================
calendar = D.calendar(freq="day")
print("\n📅 前 10 个交易日:")
print(calendar[:10])

# ==============================
# 3. 检查股票池
# ==============================
instruments = D.instruments(market="all")
print("\n📈 股票池（前 5 个）:")
print(instruments)

# ==============================
# 4. 读取单只股票数据
# ==============================
symbol = "SZ002189"
fields = ["$open", "$high", "$low", "$close", "$volume"]

df = D.features(
    instruments=[symbol],
    fields=fields,
    start_time="2025-09-01",
    end_time="2025-09-30"
)

print(f"\n📊 {symbol} 的数据 (前 5 行):")
print(df.head())

# ==============================
# 5. 检查特定字段
# ==============================
close_data = D.features([symbol], ["$close"], start_time="2025-09-01", end_time="2025-09-30")
print(f"\n💹 {symbol} 2025-09-01 到 2025-09-30 的收盘价:")
print(close_data)