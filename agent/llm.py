import os
import json

from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


SYSTEM_PROMPT = """
You are an AI assistant.

Available tools:

1. get_students
Parameters: none

2. get_student
Parameters:
- student_id

3. create_student
Parameters:
- name
- email
- age

4. update_student
Parameters:
- student_id
- name
- email
- age

5. delete_student
Parameters:
- student_id

If a tool is needed, respond ONLY with JSON.

Examples:

{
  "tool": "get_students",
  "arguments": {}
}

{
  "tool": "get_student",
  "arguments": {
    "student_id": 1
  }
}

{
  "tool": "create_student",
  "arguments": {
    "name": "Jay",
    "email": "jay@test.com",
    "age": 25
  }
}

{
  "tool": "update_student",
  "arguments": {
    "student_id": 1,
    "name": "Jay",
    "email": "jay@test.com",
    "age": 26
  }
}

{
  "tool": "delete_student",
  "arguments": {
    "student_id": 1
  }
}

If no tool is required, return:

{
  "tool": null,
  "response": "..."
}

Return ONLY valid JSON.
"""


def ask_llm(message: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            SYSTEM_PROMPT,
            message,
        ],
    )

    text = response.text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    return json.loads(text)