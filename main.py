from typing import Final
import asyncio
import httpx

import os
from dotenv import load_dotenv

from typing import Union
from fastapi import FastAPI, Request

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Load environment variables from .env file
load_dotenv()

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Access variables
API_KEY: Final = os.getenv("API_KEY")
API_URL: Final = "https://dashscope.aliyuncs.com/api/v1/services/aigc/image-generation/generation"
CALLBACK_URL: Final = "https://dashscope.aliyuncs.com/api/v1/tasks/"

# Change this to the image url that you want to ref its style:
style_ref_url = "https://pics6.baidu.com/feed/29381f30e924b899f3543621c3ae869a0b7bf6f3.jpeg@f_auto?token=cfc086a746067ded623308bf9a673c79"
# Change this to the original image's url:
# origin_image_url = "https://public-vigen-video.oss-cn-shanghai.aliyuncs.com/public/dashscope/test.png"


@app.get("/")
@limiter.limit("5/minute")
async def homepage(request: Request):
    return {"hello": "world"}


async def poll_status(task_id: str, max_retries: int = 5, delay: float = 3.0):
    """异步轮询查询状态"""
    try:
        url = CALLBACK_URL + task_id
        async with httpx.AsyncClient(headers={"Authorization": "Bearer " + API_KEY}) as client:
            for _ in range(max_retries):
                print(f"Polling status for task ID: {task_id}\n")
                response = await client.get(url)
                if response.status_code == 200:
                    response_json = response.json()
                    print(f"Response: {response_json}\n")
                    if response_json['output']['task_status'] == "SUCCEEDED":
                        # 任务成功
                        result_image_url = response_json['output']['results'][0]['url']
                        return {"result": "success", "result_image_url": result_image_url}
                await asyncio.sleep(delay)  # 休眠后重试
            return {"error": "Timeout or failed"}
    except httpx.RequestError as e:
        return(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")


@app.get("/style/{style_id}")
@limiter.limit("5/minute")
async def start_request(request: Request, style_id: int, origin_image_url: Union[str, None] = None):
    """发送请求并异步轮询"""
    try:
        async with httpx.AsyncClient(headers={"Authorization": "Bearer " + API_KEY, "X-DashScope-Async": "enable"}) as client:
            payload = {
                "model": "wanx-style-repaint-v1",
                "input": {
                    "image_url": origin_image_url,
                    "style_index": -1,
                    "style_ref_url": style_ref_url
                    
                }
            }
            print("Sending request...\n")
            response = await client.post(API_URL, json=payload)
            # print(f"create image Response : {response.text}")
            if response.status_code == 200:
                response_json = response.json()
                task_id = response_json['output']['task_id']
                print(f"Task ID: {task_id}\n")
                await asyncio.sleep(3)  # Wait for 3 seconds before sending the request
                print("Polling task status...\n")
                # 轮询查询任务状态
                return await poll_status(task_id)
            else:
                return(f"Request failed with err msg: {response.text}\n")
    except httpx.RequestError as e:
        return(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    
# This is the target image's url:
# result_image_url = asyncio.run(start_request())
# print(result_image_url)