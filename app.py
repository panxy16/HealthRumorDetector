# app.py (Python 后端)
from flask import Flask, request, jsonify
from flask_cors import CORS
import check  # 你的 AI 分析模块

app = Flask(__name__)
CORS(app)  # 允许跨域请求

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    user_message = data.get('message', '')
    
    # 调用你的 AI 分析逻辑
    result = check.analyze_text(user_message)
    
    return jsonify({
        'text': result['answer'],
        'result': result['category']  # 'positive', 'negative', 'neutral', 'uncertain'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)