from flask import Flask, request, jsonify
import checker
import pictureProcess
from pathlib import Path
import base64
import re

def get_api():
    api_setting = []
    client_info_0 = {"api_base": "https://api.deepseek.com/v1",
                "api_key": "sk-5e09567f3033401faabb0b622726fce4",
                "model_name": "deepseek-chat"}
    api_setting.append(client_info_0)
    client_info_1 = {"api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                    "api_key": "sk-72d08726be264ffb911b02e3744d31d8",
                    "model_name": "qwen-plus"}
    api_setting.append(client_info_1)
    client_info_2 = {"api_base": "https://aihubmix.com/v1",
                    "api_key": "sk-BsPxLFuT1VMaBv39532f2959Ba8d4bAcB7E6BeF69bB45c89",
                    "model_name": "gemini-2.5-pro"}
    api_setting.append(client_info_2)
    client_info_3 = {"api_base": "https://api.moonshot.cn/v1",
                    "api_key": "sk-Qu9H5NKr5NGnVVjcjBiKh5UsN9b7q4juv2CtzYhz386mDfyN",
                    "model_name": "kimi-k2-0711-preview"}
    api_setting.append(client_info_3)
    client_info_4 = {"api_base": "https://aihubmix.com/v1",
                    "api_key": "sk-BsPxLFuT1VMaBv39532f2959Ba8d4bAcB7E6BeF69bB45c89",
                    "model_name": "chatgpt-4o-latest"}
    api_setting.append(client_info_4)
    return api_setting

def fileProcess(data):
    """处理 Base64 编码的文件内容"""
    file_name = data.get('fileName', '未知文件')
    file_type = data.get('fileType', '未知类型')
    base64_data_url = data.get('content')

    # 1. 解析 Base64 数据：去除前缀 'data:image/png;base64,'
    base64_match = re.search(r'base64,(.*)', base64_data_url)
    if not base64_match:
        return {"result": "uncertain", "text": "文件解析失败，Base64 格式错误。"}

    pure_base64 = base64_match.group(1)
    # 将 Base64 解码为原始字节数据 (bytes)
    try:
        file_bytes = base64.b64decode(pure_base64)
    except Exception as e:
        return {"result": "uncertain", "text": f"Base64 解码失败: {e}"}

    # 2. 使用 pictureProcess 提取文本内容

    return {"result": "uncertain", "text": f"已识别到文件 ({file_name})，文件类型({file_type})，内容待核查。"}

def textProcess(data):
    """根据输入类型和内容进行处理"""
    content = data.get('content')
    api = get_api()
    method = "single"       # single or multi
    LLM_result = checker.check_by_LLM(content, api, method=method)
    # result = LLM_result["verdict"]
    # response_text = LLM_result["reasoning"]
    response = {
        "claim" : "", 
        "data" : "", 
        "warrant" : "",
        "backing" : "",
        "qualifier" : "",
        "rebuttal" : "",
        "verdict" : "",
        "explanation" : ""
    }
    for key, value in LLM_result.items():
        print(f"{key}: {value[:80]}..." if len(value) > 80 else f"{key}: {value}")
        key = key.lower()
        if key in response:
            response[key] = str(value)
            if value == "supported":
                response[key] = "correct"
            elif value == "refuted":
                response[key] = "incorrect"

    return response