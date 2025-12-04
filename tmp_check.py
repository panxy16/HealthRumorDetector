import checker
import warnings
warnings.simplefilter("ignore", RuntimeWarning)

# config
API_KEY="sk-5e09567f3033401faabb0b622726fce4"
BASE_URL="https://api.deepseek.com/v1"
MODEL_NAME="deepseek-chat"

# get the claim
claim = input("Enter the claim to be checked: ")

# rumor detection
results = checker.check_rumor(claim, BASE_URL, API_KEY, MODEL_NAME)
print("Final Result:")
is_rumor = results["is_rumor"]
related_info = results["related_info"]
print(f"verdict: {is_rumor["verdict"]}")
print(f"reasoning: {is_rumor["reasoning"]}")
