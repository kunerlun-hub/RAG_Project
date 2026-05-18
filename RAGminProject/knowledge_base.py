import hashlib
import os
from datetime import datetime

from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config_data as config
#将上传的数据存入向量库,利用md5去重,优化性能

def check_md5(md5_str: str):
    if not os.path.exists(config.md5_path):
        open(config.md5_path, 'w', encoding='utf-8').close()
        return False
    else:
        with open(config.md5_path, 'r', encoding='utf-8') as f:
            md5s = f.readlines()
            for md5 in md5s:
                if md5.strip() == md5_str:
                    return True
        return False
def save_md5(md5_str: str):
    with open (config.md5_path, 'a', encoding='utf-8') as f:
        f.write(md5_str + '\n')

def get_string_md5(input_str: str, encoding: str = 'utf-8'):
    str_bytes = input_str.encode(encoding=encoding)

    md5_obj = hashlib.md5()
    md5_obj.update(str_bytes)
    md5_hex = md5_obj.hexdigest()
    return md5_hex

class KnowledgeBaseService(object):
    def __init__(self):
        self.chroma = Chroma(
            collection_name=config.collection_name,
            embedding_function=DashScopeEmbeddings(model=config.text_model),
            persist_directory=config.persist_directory,
        )
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size, # 每个分块的大小
            chunk_overlap=config.chunk_overlap, # 分块之间的重叠部分
            separators=config.separators, # 分块之间的分隔符，默认为空格
            length_function=len, # 分块长度计算函数，默认为len函数
        )
    def uploader_by_str(self,data,filename):
        md5_hex = get_string_md5(data)
        if check_md5(md5_hex):
            return "数据已存在，不再次上传"
        if len(data)>config.max_split_chat_number:
            knowledge_chunks: list[str] = self.spliter.split_text(data)
        else:
            knowledge_chunks = [data]
        metadata = {
            "source": filename,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator":"小曹",
        }
        self.chroma.add_texts(
            knowledge_chunks,
            metadatas=[metadata for _ in knowledge_chunks],
        )
        save_md5(md5_hex)
        return "数据成功载入向量库"
if __name__ == '__main__':
    kbs = KnowledgeBaseService()
    t = kbs.uploader_by_str("""
    小曹，你叫什么名字？
    小曹，我叫小曹。
    """, "test.txt")
    print(t)