import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
from datetime import datetime
import ctypes


def get_battery_info():
    try:
        result = subprocess.run(
            ["wmic", "path", "Win32_Battery", "get", "EstimatedChargeRemaining"],
            capture_output=True, text=True, timeout=5
        )
        lines = [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]
        if len(lines) > 1 and lines[1].isdigit():
            return int(lines[1])
    except Exception:
        pass
    return None


def get_screen_size():
    user32 = ctypes.windll.user32
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("电脑检测器")
        self.root.geometry("480x480")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")

        # ===== 电量检测区 =====
        tk.Label(
            root, text="⚡ 电脑电量检测器 ⚡",
            font=("Microsoft YaHei", 18, "bold"),
            fg="#e0e0e0", bg="#1a1a2e"
        ).pack(pady=(25, 5))

        self.status_label = tk.Label(
            root, text="点击下方按钮开始检测",
            font=("Microsoft YaHei", 12),
            fg="#aaaacc", bg="#1a1a2e"
        )
        self.status_label.pack(pady=(2, 10))

        bar_frame = tk.Frame(root, bg="#333355", bd=0)
        bar_frame.pack(padx=60, fill="x")

        self.canvas = tk.Canvas(bar_frame, height=28, bg="#333355", highlightthickness=0)
        self.canvas.pack(fill="x", padx=2, pady=2)

        self.percent_label = tk.Label(
            root, text="0%",
            font=("Microsoft YaHei", 13, "bold"),
            fg="#00d2ff", bg="#1a1a2e"
        )
        self.percent_label.pack(pady=(5, 10))

        self.btn_detect = tk.Button(
            root, text="开始检测",
            font=("Microsoft YaHei", 13, "bold"),
            fg="white", bg="#0f3460",
            activebackground="#16537e", activeforeground="white",
            relief="flat", cursor="hand2",
            width=16, height=1,
            command=self.start_detection
        )
        self.btn_detect.pack(pady=(0, 10))

        self.detecting = False

        # ===== 分割线 =====
        tk.Frame(root, height=2, bg="#333355").pack(fill="x", padx=40, pady=(5, 10))

        # ===== 时间查看区 =====
        tk.Label(
            root, text="🕐 时间查看器",
            font=("Microsoft YaHei", 18, "bold"),
            fg="#e0e0e0", bg="#1a1a2e"
        ).pack(pady=(0, 5))

        self.time_display = tk.Label(
            root, text="",
            font=("Microsoft YaHei", 22, "bold"),
            fg="#ffcc00", bg="#1a1a2e"
        )
        self.time_display.pack(pady=(0, 0))

        self.date_display = tk.Label(
            root, text="",
            font=("Microsoft YaHei", 12),
            fg="#aaaacc", bg="#1a1a2e"
        )
        self.date_display.pack(pady=(0, 0))

        self.btn_time = tk.Button(
            root, text="查看时间",
            font=("Microsoft YaHei", 13, "bold"),
            fg="white", bg="#533483",
            activebackground="#6a45a0", activeforeground="white",
            relief="flat", cursor="hand2",
            width=16, height=1,
            command=self.show_time
        )
        self.btn_time.pack(pady=(10, 5))

        self.arrow_window = None
        self.arrow_blink = False

    # ===== 电量检测 =====
    def start_detection(self):
        if self.detecting:
            return
        self.detecting = True
        self.btn_detect.config(state="disabled", text="检测中...")
        self.status_label.config(text="大模型计算中...")
        self.percent_label.config(text="0%")
        self.canvas.delete("all")
        self.progress = 0
        self._tick()

    def _tick(self):
        if self.progress > 100:
            self.detecting = False
            self.btn_detect.config(state="normal", text="开始检测")
            battery = get_battery_info()
            if battery is not None:
                msg = f"检测完成！当前电池电量：{battery}%\n\n您的电脑有电！"
            else:
                msg = "检测完成！\n\n您的电脑有电！"
            messagebox.showinfo("检测结果", msg)
            return

        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        bar_w = int(w * self.progress / 100)
        r = int(0)
        g = int(100 + (255 - 100) * self.progress / 100)
        b = int(255 + (100 - 255) * self.progress / 100)
        color = f"#{r:02x}{g:02x}{b:02x}"
        self.canvas.create_rectangle(0, 0, bar_w, h, fill=color, outline="")
        self.canvas.create_text(w // 2, h // 2, text=f"{self.progress}%",
                                font=("Microsoft YaHei", 10, "bold"), fill="white")

        self.percent_label.config(text=f"{self.progress}%")
        self.progress += 1
        delay = 15 if self.progress < 60 else 25
        self.root.after(delay, self._tick)

    # ===== 时间查看 =====
    def show_time(self):
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%Y年%m月%d日")
        self.time_display.config(text=f"⏰ {time_str}")
        self.date_display.config(text=f"📅 {date_str}")

        # 关掉之前的箭头窗口
        if self.arrow_window:
            self.arrow_window.destroy()

        self._create_arrow_window()

    def _create_arrow_window(self):
        sw, sh = get_screen_size()
        # 任务栏时钟大致在屏幕右下角，留出任务栏高度(约48px)
        clock_x = sw - 90
        clock_y = sh - 48

        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        # 透明色背景
        win.attributes("-transparentcolor", "#010101")
        win.configure(bg="#010101")
        win.geometry(f"{sw}x{sh}+0+0")

        cv = tk.Canvas(win, width=sw, height=sh, bg="#010101",
                       highlightthickness=0)
        cv.pack()

        # 从窗口中心向右下角时钟画箭头
        app_x = self.root.winfo_x() + self.root.winfo_width() // 2
        app_y = self.root.winfo_y() + self.root.winfo_height() // 2

        # 箭头主线
        cv.create_line(app_x, app_y, clock_x, clock_y,
                       fill="#ff4444", width=5, arrow="last",
                       arrowshape=(24, 30, 12))

        # 在箭头末端（时钟附近）画一个醒目圆圈
        cv.create_oval(clock_x - 40, clock_y - 40,
                       clock_x + 40, clock_y + 40,
                       outline="#ff4444", width=3)

        # 文字标注
        cv.create_text(clock_x - 120, clock_y - 55,
                       text=f"⬇ 您的电脑时间",
                       font=("Microsoft YaHei", 16, "bold"),
                       fill="#ff6666")

        self.arrow_window = win
        self.arrow_blink = False

        # 5秒后自动关闭箭头
        self.root.after(5000, self._close_arrow)

        # 闪烁动画
        self._blink_arrow(cv, clock_x, clock_y)

    def _blink_arrow(self, cv, cx, cy):
        if not self.arrow_window:
            return
        self.arrow_blink = not self.arrow_blink
        color = "#ff4444" if self.arrow_blink else "#ff8888"
        cv.delete("ring")
        cv.create_oval(cx - 40, cy - 40, cx + 40, cy + 40,
                       outline=color, width=3, tags="ring")
        self.root.after(400, lambda: self._blink_arrow(cv, cx, cy))

    def _close_arrow(self):
        if self.arrow_window:
            self.arrow_window.destroy()
            self.arrow_window = None


def main():
    root = tk.Tk()
    try:
        root.iconbitmap(default="")
    except Exception:
        pass
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
