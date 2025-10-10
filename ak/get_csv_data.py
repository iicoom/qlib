import akshare as ak
import pandas as pd
import os

def download_and_convert_to_qlib(symbol, start_date, end_date, output_dir="."):
    """
    从 akshare 下载 A 股历史数据，转换为 Qlib 格式并保存为 CSV。

    参数:
        symbol (str): 股票代码，如 "002837"
        start_date (str): 开始日期，格式如 "20250901" 或 "2025-09-01"
        end_date (str): 结束日期，格式如 "20250930" 或 "2025-09-30"
        output_dir (str): 输出目录，默认当前目录

    返回:
        str: 保存的 CSV 文件路径
    """
    # 1. 获取数据
    print(f"📥 正在下载 {symbol} 数据...")
    df = ak.stock_zh_a_hist(
        symbol=symbol,
        period="daily",
        start_date=start_date.replace("-", ""),
        end_date=end_date.replace("-", ""),
        adjust="qfq"  # 可选：前复权
    )

    if df.empty:
        raise ValueError(f"❌ 未获取到 {symbol} 的数据，请检查股票代码或日期范围。")

    print(f"📊 获取到 {len(df)} 条数据。")

    # 2. 数据转换
    df_qlib = df.copy()

    # 重命名列（映射中文到 Qlib 字段）
    df_qlib = df_qlib.rename(columns={
        "日期": "date",
        "开盘": "open",
        "收盘": "close",
        "最高": "high",
        "最低": "low",
        "成交量": "volume",  # 单位：手
        "成交额": "amount",
    })

    # 转换日期为 date 类型（去掉时间）
    df_qlib["date"] = pd.to_datetime(df_qlib["date"]).dt.date

    # 生成 instrument（带市场前缀）
    if symbol.startswith("6"):
        instrument = f"SH{symbol}"
    elif symbol.startswith("0") or symbol.startswith("3"):
        instrument = f"SZ{symbol}"
    else:
        instrument = symbol
    df_qlib["instrument"] = instrument

    # 成交量：从“手”转为“股”（1 手 = 100 股）
    df_qlib["volume"] = df_qlib["volume"] * 100

    # 选择 Qlib 所需字段
    df_qlib = df_qlib[["date", "instrument", "open", "close", "high", "low", "volume", "amount"]]

    # 按 instrument 和 date 排序
    df_qlib = df_qlib.sort_values(["instrument", "date"]).reset_index(drop=True)

    # 3. 保存为 CSV
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{instrument}.csv"
    file_path = os.path.join(output_dir, filename)

    df_qlib.to_csv(file_path, index=False, encoding="utf-8")
    print(f"✅ 数据已保存为: {file_path}")

    return {"success": True, "file_path": file_path}
