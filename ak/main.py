from typing import Union
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from getInfo import get_stock_info
from pydantic import BaseModel
from typing import Optional
from get_csv_data import download_and_convert_to_qlib

app = FastAPI()

# 设置允许的源列表
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
]


# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的源
    allow_credentials=True,  # 允许携带凭证（cookies等）
    allow_methods=["*"],     # 允许所有方法
    allow_headers=["*"],     # 允许所有头
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

# 获取股票信息和新闻
@app.get("/symbol/{item_id}")
def read_item(item_id: str):
    return get_stock_info(item_id)

# 请求体模型
class PredictRequest(BaseModel):
    symbol: Optional[str] = None  # 股票代码
    start_date: Optional[str] = None  # 格式: "YYYY-MM-DD"
    end_date: Optional[str] = None  # 格式: "YYYY-MM-DD"

# 根据股票代码和日期区间获取股票数据
@app.post("/get_csv_data", summary="获取股票数据")
def get_csv_data(request: PredictRequest):
    try:
        print(f"request.symbol: {request.symbol}, request.start_date: {request.start_date}, request.end_date: {request.end_date}")

        result = download_and_convert_to_qlib(
            symbol=request.symbol, 
            start_date=request.start_date, 
            end_date=request.end_date,
            output_dir="/Users/mxj/Repo/qlib/csv")
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 启动方式
# fastapi dev main.py