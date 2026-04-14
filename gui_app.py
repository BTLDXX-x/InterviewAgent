# 可视化面试界面应用
import tkinter as tk
from tkinter import scrolledtext, messagebox
from interviewer_agent import InterviewerAgent
from config import INTERVIEW_TOPICS

class InterviewGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        # 设计系统颜色
        self.colors = {
            "primary": "#ff385c",  # Rausch Red
            "text": "#222222",      # Near Black
            "text_secondary": "#6a6a6a",  # Secondary Gray
            "background": "#ffffff",  # Pure White
            "surface": "#f2f2f2",    # Light Surface
            "border": "#c1c1c1"       # Border Gray
        }
        
        # 字体设置
        self.fonts = {
            "title": ("Segoe UI", 16, "bold"),
            "heading": ("Segoe UI", 14, "bold"),
            "body": ("Segoe UI", 12),
            "button": ("Segoe UI", 12, "normal")
        }
        
        # 初始化界面
        self.title("AI面试官系统")
        # 默认全屏显示
        self.state('zoomed')
        self.resizable(True, True)
        
        # 设置背景
        self.configure(bg=self.colors["background"])
        
        # 初始化面试官Agent
        self.interviewer = InterviewerAgent()
        
        # 当前面试状态
        self.current_topic_index = 0
        self.interview_results = []
        self.is_interviewing = False
        
        # 加载提示
        self.loading_label = None
        
        # 创建界面组件
        self.create_widgets()
    
    def create_widgets(self):
        # 设置网格布局
        self.grid_rowconfigure(0, weight=1)  # 主题选择区域
        self.grid_rowconfigure(1, weight=7)  # 聊天区域
        self.grid_rowconfigure(2, weight=2)  # 输入区域
        self.grid_columnconfigure(0, weight=1)
        
        # 顶部标题和主题选择区域
        top_frame = tk.Frame(self, bg=self.colors["background"])
        top_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=24, pady=12)
        
        # 移除标题
        
        # 主题选择区域
        topic_frame = tk.Frame(top_frame, bg=self.colors["background"])
        topic_frame.pack(fill=tk.X, pady=(12, 0))
        
        topic_label = tk.Label(
            topic_frame, 
            text="面试主题:", 
            font=self.fonts["body"],
            fg=self.colors["text"]
        )
        topic_label.pack(side=tk.LEFT, padx=12)
        
        self.topic_var = tk.StringVar()
        self.topic_var.set(INTERVIEW_TOPICS[0])
        
        topic_option = tk.OptionMenu(topic_frame, self.topic_var, *INTERVIEW_TOPICS)
        topic_option.config(
            font=self.fonts["body"],
            bg=self.colors["surface"],
            fg=self.colors["text"],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0
        )
        topic_option.pack(side=tk.LEFT, padx=12)
        
        # 简历上传按钮
        self.resume_path = None
        resume_button = tk.Button(
            topic_frame, 
            text="上传简历", 
            command=self.upload_resume, 
            font=self.fonts["button"],
            bg=self.colors["surface"],
            fg=self.colors["text"],
            relief=tk.FLAT,
            bd=0,
            padx=24,
            pady=8,
            borderwidth=0,
            highlightthickness=0
        )
        resume_button.pack(side=tk.RIGHT, padx=12)
        
        # 开始面试按钮
        start_button = tk.Button(
            topic_frame, 
            text="开始面试", 
            command=self.start_interview, 
            font=self.fonts["button"],
            bg=self.colors["text"],
            fg=self.colors["background"],
            relief=tk.FLAT,
            bd=0,
            padx=24,
            pady=8,
            borderwidth=0,
            highlightthickness=0
        )
        start_button.pack(side=tk.RIGHT, padx=12)
        
        # 结束面试按钮
        self.end_button = tk.Button(
            topic_frame, 
            text="结束面试", 
            command=self.finish_interview, 
            font=self.fonts["button"],
            bg=self.colors["surface"],
            fg=self.colors["text"],
            relief=tk.FLAT,
            bd=0,
            padx=24,
            pady=8,
            borderwidth=0,
            highlightthickness=0
        )
        self.end_button.pack(side=tk.RIGHT, padx=12)
        self.end_button.config(state=tk.DISABLED)
        
        # 聊天消息区域
        chat_frame = tk.Frame(self, bg=self.colors["background"])
        chat_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=24, pady=12)
        
        # 聊天文本框容器，添加黑色边框
        chat_container = tk.Frame(chat_frame, bg="#000000")
        chat_container.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        self.chat_text = scrolledtext.ScrolledText(
            chat_container, 
            wrap=tk.WORD, 
            font=self.fonts["body"],
            bg=self.colors["background"],
            fg=self.colors["text"],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            padx=16,
            pady=16
        )
        self.chat_text.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # 加载提示区域
        self.loading_frame = tk.Frame(self, bg=self.colors["background"])
        self.loading_frame.grid(row=1, column=0, sticky=tk.S, padx=24, pady=12)
        
        # 输入区域
        input_frame = tk.Frame(self, bg=self.colors["background"])
        input_frame.grid(row=2, column=0, sticky=tk.NSEW, padx=24, pady=24)
        
        input_label = tk.Label(
            input_frame, 
            text="你的回答:", 
            font=self.fonts["body"],
            fg=self.colors["text"]
        )
        input_label.pack(side=tk.TOP, anchor=tk.W, padx=0, pady=(0, 8))
        
        # 输入框容器，添加黑色边框
        input_container = tk.Frame(input_frame, bg="#000000")
        input_container.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # 输入框内部容器
        input_inner = tk.Frame(input_container, bg=self.colors["background"])
        input_inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        self.input_text = tk.Text(
            input_inner, 
            height=4, 
            font=self.fonts["body"],
            bg=self.colors["background"],
            fg=self.colors["text"],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            padx=16,
            pady=12
        )
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        send_button = tk.Button(
            input_inner, 
            text="发送", 
            command=self.send_answer, 
            font=self.fonts["button"],
            bg=self.colors["primary"],
            fg=self.colors["background"],
            relief=tk.FLAT,
            bd=0,
            padx=24,
            pady=12,
            borderwidth=0,
            highlightthickness=0
        )
        send_button.pack(side=tk.RIGHT)
    
    def show_loading(self, message):
        """显示加载提示"""
        # 清空加载提示区域
        for widget in self.loading_frame.winfo_children():
            widget.destroy()
        
        # 创建加载提示标签
        self.loading_label = tk.Label(
            self.loading_frame, 
            text=message, 
            font=self.fonts["body"],
            fg=self.colors["text_secondary"]
        )
        self.loading_label.pack(side=tk.LEFT, padx=0)
        
        # 更新界面
        self.update()
    
    def hide_loading(self):
        """隐藏加载提示"""
        if self.loading_label:
            self.loading_label.destroy()
            self.loading_label = None
        
        # 清空加载提示区域
        for widget in self.loading_frame.winfo_children():
            widget.destroy()
        
        # 更新界面
        self.update()
    
    def upload_resume(self):
        """上传简历"""
        from tkinter import filedialog
        
        file_types = [
            ("文本文件", "*.txt"),
            ("PDF文件", "*.pdf"),
            ("Word文件", "*.docx"),
            ("所有文件", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="选择简历文件",
            filetypes=file_types
        )
        
        if file_path:
            self.resume_path = file_path
            messagebox.showinfo("成功", f"简历上传成功：{file_path}")
            
            # 在聊天区域显示简历上传信息
            self.chat_text.config(state=tk.NORMAL)
            self.chat_text.insert(tk.END, f"=== 系统消息 ===\n", "system")
            self.chat_text.insert(tk.END, f"简历上传成功，面试将基于你的简历内容进行提问。\n\n", "body")
            self.chat_text.config(state=tk.DISABLED)
    
    def start_interview(self):
        """开始面试流程"""
        if self.is_interviewing:
            messagebox.showinfo("提示", "面试已经开始，请完成当前面试后再开始新的面试。")
            return
        
        # 重置面试状态
        self.interviewer = InterviewerAgent(resume_path=self.resume_path)
        self.current_topic_index = 0
        self.interview_results = []
        self.is_interviewing = True
        
        # 启用结束面试按钮
        self.end_button.config(state=tk.NORMAL)
        
        # 清空聊天区域
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.delete(1.0, tk.END)
        self.chat_text.insert(tk.END, f"=== AI面试官系统 ===\n", "system")
        self.chat_text.insert(tk.END, f"欢迎参加面试，系统将根据不同主题进行提问。\n", "body")
        if self.resume_path:
            self.chat_text.insert(tk.END, f"系统已读取你的简历，面试问题将基于你的背景进行定制。\n", "body")
        self.chat_text.insert(tk.END, f"请认真回答每个问题，系统会对你的回答进行评分。\n\n", "body")
        # 配置标签样式
        self.chat_text.tag_config("system", foreground=self.colors["primary"], font=self.fonts["heading"])
        self.chat_text.tag_config("question_label", foreground="#666666", font=self.fonts["body"])
        self.chat_text.tag_config("question_bubble", foreground=self.colors["text"], font=self.fonts["body"], background="#f0f0f0")
        self.chat_text.tag_config("user_label", foreground="#666666", font=self.fonts["body"])
        self.chat_text.tag_config("user_bubble", foreground=self.colors["text"], font=self.fonts["body"], background="#e3f2fd")
        self.chat_text.config(state=tk.DISABLED)
        
        # 开始第一个问题
        self.next_question()
        
        # 确保输入框获得焦点
        self.input_text.focus_set()
        
        # 绑定回车键发送消息
        self.input_text.bind("<Return>", lambda event: self.send_answer())
    
    def next_question(self):
        """生成下一个问题"""
        if self.current_topic_index < len(INTERVIEW_TOPICS):
            # 显示加载提示
            self.show_loading("正在生成面试题，请等待...")
            
            topic = INTERVIEW_TOPICS[self.current_topic_index]
            question = self.interviewer.generate_question(topic)
            
            # 隐藏加载提示
            self.hide_loading()
            
            # 显示问题（面试官气泡）
            self.chat_text.config(state=tk.NORMAL)
            self.chat_text.insert(tk.END, f"=== {topic} ===\n", "system")
            self.chat_text.insert(tk.END, f"面试官: \n", "question_label")
            self.chat_text.insert(tk.END, f"{question}\n\n", "question_bubble")
            self.chat_text.see(tk.END)
            self.chat_text.config(state=tk.DISABLED)
        else:
            # 面试结束
            self.finish_interview()
    
    def send_answer(self):
        """发送回答"""
        if not self.is_interviewing:
            messagebox.showinfo("提示", "请先点击'开始面试'按钮开始面试。")
            return
        
        answer = self.input_text.get(1.0, tk.END).strip()
        if not answer:
            messagebox.showinfo("提示", "请输入你的回答。")
            return
        
        # 显示用户回答（用户气泡）
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, f"你: \n", "user_label")
        self.chat_text.insert(tk.END, f"{answer}\n\n", "user_bubble")
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.DISABLED)
        
        # 清空输入框
        self.input_text.delete(1.0, tk.END)
        
        # 显示加载提示
        self.show_loading("正在评析，请等待...")
        
        # 处理回答并评分
        self.interviewer.process_answer(answer)
        topic = INTERVIEW_TOPICS[self.current_topic_index]
        question = self.interviewer.questions_asked[-1]
        score_data = self.interviewer.score_answer(question, answer, topic)
        
        # 隐藏加载提示
        self.hide_loading()
        
        # 保存结果
        self.interview_results.append({
            "topic": topic,
            "question": question,
            "answer": answer,
            "score": score_data
        })
        
        # 显示评分结果（面试官气泡）
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, "=== 评分结果 ===\n", "system")
        self.chat_text.insert(tk.END, f"面试官: \n", "question_label")
        self.chat_text.insert(tk.END, f"准确性: {score_data['scores']['准确性']}\n", "question_bubble")
        self.chat_text.insert(tk.END, f"深度: {score_data['scores']['深度']}\n", "question_bubble")
        self.chat_text.insert(tk.END, f"清晰度: {score_data['scores']['清晰度']}\n", "question_bubble")
        self.chat_text.insert(tk.END, f"完整性: {score_data['scores']['完整性']}\n", "question_bubble")
        if '与背景相关性' in score_data['scores']:
            self.chat_text.insert(tk.END, f"与背景相关性: {score_data['scores']['与背景相关性']}\n", "question_bubble")
        self.chat_text.insert(tk.END, f"总分: {score_data['total_score']}\n", "question_bubble")
        self.chat_text.insert(tk.END, f"评价: {score_data['feedback']}\n", "question_bubble")
        self.chat_text.insert(tk.END, f"正确答案: {score_data['correct_answer']}\n\n", "question_bubble")
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.DISABLED)
        
        # 进入下一个问题
        self.current_topic_index += 1
        
        # 检查是否所有主题都已完成
        if self.current_topic_index >= len(INTERVIEW_TOPICS):
            self.finish_interview()
        else:
            self.next_question()
            # 确保输入框获得焦点
            self.input_text.focus_set()
    
    def finish_interview(self):
        """结束面试"""
        self.is_interviewing = False
        
        # 禁用结束面试按钮
        self.end_button.config(state=tk.DISABLED)
        
        # 计算总体评分
        total_scores = [result['score']['total_score'] for result in self.interview_results]
        overall_score = sum(total_scores) / len(total_scores) if total_scores else 0
        
        # 显示面试总结
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, "=== 面试总结 ===\n", "system")
        self.chat_text.insert(tk.END, f"总体评分: {overall_score:.2f}\n", "body")
        self.chat_text.insert(tk.END, "面试结束，感谢你的参与！\n", "body")
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.DISABLED)

def main():
    app = InterviewGUI()
    app.mainloop()

if __name__ == "__main__":
    main()