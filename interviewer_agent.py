# 面试官Agent核心类
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_API_BASE, INTERVIEW_TOPICS, SCORE_CRITERIA
from rag_system import RAGSystem  # 导入RAG系统
import json
import os

class InterviewerAgent:
    def __init__(self, resume_path=None):
        # 初始化模拟模式标志
        self.use_mock = False
        
        try:
            # 尝试初始化OpenAI模型
            self.model = ChatOpenAI(
                api_key=OPENAI_API_KEY,
                model=OPENAI_MODEL,
                base_url=OPENAI_API_BASE
            )
            
            # 尝试初始化RAG系统并加载题库
            self.rag_system = RAGSystem()
            self.rag_system.load_question_bank("g:\\MyProject\\InterviewAgent\\题库")
        except Exception as e:
            # 如果API连接失败，使用模拟模式
            self.use_mock = True
            print(f"API连接失败，使用模拟模式: {e}")
        
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
        
        # 模拟模式：返回预设问题
        if self.use_mock:
            mock_questions = {
                "AI应用产品经理": [
                    "请描述你如何将AI技术嵌入到团队的日常工作流程中，提高工作效率？",
                    "你如何将零散的AI使用方式产品化、系统化，沉淀为可复制的内部能力？",
                    "请分享一个你成功影响团队更高质量使用AI的案例。",
                    "你如何进行AI应用的产品规划和设计，确保其能够落地实施？",
                    "在开发AI应用时，你如何平衡技术可行性和业务需求？"
                ],
                "AI Agent基础概念": [
                    "请解释什么是AI Agent，它与传统AI系统有什么区别？",
                    "AI Agent的核心组件有哪些？它们如何协同工作？",
                    "请描述AI Agent的决策过程和工作原理。",
                    "AI Agent在实际应用中面临哪些挑战？如何解决这些挑战？",
                    "请举例说明AI Agent的典型应用场景。"
                ],
                "大模型原理与应用": [
                    "请解释大语言模型的基本原理和训练过程。",
                    "大语言模型与传统机器学习模型有什么区别？",
                    "请描述大语言模型的优缺点。",
                    "大语言模型在实际应用中面临哪些挑战？如何解决这些挑战？",
                    "请举例说明大语言模型的典型应用场景。"
                ],
                "AI Agent开发实践": [
                    "请描述AI Agent开发的基本流程和步骤。",
                    "在开发AI Agent时，如何设计其决策机制和行为模式？",
                    "如何评估AI Agent的性能和效果？",
                    "AI Agent开发中常见的错误和陷阱有哪些？如何避免？",
                    "请分享一个你开发AI Agent的实际案例。"
                ],
                "大模型部署与优化": [
                    "请描述大模型部署的基本流程和步骤。",
                    "大模型部署面临哪些挑战？如何解决这些挑战？",
                    "如何优化大模型的推理性能和响应速度？",
                    "大模型部署的最佳实践有哪些？",
                    "请分享一个大模型部署的实际案例。"
                ],
                "AI伦理与安全": [
                    "AI伦理的核心原则有哪些？",
                    "如何确保AI系统的公平性和透明度？",
                    "AI系统可能带来哪些安全风险？如何防范这些风险？",
                    "如何制定AI伦理准则和规范？",
                    "请举例说明AI伦理问题的实际案例。"
                ]
            }
            
            # 选择对应主题的问题
            if topic in mock_questions:
                questions = mock_questions[topic]
                # 根据已问问题数量选择下一个问题
                index = len(self.questions_asked) % len(questions)
                question = questions[index]
            else:
                question = "请描述你对这个主题的理解和经验。"
            
            self.questions_asked.append(question)
            return question
        
        # 正常模式：使用RAG系统和LLM生成问题
        try:
            # 使用RAG系统获取相关内容
            relevant_content = self.rag_system.get_relevant_answers(topic)
            context = "\n".join(relevant_content[:2])  # 取前两个相关结果作为上下文
            
            # 构建提示模板
            if topic == "AI应用产品经理":
                # 针对AI应用产品经理的特定提示
                if self.resume_content:
                    prompt = ChatPromptTemplate.from_template(
                        "你是一名专业的产品面试官，现在需要为{topic}主题生成一个深度适中的面试问题。\n"
                        "候选人简历：\n{resume}\n"
                        "参考以下相关内容：\n{context}\n"
                        "AI应用产品经理的职责包括：\n"
                        "1、负责AI应用的产品规划、设计与落地(效率工具、智能助手、自动化流程等)\n"
                        "2、深入理解团队(产品/运营/研发/数据等)的真实工作场景，把AI嵌入到日常工作流中\n"
                        "3、将零散的AI使用方式，产品化、系统化，沉淀为可复制的内部能力，提升个人和组织的产出\n"
                        "4、影响和带动团队更高质量地使用AI\n"
                        "请根据候选人的简历背景，生成与{topic}相关的问题，问题应该：\n"
                        "1. 考察候选人的产品规划和设计能力\n"
                        "2. 考察候选人如何将AI嵌入到工作流程中\n"
                        "3. 考察候选人的产品化思维和系统化能力\n"
                        "4. 考察候选人的团队影响力和领导力\n"
                        "5. 与候选人的工作经验或项目经历相关\n"
                        "请直接输出问题内容，不要有任何引言或开场白。"
                    )
                    response = self.model.invoke(prompt.format(topic=topic, context=context, resume=self.resume_content))
                else:
                    prompt = ChatPromptTemplate.from_template(
                        "你是一名专业的产品面试官，现在需要为{topic}主题生成一个深度适中的面试问题。\n"
                        "参考以下相关内容：\n{context}\n"
                        "AI应用产品经理的职责包括：\n"
                        "1、负责AI应用的产品规划、设计与落地(效率工具、智能助手、自动化流程等)\n"
                        "2、深入理解团队(产品/运营/研发/数据等)的真实工作场景，把AI嵌入到日常工作流中\n"
                        "3、将零散的AI使用方式，产品化、系统化，沉淀为可复制的内部能力，提升个人和组织的产出\n"
                        "4、影响和带动团队更高质量地使用AI\n"
                        "问题应该能够考察候选人的：\n"
                        "1. 产品规划和设计能力\n"
                        "2. 将AI嵌入到工作流程的能力\n"
                        "3. 产品化思维和系统化能力\n"
                        "4. 团队影响力和领导力\n"
                        "请直接输出问题内容，不要有任何引言或开场白。"
                    )
                    response = self.model.invoke(prompt.format(topic=topic, context=context))
            else:
                # 其他技术主题的通用提示
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
        except Exception as e:
            # 如果生成问题失败，使用模拟问题
            print(f"生成问题失败，使用模拟问题: {e}")
            return self.generate_question(topic)
    
    def process_answer(self, answer):
        """处理用户的回答"""
        self.answers_received.append(answer)
        return answer
    
    def score_answer(self, question, answer, topic):
        """对用户的回答进行打分"""
        # 模拟模式：返回预设评分
        if self.use_mock:
            # 检测无效回答
            invalid_answers = ["没有经验", "不知道", "不清楚", "没做过", "不会", "没有", "无", "没经验"]
            answer_lower = answer.lower().strip()
            if any(invalid in answer_lower for invalid in invalid_answers):
                # 无效回答，评分很低
                base_score = 2
                feedback = "回答无效，未能提供任何有价值的信息。"
            else:
                # 根据回答长度调整评分
                answer_length = len(answer)
                if answer_length < 10:
                    # 回答太短，评分较低
                    base_score = 4
                    feedback = "回答过于简略，需要更详细的阐述。"
                elif answer_length < 50:
                    # 回答适中
                    base_score = 6
                    feedback = "回答内容基本合理，但可以更深入。"
                else:
                    # 回答详细
                    base_score = 8
                    feedback = "回答内容全面，思路清晰，体现了对该主题的理解。"
            
            # 为不同主题创建不同的预设评分
            if topic == "AI应用产品经理":
                if self.resume_content:
                    mock_score = {
                        "scores": {
                            "产品规划能力": base_score + 1 if base_score < 9 else 9,
                            "AI应用能力": base_score + 1 if base_score < 9 else 9,
                            "产品化思维": base_score - 1 if base_score > 3 else 2,
                            "团队影响力": base_score,
                            "与背景相关性": base_score - 1 if base_score > 3 else 2
                        },
                        "total_score": round((base_score * 3 + (base_score - 1) * 2) / 5, 1),
                        "feedback": feedback if feedback else "回答内容全面，思路清晰，体现了较强的产品规划能力和AI应用能力。",
                        "correct_answer": "优秀的AI应用产品经理需要具备产品规划能力、AI应用能力、产品化思维和团队影响力，能够将AI技术嵌入到工作流程中，提高团队效率。"
                    }
                else:
                    mock_score = {
                        "scores": {
                            "产品规划能力": base_score + 1 if base_score < 9 else 9,
                            "AI应用能力": base_score + 1 if base_score < 9 else 9,
                            "产品化思维": base_score - 1 if base_score > 3 else 2,
                            "团队影响力": base_score
                        },
                        "total_score": round((base_score * 2 + (base_score + 1) * 2) / 4, 1),
                        "feedback": feedback if feedback else "回答内容全面，思路清晰，体现了较强的产品规划能力和AI应用能力。",
                        "correct_answer": "优秀的AI应用产品经理需要具备产品规划能力、AI应用能力、产品化思维和团队影响力，能够将AI技术嵌入到工作流程中，提高团队效率。"
                    }
            elif topic == "AI Agent基础概念":
                if self.resume_content:
                    mock_score = {
                        "scores": {
                            "准确性": base_score,
                            "深度": base_score - 1 if base_score > 3 else 2,
                            "清晰度": base_score + 1 if base_score < 9 else 9,
                            "完整性": base_score,
                            "与背景相关性": base_score - 1 if base_score > 3 else 2
                        },
                        "total_score": round((base_score * 3 + (base_score - 1) * 2) / 5, 1),
                        "feedback": feedback if feedback else "回答内容准确，思路清晰，体现了对AI Agent基础概念的理解。",
                        "correct_answer": "AI Agent的核心组件包括：1. 感知系统：获取外部信息；2. 决策系统：基于信息做出决策；3. 执行系统：执行决策；4. 学习系统：从经验中学习。这些组件协同工作，使Agent能够自主完成任务。"
                    }
                else:
                    mock_score = {
                        "scores": {
                            "准确性": base_score,
                            "深度": base_score - 1 if base_score > 3 else 2,
                            "清晰度": base_score + 1 if base_score < 9 else 9,
                            "完整性": base_score
                        },
                        "total_score": round((base_score * 3 + (base_score - 1)) / 4, 1),
                        "feedback": feedback if feedback else "回答内容准确，思路清晰，体现了对AI Agent基础概念的理解。",
                        "correct_answer": "AI Agent的核心组件包括：1. 感知系统：获取外部信息；2. 决策系统：基于信息做出决策；3. 执行系统：执行决策；4. 学习系统：从经验中学习。这些组件协同工作，使Agent能够自主完成任务。"
                    }
            elif topic == "大模型原理与应用":
                if self.resume_content:
                    mock_score = {
                        "scores": {
                            "准确性": base_score,
                            "深度": base_score,
                            "清晰度": base_score,
                            "完整性": base_score - 1 if base_score > 3 else 2,
                            "与背景相关性": base_score - 1 if base_score > 3 else 2
                        },
                        "total_score": round((base_score * 3 + (base_score - 1) * 2) / 5, 1),
                        "feedback": feedback if feedback else "回答内容准确，思路清晰，体现了对大模型原理与应用的理解。",
                        "correct_answer": "大语言模型的优点包括：1. 强大的文本理解和生成能力；2. 广泛的知识覆盖；3. 良好的上下文理解能力。缺点包括：1. 计算资源消耗大；2. 可能产生幻觉；3. 存在偏见；4. 缺乏真正的理解能力。"
                    }
                else:
                    mock_score = {
                        "scores": {
                            "准确性": base_score,
                            "深度": base_score,
                            "清晰度": base_score,
                            "完整性": base_score - 1 if base_score > 3 else 2
                        },
                        "total_score": round((base_score * 3 + (base_score - 1)) / 4, 1),
                        "feedback": feedback if feedback else "回答内容准确，思路清晰，体现了对大模型原理与应用的理解。",
                        "correct_answer": "大语言模型的优点包括：1. 强大的文本理解和生成能力；2. 广泛的知识覆盖；3. 良好的上下文理解能力。缺点包括：1. 计算资源消耗大；2. 可能产生幻觉；3. 存在偏见；4. 缺乏真正的理解能力。"
                    }
            elif topic == "AI Agent开发实践":
                if self.resume_content:
                    mock_score = {
                        "scores": {
                            "准确性": base_score + 1 if base_score < 9 else 9,
                            "深度": base_score,
                            "清晰度": base_score,
                            "完整性": base_score - 1 if base_score > 3 else 2,
                            "与背景相关性": base_score
                        },
                        "total_score": round((base_score * 3 + (base_score + 1) + (base_score - 1)) / 5, 1),
                        "feedback": feedback if feedback else "回答内容准确，思路清晰，体现了对AI Agent开发实践的理解。",
                        "correct_answer": "AI Agent开发中常见的错误和陷阱包括：1. 上下文管理不当导致信息丢失；2. 过度依赖大模型导致性能问题；3. 缺乏适当的错误处理机制；4. 没有考虑到Agent的安全性和伦理问题。避免方法：1. 实现有效的上下文管理；2. 合理使用RAG等技术；3. 设计健壮的错误处理流程；4. 建立安全和伦理审查机制。"
                    }
                else:
                    mock_score = {
                        "scores": {
                            "准确性": base_score + 1 if base_score < 9 else 9,
                            "深度": base_score,
                            "清晰度": base_score,
                            "完整性": base_score - 1 if base_score > 3 else 2
                        },
                        "total_score": round((base_score * 3 + (base_score + 1) + (base_score - 1)) / 4, 1),
                        "feedback": feedback if feedback else "回答内容准确，思路清晰，体现了对AI Agent开发实践的理解。",
                        "correct_answer": "AI Agent开发中常见的错误和陷阱包括：1. 上下文管理不当导致信息丢失；2. 过度依赖大模型导致性能问题；3. 缺乏适当的错误处理机制；4. 没有考虑到Agent的安全性和伦理问题。避免方法：1. 实现有效的上下文管理；2. 合理使用RAG等技术；3. 设计健壮的错误处理流程；4. 建立安全和伦理审查机制。"
                    }
            elif topic == "大模型部署与优化":
                if self.resume_content:
                    mock_score = {
                        "scores": {
                            "准确性": base_score,
                            "深度": base_score + 1 if base_score < 9 else 9,
                            "清晰度": base_score - 1 if base_score > 3 else 2,
                            "完整性": base_score,
                            "与背景相关性": base_score
                        },
                        "total_score": round((base_score * 3 + (base_score + 1) + (base_score - 1)) / 5, 1),
                        "feedback": feedback if feedback else "回答内容准确，思路清晰，体现了对大模型部署与优化的理解。",
                        "correct_answer": "大模型部署的实际案例：某公司部署了一个基于GPT的客服系统，通过模型量化和知识蒸馏将模型大小减少了70%，使用Kubernetes进行容器化部署，实现了自动扩缩容，通过CDN缓存热门回答提高响应速度，最终系统响应时间从5秒降至0.5秒，成本降低了60%。"
                    }
                else:
                    mock_score = {
                        "scores": {
                            "准确性": base_score,
                            "深度": base_score + 1 if base_score < 9 else 9,
                            "清晰度": base_score - 1 if base_score > 3 else 2,
                            "完整性": base_score
                        },
                        "total_score": round((base_score * 3 + (base_score + 1) + (base_score - 1)) / 4, 1),
                        "feedback": feedback if feedback else "回答内容准确，思路清晰，体现了对大模型部署与优化的理解。",
                        "correct_answer": "大模型部署的实际案例：某公司部署了一个基于GPT的客服系统，通过模型量化和知识蒸馏将模型大小减少了70%，使用Kubernetes进行容器化部署，实现了自动扩缩容，通过CDN缓存热门回答提高响应速度，最终系统响应时间从5秒降至0.5秒，成本降低了60%。"
                    }
            elif topic == "AI伦理与安全":
                if self.resume_content:
                    mock_score = {
                        "scores": {
                            "准确性": base_score - 1 if base_score > 3 else 2,
                            "深度": base_score,
                            "清晰度": base_score,
                            "完整性": base_score + 1 if base_score < 9 else 9,
                            "与背景相关性": base_score - 1 if base_score > 3 else 2
                        },
                        "total_score": round((base_score * 2 + (base_score - 1) * 2 + (base_score + 1)) / 5, 1),
                        "feedback": feedback if feedback else "回答内容准确，思路清晰，体现了对AI伦理与安全的理解。",
                        "correct_answer": "AI伦理的核心原则包括：1. 公平性：避免算法偏见；2. 透明度：确保AI决策可解释；3. 隐私保护：保护用户数据；4. 安全性：防止AI系统被滥用；5. 问责制：明确AI系统的责任归属；6. 有益性：确保AI系统对人类有益。"
                    }
                else:
                    mock_score = {
                        "scores": {
                            "准确性": base_score - 1 if base_score > 3 else 2,
                            "深度": base_score,
                            "清晰度": base_score,
                            "完整性": base_score + 1 if base_score < 9 else 9
                        },
                        "total_score": round((base_score * 2 + (base_score - 1) + (base_score + 1)) / 4, 1),
                        "feedback": feedback if feedback else "回答内容准确，思路清晰，体现了对AI伦理与安全的理解。",
                        "correct_answer": "AI伦理的核心原则包括：1. 公平性：避免算法偏见；2. 透明度：确保AI决策可解释；3. 隐私保护：保护用户数据；4. 安全性：防止AI系统被滥用；5. 问责制：明确AI系统的责任归属；6. 有益性：确保AI系统对人类有益。"
                    }
            else:
                if self.resume_content:
                    mock_score = {
                        "scores": {
                            "准确性": base_score,
                            "深度": base_score - 1 if base_score > 3 else 2,
                            "清晰度": base_score + 1 if base_score < 9 else 9,
                            "完整性": base_score,
                            "与背景相关性": base_score - 1 if base_score > 3 else 2
                        },
                        "total_score": round((base_score * 3 + (base_score - 1) * 2) / 5, 1),
                        "feedback": feedback if feedback else "回答内容准确，思路清晰，体现了对该主题的理解。",
                        "correct_answer": "这是一个关于该主题的详细回答，涵盖了核心概念、原理和应用场景。"
                    }
                else:
                    mock_score = {
                        "scores": {
                            "准确性": base_score,
                            "深度": base_score - 1 if base_score > 3 else 2,
                            "清晰度": base_score + 1 if base_score < 9 else 9,
                            "完整性": base_score
                        },
                        "total_score": round((base_score * 3 + (base_score - 1)) / 4, 1),
                        "feedback": feedback if feedback else "回答内容准确，思路清晰，体现了对该主题的理解。",
                        "correct_answer": "这是一个关于该主题的详细回答，涵盖了核心概念、原理和应用场景。"
                    }
            self.scores.append(mock_score)
            return mock_score
        
        # 正常模式：使用RAG系统和LLM评分
        try:
            # 使用RAG系统获取相关内容作为参考
            relevant_content = self.rag_system.get_relevant_answers(question)
            context = "\n".join(relevant_content[:2])  # 取前两个相关结果作为上下文
            
            # 构建提示模板
            if topic == "AI应用产品经理":
                # 针对AI应用产品经理的特定评分标准
                if self.resume_content:
                    prompt = ChatPromptTemplate.from_template(
                        "你是一名专业的产品面试官，需要对候选人的回答进行评分并提供正确答案。\n"
                        "面试主题：{topic}\n"
                        "问题：{question}\n"
                        "回答：{answer}\n"
                        "候选人简历：\n{resume}\n"
                        "参考内容：\n{context}\n"
                        "请根据以下评分标准对回答进行评估：\n"
                        "1. 产品规划能力：回答中体现的产品规划和设计能力\n"
                        "2. AI应用能力：将AI嵌入到工作流程的能力和思路\n"
                        "3. 产品化思维：将零散AI使用方式产品化、系统化的能力\n"
                        "4. 团队影响力：影响和带动团队使用AI的能力\n"
                        "5. 与背景相关性：回答是否与候选人的工作经验或项目经历相关\n"
                        "请为每个维度打分（0-10分），提供简要的评价理由，并给出该问题的正确答案。\n"
                        "最后计算总分（各维度加权平均）。\n"
                        "请按照JSON格式输出，包含以下字段：\n"
                        "- scores: 包含产品规划能力、AI应用能力、产品化思维、团队影响力、与背景相关性五个维度的分数\n"
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
                        "你是一名专业的产品面试官，需要对候选人的回答进行评分并提供正确答案。\n"
                        "面试主题：{topic}\n"
                        "问题：{question}\n"
                        "回答：{answer}\n"
                        "参考内容：\n{context}\n"
                        "请根据以下评分标准对回答进行评估：\n"
                        "1. 产品规划能力：回答中体现的产品规划和设计能力\n"
                        "2. AI应用能力：将AI嵌入到工作流程的能力和思路\n"
                        "3. 产品化思维：将零散AI使用方式产品化、系统化的能力\n"
                        "4. 团队影响力：影响和带动团队使用AI的能力\n"
                        "请为每个维度打分（0-10分），提供简要的评价理由，并给出该问题的正确答案。\n"
                        "最后计算总分（各维度加权平均）。\n"
                        "请按照JSON格式输出，包含以下字段：\n"
                        "- scores: 包含产品规划能力、AI应用能力、产品化思维、团队影响力四个维度的分数\n"
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
            else:
                # 其他技术主题的通用评分标准
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
        except Exception as e:
            # 如果评分失败，使用模拟评分
            print(f"评分失败，使用模拟评分: {e}")
            return self.score_answer(question, answer, topic)
    
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