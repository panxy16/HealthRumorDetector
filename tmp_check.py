import checker
import warnings
warnings.simplefilter("ignore", RuntimeWarning)
import pictureProcess
from pathlib import Path

# config
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


# get the claim
print("----Rumor Detection----")
upload_method = input("Choose upload method (Enter 1 for text, enter 2 for picture):")

claim = ""
while(1):
    if upload_method == '1':
        claim = input("Enter the claim to be checked: ")
        break
    elif upload_method == '2':
        filepath = input("Enter the image file path: ")
        claim = pictureProcess.process_file(filepath)
        print(f"Extracted claim: {claim}")
        break
    else:
        print("Invalid input.")
        upload_method = input("Choose upload method (Enter 1 for text, enter 2 for picture):")

# rumor detection
# results = checker.check_rumor(claim, api_setting)

results = checker.check_by_LLM(claim, api_setting)
print("Final Result:")
is_rumor = results["is_rumor"]
related_info = results["related_info"]
print(f"verdict: {is_rumor["verdict"]}")
print(f"reasoning: {is_rumor["reasoning"]}")
