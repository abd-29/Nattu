import re


def clean_text(
    text: str,
) -> str:
    """
    Remove common extraction noise from text.
    """

    cleaned_lines = []

    for line in text.splitlines():

        normalized_line = " ".join(
            line.split()
        )

        if not normalized_line:
            cleaned_lines.append("")
            continue

        if re.fullmatch(
            r"\d+",
            normalized_line,
        ):
            continue

        if normalized_line.startswith(
            "NovaTech Industries - Document interne"
        ):
            continue

        cleaned_lines.append(
            line.strip()
        )

    return "\n".join(
        cleaned_lines
    ).strip()




def clean_units(
    units: list[dict],
) -> list[dict]:
    """
    Clean text while preserving unit metadata.
    """

    cleaned_units = []

    for unit in units:

        cleaned_units.append(
            {
                **unit,
                "text": clean_text(
                    unit["text"]
                ),
            }
        )

    return cleaned_units



