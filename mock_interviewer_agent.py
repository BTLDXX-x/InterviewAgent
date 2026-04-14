# 模拟面试官Agent（不依赖OpenAI API）
from config import INTERVIEW_TOPICS, SCORE_CRITERIA
import random

class MockInterviewerAgent:
    def __init__(self):
        # 模拟问题库
        self.question_bank = {
            'AI Agent基础概念': [
                '请解释什么是AI Agent，以及它的核心组成部分。',
                'AI Agent与传统AI系统的主要区别是什么？',
                '请描述AI Agent的典型工作流程。'
            ],
            '大模型原理与应用': [
                '请解释Transformer架构的基本原理，以及它在大模型中的应用。',
                '什么是提示工程（Prompt Engineering）？它在大模型应用中的重要性是什么？',
                '请描述大模型的训练过程，以及面临的主要挑战。'
            ],
            'AI Agent开发实践': [
                '如何设计一个基于大模型的AI Agent系统？',
                '在开发AI Agent时，如何处理上下文管理和记忆机制？',
                '请分享一个你开发AI Agent的项目经验，以及遇到的挑战和解决方案。'
            ],
            '大模型部署与优化': [
                '大模型部署的主要挑战有哪些？如何应对这些挑战？',
                '请解释模型量化（Model Quantization）的原理和应用场景。',
                '如何优化大模型的推理性能？'
            ],
            'AI伦理与安全': [
                '大模型应用中面临哪些伦理问题？如何应对这些问题？',
                '如何防止AI Agent产生有害输出？',
                '请解释AI安全的主要威胁，以及相应的防护措施。'
            ]
        }
        
        # 初始化面试状态
        self.current_topic = None
        self.questions_asked = []
        self.answers_received = []
        self.scores = []
    
    def generate_question(self, topic):
        """根据指定主题生成面试问题"""
        self.current_topic = topic
        
        # 从问题库中随机选择一个问题
        questions = self.question_bank.get(topic, ['请介绍一下你自己。'])
        question = random.choice(questions)
        self.questions_asked.append(question)
        return question
    
    def process_answer(self, answer):
        """处理用户的回答"""
        self.answers_received.append(answer)
        return answer
    
    def score_answer(self, question, answer, topic):
        """对用户的回答进行打分"""
        # 模拟评分
        scores = {
            "准确性": random.randint(6, 10),
            "深度": random.randint(6, 10),
            "清晰度": random.randint(6, 10),
            "完整性": random.randint(6, 10)
        }
        
        # 计算总分
        total_score = sum(scores.values()) / len(scores)
        
        # 生成评价
        feedback = "你的回答很全面，展示了良好的专业知识和表达能力。"
        
        score_data = {
            "scores": scores,
            "total_score": total_score,
            "feedback": feedback
        }
        
        self.scores.append(score_data)
        return score_data
    
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
            print(f"总分: {score_data['total_score']:.2f}")
            print(f"评价: {score_data['feedback']}")
        
        # 计算总体评分
        total_scores = [result['score']['total_score'] for result in interview_results]
        overall_score = sum(total_scores) / len(total_scores) if total_scores else 0
        
        print(f"\n=== 面试总结 ===")
        print(f"总体评分: {overall_score:.2f}")
        
        return interview_results
