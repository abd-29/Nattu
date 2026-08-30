import re

from config import DATA_DIR

from src.embeddings.embedding_model import (
    load_embedding_model,
)
from src.generation.answer_generator import check_faithfulness
from src.indexing.index_state import (
    load_index_state,
)
from src.retrieval.hybrid_search import (
    retrieve_query, hybrid_search, answer_query, build_context,
)
from src.retrieval.reranker import (
    load_reranker, rerank_results,
)


TEST_CASES = [
    # Normal retrieval - Quality
    {
        "query": (
            "Que faut-il faire lorsqu'un "
            "incident sécurité client est qualifié ?"
        ),
        "expected_status": "success",
        "expected_document_id": "QUA-ESC-011",
    },
    {
        "query": (
            "Quelles informations doivent être définies "
            "pour une CAPA majeure ?"
        ),
        "expected_status": "success",
        "expected_document_id": "QUA-CAPA-002",
    },
    {
        "query": (
            "Que se passe-t-il lorsqu'une non-conformité "
            "de niveau A est détectée ?"
        ),
        "expected_status": "success",
        "expected_document_id": "QUA-NCR-003",
    },
    {
        "query": (
            "À quelle fréquence l'habilitation "
            "incident critique doit-elle être renouvelée ?"
        ),
        "expected_status": "success",
        "expected_document_id": "QUA-TRAIN-010",
    },

    # Normal retrieval - Support
    {
        "query": (
            "Quel est le délai de première prise en charge "
            "d'un incident critique pour un contrat Premium ?"
        ),
        "expected_status": "success",
        "expected_document_id": "SUP-SLA-008",
    },
    {
        "query": (
            "Peut-on retourner un équipement "
            "sans numéro RMA ?"
        ),
        "expected_status": "success",
        "expected_document_id": "SUP-RMA-009",
    },
    {
        "query": (
            "Que doit contenir le titre "
            "d'un ticket Support ?"
        ),
        "expected_status": "success",
        "expected_document_id": "SUP-TICKET-007",
    },
    {
        "query": (
            "Que faut-il faire pour l'erreur E17 "
            "si la tension passe sous 18 volts ?"
        ),
        "expected_status": "success",
        "expected_document_id": "KB-1001",
    },

    # Normal retrieval - Products
    {
        "query": (
            "À quelle fréquence faut-il effectuer "
            "une inspection visuelle du produit Alpha ?"
        ),
        "expected_status": "success",
        "expected_document_id": "PRD-ALP-MAINT",
    },
    {
        "query": (
            "Quelles précautions faut-il prendre "
            "lors de l'installation du produit Alpha ?"
        ),
        "expected_status": "success",
        "expected_document_id": "PRD-ALP-INST",
    },
    {
        "query": (
            "Qu'apporte la version 4.2.3 "
            "du produit Alpha ?"
        ),
        "expected_status": "success",
        "expected_document_id": "PRD-ALP-RN42",
    },

    # Normal retrieval - HR
    {
        "query": (
            "Comment un salarié doit-il poser "
            "ses congés chez NovaTech ?"
        ),
        "expected_status": "success",
        "expected_document_id": "HR-POL-002",
    },
    {
        "query": (
            "Quels modules un nouvel arrivant "
            "doit-il suivre pendant son premier mois ?"
        ),
        "expected_status": "success",
        "expected_document_id": "HR-POL-005",
    },

    # Conflict
    {
        "query": (
            "Quel est le délai pour informer "
            "le responsable Quality lors "
            "d'un incident critique ?"
        ),
        "expected_status": "conflict",
        "expected_document_id": "QUA-INC-001",
    },

    # Outside the corpus
    {
        "query": (
            "Quelle est la capitale du Japon ?"
        ),
        "expected_status": "no_answer",
        "expected_document_id": None,
    },

    # Hard no-answer cases
    {
        "query": (
            "Que prévoit la version 9.9.9 "
            "du produit Alpha ?"
        ),
        "expected_status": "no_answer",
        "expected_document_id": None,
    },
    {
        "query": (
            "Que faut-il faire pour l'erreur E99 "
            "sur le produit Alpha ?"
        ),
        "expected_status": "no_answer",
        "expected_document_id": None,
    },
    {
        "query": (
            "Quel est le délai de première prise "
            "en charge pour un contrat Diamond ?"
        ),
        "expected_status": "no_answer",
        "expected_document_id": None,
    },
    {
        "query": (
            "Quel est le prix catalogue "
            "du produit Alpha ?"
        ),
        "expected_status": "no_answer",
        "expected_document_id": None,
    },
    {
        "query": (
            "Quelle est la procédure d'installation "
            "du produit Gamma ?"
        ),
        "expected_status": "success",
        "expected_document_id": "PRD-GAM-INST",
    },
    {
        "query": (
            "Quel est le numéro de téléphone "
            "du directeur Quality ?"
        ),
        "expected_status": "no_answer",
        "expected_document_id": None,
    },
]

