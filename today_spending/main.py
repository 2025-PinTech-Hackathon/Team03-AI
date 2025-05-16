from fastapi import FastAPI
from schemas import SpendingRequest, ReviewResponse
from gpt_service import generate_summary

app = FastAPI()

@app.post("/summary", response_model=ReviewResponse)
def summarize_spending(request: SpendingRequest):
    # 필요한 날짜 필터링도 여기서 가능
    today_transactions = [t.dict() for t in request.transactions if t['timestamp'].date().isoformat() == "2025-05-17"]
    summary = generate_summary(today_transactions)
    return ReviewResponse(summary=summary)