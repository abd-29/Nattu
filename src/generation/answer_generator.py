from openai import OpenAI

from config import OPENROUTER_API_KEY


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)


def call_llm(prompt: str) -> str:
    """Call a free model through OpenRouter."""
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def generate_answer(prompt: str) -> str:
    """Generate an answer from the provided RAG context."""
    return call_llm(prompt)


def generate_general_answer(query: str) -> str:
    """Generate a concise general answer."""
    prompt = f"""
Tu es Nattu Assistant.

Réponds directement et simplement à la question de l'utilisateur.

Règles obligatoires :
- Donne uniquement la réponse utile.
- Pas d'introduction.
- Pas de conclusion inutile.
- Ne mentionne jamais "mes connaissances générales".
- Ne mentionne jamais que la réponse ne vient pas des documents.
- Ne reformule pas la question.
- Pour une salutation, réponds simplement par une salutation.
- Sois concis.

Question :
{query}
"""
    return call_llm(prompt).strip()


def check_answerability(query: str, context: str) -> list[int]:
    """Identify which sources can answer the question."""
    prompt = f"""
Tu dois déterminer quelles sources permettent réellement de répondre à la question.

Retourne uniquement les numéros des sources pertinentes séparés par des virgules.

Exemples :
1
1,3
2,4

Si aucune source ne permet de répondre, retourne :
NONE

Question :
{query}

Contexte :
{context}

Sources pertinentes :
""".strip()

    answer = call_llm(prompt).strip()

    if answer.upper() == "NONE":
        return []

    source_numbers = []

    for value in answer.split(","):
        value = value.strip()

        if value.isdigit():
            source_numbers.append(int(value))

    return source_numbers