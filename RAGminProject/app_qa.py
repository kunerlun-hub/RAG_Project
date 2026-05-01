import streamlit as st
from rag import Rag
import config_data as config

st.title("智能答题")
st.divider()

if "message" not in st.session_state:
    st.session_state["message"] = [{"role":"assistant","content":"你好,有什么可以帮助你的?"}]

if "rag" not in st.session_state:
    st.session_state["rag"] = Rag()

for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input()

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role":"user","content":prompt})

    ai_rs_list = []
    with st.spinner("AI思考中..."):
        res_stream = st.session_state["rag"].chain.stream({"input":prompt},config.session_config)

        def capture(generator,cache_list):
            for chunk in generator:
                cache_list.append(chunk)
                yield chunk

        st.chat_message("assistant").write_stream(capture(res_stream,ai_rs_list))
        st.session_state["message"].append({"role":"assistant","content":"".join(ai_rs_list)})

