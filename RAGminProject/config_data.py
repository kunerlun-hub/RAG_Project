md5_path = './md5.txt'

#Chroma
collection_name = 'rag'
persist_directory = './chroma_db'

#splitter
chunk_size = 1000
chunk_overlap = 100
separators = ['.', '?', '!', '。', '？', '！', '\n']
max_split_chat_number = 1000

similarity_threshold = 1

text_model = "text-embedding-v4"
chat_model = "qwen3-max"

session_config = {
        "configurable":{
            "session_id":"user_001"
        }
    }