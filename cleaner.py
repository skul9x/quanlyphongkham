import os
import shutil
import tkinter as tk
from tkinter import messagebox, scrolledtext

class PycacheCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Công cụ Xóa __pycache__")
        self.root.geometry("500x350")
        
        # Xác định thư mục hiện tại nơi chứa script này
        self.current_dir = os.path.dirname(os.path.abspath(__file__))

        # UI Components
        self.create_widgets()

    def create_widgets(self):
        # Tiêu đề
        lbl_title = tk.Label(self.root, text="Dọn dẹp file rác Python", font=("Arial", 14, "bold"))
        lbl_title.pack(pady=10)

        # Hiển thị đường dẫn đang chọn
        frame_path = tk.Frame(self.root)
        frame_path.pack(pady=5, padx=10, fill=tk.X)
        
        lbl_path_title = tk.Label(frame_path, text="Thư mục mục tiêu:", font=("Arial", 10, "bold"))
        lbl_path_title.pack(anchor="w")
        
        lbl_path = tk.Label(frame_path, text=self.current_dir, fg="blue", wraplength=480, justify="left")
        lbl_path.pack(anchor="w")

        # Nút hành động
        btn_clean = tk.Button(self.root, text="Xóa tất cả __pycache__", bg="red", fg="white", font=("Arial", 10, "bold"), command=self.confirm_clean)
        btn_clean.pack(pady=15)

        # Khu vực log kết quả
        lbl_log = tk.Label(self.root, text="Nhật ký hoạt động:")
        lbl_log.pack(anchor="w", padx=10)

        self.txt_log = scrolledtext.ScrolledText(self.root, height=10, state='disabled')
        self.txt_log.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    def log_message(self, message):
        """Ghi log ra màn hình"""
        self.txt_log.config(state='normal')
        self.txt_log.insert(tk.END, message + "\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state='disabled')

    def confirm_clean(self):
        """Hỏi xác nhận trước khi xóa"""
        response = messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa tất cả thư mục '__pycache__' trong:\n{self.current_dir}\nvà các thư mục con không?")
        if response:
            self.clean_pycache()

    def clean_pycache(self):
        """Thực hiện logic xóa"""
        self.txt_log.config(state='normal')
        self.txt_log.delete(1.0, tk.END) # Xóa log cũ
        self.txt_log.config(state='disabled')
        
        deleted_count = 0
        errors = 0

        self.log_message(f"Đang quét: {self.current_dir} ...")

        # Duyệt cây thư mục (bottom-up để an toàn hơn khi xóa)
        for root_path, dirs, files in os.walk(self.current_dir, topdown=False):
            if "__pycache__" in dirs:
                target_path = os.path.join(root_path, "__pycache__")
                try:
                    shutil.rmtree(target_path)
                    self.log_message(f"Đã xóa: {target_path}")
                    deleted_count += 1
                except Exception as e:
                    self.log_message(f"LỖI khi xóa {target_path}: {e}")
                    errors += 1

        # Tổng kết
        summary = f"\n--- HOÀN TẤT ---\nĐã xóa: {deleted_count} thư mục.\nLỗi: {errors}."
        self.log_message(summary)
        messagebox.showinfo("Hoàn tất", f"Đã xóa xong {deleted_count} thư mục __pycache__.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PycacheCleanerApp(root)
    root.mainloop()