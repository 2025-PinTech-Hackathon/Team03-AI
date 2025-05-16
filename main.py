from fastapi import FastAPI
from consume_report.schemas import SpendingRequest, ReviewResponse, MonthlyReportResponse
from consume_report.gpt_service import generate_summary, generate_monthly_report

app = FastAPI()

@app.post("/summary", response_model=ReviewResponse)
async def summarize_spending(request: SpendingRequest):
    summary = generate_summary(request)
    return ReviewResponse(summary=summary)

@app.post("/monthly-report", response_model=MonthlyReportResponse)
async def monthly_report(request: SpendingRequest):
    return generate_monthly_report(request)