from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).resolve().parents[1]
KB_PATH = PROJECT_ROOT / "knowledge_base" / "ai_career_guide.md"

STOP_WORDS = {
    "the", "is", "are", "a", "an", "to", "of", "and", "or", "in", "on",
    "for", "with", "what", "how", "why", "can", "i", "me", "my", "you"
}


def load_knowledge_base():
    """
    Loads the local AI career guide.
    """
    if not KB_PATH.exists():
        return ""

    return KB_PATH.read_text(encoding="utf-8")


def tokenize(text):
    """
    Converts text into simple lowercase words.
    """
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    return [word for word in words if word not in STOP_WORDS]


def split_sections(text):
    """
    Splits the markdown knowledge base into sections.
    """
    sections = text.split("\n## ")
    cleaned_sections = []

    for section in sections:
        section = section.strip()
        if section:
            cleaned_sections.append(section)

    return cleaned_sections


def retrieve_context(query, max_sections=2):
    """
    Simple keyword-based retrieval.
    It finds the most relevant sections from the local knowledge base.
    """
    knowledge_text = load_knowledge_base()

    if not knowledge_text:
        return ""

    query_words = set(tokenize(query))
    sections = split_sections(knowledge_text)

    scored_sections = []

    for section in sections:
        section_words = set(tokenize(section))
        score = len(query_words.intersection(section_words))

        if score > 0:
            scored_sections.append((score, section))

    scored_sections.sort(reverse=True, key=lambda item: item[0])

    top_sections = [section for score, section in scored_sections[:max_sections]]

    return "\n\n---\n\n".join(top_sections)