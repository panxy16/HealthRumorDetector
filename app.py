import streamlit as st
import os
from datetime import datetime
import time
import base64
from checker import RumorChecker
import auth
import db_utils
from pdf_export import generate_fact_check_pdf
from model_manager import model_manager

from reportlab.pdfgen import canvas
from io import BytesIO

st.set_page_config(
    page_title="Health Rumor Checker",
    page_icon="🚀",
    layout="wide"
)

# 应用标题
st.title("🚀 Health Rumor Checker")
st.markdown("---")