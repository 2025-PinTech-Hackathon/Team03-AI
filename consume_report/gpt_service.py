import os
from openai import OpenAI
from dotenv import load_dotenv
from consume_report.schemas import SpendingRequest
import httpx

load_dotenv()

http_client = httpx.Client()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=http_client
)

def generate_summary(request: SpendingRequest) -> str:
    role = request.role.upper()
    transactions = request.transactions

    if not transactions:
        return "오늘은 소비 기록이 없었어요."

    formatted = [f"{t.merchant_name}({abs(t.amount)}원)" for t in transactions]
    description = ", ".join(formatted)

    if role == "CHILD":
        prompt = (
            f"나는 초등학생이고, 오늘 아래와 같은 소비를 했어: {description}. "
            "이걸 바탕으로 나의 소비를 돌아보며 감성적이고 짧은 한 줄 평을 50자 이내로 써줘. "
            "예: 간식이랑 장난감에 꽤 많이 썼네! 재미있는 하루였어!"
            "\"이런거 추가하지 말고 그냥 텍스트만 반환해"
        )
        system_prompt = "너는 초등학생의 소비 내역을 듣고, 아이의 입장에서 한 줄 평을 해주는 사람이야."
    elif role == "PARENT":
        prompt = (
            f"다음은 내 아이의 오늘 소비 내역이야: {description}. "
            "이 소비를 보고 부모의 시선에서 짧고 감성적인 한 줄 평가를 50자 이내로 해줘. "
            "예: 간식과 쇼핑에 집중한 하루였네요. 즐겁게 보낸 것 같아요."
            "\"이런거 추가하지 말고 그냥 텍스트만 반환해"
        )
        system_prompt = "너는 부모의 입장에서 자녀의 소비를 보고 한 줄 평을 이야기 해주는 사람이야."
    else:
        prompt = f"소비 내역: {description}"
        system_prompt = "소비 내역을 요약해주는 비서야."

    chat_completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

    return chat_completion.choices[0].message.content.strip()