
import ollama

from backend.core.config import LLM_MODEL


def generate_answer(query: str) -> dict:
    """Generate an answer and return its token usage."""

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful AI assistant. "
                    "Answer the user's question clearly, accurately, "
                    "and concisely. If you are unsure, acknowledge "
                    "the uncertainty instead of inventing information."
                )
            },
            {
                "role": "user",
                "content": query
            }
        ]
    )

    return {
        "answer": response["message"]["content"],
        "prompt_tokens": response.get("prompt_eval_count", 0),
        "completion_tokens": response.get("eval_count", 0)
    }
