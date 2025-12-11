from openai import OpenAI
from typing import Dict, List, Tuple, Any
from duckduckgo_search import DDGS
from FlagEmbedding import BGEM3FlagModel
import requests
import numpy as np
import re
import json

class RumorChecker:
    def __init__(self, api_setting: List[Dict[str, str]]):
        self.api_base = []
        self.api_key = []
        self.model = []
        for i in range(len(api_setting)):
            self.api_base.append(api_setting[i]['api_base'])
            self.api_key.append(api_setting[i]['api_key'])
            self.model.append(api_setting[i]['model_name'])

    def check_with_client(self, claim: str, clientNo: int = 0):
        # Analyze the claim directly using the provided client
        model_name = self.model[clientNo]
        client = OpenAI(api_key=self.api_key[clientNo], base_url=self.api_base[clientNo])
        print(f"Checking claim with model {model_name}...\n")
        prompt = """
            你是一名健康信息的事实核查专家。请使用图尔敏(Toulmin)  论证模型的分析要求来分析下列论断（claim），并按照示例的json格式输出。
            <图尔敏分析要求>
            你需要严格遵循以下步骤进行分析：
            1. **Claim（论断）**：清晰地重述该论断。
            2. **Data（论据）**：输入文本中提供了哪些证据（如果有的话）？
            3. **Warrant（推理桥梁）**：哪些推理将论据与论断联系起来？
            4. **Backing（支撑）**：有哪些额外证据或科学共识可以支持或质疑该推理桥梁？
            5. **Qualifier（限定条件）**：在什么条件下，该论断成立（如果有的话）？
            6. **Rebuttal（反驳条件）**：在什么条件下，该论断不成立？
            7. **Fact-checking Verdict（事实核查结论）**：- Supported（支持） / Refuted（反驳） / Not enough evidence（证据不足）
            8. **Explanation（解释）**：请基于 Data、Warrant 和 Rebuttal，给出简明的解释。
            </图尔敏分析要求>
            <json输出格式示例>
            ```json
            {
            "claim": "无论何种蚊子，都有可能传播基孔肯亚热。",
            "data": "该陈述未提供任何证据，只是绝对化断言所有蚊子都具有传播能力。",
            "warrant": "如果一种疾病通过蚊虫叮咬传播，那么所有会叮咬人的蚊子都有可能传播这种疾病。",
            "backing": "根据权威机构（WHO、CDC）与流行病学研究，基孔肯亚热病毒的自然传播媒介高度特异，仅限于特定伊蚊种类，主要为埃及伊蚊（Aedes aegypti）与白纹伊蚊（Aedes albopictus）。其他蚊种通常不能感染或有效传播该病毒。",
            "qualifier": "仅在特定地区和条件下，由已感染基孔肯亚病毒的伊蚊才可能传播该疾病。",
            "rebuttal": "大多数蚊子（例如许多库蚊 Culex）并不能感染或传播基孔肯亚病毒，因此“所有蚊子都可能传播”属于过度泛化。",
            "verdict": "refuted",
            "explanation": "证据表明基孔肯亚热只由特定伊蚊传播，而非所有蚊子。原论断与科学共识不符，属于过度泛化，因此被判定为错误。"
            }
            ```
            """
        messages = [
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": f"CLAIM: {claim}\nPlease determine whether the claim is correct.",
            },
        ]
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.3,
            max_tokens=1000,
            response_format={"type": "json_object"}, 
        )
        # 此时 response.choices[0].message.content 应该是一个纯 JSON 字符串
        result_text = response.choices[0].message.content
        data_dict: Dict[str, str] = json.loads(result_text)
        return data_dict


    def check_by_single_LLM(self, claim: str):
        # Directly analyze the claim using LLM without external evidence
        response = self.check_with_client(claim)
        return response
    
def check_by_LLM(claim: str, api_setting: List[Dict[str, str]], method: str = "single"):
    checker = RumorChecker(api_setting)
    if method == "single":
        result = checker.check_by_single_LLM(claim)
    else:
        raise ValueError("Unsupported method. Use 'single'.")
    return result

# 测试代码
if __name__ == "__main__":
    api_setting = [{"api_base": "https://api.deepseek.com/v1",
                "api_key": "sk-5e09567f3033401faabb0b622726fce4",
                "model_name": "deepseek-chat"}]
    checker = RumorChecker(api_setting)
    claim = "每天喝一杯漂白水可以有效杀死体内癌细胞，预防所有类型的癌症。多位‘匿名医生’证实，这种方法已在地下医疗圈使用多年，效果显著。"
    result = checker.check_by_single_LLM(claim)
    for key, value in result.items():
        print(f"{key}: {value[:80]}..." if len(value) > 80 else f"{key}: {value}")

