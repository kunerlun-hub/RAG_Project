from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings

import config_data as config

#到向量库检索到匹配度最高的并返回结果
class VectorStoreService(object):
    def __init__(self,embedding1):
        self.embedding = embedding1
        self.vector_store = Chroma(
            collection_name=config.collection_name,
            embedding_function=self.embedding,
            persist_directory=config.persist_directory
             )
    def get_retriver(self):
        return self.vector_store.as_retriever(search_kwargs={"k": config.similarity_threshold})

# if __name__ == '__main__':
#     vector_store = VectorStoreService(DashScopeEmbeddings(model = "text-embedding-v4"))
#     retriver = vector_store.get_retriver()
#     res = retriver.invoke("我的体重180斤,尺码推荐")
#     print(res)