def evaluate_generation():
    """
    Evaluate final RAG-generated answers.
    """

    embedding_model = load_embedding_model()
    reranker = load_reranker()
    faithfulness_correct = 0

    index_state_path = (
        DATA_DIR
        / "processed"
        / "index_state.json"
    )

    index_state = load_index_state(
        index_state_path
    )

    generation_cases = [
        {
            "query": (
                "Que faut-il faire lorsqu'un "
                "incident sécurité client est qualifié ?"
            ),
            "expected_document_id": "QUA-ESC-011",
            "expected_terms": [
                "directeur quality",
                "preuves",
                "décisions",
            ],
        },
        {
            "query": (
                "Quel est le délai de première prise "
                "en charge d'un incident critique "
                "pour un contrat Premium ?"
            ),
            "expected_document_id": "SUP-SLA-008",
            "expected_terms": [
                "30 minutes",
            ],
        },
        {
            "query": (
                "À quelle fréquence faut-il effectuer "
                "une inspection visuelle du produit Alpha ?"
            ),
            "expected_document_id": "PRD-ALP-MAINT",
            "expected_terms": [
                "6 mois",
            ],
        },
        {
            "query": (
                "Quelles précautions faut-il prendre "
                "lors de l'installation du produit Alpha ?"
            ),
            "expected_document_id": "PRD-ALP-INST",
            "expected_terms": [
                "hors tension",
                "verrou",
            ],
        },
        {
            "query": (
                "Qu'apporte la version 4.2.3 "
                "du produit Alpha ?"
            ),
            "expected_document_id": "PRD-ALP-RN42",
            "expected_terms": [
                "microcoupures",
                "journal",
            ],
        },
    ]

    total = len(generation_cases)

    status_correct = 0
    source_correct = 0
    content_correct = 0
    citation_correct = 0
    citation_reference_correct = 0

    print()
    print("=" * 70)
    print("GENERATION EVALUATION")

    for index, case in enumerate(
        generation_cases,
        start=1,
    ):

        query = case["query"]

        result = answer_query(
            query=query,
            embedding_model=embedding_model,
            reranker=reranker,
            index_state=index_state,
        )

        answer = result["answer"]

        context = build_context(
            result["results"]
        )

        faithfulness_ok = check_faithfulness(
            answer=answer,
            context=context,
        )

        if faithfulness_ok:
            faithfulness_correct += 1

        normalized_answer = (
            answer
            .lower()
            .replace("’", "'")
        )

        # ----------------------------------------------
        # Status
        # ----------------------------------------------

        status_ok = (
            result["status"]
            == "success"
        )

        if status_ok:
            status_correct += 1

        # ----------------------------------------------
        # Expected document
        # ----------------------------------------------

        retrieved_document_ids = {
            item["document_id"]
            for item in result["results"]
        }

        source_ok = (
            case["expected_document_id"]
            in retrieved_document_ids
        )

        if source_ok:
            source_correct += 1

        # ----------------------------------------------
        # Expected factual content
        # ----------------------------------------------

        content_ok = all(
            term.lower()
            in normalized_answer
            for term in case[
                "expected_terms"
            ]
        )

        if content_ok:
            content_correct += 1

        # ----------------------------------------------
        # Citations
        # ----------------------------------------------

        cited_sources = [
            int(number)
            for number in re.findall(
                r"\[Source\s+(\d+)\]",
                answer,
                flags=re.IGNORECASE,
            )
        ]

        citation_ok = bool(
            cited_sources
        )

        if citation_ok:
            citation_correct += 1

        # Ensure cited source numbers
        # actually exist in the context.
        number_of_sources = len(
            result["results"]
        )

        citation_reference_ok = (
            citation_ok
            and all(
                1 <= source_number
                <= number_of_sources
                for source_number
                in cited_sources
            )
        )

        if citation_reference_ok:
            citation_reference_correct += 1

        # ----------------------------------------------
        # Display
        # ----------------------------------------------

        print()
        print("=" * 70)

        print(
            f"Generation test {index}"
        )

        print(
            f"Question: {query}"
        )

        print(
            f"Status: {result['status']}"
        )

        print(
            f"Status correct: "
            f"{status_ok}"
        )

        print(
            f"Expected source found: "
            f"{source_ok}"
        )

        print(
            f"Expected content found: "
            f"{content_ok}"
        )

        print(
            f"Citation found: "
            f"{citation_ok}"
        )

        print(
            f"Citation references valid: "
            f"{citation_reference_ok}"
        )

        print()
        print("ANSWER")
        print("-" * 70)

        print(
            answer
        )

        print()
        print("SOURCES")
        print("-" * 70)

        print(
            f"Faithful: "
            f"{faithfulness_ok}"
        )

        for rank, source in enumerate(
            result["results"],
            start=1,
        ):

            print(
                f"{rank}. "
                f"{source['document_id']} "
                f"v{source['version']} "
                f"| reranker="
                f"{source['reranker_score']:.4f}"
            )

    # ----------------------------------------------
    # Summary
    # ----------------------------------------------

    print()
    print("=" * 70)
    print("GENERATION SUMMARY")

    print(
        f"Success status: "
        f"{status_correct}/{total}"
    )

    print(
        f"Expected source: "
        f"{source_correct}/{total}"
    )

    print(
        f"Expected content: "
        f"{content_correct}/{total}"
    )

    print(
        f"Citations present: "
        f"{citation_correct}/{total}"
    )

    print(
        f"Citation references valid: "
        f"{citation_reference_correct}/{total}"
    )

    print(
        f"Faithfulness: "
        f"{faithfulness_correct}/{total}"
    )

if __name__ == "__main__":
    evaluate_generation()