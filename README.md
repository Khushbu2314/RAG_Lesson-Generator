# Beginner Lesson Generator

This project uses AI to make a beginner lesson about a topic, check the lesson, and try to improve it if the check finds problems.

## In simple words

Think of it like a student and a teacher:

1. The **generator** writes a lesson.
2. The **evaluator** checks the lesson using a list of rules.
3. If the evaluator finds a problem, it gives feedback.
4. The generator uses that feedback to try again.
5. The process stops when the lesson passes or reaches the retry limit.

The project allows two retries. This means there can be up to three attempts in total: the first lesson and two improved versions.

## What is RAG?

RAG means **Retrieval-Augmented Generation**. It is an AI approach where a system finds useful information from selected documents and gives that information to an AI model to help it answer a question.

This project is a **lesson generator about RAG**. It does not currently use a document search system to check whether lesson facts are true.

## What does the evaluator check?

The evaluator uses the rules in `prompts/evaluator_prompt.txt`. It checks:

- Accuracy and grounding
- Simple language for beginners
- Useful examples
- Explanations of technical words
- Coverage of the topic
- A clear order of ideas

The requested topic is also included in the evaluator prompt. For example, the prompt tells the evaluator to fail an unintelligible topic.

### Important accuracy note

The evaluator is an AI model. It judges accuracy using its own learned knowledge and the instructions in the prompt. It does **not** compare the lesson with trusted reference documents, so it cannot guarantee that every fact is correct.

For stronger fact-checking, provide reliable source documents and require the evaluator to verify important claims against those sources. A person should still review the lesson before sharing it with learners.

## Project files

- `workflow.py` runs the generate, evaluate, and retry steps.
- `generator.py` asks the AI model to write the lesson.
- `evaluator.py` asks the AI model to evaluate the lesson.
- `prompts/generator_prompt.txt` contains the lesson-writing instructions.
- `prompts/evaluator_prompt.txt` contains the evaluation rules.
- `memory.json` stores counts and patterns from past failures to guide later runs.
- `output/generated_lesson.md` stores the latest generated draft.
- `output/evaluation.json` stores the latest evaluation.
- `output/rejection_log.md` records rejected attempts. It can contain failures from earlier runs too.
- `output/final_lesson.md` stores the lesson when a run passes.

The rejection log is not cleared automatically between runs, so check the attempt number and topic when showing an example. A previous rejection and a later pass may be from different runs.

## Setup on Windows

Open PowerShell in this project folder.

1. Create a virtual environment:

   ```powershell
   python -m venv venv
   ```

2. Activate it:

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. Install the project packages:

   ```powershell
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project folder. Add your Groq API key:

   ```text
   GROQ_API_KEY=your_api_key_here
   ```

   Keep this key private. Do not upload `.env` or share your key.

## Run the workflow

With the virtual environment active, run:

```powershell
python workflow.py
```

When asked for a topic, enter:

```text
Introduction to RAG
```

The program prints each attempt and whether it passed or failed. Open the files in the `output` folder to read the lesson, evaluation, and rejection log.

## Showing a failure in a demo

A good lesson may pass on its first attempt. Do not change the result just to make a failure appear.

To show a genuine rejection, open `output/rejection_log.md` and explain that it records a failed attempt from an earlier run. Then show the passing lesson and evaluation from a run that passed. Be clear if they came from separate runs.

## Limits

- The AI evaluator can make mistakes and may judge the same lesson differently on different runs.
- The accuracy check is not verified against trusted sources.
- The workflow can retry only up to two times after the first attempt.
- The saved rejection log contains history from previous runs.
