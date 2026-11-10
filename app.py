import streamlit as st

from config import DATA_DIR
from src.auth.user_repository import authenticate_user
from src.embeddings.embedding_model import load_embedding_model
from src.indexing.index_state import load_index_state
from src.retrieval.hybrid_search import answer_query
from src.retrieval.reranker import load_reranker


st.set_page_config(page_title="Nattu Assistant", page_icon="💬", layout="centered")


@st.cache_resource
def load_models():
    """Load embedding and reranking models once."""
    embedding_model = load_embedding_model()
    reranker = load_reranker()
    return embedding_model, reranker


@st.cache_resource
def load_state():
    """Load the document index state."""
    index_state_path = DATA_DIR / "processed" / "index_state.json"
    return load_index_state(index_state_path)


def login_page():
    """Display the authentication page."""
    st.title("Nattu Assistant")
    st.caption("Assistant documentaire interne de Nattu Industries")

    with st.form("login_form"):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Se connecter", use_container_width=True)

    if submitted:
        user = authenticate_user(username, password)

        if user is None:
            st.error("Nom d'utilisateur ou mot de passe incorrect.")
            return

        st.session_state.user = user
        st.session_state.messages = []
        st.rerun()


def logout():
    """Clear the authenticated session."""
    st.session_state.pop("user", None)
    st.session_state.pop("messages", None)
    st.rerun()


def chat_page():
    """Display the authenticated chat interface."""
    user = st.session_state.user

    with st.sidebar:
        st.image("assets/logo.png", width=300)
        st.title("Nattu")
        st.success(f"Connecté : {user.username}")
        st.write(f"Département : **{user.department}**")
        st.write(f"Rôle : **{user.role}**")

        if st.button("Se déconnecter", use_container_width=True):
            logout()

    st.title("Nattu Assistant")
    st.caption("Posez une question sur la documentation interne de Nattu.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("results"):
                with st.expander("Sources"):
                    for result in message["results"]:
                        st.write(
                            f"**{result['document_id']}** "
                            f"- version {result['version']}"
                        )

    query = st.chat_input("Posez votre question...")

    if not query:
        return

    st.session_state.messages.append({
        "role": "user",
        "content": query,
    })

    with st.chat_message("user"):
        st.markdown(query)

    embedding_model, reranker = load_models()
    index_state = load_state()

    with st.chat_message("assistant"):
        with st.spinner("Recherche en cours..."):
            result = answer_query(
                query=query,
                embedding_model=embedding_model,
                reranker=reranker,
                index_state=index_state,
                user=user,
            )

        st.markdown(result["answer"])

        if result["results"]:
            with st.expander("Sources"):
                for document in result["results"]:
                    st.write(
                        f"**{document['document_id']}** "
                        f"- version {document['version']}"
                    )

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "results": result["results"],
    })


if "user" not in st.session_state:
    login_page()
else:
    chat_page()