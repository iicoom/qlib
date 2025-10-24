# predictor.py
import sys
import os
# 添加父目录到Python路径，以便导入qlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import qlib
from qlib.data import D
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from qlib.constant import REG_CN


def init_qlib():
    """初始化QLib"""
    try:
        # 使用绝对路径
        home_path = os.path.expanduser('~')
        provider_uri = os.path.join(home_path, '.qlib', 'qlib_data', 'my_data')
        
        qlib.init(
            provider_uri=provider_uri,
            region=REG_CN
        )
        print(f"QLib初始化成功! 数据路径: {provider_uri}")
        return True
    except Exception as e:
        print(f"QLib初始化失败: {e}")
        return False

def debug_data_loading(symbol="SZ002837"):
    """调试数据加载过程"""
    print("\n=== 调试信息 ===")
    
    # 检查QLib是否初始化
    try:
        from qlib.tests.data import GetData
        print("QLib状态: 已初始化")
    except:
        print("QLib状态: 未初始化")
        return
    
    # 尝试不同的数据获取方式
    try:
        # 方式1: 使用D.features
        print("尝试方式1: D.features")
        data = D.features([symbol], fields=['$open', '$close', '$high', '$low', '$volume'])
        print(f"数据形状: {data.shape}")
        print(f"数据列: {data.columns.tolist()}")
        if len(data) > 0:
            print(f"数据样例:\n{data.head(3)}")
            return True
        else:
            print("没有数据返回")
            return False
    except Exception as e:
        print(f"方式1失败: {e}")
        return False

