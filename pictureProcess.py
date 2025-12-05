from pathlib import Path
from openai import OpenAI
 


def process_file(path: str):
    client = OpenAI(
    api_key="sk-Qu9H5NKr5NGnVVjcjBiKh5UsN9b7q4juv2CtzYhz386mDfyN", 
    base_url="https://api.moonshot.cn/v1",
    )
    file_object = client.files.create(file=Path(path), purpose="file-extract")
    file_content = client.files.content(file_id=file_object.id).text
 
    messages = [
        {
            "role": "system",
            "content": "你是一个内容提取专家，请从用户上传的图片中提取关键内容",
        },
        {
            "role": "system",
            "content": file_content, 
        },
        {"role": "user", "content": "请提取图片中关键内容，不要包含多余信息（如用户名等）。" },
    ]
    
    # 然后调用 chat-completion, 获取 Kimi 的回答
    completion = client.chat.completions.create(
    model="kimi-k2-turbo-preview",
    messages=messages,
    temperature=0.6,
    )
    
    return completion.choices[0].message.content

if __name__ == "__main__":
    process_file("test.jpg")