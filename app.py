import streamlit as st
import os
from datetime import datetime
import time
import base64
from checker import RumorChecker

from io import BytesIO

st.set_page_config(
    page_title="Health Rumor Checker",
    page_icon="🚀",
    layout="wide"
)

def get_config():
    config_info = {
        "api_key": "sk-5e09567f3033401faabb0b622726fce4", 
        "base_url": "https://api.deepseek.com/v1", 
        "model_name": "deepseek-chat", 
        "search_name": "duckduckgo"
    }
    return config_info

# 应用标题
st.title("🚀 Health Rumor Checker")
st.markdown(
    """
    本应用程序使用大模型验证陈述的准确性。
    请在下方输入需要核查的新闻，系统将检索网络证据进行新闻核查。
    """
    )
with st.sidebar:
    st.header("📊 系统状态")
    config_info = get_config()
    st.success(f"模型加载完成: {config_info['model_name']}")
    st.success(f"搜索引擎: {config_info['search_name']}")

