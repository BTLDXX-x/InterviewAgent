# RAG系统，用于加载和检索题库
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from config import OPENAI_API_KEY, OPENAI_API_BASE
import os

class RAGSystem:
    def __init__(self):
        # 初始化向量数据库
        self.embeddings = OpenAIEmbeddings(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_API_BASE,
            model="text-embedding-3-small"
        )
        self.vector_db = None
    
    def load_question_bank(self, file_path):
        """加载题库文件并创建向量数据库"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"题库文件不存在: {file_path}")
        
        # 加载文本
        loader = TextLoader(file_path, encoding='utf-8')
        documents = loader.load()
        
        # 分割文本
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)
        
        # 创建向量数据库
        self.vector_db = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings
        )
        
        return len(splits)
    
    def retrieve(self, query, k=3):
        """根据查询检索相关文档"""
        if not self.vector_db:
            raise ValueError("请先加载题库文件")
        
        # 相似度搜索
        results = self.vector_db.similarity_search(
            query=query,
            k=k
        )
        
        return results
    
    def get_relevant_answers(self, question, k=3):
        """获取与问题相关的答案"""
        results = self.retrieve(question, k)
        
        # 提取相关内容
        relevant_content = []
        for doc in results:
            content = doc.page_content
            # 提取问题和答案
            if "**" in content:
                relevant_content.append(content)
        
        return relevant_content

# 测试RAG系统
if __name__ == "__main__":
    rag = RAGSystem()
    
    # 加载题库
    file_path = "g:\\MyProject\\InterviewAgent\\题库"
    try:
        count = rag.load_question_bank(file_path)
        print(f"成功加载题库，分割为 {count} 个文档块")
        
        # 测试检索
        test_query = "Agent和Workflow的区别"
        results = rag.get_relevant_answers(test_query)
        print(f"\n关于'{test_query}'的相关内容:")
        for i, result in enumerate(results):
            print(f"\n结果 {i+1}:\n{result}")
            
    except Exception as e:
        print(f"错误: {e}")