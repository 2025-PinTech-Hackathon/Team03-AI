import os
import openai
from typing import List
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_summary(transactions: List[dict]) -> str:
    formatted = [f"{t['merchant_name']}에서 {abs(t['amount'])}원 사용" for t in transactions]
    user_input = ", ".join(formatted)
    prompt = (
        f"{user_input} 이 소비 내역을 보고 오늘 하루를 한 문장으로 요약해줘. "
        "짧고 자연스럽고, 가볍게 말해줘. 예: '커피와 쇼핑으로 가득한 하루였네요!'"
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "너는 소비 내역을 보고 감성적인 한줄평을 해주는 비서야."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response["choices"][0]["message"]["content"].strip()