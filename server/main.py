# main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
from predictor import run_qlib_prediction
from utils import qlib_dump_all
from openai import OpenAI
import json

app = FastAPI(
    title="Qlib Prediction API",
    description="通过 FastAPI 暴露 Qlib 预测能力",
    version="1.0.0"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的源
    allow_credentials=True,  # 允许携带凭证（cookies等）
    allow_methods=["*"],     # 允许所有方法
    allow_headers=["*"],     # 允许所有头
)

# 请求体模型
class PredictRequest(BaseModel):
    symbol: Optional[str] = None  # 格式: "YYYY-MM-DD"

# 健康检查
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Qlib FastAPI 服务运行正常"}

@app.post("/predict", summary="执行 Qlib 预测")
def predict(request: PredictRequest):
    """
    预测接口  
    """
    try:
        # 生成 instrument（带市场前缀）
        if request.symbol.startswith("6"):
            instrument = f"SH{request.symbol}"
        elif request.symbol.startswith("0") or request.symbol.startswith("3"):
            instrument = f"SZ{request.symbol}"
        else:
            instrument = request.symbol
        result = run_qlib_prediction(instrument)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/dump_all", summary="执行 Qlib 数据导入")
def dump_all():  
    """
    数据导入接口  
    """
    try:
        qlib_dump_all(
            data_path="/Users/mxj/Repo/qlib/csv",
            qlib_dir="~/.qlib/qlib_data/my_data",
            freq="day",
            symbol_field_name="instrument",
            date_field_name="date",
            exclude_fields="instrument",  # 也可以是 ["field1", "field2"]
        )
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# 初始化 OpenAI 客户端（兼容百炼）
client = OpenAI(
    api_key="sk-19dce3dc7cbc44fab6c61081180e8f7b",  # 建议使用环境变量
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

@app.get("/chat")
async def chat_stream(prompt: str = Query(..., description="用户输入的问题"),):
    """
    流式对话接口，返回 Server-Sent Events
    """

    # 构造 messages（这里只支持单轮，若需多轮请扩展）
    messages = [
        {"role": "system", "content": "你是一个股市AI专家。"},
        {"role": "user", "content": prompt}
    ]

    def event_generator():
        full_response = ""
        try:
            stream = client.chat.completions.create(
                model="qwen-plus",
                messages=messages,
                stream=True,
                stream_options={"include_usage": True}
            )

            for chunk in stream:
                # 普通文本流
                if chunk.choices:
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                        # 发送文本块 (SSE 格式)
                        yield f"data: {json.dumps({'type': 'content', 'text': content}, ensure_ascii=False)}\n\n"

                # 最后的 usage 信息
                if chunk.usage:
                    usage_data = {
                        "type": "usage",
                        "prompt_tokens": chunk.usage.prompt_tokens,
                        "completion_tokens": chunk.usage.completion_tokens,
                        "total_tokens": chunk.usage.total_tokens
                    }
                    yield f"data: {json.dumps(usage_data, ensure_ascii=False)}\n\n"
                    yield "data: [DONE]\n\n"  # 表示结束

        except Exception as e:
            error_data = {
                "type": "error",
                "message": str(e)
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

# uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# http://localhost:8001/docs#/default/predict_predict_post
