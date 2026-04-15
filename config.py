# 配置文件
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# OpenAI配置
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_API_BASE = os.getenv('OPENAI_API_BASE')
OPENAI_MODEL = 'gpt-3.5-turbo'

# 面试配置
INTERVIEW_TOPICS = [
    'AI应用产品经理',
    'AI Agent基础概念',
    '大模型原理与应用',
    'AI Agent开发实践',
    '大模型部署与优化',
    'AI伦理与安全'
]

# 评分标准
SCORE_CRITERIA = {
    '准确性': 0.3,
    '深度': 0.25,
    '清晰度': 0.2,
    '完整性': 0.25
}