def load_qlib_data(symbol="SZ002837", count=30):
    """从QLib加载股票数据"""
    try:
        # 使用正确的QLib字段名（不包含复权因子）
        fields = ['$open', '$close', '$high', '$low', '$volume']
        data = D.features([symbol], fields=fields)
        
        print(f"原始数据形状: {data.shape}")
        print(f"数据列名: {data.columns.tolist()}")
        
        # 转换为DataFrame
        df = data.reset_index()
        
        # 检查数据
        print(f"数据前3行:\n{df.head(3)}")
        
        # 重命名列（去掉$符号）
        column_mapping = {
            '$open': 'open',
            '$close': 'close', 
            '$high': 'high',
            '$low': 'low',
            '$volume': 'volume'
        }
        
        df = df.rename(columns=column_mapping)
        
        # 确保必要的列存在
        required_cols = ['open', 'close', 'high', 'low', 'volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"缺少列: {missing_cols}")
            return get_fallback_data()
        
        # 取最近count个交易日的数据
        df = df.tail(count).reset_index(drop=True)
        
        # 添加日期列和股票代码列
        if 'datetime' in df.columns:
            df['date'] = df['datetime'].dt.strftime('%Y-%m-%d')
        df['instrument'] = symbol
        
        # 检查数据是否有效
        if df['close'].isna().all() or len(df) == 0:
            print("数据无效，使用备用数据")
            return get_fallback_data()
        
        print(f"成功加载 {len(df)} 条数据")
        print(f"最新收盘价: {df['close'].iloc[-1]:.2f}")
            
        return df[['date', 'instrument', 'open', 'close', 'high', 'low', 'volume']]
    
    except Exception as e:
        print(f"从QLib加载数据失败: {e}")
        print("使用备用数据...")
        return get_fallback_data()
    
def get_fallback_data():
    """备用数据（当QLib数据不可用时使用）"""
    print("使用备用示例数据...")
    data = {
        'date': ['2025-09-23', '2025-09-24', '2025-09-25', '2025-09-26', '2025-09-29', '2025-09-30'],
        'instrument': ['SZ002837', 'SZ002837', 'SZ002837', 'SZ002837', 'SZ002837', 'SZ002837'],
        'open': [8.45, 8.50, 8.55, 8.48, 8.42, 8.40],
        'close': [8.52, 8.58, 8.50, 8.45, 8.38, 8.35],
        'high': [8.60, 8.65, 8.62, 8.55, 8.50, 8.45],
        'low': [8.40, 8.45, 8.42, 8.38, 8.35, 8.30],
        'volume': [15678900, 14235600, 13894200, 16789300, 15876400, 3428700],
    }
    return pd.DataFrame(data)
    
# 预测函数
def simple_trend_prediction(df):
    """基于价格趋势的简单预测"""
    prices = df['close'].values
    
    if len(prices) < 3 or np.any(np.isnan(prices)):
        current_price = df['close'].iloc[-1]
        return current_price, "数据不足或有NaN"
    
    # 计算近期趋势
    recent_trend = (prices[-1] - prices[-3]) / prices[-3]
    
    if recent_trend < -0.05:
        prediction = prices[-1] * 0.98
        trend = "下跌"
    elif recent_trend > 0.02:
        prediction = prices[-1] * 1.02
        trend = "上涨"
    else:
        prediction = prices[-1] * 1.00
        trend = "横盘"
    
    return prediction, trend

def moving_average_prediction(df):
    """基于移动平均的预测"""
    prices = df['close'].values
    
    if len(prices) < 3 or np.any(np.isnan(prices)):
        return df['close'].iloc[-1]
    
    ma_3 = np.mean(prices[-3:])
    if prices[-1] < ma_3:
        prediction = (prices[-1] + ma_3) / 2
    else:
        prediction = prices[-1] * 0.995
    
    return prediction

def pattern_recognition_prediction(df):
    """基于价格模式的简单识别"""
    if len(df) < 2 or df['close'].isna().any():
        return df['close'].iloc[-1], "数据不足或有NaN"
    
    latest = df.iloc[-1]
    volume_mean = df['volume'].mean()
    has_high_volume = latest['volume'] > volume_mean
    is_oversold = latest['close'] < latest['open']
    
    if is_oversold and has_high_volume:
        prediction = latest['close'] * 1.015
        reason = "放量下跌后可能技术性反弹"
    elif not is_oversold and has_high_volume:
        prediction = latest['close'] * 1.008
        reason = "放量上涨可能延续"
    else:
        prediction = latest['close'] * 0.998
        reason = "缩量整理，小幅波动"
    
    return prediction, reason

def technical_analysis_prediction(df):
    """基于技术指标的预测"""
    prices = df['close'].values
    
    if len(prices) < 15 or np.any(np.isnan(prices)):
        return df['close'].iloc[-1] * 1.001, "数据不足，默认小幅看涨"
    
    # 计算RSI
    gains = np.where(np.diff(prices) > 0, np.diff(prices), 0)
    losses = np.where(np.diff(prices) < 0, -np.diff(prices), 0)
    
    avg_gain = np.mean(gains[-14:])
    avg_loss = np.mean(losses[-14:])
    
    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
    
    # 基于RSI判断
    if rsi < 30:
        prediction = prices[-1] * 1.02
        reason = f"RSI超卖({rsi:.1f})，可能反弹"
    elif rsi > 70:
        prediction = prices[-1] * 0.985
        reason = f"RSI超买({rsi:.1f})，可能回调"
    else:
        prediction = prices[-1] * 1.005
        reason = f"RSI中性({rsi:.1f})，小幅看涨"
    
    return prediction, reason


def run_qlib_prediction(symbol="SZ002837") -> Dict[str, Any]:
    # 数据初始化
    print("正在初始化QLib...")
    init_qlib()

    # 调试数据加载
    result = debug_data_loading(symbol)
    if not result:
        return {
            "success": True,
            "error": "未找到对应股票数据"
        }

    # 从QLib加载数据
    print(f"\n正在从QLib加载{symbol}数据...")
    df = load_qlib_data(symbol, count=20)

    print("\n当前数据概览:")
    print(df.tail())
    print(f"\n数据基本信息:")
    print(f"数据形状: {df.shape}")
    print(f"收盘价范围: {df['close'].min():.2f} - {df['close'].max():.2f}")
    print(f"最新收盘价: {df['close'].iloc[-1]:.2f}")
    
    print("\n" + "="*50)


    try:
        # 执行预测
        latest_date = df['date'].iloc[-1]
        print(f"开始预测{symbol}在{latest_date}后下一个交易日的股价...\n")

        # 各方法预测
        trend_pred, trend = simple_trend_prediction(df)
        print(f"1. 趋势分析预测: {trend_pred:.2f}")
        print(f"   判断依据: {trend}")

        ma_pred = moving_average_prediction(df)
        print(f"2. 移动平均预测: {ma_pred:.2f}")

        pattern_pred, pattern_reason = pattern_recognition_prediction(df)
        print(f"3. 模式识别预测: {pattern_pred:.2f}")
        print(f"   判断依据: {pattern_reason}")

        tech_pred, tech_reason = technical_analysis_prediction(df)
        print(f"4. 技术指标预测: {tech_pred:.2f}")
        print(f"   判断依据: {tech_reason}")

        # 集成最终预测
        final_prediction = (trend_pred * 0.3 + ma_pred * 0.25 + pattern_pred * 0.25 + tech_pred * 0.2)
        print(f"\n" + "="*50)
        
        current_close = df['close'].iloc[-1]
        change_pct = ((final_prediction / current_close) - 1) * 100
        
        print(f"📈 {symbol} 最终集成预测: {final_prediction:.2f}")
        print(f"📊 相对于最新收盘价({current_close:.2f}): {change_pct:+.2f}%")

        # 交易建议
        print(f"\n💡 交易建议:")
        if final_prediction > current_close * 1.01:
            print("   - 🟢 强烈看涨：可考虑适量买入")
            print(f"   - 阻力位参考: {df['high'].max():.2f}")
            s = "🟢 强烈看涨：可考虑适量买入"
            h = f"阻力位参考: {df['high'].max():.2f}"
        elif final_prediction > current_close:
            print("   - 🟡 谨慎看涨：可考虑观望或轻仓试多")
            print(f"   - 阻力位参考: {df['high'].max():.2f}")
            s = "🟡 谨慎看涨：可考虑观望或轻仓试多"
            h = f"阻力位参考: {df['high'].max():.2f}"
        else:
            print("   - 🔴 看跌：建议谨慎操作或考虑减仓")
            print(f"   - 支撑位参考: {df['low'].min():.2f}")
            s = "🔴 看跌：建议谨慎操作或考虑减仓"
            h = f"支撑位参考: {df['low'].min():.2f}"

        # 显示关键技术位
        print(f"\n📊 关键技术位置:")
        print(f"   - 近期高点: {df['high'].max():.2f}")
        print(f"   - 近期低点: {df['low'].min():.2f}")
        print(f"   - 当前收盘: {current_close:.2f}")
        print(f"   - 5日均价: {df['close'].tail(5).mean():.2f}")
        print(f"   - 10日均价: {df['close'].tail(10).mean():.2f}")
        print(f"   - 最新成交量: {df['volume'].iloc[-1]:,.0f}")

        print(f"\n⚠️  风险提示: 基于{len(df)}个交易日的历史数据预测，仅供参考!")

        return {
            "success": True,
            "symbol": symbol,
            "prediction": f"<ul><li>1. 趋势分析预测: {trend_pred:.2f} 判断依据: {trend} </li> <li>2. 移动平均预测: {ma_pred:.2f}</li> <li>3. 模式识别预测: {pattern_pred:.2f} 判断依据: {pattern_reason}</li> <li>4. 技术指标预测: {tech_pred:.2f} 判断依据: {tech_reason}</li></ul>",
            "final_prediction_price": f"📈 {symbol} 最终集成预测: {final_prediction:.2f}  📊 相对于最新收盘价({current_close:.2f}): {change_pct:+.2f}%",
            "suggestion": {s,h},
            "keys": f"📊 关键技术位置:近期高点: {df['high'].max():.2f} 近期低点: {df['low'].min():.2f} 当前收盘: {current_close:.2f} 5日均价: {df['close'].tail(5).mean():.2f} 10日均价: {df['close'].tail(10).mean():.2f} 最新成交量: {df['volume'].iloc[-1]:,.0f}",
            "tips": f"⚠️ 风险提示: 基于{len(df)}个交易日的历史数据预测，仅供参考!"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }