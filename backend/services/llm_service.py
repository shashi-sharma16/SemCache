import ollama

from backend.core.config import LLM_MODEL


def generate_answer(query: str, context: str) -> str:
    """Generate an answer using the local Ollama model and policy context."""

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a customer support assistant for ShopEase. "
                    "Answer the user's question using only the policy context below. "
                    "Do not invent order statuses, refund statuses, or customer-specific details. "
                    "If the context does not contain enough information, say so.\n\n"
                    f"Policy context:\n{context}"
                )
            },
            {
                "role": "user",
                "content": query
            }
        ]
    )

    return response["message"]["content"]