import subprocess
from pathlib import Path

def qlib_dump_all(data_path, qlib_dir, freq="day", symbol_field_name="instrument", 
                  date_field_name="date", exclude_fields=None, delete_existing=True):
    """
    使用 Qlib 的 dump_bin.py 将 CSV 文件转换为 Qlib 二进制数据格式。

    参数:
        data_path (str): CSV 文件路径，包含多只股票数据（需有 symbol 字段）
        qlib_dir (str): 目标 qlib 数据存储目录
        freq (str): 频率，"day" / "1min" / "5min" 等
        symbol_field_name (str): CSV 中表示股票代码的列名，默认 "instrument"
        date_field_name (str): CSV 中表示日期的列名，默认 "date"
        exclude_fields (list or str): 要排除的字段，如 "instrument" 或 ["volume", "amount"]
        delete_existing (bool): 是否删除已存在的 qlib_dir 目录（避免冲突）

    返回:
        bool: 成功返回 True，失败抛出异常
    """
    # 检查文件是否存在
    data_path = Path(data_path).resolve()
    if not data_path.exists():
        raise FileNotFoundError(f"❌ 数据文件不存在: {data_path}")

    qlib_dir = Path(qlib_dir).expanduser().resolve()
    
    # 删除已有目录（避免 dump 冲突）
    if delete_existing and qlib_dir.exists():
        print(f"🗑️ 删除已有数据目录: {qlib_dir}")
        subprocess.run(["rm", "-rf", str(qlib_dir)], check=True)
    
    # 获取当前脚本所在目录
    current_dir = Path(__file__).parent
    grandparent_dir = current_dir.parent  # 上上级目录: /Users/mxj

    print(f"📂 当前脚本所在目录: {grandparent_dir}")

    # 检查 dump_bin.py 文件是否存在
    dump_bin_path = grandparent_dir / "scripts" / "dump_bin.py"
    print(f"📂 dump_bin.py 文件路径: {dump_bin_path}")
    if not dump_bin_path.exists():
        raise FileNotFoundError(f"❌ dump_bin.py 文件不存在: {dump_bin_path}")

    # 构建命令
    cmd = [
        "python", str(dump_bin_path), "dump_all",
        "--data_path", str(data_path),
        "--qlib_dir", str(qlib_dir),
        "--freq", freq,
        "--symbol_field_name", symbol_field_name,
        "--date_field_name", date_field_name,
    ]

    # 添加 exclude_fields
    if exclude_fields:
        if isinstance(exclude_fields, list):
            exclude_fields = ",".join(exclude_fields)
        cmd.extend(["--exclude_fields", exclude_fields])

    # 打印执行命令（便于调试）
    print("🚀 执行命令:")
    print(" ".join(cmd))

    # 执行命令
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        print("✅ dump_all 执行成功!")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ dump_all 执行失败!")
        print("错误输出:")
        print(e.stderr)
        raise


# ======================
# 使用示例
# ======================
if __name__ == "__main__":
    try:
        qlib_dump_all(
            data_path="/Users/mxj/Repo/myAk/SZ002837.csv",
            qlib_dir="~/.qlib/qlib_data/my_data",
            freq="day",
            symbol_field_name="instrument",
            date_field_name="date",
            exclude_fields="instrument",  # 也可以是 ["field1", "field2"]
        )
    except Exception as e:
        print(f"执行出错: {e}")