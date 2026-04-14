# 测试GUI应用是否可以正常导入和实例化

try:
    from gui_app import InterviewGUI
    print("GUI应用导入成功")
    
    # 测试初始化
    print("正在初始化GUI应用...")
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()  # 隐藏窗口
    app = InterviewGUI()
    print("GUI应用初始化成功")
    root.destroy()
    
    print("所有测试通过！")
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()