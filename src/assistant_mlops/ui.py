import os

import httpx
import streamlit as st

st.set_page_config(page_title="MLOps Knowledge Assistant", page_icon="📚")
st.title("MLOps Knowledge Assistant")
st.caption("Ask about the example company handbook. Answers include retrieved source quotations.")
question = st.text_area(
    "Your question", placeholder="What happens after drift, and when can we promote?"
)
if st.button("Verify answer", disabled=len(question.strip()) < 3):
    with st.spinner("Checking sources…"):
        try:
            response = httpx.post(
                os.getenv("BACKEND_URL", "http://localhost:8000") + "/ask",
                json={"question": question},
                timeout=190,
            )
            response.raise_for_status()
            result = response.json()
            st.write(result["answer"])
            st.caption(
                f"Status: {result['status']} · steps: {result['iterations']} · "
                f"tokens: {result['tokens']} · cached: {result['cache_hit']}"
            )
            for source in result["sources"]:
                with st.expander(source["source_id"]):
                    st.write(source["quote"])
        except (httpx.HTTPError, ValueError):
            st.error("The service could not complete this request. Please try again shortly.")
