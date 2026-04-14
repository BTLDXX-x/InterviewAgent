# 测试评分功能
from interviewer_agent import InterviewerAgent

# 初始化面试官Agent
interviewer = InterviewerAgent()

# 测试评分功能
topic = "编程基础"
question = "请编写一个函数，判断一个字符串中所有字符是否都唯一。要求不使用额外的数据结构，且时间复杂度尽可能优化。"
answer = "我会使用位运算的方法，因为字符的ASCII码范围有限。对于每个字符，检查对应的位是否已经被设置，如果是则返回False，否则设置该位。"

# 评分
score_data = interviewer.score_answer(question, answer, topic)

# 显示结果
print("测试评分功能:")
print(f"问题: {question}")
print(f"回答: {answer}")
print(f"\n评分结果:")
print(f"准确性: {score_data['scores']['准确性']}")
print(f"深度: {score_data['scores']['深度']}")
print(f"清晰度: {score_data['scores']['清晰度']}")
print(f"完整性: {score_data['scores']['完整性']}")
print(f"总分: {score_data['total_score']}")
print(f"评价: {score_data['feedback']}")
print(f"正确答案: {score_data['correct_answer']}")
