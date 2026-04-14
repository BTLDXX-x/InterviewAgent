# AI面试官系统

一个基于AI的智能面试官系统，用于模拟面试过程并对面试者的回答进行评分。

## 功能特点

- **可视化聊天界面**：使用Tkinter实现的图形化界面，支持气泡式对话
- **多主题面试**：支持多个面试主题，包括AI Agent基础概念、大模型原理与应用等
- **简历分析**：支持上传简历，基于简历内容生成定制化问题
- **智能评分**：对面试者的回答进行多维度评分，包括准确性、深度、清晰度和完整性
- **RAG技术**：使用检索增强生成技术，基于题库文件生成问题
- **响应式布局**：自适应窗口大小，确保界面在不同尺寸下都能正常显示

## 技术栈

- Python 3.12+
- Tkinter（GUI）
- LangChain（RAG系统）
- Chroma（向量数据库）
- OpenAI API（大语言模型）

## 安装步骤

1. **克隆仓库**
   ```bash
   git clone <repository-url>
   cd InterviewAgent
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   ```

3. **激活虚拟环境**
   - Windows：
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux：
     ```bash
     source venv/bin/activate
     ```

4. **安装依赖**
   ```bash
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

5. **配置API密钥**
   - 复制`.env`文件并填写OpenAI API密钥：
     ```bash
     # OpenAI API密钥
     OPENAI_API_KEY=your_openai_api_key_here
     OPENAI_API_BASE=your_openai_api_base_here
     ```

## 使用方法

1. **启动应用**
   ```bash
   python main.py
   ```

2. **开始面试**
   - 选择面试主题
   - 可选：上传简历（支持PDF、Word、TXT格式）
   - 点击「开始面试」按钮

3. **回答问题**
   - 在输入框中输入你的回答
   - 点击「发送」按钮或按回车键提交

4. **查看评分**
   - 系统会自动对每个问题的回答进行评分
   - 显示评分结果和反馈

5. **结束面试**
   - 面试完成后，系统会自动结束
   - 也可以随时点击「结束面试」按钮手动结束

## 项目结构

```
InterviewAgent/
├── .env              # 环境变量配置
├── .gitignore        # Git忽略文件
├── DESIGN.md         # 设计文档
├── README.md         # 项目说明
├── config.py         # 配置文件
├── gui_app.py        # GUI应用
├── interviewer_agent.py  # 面试官Agent
├── main.py           # 主入口
├── mock_interviewer_agent.py  # 模拟面试官Agent
├── rag_system.py     # RAG系统
├── requirements.txt  # 依赖项
├── test_gui.py       # GUI测试
├── test_score.py     # 评分测试
└── 题库              # 面试题库
```

## 注意事项

- 需要有效的OpenAI API密钥才能使用完整功能
- 上传的简历会被系统分析，用于生成相关问题
- 面试过程中，系统会根据你的回答实时生成评分和反馈
- 系统支持多种面试主题，你可以根据需要选择合适的主题

## 贡献

欢迎提交Issue和Pull Request，帮助改进这个项目。

## 许可证

MIT License
