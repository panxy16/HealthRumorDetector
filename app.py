import streamlit as st
import tempfile
from PIL import Image
import os

# 假设这是已有的Process函数
# 你需要根据实际情况修改这个函数
def Process(input_data, input_type):
    """
    处理函数，根据输入类型处理文本或图片
    input_type: 'text' 或 'image'
    """
    if input_type == 'text':
        # 处理文本的逻辑
        return f"处理后的文本结果: {input_data.upper()}"
    elif input_type == 'image':
        # 处理图片的逻辑
        # 这里只是一个示例，你应该根据实际情况实现
        return f"图片已处理，尺寸: {input_data.size if hasattr(input_data, 'size') else '未知'}"
    return "处理失败"

def get_config():
    config_info = {
        "api_key": "sk-5e09567f3033401faabb0b622726fce4", 
        "base_url": "https://api.deepseek.com/v1", 
        "model_name": "deepseek-chat", 
        "search_name": "duckduckgo"
    }
    return config_info

st.set_page_config(
    page_title="Health Rumor Detection System",
    page_icon="🤖",
    layout="wide"
)

# 标题
st.title("🤖 Health Rumor Detection System")
st.markdown("---")

# 创建标签页
tab1, tab2 = st.tabs(["📝 文本输入", "🖼️ 图片上传"])

# 文本处理标签页
with tab1:
    st.header("文本输入")
    
    # 文本输入区域
    text_input = st.text_area(
        "请输入要判断的文本：",
        placeholder="在这里输入您的文本...",
        height=150
    )
    
    # 处理按钮
    if st.button("谣言判断", type="primary", key="text_btn"):
        if text_input.strip():
            with st.spinner("正在处理文本..."):
                # 调用Process函数
                result = Process(text_input, 'text')
                
                # 显示结果
                st.success("处理完成！")
                st.subheader("结果：")
                st.write(result)
        else:
            st.warning("请输入文本内容！")

# 图片处理标签页
with tab2:
    st.header("图片上传")
    
    image = None
    
    # 文件上传器
    uploaded_file = st.file_uploader(
        "选择图片文件",
        type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
        key="file_uploader"
    )
    
    if uploaded_file is not None:
        try:
            # 打开图片
            image = Image.open(uploaded_file)
            
            # 显示预览
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("原始图片")
                st.image(image, caption="上传的图片", use_column_width=True)
            
            # 显示图片信息
            with col2:
                st.subheader("图片信息")
                st.write(f"文件名: {uploaded_file.name}")
                st.write(f"格式: {image.format}")
                st.write(f"尺寸: {image.size}")
                st.write(f"模式: {image.mode}")
                
        except Exception as e:
            st.error(f"读取图片失败: {e}")
            
    # 处理按钮
    if st.button("谣言判断", type="primary", key="image_btn"):
        if image is not None:
            with st.spinner("正在处理图片..."):
                # 调用Process函数
                result = Process(image, 'image')
                
                # 显示结果
                st.success("处理完成！")
                st.subheader("结果：")
                st.write(result)
                
                # 如果需要，可以显示处理后的图片
                # 这里假设Process函数返回处理后的图片
                if hasattr(result, 'show'):  # 如果是图片对象
                    st.image(result, caption="处理后的图片", use_column_width=True)
        else:
            st.warning("请先上传或选择图片！")

# 侧边栏信息
with st.sidebar:
    st.header("📊 系统状态")
    config_info = get_config()
    st.success(f"模型加载完成: {config_info['model_name']}")
    st.success(f"搜索引擎: {config_info['search_name']}")
