from flask import Flask, request, jsonify
import checker
import pictureProcess
from pathlib import Path

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
    api_setting.append(client_info_2)
    client_info_4 = {"api_base": "https://aihubmix.com/v1",
                    "api_key": "sk-BsPxLFuT1VMaBv39532f2959Ba8d4bAcB7E6BeF69bB45c89",
                    "model_name": "chatgpt-4o-latest"}
    api_setting.append(client_info_2)
    return api_setting

def analyze_input(user_message):
    # 判断输入是否是文本
    claim = ""



def analyze_text(text):
    answer = f"{type(text)}"
    result = f"{type(text)}"
    res = {'answer': answer, 'category': result}
    return res