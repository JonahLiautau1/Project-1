
import os
import time
import streamlit as st
from dotenv import load_dotenv
from anthropic import Anthropic
from credibility.scorer import score_url

# ---------------------------------------------------------------------------
# Streamlit app entrypoint for Deliverable 3.
# Two tabs:
#   1) URL Credibility Scorer (uses D1 heuristics in scorer.py)
#   2) Optional Anthropic chatbot (requires ANTHROPIC_API_KEY in .env)
# The layout is intentionally simple and readable for grading.
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Deliverable 3 — Credibility App", layout="centered")
st.title("Deliverable 3 — Credibility App")

tab1, tab2 = st.tabs(["🔗 URL Scorer", "🤖 Chatbot (Anthropic)"])

# ---------------------------
# Tab 1 — URL Credibility
# ---------------------------
with tab1:
    st.subheader("URL Credibility Scorer")
    url = st.text_input("Enter a URL (e.g., https://www.nih.gov):", "")
    if st.button("Analyze URL"):
        t0 = time.time()
        try:
            result = score_url(url)
            elapsed = (time.time() - t0) * 1000
            label = "high" if result["score"] >= 0.8 else ("medium" if result["score"] >= 0.5 else "low")
            st.metric(label=f"Credibility ({label})", value=result["score"])
            st.caption(result["explanation"])
            st.write(f"Latency: {elapsed:.1f} ms")
        except Exception as e:
            st.error(f"Error: {e}")

# ---------------------------
# Tab 2 — Anthropic Chatbot
# ---------------------------
with tab2:
    st.subheader("Chat with Claude (optional)")

    # Load .env only when this tab is used; show helpful message if missing.
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        st.info("Add ANTHROPIC_API_KEY to .env to enable the chatbot tab.")
    else:
        client = Anthropic(api_key=api_key)

        # Maintain conversation state between interactions.
        if "history" not in st.session_state:
            st.session_state.history = []

        # Render prior messages.
        for msg in st.session_state.history:
            st.chat_message(msg["role"]).write(msg["content"])

        # New user input.
        prompt = st.chat_input("Ask a question")
        if prompt:
            st.chat_message("user").write(prompt)
            st.session_state.history.append({"role": "user", "content": prompt})

            # Simple timing for the "anthropic clock" concept (latency tracking)
            t0 = time.time()
            with st.spinner("Thinking..."):
                try:
                    resp = client.messages.create(
                        model="claude-3-5-sonnet-20240620",
                        max_tokens=300,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    reply = resp.content[0].text
                except Exception as e:
                    reply = f"(Error contacting Anthropic API: {e})"
            elapsed = (time.time() - t0)
            st.chat_message("assistant").write(reply + f"\n\n_(Latency: {elapsed:.2f}s)_")
            st.session_state.history.append({"role": "assistant", "content": reply})
