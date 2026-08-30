import streamlit as st

from config import DATA_DIR, ASSETS_DIR
from src.embeddings.embedding_model import load_embedding_model
from src.indexing.index_state import load_index_state
from src.retrieval.hybrid_search import answer_query
from src.retrieval.reranker import load_reranker

LOGO = ASSETS_DIR / "logo.png"

st.set_page_config(
    page_title="Nova Assistant",
    page_icon="💬",
    layout="wide",
)


@st.cache_resource
def load_models():
    """
    Load retrieval models once.
    """

    embedding_model = load_embedding_model()
    reranker = load_reranker()

    return embedding_model, reranker


@st.cache_resource
def load_state():
    """
    Load the document index state.
    """

    index_state_path = (
        DATA_DIR
        / "processed"
        / "index_state.json"
    )

    return load_index_state(index_state_path)


def display_sources(results: list[dict]):
    """
    Display the sources used for an answer.
    """

    if not results:
        return

    with st.expander(
        "Sources utilisées"
    ):

        for index, result in enumerate(
            results,
            start=1,
        ):

            st.markdown(
                f"""
**Source {index} — {result["document_id"]}**

Version : `{result["version"]}`  
Source : `{result["source"]}`
"""
            )

            if (
                result.get("start_page")
                is not None
            ):

                st.caption(
                    f"Page "
                    f"{result['start_page']}"
                )

            st.divider()


def main():
    """
    Run the NovaTech RAG interface.
    """

    embedding_model, reranker = (
        load_models()
    )

    index_state = load_state()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Two-column layout.
    logo_column, chat_column = st.columns(
        [1, 2],
        gap="large",
    )

    # --------------------------------------------------
    # Left side: branding
    # --------------------------------------------------

    with logo_column:

        st.write("")
        st.write("")
        st.write("")

        st.image(
            str(LOGO),
            use_container_width=True,
        )

        st.markdown(
            """
            <div style="
                text-align: center;
                margin-top: 20px;
            ">
                <h3>NovaTech Industries</h3>
                <p style="
                    color: gray;
                    font-size: 14px;
                ">
                    Intelligent knowledge assistant
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------
    # Right side: assistant
    # --------------------------------------------------

    with chat_column:

        st.title(
            "Nova Assistant"
        )

        st.caption(
            "Assistant documentaire interne"
        )

        st.divider()

        # Display conversation history.
        for message in (
            st.session_state.messages
        ):

            with st.chat_message(
                message["role"]
            ):

                st.markdown(
                    message["content"]
                )

                if (
                    message["role"]
                    == "assistant"
                ):

                    display_sources(
                        message.get(
                            "results",
                            [],
                        )
                    )

        query = st.chat_input(
            "Posez votre question à Nova..."
        )

        if not query:
            return

        # User message.
        st.session_state.messages.append(
            {
                "role": "user",
                "content": query,
            }
        )

        with st.chat_message(
            "user"
        ):

            st.markdown(
                query
            )

        # Assistant response.
        with st.chat_message(
            "assistant"
        ):

            with st.spinner(
                "Nova réfléchit..."
            ):

                try:

                    result = answer_query(
                        query=query,
                        embedding_model=embedding_model,
                        reranker=reranker,
                        index_state=index_state,
                    )

                    answer = result[
                        "answer"
                    ]

                    st.markdown(
                        answer
                    )

                    display_sources(
                        result.get(
                            "results",
                            [],
                        )
                    )

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "status": result.get(
                                "status"
                            ),
                            "results": result.get(
                                "results",
                                [],
                            ),
                        }
                    )

                except Exception as error:

                    st.error(
                        "Une erreur est survenue "
                        "pendant le traitement."
                    )

                    st.exception(
                        error
                    )


if __name__ == "__main__":
    main()