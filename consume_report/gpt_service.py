import os
from openai import OpenAI
from dotenv import load_dotenv
from consume_report.schemas import SpendingRequest, MonthlyReportResponse
import httpx

load_dotenv()

http_client = httpx.Client()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=http_client
)

# 오늘의 소비 한줄평
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


# 한달 소비 리포트
def generate_monthly_report(request: SpendingRequest) -> MonthlyReportResponse:
    role = request.role.upper()
    transactions = request.transactions

    if not transactions:
        return MonthlyReportResponse(summary="이번 달 소비 내역이 없습니다.", shopping=0, food=0, culture=0, etc=0)

    formatted = [f"{t.merchant_name}({abs(t.amount)}원)" for t in transactions]
    description = ", ".join(formatted)

    prompt = (
        f"다음은 이번 달 소비 내역이야: {description}. 각 소비 항목의 상호명을 참고해서 총 4개의 카테고리로 분류해줘: "
        "'쇼핑', '식비', '문화', '기타'. 각 카테고리에 해당하는 소비 비율을 백분율로 추정해줘 (반드시 합이 100이 되게)."
    )

    if role == "CHILD":
        prompt += (" 그리고 어린이의 입장에서 카테고리 상관없이 이번 달 소비를 돌아보며 짧은 한줄 평가를 50자 이내로 작성해줘."
            "예시: '이번 달은 먹고 싶은 거 많이 먹어서 행복했어!' 또는 '장난감도 사고 재미있는 시간 보냈어!' 같은 느낌으로 작성해줘."
        )
        system_prompt = "너는 초등학생의 한 달 소비 리포트를 분석해주는 도우미야."
    else:
        prompt += (" 그리고 부모의 입장에서 카테고리 상관없이 아이의 소비를 돌아보며 한줄 평가를 50자 이내로 작성해줘."
            "예시: '필요한 곳에 잘 소비한 한 달이네요.' 또는 '간식이 많지만 즐거운 소비였던 것 같아요.' 같은 느낌으로 작성해줘."
        )

        system_prompt = "너는 부모의 입장에서 자녀의 한 달 소비를 보고 리포트를 작성해주는 분석가야."

    prompt += (
        "\n\n아래 JSON 형식으로 정확하게 응답해줘. 다른 텍스트는 절대 포함하지 마:\n"
        '''{
        "summary": "한줄평 텍스트",
        "shopping": 숫자,
        "food": 숫자,
        "culture": 숫자,
        "etc": 숫자
        }'''
    )

    chat_completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

    response_text = chat_completion.choices[0].message.content.strip()

    try:
        import json
        parsed = json.loads(response_text)
        return MonthlyReportResponse(
            summary=parsed['summary'],
            shopping=parsed['shopping'],
            food=parsed['food'],
            culture=parsed['culture'],
            etc=parsed['etc']
        )
    except Exception:
        return MonthlyReportResponse(
            summary="GPT 응답을 파싱하는 데 실패했어요.",
            shopping=0, food=0, culture=0, etc=0
        )