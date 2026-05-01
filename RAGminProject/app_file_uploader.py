import streamlit as st
from knowledge_base import KnowledgeBaseService

#上传文件到数据库

st.title("文件上传服务")
uploader_file = st.file_uploader(
    label="请上传TXT文件",
    type=['txt'],
    accept_multiple_files=False #仅接收一个文件
)
if uploader_file is not None:
    #提取文件信息
    file_name = uploader_file.name
    file_type = uploader_file.type
    file_size = uploader_file.size/1024 #kb

    if "service" not in st.session_state:
        st.session_state["service"] = KnowledgeBaseService()

    st.subheader(f"文件名:{file_name}")
    st.write(f"文件类型:{file_type} | 文件大小{file_size:.2f}kb")
    text = uploader_file.getvalue().decode("utf-8")
    st.write(text)
    st.write(st.session_state["service"].uploader_by_str(text,file_name))