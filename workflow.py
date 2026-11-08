
import json
from pathlib import Path

from generator import generate_lesson
from evaluator import evaluate_lesson


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"

MEMORY_FILE = BASE_DIR / "memory.json"

MAX_RETRIES = 2


def load_memory():

    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    return {
        "total_runs": 0,
        "passed_runs": 0,
        "failed_attempts": 0,
        "failure_patterns": {}
    }


def save_memory(memory):

    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(memory, file, indent=4)


def get_memory_context(memory):

    patterns = memory.get("failure_patterns", {})

    if not patterns:
        return ""

    feedback = []

    for criterion, details in patterns.items():

        feedback.append(
            f"""
        Previous failure category: {criterion}

        Number of previous failures: {details['count']}

        Previous problem:
        {details['last_reason']}

        Required improvement:
        {details['suggestion']}
        """
        )

    return """
    IMPORTANT: Use these lessons from previous generations.

    Before writing the new lesson:
    1. Review every previous failure.
    2. Apply the suggested improvements.
    3. Avoid repeating the same mistakes.
    4. Make sure all important topic sections are covered.

    Previous learning history:

    """ + "\n\n".join(feedback)


def update_memory(memory, evaluation):

    status = evaluation.get("overall_status", "FAIL").upper()

    if status == "PASS":
        memory["passed_runs"] += 1
        return

    memory["failed_attempts"] += 1

    for criterion in evaluation.get("criteria", []):

        if criterion.get("status", "").upper() == "FAIL":

            name = criterion.get("name", "Unknown")

            if name not in memory["failure_patterns"]:
                memory["failure_patterns"][name] = {
                    "count": 0,
                    "last_reason": "",
                    "suggestion": ""
                }

            pattern = memory["failure_patterns"][name]

            pattern["count"] += 1
            pattern["last_reason"] = criterion.get("reason", "")
            pattern["suggestion"] = criterion.get("suggestion", "")

    save_memory(memory)


def format_feedback(evaluation):

    feedback = []

    for criterion in evaluation.get("criteria", []):

        if criterion.get("status", "").upper() == "FAIL":

            feedback.append(
                f"Criterion: {criterion.get('name')}\n"
                f"Reason: {criterion.get('reason')}\n"
                f"Suggestion: {criterion.get('suggestion')}"
            )

    return "\n\n".join(feedback)


def run_workflow(topic):

    OUTPUT_DIR.mkdir(exist_ok=True)

    rejection_log = OUTPUT_DIR / "rejection_log.md"
    generated_file = OUTPUT_DIR / "generated_lesson.md"
    final_file = OUTPUT_DIR / "final_lesson.md"
    evaluation_file = OUTPUT_DIR / "evaluation.json"

    memory = load_memory()
    memory["total_runs"] += 1
    save_memory(memory)

    feedback = None

    for attempt in range(MAX_RETRIES + 1):

        print("\n" + "=" * 45)
        print(f"ATTEMPT {attempt + 1}")
        print("=" * 45)

        # Get previous learning from memory
        memory_context = get_memory_context(memory)

        # Generate lesson
        lesson = generate_lesson(
            topic,
            feedback,
            memory_context
        )

        generated_file.write_text(
            lesson,
            encoding="utf-8"
        )

        print("Lesson generated successfully.")

        # Evaluate lesson
        evaluation = evaluate_lesson(lesson, topic)

        with open(evaluation_file, "w", encoding="utf-8") as file:
            json.dump(evaluation, file, indent=4)

        status = evaluation.get("overall_status", "FAIL").upper()

        print("\nEvaluation result:", status)

        # Update persistent memory
        update_memory(memory, evaluation)

        # If PASS
        if status == "PASS":

            final_file.write_text(
                lesson,
                encoding="utf-8"
            )

            print("\nSUCCESS! Lesson approved.")
            print("Final lesson saved at:", final_file)

            save_memory(memory)

            return

        # If FAIL
        feedback = format_feedback(evaluation)

        with open(rejection_log, "a", encoding="utf-8") as file:

            file.write(f"\n\n# Attempt {attempt + 1} - REJECTED\n\n")

            file.write(
                evaluation.get("summary", "No summary provided.")
                + "\n\n"
            )

            file.write(feedback)

        print("Lesson rejected. Feedback recorded.")
        print("Persistent memory updated.")

        if attempt == MAX_RETRIES:

            print("\nMaximum retries reached.")
            print("Check rejection_log.md for details.")

            return

        print("Regenerating lesson using feedback and memory...")


if __name__ == "__main__":

    topic = input("Enter lesson topic: ").strip()

    if topic:
        run_workflow(topic)
    else:
        print("Please enter a valid topic.")
