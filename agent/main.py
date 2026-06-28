from fastapi import FastAPI
from pydantic import BaseModel

from llm import ask_llm
from tools.registry import TOOLS

app = FastAPI()


class ChatRequest(BaseModel):
    message: str


@app.get("/healthcheck")
def healthcheck():
    return {"status": "healthy"}


@app.post("/chat")
def chat(request: ChatRequest):

    decision = ask_llm(request.message)
    print("Decision:", decision)

    print(f"LLM Decision: {decision}")

    if decision["tool"]:

        tool = TOOLS[decision["tool"]]

        print("Tool:", decision["tool"])
        print("Arguments:", decision["arguments"])

        result = tool(**decision["arguments"])

        return {
            "result": result
        }

    return {
        "response": decision["response"]
    }