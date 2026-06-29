from fastapi import FastAPI
from pydantic import BaseModel

from llm import ask_llm
from tools.registry import TOOLS

from otel import init_otel
from opentelemetry import trace

app = FastAPI()
init_otel(app)
tracer = trace.get_tracer(__name__)

class ChatRequest(BaseModel):
    message: str


@app.get("/healthcheck")
def healthcheck():
    return {"status": "healthy"}


@app.post("/chat")
def chat(request: ChatRequest):

    with tracer.start_as_current_span("Ask Gemini"):
        decision = ask_llm(request.message)
    
    with tracer.start_as_current_span("Execute Tool"):
        if decision["tool"]:
            tool = TOOLS[decision["tool"]]
            result = tool(**decision["arguments"])
    return result