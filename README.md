# ali-wanx-style-repaint
Use Alibaba Wanx API to convert image to a different style, say Ghibli.

Use [fastapi](https://github.com/fastapi/fastapi) for API endpoints, use [showapi](https://github.com/laurentS/slowapi?tab=readme-ov-file) for API rate limitaion.


# Usage
1. Accquire an api-key from [`aliyun bailian console`](https://bailian.console.aliyun.com/?apiKey=1#/api-key), and set the api-key in .env

2. Setup python environment by running: ```python -m venv .venv && source .venv/bin/activate```

3. Install the requirments by: ```pip install -r requirements.txt```

4. Start the fastapi web server: ```fastapi dev main.py```

5. Go to e.g: http://127.0.0.1:8000/style/1?origin_image_url=https://public-vigen-video.oss-cn-shanghai.aliyuncs.com/public/dashscope/test.png to see the results.
