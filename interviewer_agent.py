# 面试官Agent核心类
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_API_BASE, INTERVIEW_TOPICS, SCORE_CRITERIA
from rag_system import RAGSystem  # 导入RAG系统
import json
import os

class InterviewerAgent:
    def __init__(self, resume_path=None):
        # 初始化OpenAI模型
        self.model = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model=OPENAI_MODEL,
            base_url=OPENAI_API_BASE
        )
        
        # 初始化RAG系统并加载题库
        self.rag_system = RAGSystem()
        self.rag_system.load_question_bank("g:\\MyProject\\InterviewAgent\\题库")
        
        # 初始化面试状态
        self.current_topic = None
        self.questions_asked = []
        self.answers_received = []
        self.scores = []
        
        # 处理简历
        self.resume_content = ""
        if resume_path:
            self.resume_content = self._load_resume(resume_path)
    
    def _load_resume(self, resume_path):
        """加载简历内容"""
        try:
            if resume_path.endswith('.txt'):
                with open(resume_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif resume_path.endswith('.pdf'):
                # 尝试使用PyPDF2读取PDF
                try:
                    from PyPDF2 import PdfReader
                    reader = PdfReader(resume_path)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return text
                except ImportError:
                    return "[PDF格式，需要安装PyPDF2才能读取]"
            elif resume_path.endswith('.docx'):
                # 尝试使用python-docx读取Word文档
                try:
                    from docx import Document
                    doc = Document(resume_path)
                    text = ""
                    for para in doc.paragraphs:
                        text += para.text + "\n"
                    return text
                except ImportError:
                    return "[Word格式，需要安装python-docx才能读取]"
            else:
                return "[不支持的文件格式]"
        except Exception as e:
            return f"[简历读取失败: {str(e)}]"
    
    def generate_question(self, topic):
        """根据指定主题生成面试问题"""
        self.current_topic = topic
        
        # 使用RAG系统获取相关内容
        relevant_content = self.rag_system.get_relevant_answers(topic)
        context = "\n".join(relevant_content[:2])  # 取前两个相关结果作为上下文
        
        # 构建提示模板
        if self.resume_content:
            prompt = ChatPromptTemplate.from_template(
                "你是一名专业的技术面试官，现在需要为{topic}主题生成一个深度适中的面试问题。\n"
                "候选人简历：\n{resume}\n"
                "参考以下相关内容：\n{context}\n"
                "请根据候选人的简历背景，生成与{topic}相关的问题，问题应该：\n"
                "1. 考察候选人的专业知识和解决问题的能力\n"
                "2. 与候选人的工作经验或项目经历相关\n"
                "3. 具有一定的深度和挑战性\n"
                "请直接输出问题内容，不要有任何引言或开场白。"
            )
            response = self.model.invoke(prompt.format(topic=topic, context=context, resume=self.resume_content))
        else:
            prompt = ChatPromptTemplate.from_template(
                "你是一名专业的技术面试官，现在需要为{topic}主题生成一个深度适中的面试问题。\n"
                "参考以下相关内容：\n{context}\n"
                "问题应该能够考察候选人的专业知识和解决问题的能力。\n"
                "请直接输出问题内容，不要有任何引言或开场白。"
            )
            response = self.model.invoke(prompt.format(topic=topic, context=context))
        
        question = response.content.strip()
        self.questions_asked.append(question)
        return question
    
    def process_answer(self, answer):
        """处理用户的回答"""
        self.answers_received.append(answer)
        return answer
    
    def score_answer(self, question, answer, topic):
        """对用户的回答进行打分"""
        # 使用RAG系统获取相关内容作为参考
        relevant_content = self.rag_system.get_relevant_answers(question)
        context = "\n".join(relevant_content[:2])  # 取前两个相关结果作为上下文
        
        # 构建提示模板
        if self.resume_content:
            prompt = ChatPromptTemplate.from_template(
                "你是一名专业的技术面试官，需要对候选人的回答进行评分并提供正确答案。\n"
                "面试主题：{topic}\n"
                "问题：{question}\n"
                "回答：{answer}\n"
                "候选人简历：\n{resume}\n"
                "参考内容：\n{context}\n"
                "请根据以下评分标准对回答进行评估：\n"
                "1. 准确性：回答内容的正确性和专业度\n"
                "2. 深度：回答的深度和广度，是否有独到见解\n"
                "3. 清晰度：回答的逻辑结构和表达清晰度\n"
                "4. 完整性：回答是否全面覆盖问题要点\n"
                "5. 与背景相关性：回答是否与候选人的工作经验或项目经历相关\n"
                "请为每个维度打分（0-10分），提供简要的评价理由，并给出该问题的正确答案。\n"
                "最后计算总分（各维度加权平均）。\n"
                "请按照JSON格式输出，包含以下字段：\n"
                "- scores: 包含准确性、深度、清晰度、完整性、与背景相关性五个维度的分数\n"
                "- total_score: 总分\n"
                "- feedback: 评价理由\n"
                "- correct_answer: 正确答案\n"
                "请确保输出是有效的JSON格式，不要包含任何其他文本。"
            )
            response = self.model.invoke(prompt.format(
                topic=topic,
                question=question,
                answer=answer,
                resume=self.resume_content,
                context=context
            ))
        else:
            prompt = ChatPromptTemplate.from_template(
                "你是一名专业的技术面试官，需要对候选人的回答进行评分并提供正确答案。\n"
                "面试主题：{topic}\n"
                "问题：{question}\n"
                "回答：{answer}\n"
                "参考内容：\n{context}\n"
                "请根据以下评分标准对回答进行评估：\n"
                "1. 准确性：回答内容的正确性和专业度\n"
                "2. 深度：回答的深度和广度，是否有独到见解\n"
                "3. 清晰度：回答的逻辑结构和表达清晰度\n"
                "4. 完整性：回答是否全面覆盖问题要点\n"
                "请为每个维度打分（0-10分），提供简要的评价理由，并给出该问题的正确答案。\n"
                "最后计算总分（各维度加权平均）。\n"
                "请按照JSON格式输出，包含以下字段：\n"
                "- scores: 包含准确性、深度、清晰度、完整性四个维度的分数\n"
                "- total_score: 总分\n"
                "- feedback: 评价理由\n"
                "- correct_answer: 正确答案\n"
                "请确保输出是有效的JSON格式，不要包含任何其他文本。"
            )
            response = self.model.invoke(prompt.format(
                topic=topic,
                question=question,
                answer=answer,
                context=context
            ))
        
        # 解析JSON响应
        try:
            # 提取响应中的JSON部分
            content = response.content.strip()
            # 尝试找到JSON的开始和结束位置
            if '{' in content:
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = content[start_idx:end_idx]
                    score_data = json.loads(json_str)
                    # 确保所有必要的字段都存在
                    if 'scores' not in score_data:
                        score_data['scores'] = {"准确性": 5, "深度": 5, "清晰度": 5, "完整性": 5}
                    if 'total_score' not in score_data:
                        score_data['total_score'] = 5
                    if 'feedback' not in score_data:
                        score_data['feedback'] = "评价理由"
                    if 'correct_answer' not in score_data:
                        score_data['correct_answer'] = "正确答案"
                    self.scores.append(score_data)
                    return score_data
            # 如果提取失败，使用默认值
            raise json.JSONDecodeError("Invalid JSON", content, 0)
        except json.JSONDecodeError:
            # 如果解析失败，返回默认分数
            if self.resume_content:
                default_score = {
                    "scores": {
                        "准确性": 5,
                        "深度": 5,
                        "清晰度": 5,
                        "完整性": 5,
                        "与背景相关性": 5
                    },
                    "total_score": 5,
                    "feedback": "评分解析失败，使用默认分数",
                    "correct_answer": "正确答案"
                }
            else:
                default_score = {
                    "scores": {
                        "准确性": 5,
                        "深度": 5,
                        "清晰度": 5,
                        "完整性": 5
                    },
                    "total_score": 5,
                    "feedback": "评分解析失败，使用默认分数",
                    "correct_answer": "正确答案"
                }
            self.scores.append(default_score)
            return default_score
    
    def run_interview(self, topics=None):
        """运行完整的面试流程"""
        if topics is None:
            topics = INTERVIEW_TOPICS
        
        interview_results = []
        
        for topic in topics:
            # 生成问题
            question = self.generate_question(topic)
            print(f"\n=== {topic} ===")
            print(f"问题: {question}")
            
            # 获取用户回答
            answer = input("请输入你的回答: ")
            self.process_answer(answer)
            
            # 评分
            score_data = self.score_answer(question, answer, topic)
            interview_results.append({
                "topic": topic,
                "question": question,
                "answer": answer,
                "score": score_data
            })
            
            # 显示评分结果
            print(f"\n评分结果:")
            print(f"准确性: {score_data['scores']['准确性']}")
            print(f"深度: {score_data['scores']['深度']}")
            print(f"清晰度: {score_data['scores']['清晰度']}")
            print(f"完整性: {score_data['scores']['完整性']}")
            print(f"总分: {score_data['total_score']}")
            print(f"评价: {score_data['feedback']}")
            print(f"正确答案: {score_data['correct_answer']}")
        
        # 计算总体评分
        total_scores = [result['score']['total_score'] for result in interview_results]
        overall_score = sum(total_scores) / len(total_scores) if total_scores else 0
        
        print(f"\n=== 面试总结 ===")
        print(f"总体评分: {overall_score:.2f}")
        
        return interview_results