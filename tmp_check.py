import checker
import warnings
warnings.simplefilter("ignore", RuntimeWarning)
import pictureProcess
from pathlib import Path

# config
API_KEY="sk-5e09567f3033401faabb0b622726fce4"
BASE_URL="https://api.deepseek.com/v1"
MODEL_NAME="deepseek-chat"

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
results = checker.check_rumor(claim, BASE_URL, API_KEY, MODEL_NAME)
print("Final Result:")
is_rumor = results["is_rumor"]
related_info = results["related_info"]
print(f"verdict: {is_rumor["verdict"]}")
print(f"reasoning: {is_rumor["reasoning"]}")
