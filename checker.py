from openai import OpenAI
from typing import Dict, List, Tuple, Any
from duckduckgo_search import DDGS
from FlagEmbedding import BGEM3FlagModel
import requests
import numpy as np
import re

class RumorChecker:
    def __init__(self, api_setting: List[Dict[str, str]]):
        self.api_base = api_setting[0]["api_base"]
        self.api_key = api_setting[0]["api_key"]
        self.base_model = api_setting[0]["model_name"]
        self.base_client = OpenAI(api_key = self.api_key,
                             base_url = self.api_base)
        
        self.client = []
        self.model = []
        for i in range(len(api_setting)):
            api_base = api_setting[i]["api_base"]
            api_key = api_setting[i]["api_key"]
            model_name = api_setting[i]["model_name"]
            client = OpenAI(api_key = api_key,
                             base_url = api_base)
            self.client.append(client)
            self.model.append(model_name)
    
    def _get_prompts(self):
        prompts = {
            "zh": {
                "extract_claim": """
                你是一个精确的声明提取助手。分析提供的新闻并总结其核心思想。
                将核心思想格式化为一个值得验证的陈述，即一个可以独立验证的声明。
                输出格式：
                claim: <声明>
                """,
                "evaluate_claim": """
                你是事实核查助手。根据证据判断声明的真实性。请用中文回复。

                格式要求：
                VERDICT: TRUE/FALSE/PARTIALLY TRUE
                REASONING: 你的中文推理过程

                重要：请确保推理过程使用中文撰写。
                """,
                "user_extract": "从以下文本中提取关键的事实声明：",
                "user_evaluate": "声明：{claim}\n\n证据：\n{evidence}\n\n请判断声明是否正确。",
                "extract_keyword": """
                你是一个精确的关键词提取助手。分析陈述并提取其中的关键词。
                输出格式：
                <关键词1>, <关键词2>, <关键词3>
                """,
            },
            "en": {
                "extract_claim": """
                You are a precise claim extraction assistant. Analyze the provided news and summarize the central idea of it.
                Format the central idea as a worthy-check statement, which is a claim that can be verified independently.
                output format:
                claim: <claim>
                """,
                "evaluate_claim": """
                You are a fact-checking assistant. Judge if the claim is true based on evidence.

                Format required:
                VERDICT: TRUE/FALSE/PARTIALLY TRUE
                REASONING: Your reasoning process
                """,
                "user_extract": "Extract the key factual claims from this text:",
                "user_evaluate": "CLAIM: {claim}\n\nEVIDENCE:\n{evidence}",
                "extract_keyword": """
                You are an accurate keyword extraction assistant. Analyze the statements and extract the keywords.
                Output format:
                <keyword1>, <keyword2>, <keyword3>
                """,
            }
        }
        return prompts
    
    def _detect_language(self, text: str) -> str:
        """
        Simple language detection based on character patterns
        """
        # Check for Chinese characters
        chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
        # Check for Japanese characters
        japanese_chars = len(re.findall(r"[\u3040-\u309f\u30a0-\u30ff]", text))
        # Check for Korean characters
        korean_chars = len(re.findall(r"[\uac00-\ud7af]", text))

        total_chars = len(text)
        if total_chars == 0:
            return "en"

        # If more than 30% are CJK characters, detect specific language
        cjk_ratio = (chinese_chars + japanese_chars + korean_chars) / total_chars
        if cjk_ratio > 0.3:
            if chinese_chars > japanese_chars and chinese_chars > korean_chars:
                return "zh"
            elif japanese_chars > korean_chars:
                return "ja"
            elif korean_chars > 0:
                return "ko"

        return "en"

    def _translate_claim(self, claim: str, target_languages: list):
        translations = {self._detect_language(claim): claim}
        translation_prompt = {
            "en": f"Please translate the following text to English, keep the meaning precise. Please be sure to ensure the translation of technical terms.: {claim}",
            "zh": f"请将以下文本翻译成中文，保持意思准确: {claim}",
            "ja": f"以下のテキストを日本語に翻訳してください、意味を正確に保ってください: {claim}",
            "ko": f"다음 텍스트를 한국어로 번역해주세요, 의미를 정확하게 유지하세요: {claim}"
        }
        for lang in target_languages:
            if lang not in translations:
                if lang not in translation_prompt:
                    continue
                response = self.base_client.chat.completions.create(
                    model=self.base_model,
                    messages=[
                        {"role": "system", "content": "You are a professional translator. Translate accurately and concisely."},
                        {"role": "user", "content": translation_prompt[lang]}
                    ],
                    temperature=0.0,
                    max_tokens=200
                )
                translated_text = response.choices[0].message.content.strip()
                # Clean up any translation artifacts
                if translated_text and not translated_text.startswith("Translation:"):
                    translations[lang] = translated_text
        return translations
    
    def _search_with_searxng(self, query: str, max_results: int = 5):
        # 使用Searxng实例（开源元搜索引擎）
        SEARXNG_URL = "https://searx.space/search"
        
        params = {
            "q": query,  # 精确匹配
            "format": "json",
            "count": max_results
        }

        response = requests.get(SEARXNG_URL, params=params, timeout=30)
        data = response.json()
        print(f"Searxng search data: {data}\n")
        evidence_docs = []
        for result in data.get("results", [])[:max_results]:
            evidence_docs.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "snippet": result.get("content", "")
            })
        return evidence_docs

    def _extract_keywords(self, text: str):
        prompts = self._get_prompts()
        lang = self._detect_language(text)
        response = self.base_client.chat.completions.create(
            model=self.base_model,
            messages=[
                {"role": "system", "content": prompts[lang]["extract_keyword"]},
                {"role": "user", "content": text}
            ],
            temperature=0,
            max_tokens=100
        )
        keywords_text = response.choices[0].message.content.strip()
        # Clean and return keywords
        keywords = re.split(r",\s*|\n", keywords_text)
        keywords = [kw.strip() for kw in keywords if kw.strip()]
        return keywords
    
    def _search_with_duckduckgo(self, lang: str, query: str, max_results: int = 10):
        if lang == "zh":
            region = 'zh-cn'
        else:
            region = 'us-en'
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            query_keyword = self._extract_keywords(query)[:1]
            ddgs = DDGS(timeout=60, headers=headers)
            results = []
            for kw in query_keyword:
                # print(f"Searching DuckDuckGo with keyword: {kw}\n")
                results.extend(list(ddgs.text(kw, region=region, max_results=max_results)))

            evidence_docs = []
            for result in results:
                evidence_docs.append(
                    {
                        "title": result.get("title", ""),
                        "url": result.get("href", ""),
                        "snippet": result.get("body", ""),
                    }
                )
        except Exception as e:
            print(f"DuckDuckGo search failed: {str(e)}")
            return []
        return evidence_docs
    


    def extract_key_info(self, claim: str):
        print("Extracting key information from claim...\n")
        prompts = self._get_prompts()
        response = self.base_client.chat.completions.create(
            model=self.base_model,
            messages=[
                {"role": "system", "content": prompts["en"]["extract_claim"]},
                {"role": "user", "content": prompts["en"]["user_extract"] + "\n" + claim}
            ],
            temperature = 0,
            max_tokens = 500
        )
        claim_text = response.choices[0].message.content
        claims = re.findall(r"\d+\.\s+(.*?)(?=\n\d+\.|\Z)", claim_text, re.DOTALL)
        claims = [claim.strip() for claim in claims if claim.strip()]

        if not claims and claim_text.strip():
                claims = [
                    line.strip()
                    for line in claim_text.strip().split("\n")
                    if line.strip()
                ]
        # Return the first claim if available, otherwise return the original text
        if claims:
            return claims[0]
        else:
            # Fallback: return the original text or a cleaned version
            return claim_text.strip() if claim_text.strip() else claim

    def search_related_info(self, key_info: str):
        print("Searching for related information...\n")
        search_languages = ['en', 'zh']
        translations = self._translate_claim(key_info, search_languages)
        
        all_evidence = []
        for lang, translated_claim in translations.items():
            # print(f"Searching in language: {lang} for claim: {translated_claim}\n")
            evidence_docs = self._search_with_duckduckgo(lang, translated_claim)
            for doc in evidence_docs:
                doc['search_language'] = lang
                doc['search_query'] = translated_claim
            all_evidence.extend(evidence_docs)

        seen_urls = set()
        unique_evidence = []
        for doc in all_evidence:
            if doc['url'] not in seen_urls:
                seen_urls.add(doc['url'])
                unique_evidence.append(doc) 
        return unique_evidence   
    
    def get_evidence_chunks(self, evidence_docs: List[Dict[str, str]],
        claim: str,
        chunk_size: int = 200,
        chunk_overlap: int = 50,
        top_k: int = 10,
    ):
        model = BGEM3FlagModel('BAAI/bge-m3',  
                       use_fp16=True)
        chunks = []
        for doc in evidence_docs:
            chunk_data = {
                "text": doc["title"],
                "url": doc["url"],
            }
            chunks.append(chunk_data)
            snippet = doc["snippet"]
            if len(snippet) <= chunk_size:
                chunk_data = {
                    "text": snippet,
                    "url": doc["url"],
                }
                chunks.append(chunk_data)
            else:
                for i in range(0, len(snippet), chunk_size - chunk_overlap):
                    chunk_text = snippet[i : i + chunk_size]
                    chunk_data = {
                        "text": chunk_text,
                        "url": doc["url"],
                    }
                    chunks.append(chunk_data)
        chunk_texts = [chunk["text"] for chunk in chunks]
        claim_embedding = model.encode([claim],batch_size=12, max_length=8192)['dense_vecs']
        evidence_embeddings = model.encode(chunk_texts,batch_size=12, max_length=8192)['dense_vecs']
        similarities = claim_embedding @ evidence_embeddings.T
        # print(f"Similarities: {similarities}\n")
        for i, similarity in enumerate(similarities[0]):
            chunks[i]["similarity"] = similarity
        ranked_chunks = sorted(chunks, key=lambda x: x["similarity"], reverse=True)
        optimized_evidence = ranked_chunks[:top_k]
        # optimized_evidence = evidence_docs
        return optimized_evidence
        
    def analyze_information(self, claim: str, evidence_chunks: List[Dict[str, str]]):
        print("Analyzing information to determine if the claim is a rumor...\n")
        prompts = self._get_prompts()
        evidence_text = "\n\n".join(
            [
                f"EVIDENCE {i+1} :\n{chunk['text']}\nSource: {chunk['url']}"
                for i, chunk in enumerate(evidence_chunks)
            ]
        )
        # print(f"Compiled evidence text:\n{evidence_text}\n")

        messages = [
            {"role": "system", "content": prompts["en"]["evaluate_claim"]},
            {
                "role": "user",
                "content": prompts["en"]["user_evaluate"].format(
                    claim=claim, evidence=evidence_text
                ),
            },
        ]
        response = self.base_client.chat.completions.create(
            model=self.base_model,
            messages=messages,
            temperature=0,
            max_tokens=500,
        )
        result_text = response.choices[0].message.content

        if result_text:
            # Replace problematic Unicode characters
            result_text = result_text.replace('\u2011', '-')  # Non-breaking hyphen to normal hyphen
            result_text = result_text.replace('\u2013', '-')  # En dash to normal hyphen
            result_text = result_text.replace('\u2014', '-')  # Em dash to normal hyphen
            result_text = result_text.replace('\u2010', '-')  # Hyphen to normal hyphen
            # Remove other potentially problematic characters
            result_text = ''.join(char for char in result_text if ord(char) < 65536)
        verdict_match = re.search(
                r"(?:VERDICT|判断|结论)[:：]\s*(TRUE|FALSE|PARTIALLY TRUE|正确|错误|部分正确|无法验证)",
                result_text,
                re.IGNORECASE,
            )

        if verdict_match:
            verdict_raw = verdict_match.group(1).upper()
            # Map Chinese terms to English
            if verdict_raw in ["正确", "TRUE"]:
                verdict = "TRUE"
            elif verdict_raw in ["错误", "FALSE"]:
                verdict = "FALSE"
            elif verdict_raw in ["部分正确", "PARTIALLY TRUE"]:
                verdict = "PARTIALLY TRUE"
            else:
                verdict = "UNVERIFIABLE"
        else:
            # Try to infer from content if no explicit verdict found
            if "is true" in result_text.lower() or "supported" in result_text.lower():
                verdict = "TRUE"
            elif "is false" in result_text.lower() or "contradicted" in result_text.lower():
                verdict = "FALSE"
            else:
                verdict = "UNVERIFIABLE"
        reasoning_match = re.search(
                r"(?:REASONING|推理过程|推理|分析)[:：]\s*(.*)",
                result_text,
                re.DOTALL | re.IGNORECASE,
            )
        reasoning = (
            reasoning_match.group(1).strip()
            if reasoning_match
            else result_text.strip()
        )
        return {"verdict": verdict, "reasoning": reasoning}


    def check(self, claim: str):
        # 1. Extract key information from the claim
        key_info = self.extract_key_info(claim)
        # print(f"Key information extracted: {key_info}\n")

        # 2. Search for related information using the API
        # TODO: Implement database search
        # TODO: Implement multi-source search
        related_info = self.search_related_info(key_info)
        print(f"Found {len(related_info)} related information pieces.\n")

        evidence_chunks = self.get_evidence_chunks(related_info, claim)

        # 3. Analyze the related information to determine if the claim is a rumor
        is_rumor = self.analyze_information(claim, evidence_chunks)

        result = {
            "claim": claim,
            "is_rumor": is_rumor,
            "related_info": related_info
        }
        return result
    
    def _result_parser(self, result_text: str) -> Dict[str, Any]:
        if result_text:
            # Replace problematic Unicode characters
            result_text = result_text.replace('\u2011', '-')  # Non-breaking hyphen to normal hyphen
            result_text = result_text.replace('\u2013', '-')  # En dash to normal hyphen
            result_text = result_text.replace('\u2014', '-')  # Em dash to normal hyphen
            result_text = result_text.replace('\u2010', '-')  # Hyphen to normal hyphen
            # Remove other potentially problematic characters
            result_text = ''.join(char for char in result_text if ord(char) < 65536)
        verdict_match = re.search(
                r"(?:VERDICT|判断|结论)[:：]\s*(TRUE|FALSE|PARTIALLY TRUE|正确|错误|部分正确|无法验证)",
                result_text,
                re.IGNORECASE,
            )
        if verdict_match:
            verdict_raw = verdict_match.group(1).upper()
            # Map Chinese terms to English
            if verdict_raw in ["正确", "TRUE"]:
                verdict = "TRUE"
            elif verdict_raw in ["错误", "FALSE"]:
                verdict = "FALSE"
            elif verdict_raw in ["部分正确", "PARTIALLY TRUE"]:
                verdict = "PARTIALLY TRUE"
            else:
                verdict = "UNVERIFIABLE"
        else:
            # Try to infer from content if no explicit verdict found
            if "is true" in result_text.lower() or "supported" in result_text.lower():
                verdict = "TRUE"
            elif "is false" in result_text.lower() or "contradicted" in result_text.lower():
                verdict = "FALSE"
            else:
                verdict = "UNVERIFIABLE"
        reasoning_match = re.search(
                r"(?:REASONING|推理过程|推理|分析)[:：]\s*(.*)",
                result_text,
                re.DOTALL | re.IGNORECASE,
            )
        reasoning = (
            reasoning_match.group(1).strip()
            if reasoning_match
            else result_text.strip()
        )
        return {"verdict": verdict, "reasoning": reasoning}

    def check_with_client(self, claim: str, client: OpenAI, model_name: str):
        # Analyze the claim directly using the provided client
        prompt = """
                You are a fact-checking assistant. Judge if the claim is true based on evidence.

                Format required:
                VERDICT: TRUE/FALSE/PARTIALLY TRUE
                REASONING: Your reasoning process
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
            temperature=0,
            max_tokens=500,
        )
        result_text = response.choices[0].message.content
        result = self._result_parser(result_text)
        print(f"Result from model {model_name}:{result["verdict"]}\n")
        return result


    def check_by_LLM(self, claim: str):
        # Directly analyze the claim using LLM without external evidence
        # Using multi-client to get diverse perspectives
        combined_responses = []
        for i in range(len(self.client)):
            print(f"Checking with client {i+1} using model {self.model[i]}...\n")
            for j in range(3):  # Get multiple responses per client
                response = self.check_with_client(claim, self.client[i], self.model[i])
                combined_responses.append(response)
        return combined_responses


def check_rumor(claim: str, api_setting: List[Dict[str, str]]):
    checker = RumorChecker(api_setting)
    result = checker.check(claim)
    return result

def check_by_LLM(claim: str, api_setting: List[Dict[str, str]]):
    print("Checking by LLM...")
    checker = RumorChecker(api_setting)
    result = checker.check_by_LLM(claim)
    return result
