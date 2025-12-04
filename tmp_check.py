import checker

# config
API_KEY="sk-5e09567f3033401faabb0b622726fce4"
BASE_URL="https://api.deepseek.com/v1"
MODEL_NAME="deepseek-chat"

# get the claim
claim = ""
claim = input("Enter the claim to be checked: ")

# rumor detection
result = checker.check_rumor(claim, BASE_URL, API_KEY, MODEL_NAME)
print(result)