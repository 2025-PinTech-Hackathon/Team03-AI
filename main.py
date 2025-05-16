from fastapi import FastAPI, Request
from consume_report.schemas import SpendingRequest, ReviewResponse
from consume_report.gpt_service import generate_summary

app = FastAPI()

@app.post("/summary", response_model=ReviewResponse)
async def summarize_spending(request: SpendingRequest):
    summary = generate_summary(request)
    return ReviewResponse(summary=summary)