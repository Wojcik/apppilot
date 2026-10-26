"""AppPilot · M0 — send one prompt to two providers, compare answers + token usage.

Run:  uv run python -m apppilot.llm "your prompt"
"""
import os
import sys

from anthropic import Anthropic
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # reads ANTHROPIC_API_KEY, OPENAI_API_KEY, OPENAI_MODEL from .env

CLAUDE_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-5-5")  # small + cheap for experiments
OPENAI_MODEL = os.getenv("OPENAI_MODEL")  # a current small model from OpenAI's model list


def ask_claude(prompt: str) -> tuple[str, int, int]:
    """Return (answer, input_tokens, output_tokens)."""
    client = Anthropic()
    response = client.messages.create(model=CLAUDE_MODEL, max_tokens=300, messages=[{"role":"user", "content": prompt}])
    answer = response.content[0].text
    return answer, response.usage.input_tokens, response.usage.output_tokens


def ask_openai(prompt: str) -> tuple[str, int, int]:
    """Return (answer, input_tokens, output_tokens)."""
    client = OpenAI()
    response = client.chat.completions.create(model=OPENAI_MODEL, messages=[{"role":"user", "content": prompt}])
    answer = response.choices[0].message.content
    return answer, response.usage.prompt_tokens, response.usage.completion_tokens


def main() -> None:
    if not OPENAI_MODEL:
        sys.exit("Set OPENAI_MODEL in .env")
    prompt = " ".join(sys.argv[1:]) or "Explain what an LLM token is in two sentences."
    print(f"Prompt: {prompt}\n")
    for name, model, ask in [("Claude", CLAUDE_MODEL, ask_claude), ("OpenAI", OPENAI_MODEL, ask_openai)]:
        answer, tokens_in, tokens_out = ask(prompt)
        print(f"=== {name} ({model}) · in {tokens_in} / out {tokens_out} tokens ===\n{answer}\n")


if __name__ == "__main__":
    main()
