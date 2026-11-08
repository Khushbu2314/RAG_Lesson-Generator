
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# Project folder
BASE_DIR = Path(__file__).resolve().parent

# Load API key
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found.")

client = Groq(api_key=api_key)

def evaluate_lesson(lesson, topic):

    # Read evaluator prompt
    prompt_path = BASE_DIR / "prompts" / "evaluator_prompt.txt"

    with open(prompt_path, "r", encoding="utf-8") as file:
        prompt_template = file.read()

    prompt = prompt_template.replace("{topic}", topic).replace("{lesson}", lesson)

    print("\nEvaluating lesson... Please wait.\n")

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "You are a strict educational content evaluator. Return valid JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        max_tokens=2500
    )

    result = response.choices[0].message.content.strip()

    try:
        evaluation = json.loads(result)

    except json.JSONDecodeError:
        start = result.find("{")
        end = result.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("Evaluator did not return valid JSON.")

        evaluation = json.loads(result[start:end + 1])

    return evaluation
