# app.py (Python 后端)
from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import re
import check  # 你的 AI 分析模块

app = Flask(__name__)
CORS(app)  # 允许跨域请求

@app.route('/api/analyze', methods=['POST'])
def analyze():
    # ... (JSON 检查逻辑)
    data = request.get_json()
    input_type = data.get('type')
    
    if input_type == 'text':
        # 调用原有的文本处理逻辑
        response_data = check.textProcess(data) 
    elif input_type == 'file':
        # 调用新的文件处理逻辑
        response_data = check.fileProcess(data)
    
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=False, port=5000)