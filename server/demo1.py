import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

# 使用你提供的数据
data = {
    'date': ['2025-09-23', '2025-09-24', '2025-09-25', '2025-09-26', '2025-09-29'],
    'instrument': ['SH603716', 'SH603716', 'SH603716', 'SH603716', 'SH603716'],
    'open': [27.89, 27.20, 27.50, 27.17, 25.60],
    'close': [27.39, 27.80, 27.44, 25.65, 24.42],
    'high': [28.50, 28.21, 28.19, 27.17, 25.60],
    'low': [26.80, 26.67, 27.16, 25.57, 24.38],
    'volume': [19401400, 16630700, 15845300, 21267100, 20101100],
    'amount': [532939872.0, 459676987.0, 436070179.0, 553639709.0, 494473686.0]
}

df = pd.DataFrame(data)

print("当前数据概览:")
print(df)
print("\n" + "="*50)

# 方法1：简单趋势外推
def simple_trend_prediction(df):
    """基于价格趋势的简单预测"""
    prices = df['close'].values
    
    # 计算近期趋势
    recent_trend = (prices[-1] - prices[-3]) / prices[-3]  # 3日趋势
    
    if recent_trend < -0.05:  # 下跌趋势明显
        prediction = prices[-1] * 0.98  # 继续下跌2%
        trend = "下跌"
    elif recent_trend > 0.02:  # 上涨趋势
        prediction = prices[-1] * 1.02  # 继续上涨2%
        trend = "上涨"
    else:  # 横盘
        prediction = prices[-1] * 1.00  # 基本持平
        trend = "横盘"
    
    return prediction, trend

# 方法2：移动平均预测
def moving_average_prediction(df):
    """基于移动平均的预测"""
    prices = df['close'].values
    
    # 计算3日移动平均
    if len(prices) >= 3:
        ma_3 = np.mean(prices[-3:])
        # 如果当前价格低于移动平均，可能反弹
        if prices[-1] < ma_3:
            prediction = (prices[-1] + ma_3) / 2
        else:
            prediction = prices[-1] * 0.995
    else:
        prediction = prices[-1]
    
    return prediction

# 方法3：价格模式识别
def pattern_recognition_prediction(df):
    """基于价格模式的简单识别"""
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    # 分析价格行为
    is_oversold = latest['close'] < latest['open']  # 收盘低于开盘
    has_high_volume = latest['volume'] > df['volume'].mean()  # 高成交量
    
    if is_oversold and has_high_volume:
        # 放量下跌后可能反弹
        prediction = latest['close'] * 1.015
        reason = "放量下跌后可能技术性反弹"
    elif not is_oversold and has_high_volume:
        # 放量上涨可能延续
        prediction = latest['close'] * 1.008
        reason = "放量上涨可能延续"
    else:
        # 缩量整理
        prediction = latest['close'] * 0.998
        reason = "缩量整理，小幅波动"
    
    return prediction, reason

# 执行所有预测方法
print("开始预测2025-09-30的股价...\n")

# 方法1：趋势预测
trend_pred, trend = simple_trend_prediction(df)
print(f"1. 趋势分析预测: {trend_pred:.2f}")
print(f"   判断依据: 当前处于{trend}趋势")

# 方法2：移动平均预测
ma_pred = moving_average_prediction(df)
print(f"2. 移动平均预测: {ma_pred:.2f}")

# 方法3：模式识别预测
pattern_pred, reason = pattern_recognition_prediction(df)
print(f"3. 模式识别预测: {pattern_pred:.2f}")
print(f"   判断依据: {reason}")

# 集成最终预测（加权平均）
final_prediction = (trend_pred * 0.4 + ma_pred * 0.3 + pattern_pred * 0.3)
print(f"\n" + "="*50)
print(f"📈 最终集成预测: {final_prediction:.2f}")
print(f"📊 相对于最新收盘价({df['close'].iloc[-1]:.2f}): {((final_prediction/df['close'].iloc[-1])-1)*100:+.2f}%")

# 提供交易建议
print(f"\n💡 交易建议:")
if final_prediction > df['close'].iloc[-1]:
    print("   - 预期上涨，可考虑观望或轻仓试多")
    print("   - 阻力位参考: {:.2f}".format(df['high'].max()))
else:
    print("   - 预期下跌，建议谨慎操作")
    print("   - 支撑位参考: {:.2f}".format(df['low'].min()))

# 显示关键技术位
print(f"\n📊 关键技术位置:")
print(f"   - 近期高点: {df['high'].max():.2f}")
print(f"   - 近期低点: {df['low'].min():.2f}")
print(f"   - 5日均价: {df['close'].mean():.2f}")
print(f"   - 最新成交量: {df['volume'].iloc[-1]:,.0f}")

print(f"\n⚠️  风险提示: 基于5日数据的预测仅供参考，实际投资需谨慎!")