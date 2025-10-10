import akshare as ak
import pandas as pd

# 1. 获取数据
symbol = "002837"
df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date="20250901", end_date="20250930")

# 2. 打印原始数据结构（调试用）
print("原始数据：")
print(df.tail())

# 3. 数据转换
df_qlib = df.copy()

# 重命名列
df_qlib = df_qlib.rename(columns={
    "日期": "date",
    "开盘": "open",
    "收盘": "close",
    "最高": "high",
    "最低": "low",
    "成交量": "volume",      # 注意：单位是“手”
    "成交额": "amount",
})

# 转换日期格式
df_qlib["date"] = pd.to_datetime(df_qlib["date"]).dt.date  # 只保留日期

# 添加 instrument 列（带 SH/SZ 前缀）
if symbol.startswith("6"):
    instrument = f"SH{symbol}"
elif symbol.startswith("0") or symbol.startswith("3"):
    instrument = f"SZ{symbol}"
else:
    instrument = symbol
df_qlib["instrument"] = instrument

# 单位转换：成交量从“手” → “股”
df_qlib["volume"] = df_qlib["volume"] * 100

# 选择必要列（按 Qlib 要求）
df_qlib = df_qlib[["date", "instrument", "open", "close", "high", "low", "volume", "amount"]]

# 排序
df_qlib = df_qlib.sort_values(["instrument", "date"]).reset_index(drop=True)

# 4. 保存为 CSV（Qlib dump_bin.py 可读）
output_csv = f"{instrument}.csv"
df_qlib.to_csv(output_csv, index=False, encoding="utf-8")

print(f"\n✅ 数据已转换并保存为: {output_csv}")
print("\n前几行数据：")
print(df_qlib.tail())
