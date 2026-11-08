
import os
from dotenv import load_dotenv
from groq import Groq

# Load API key from .env file
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set.")

client = Groq(api_key=api_key)


def generate_lesson(topic, feedback=None, memory_context=None):

    # Read the generator prompt
    with open(
        "prompts/generator_prompt.txt",
        "r",
        encoding="utf-8"
    ) as file:
        prompt_template = file.read()

    # Insert the topic into the prompt
    prompt = prompt_template.replace("{topic}", topic)

    # Add evaluator feedback from the current workflow
    if feedback:
        prompt += """

    PREVIOUS EVALUATION FEEDBACK:

    """ + feedback

    # Add feedback remembered from previous workflow runs
    if memory_context:
        prompt += """

    LESSONS FROM PREVIOUS RUNS:

    Use the following stored feedback to avoid repeating
    previous mistakes.

    """ + memory_context

    print("\nGenerating lesson... Please wait.\n")

    # Send prompt to Groq
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that generates lessons for students."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4,
        max_tokens=4000
    )

    return response.choices[0].message.content.strip()


if __name__ == "__main__":

    topic = input("Enter a topic for the lesson: ").strip()

    if not topic:
        print("Please enter a valid topic.")
    else:
        lesson = generate_lesson(topic)

        # Create output folder if it does not exist
        os.makedirs("output", exist_ok=True)

        # Save generated lesson
        with open(
            "output/generated_lesson.md",
            "w",
            encoding="utf-8"
        ) as file:
            file.write(lesson)

        print("\nDone! Saved at output/generated_lesson.md")
        print("\n--- GENERATED LESSON ---\n")
        print(lesson)
