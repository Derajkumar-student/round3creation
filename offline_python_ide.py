#!/usr/bin/env python3
import sys
import os
import tempfile
import random
import subprocess
import ctypes
from ctypes import wintypes

from PyQt5.QtWidgets import (
    QApplication, QWidget, QPlainTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QInputDialog,
    QMenuBar, QAction, QFileDialog
)
from PyQt5.QtCore import Qt, QProcess, QTimer
from PyQt5.QtGui import QTextCursor


class OfflinePythonIDE(QWidget):
    HARD_TIMEOUT_MS = 15 * 60 * 1000
    GROUP_TIMER_MS = 20 * 60 * 1000  # 20 minutes in milliseconds

    # Template codes for each program (prog1..prog15)
    PROGRAM_TEMPLATES = {
        "prog1": """# Program 1: Basic Input/Output and Arithmetic Operations
num1 = int(input("Enter first number: "))
num2 = int(input("Enter second number: "))
sum_result = num1 + num2
difference = num1 - num2
product = num1 * num2
print(f"Sum: {sum_result}")
print(f"Difference: {difference}")
print(f"Product: {product}")
if num2 != 0:
    quotient = num1 / num2
    print(f"Quotient: {quotient}")
else:
    print("Cannot divide by zero!")
""",
        "prog2": """# Program 2: List/Array Operations
numbers = []
n = int(input("How many numbers do you want to add? "))
for i in range(n):
    num = int(input(f"Enter number {i+1}: "))
    numbers.append(num)
print(f"Original list: {numbers}")
if len(numbers) > 0:
    total = sum(numbers)
    average = total / len(numbers)
    print(f"Sum: {total}")
    print(f"Average: {average}")
    print(f"Maximum: {max(numbers)}")
    print(f"Minimum: {min(numbers)}")
else:
    print("List is empty!")
""",
        "prog3": """# Program 3: String Processing and Manipulation
text = input("Enter a string: ")
print(f"Original string: {text}")
print(f"Length: {len(text)}")
print(f"Uppercase: {text.upper()}")
print(f"Lowercase: {text.lower()}")
vowels = "aeiouAEIOU"
vowel_count = sum(1 for char in text if char in vowels)
print(f"Number of vowels: {vowel_count}")
reversed_text = text[::-1]
print(f"Reversed: {reversed_text}")
if text.lower().replace(' ', '') == reversed_text.lower().replace(' ', ''):
    print("The string is a palindrome!")
else:
    print("The string is not a palindrome.")
""",
        "prog4": """# Program 4: Mathematical Computations
def factorial(n):
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True

num = int(input("Enter a number: "))
if num >= 0:
    fact = factorial(num)
    print(f"Factorial of {num} is: {fact}")
else:
    print("Factorial is not defined for negative numbers!")
if is_prime(num):
    print(f"{num} is a prime number.")
else:
    print(f"{num} is not a prime number.")
print(f"Square: {num ** 2}")
print(f"Cube: {num ** 3}")
""",
        "prog5": """# Program 5: Control Structures and Problem Solving
start = int(input("Enter start number: "))
end = int(input("Enter end number: "))
divisor1 = int(input("Enter first divisor: "))
divisor2 = int(input("Enter second divisor: "))
print(f"\\nNumbers between {start} and {end} divisible by {divisor1} or {divisor2}:")
count = 0
for num in range(start, end + 1):
    if num % divisor1 == 0 or num % divisor2 == 0:
        print(num, end=" ")
        count += 1
print(f"\\n\\nTotal count: {count}")
print(f"\\nNumbers divisible by both {divisor1} and {divisor2}:")
both_count = 0
for num in range(start, end + 1):
    if num % divisor1 == 0 and num % divisor2 == 0:
        print(num, end=" ")
        both_count += 1
print(f"\\n\\nTotal count: {both_count}")
""",
        "prog6": """# Program 6: File I/O Example
lines = []
n = int(input("How many lines will you enter? "))
for i in range(n):
    lines.append(input(f"Line {i+1}: "))
import tempfile
with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
    fname = f.name
    for line in lines:
        f.write(line + '\\n')
print(f"Saved to temporary file: {fname}")
with open(fname, 'r') as f:
    content = f.read()
print("File contents:")
print(content)
""",
        "prog7": """# Program 7: Dictionary and Count Operations
text = input("Enter a sentence: ")
words = text.strip().split()
freq = {}
for w in words:
    w = w.lower()
    freq[w] = freq.get(w, 0) + 1
print("Word frequencies:")
for w, c in sorted(freq.items(), key=lambda x: (-x[1], x[0])):
    print(f"{w}: {c}")
""",
        "prog8": """# Program 8: Recursion (Fibonacci)
def fib(n):
    if n <= 0:
        return 0
    if n == 1:
        return 1
    return fib(n-1) + fib(n-2)
n = int(input("Compute Fibonacci for n (<=30 recommended): "))
print(f"Fibonacci({n}) = {fib(n)}")
""",
        "prog9": """# Program 9: Simple Class Example
class Rectangle:
    def __init__(self, w, h):
        self.w = w
        self.h = h
    def area(self):
        return self.w * self.h
    def perimeter(self):
        return 2 * (self.w + self.h)
w = int(input("Width: "))
h = int(input("Height: "))
r = Rectangle(w, h)
print(f"Area: {r.area()}")
print(f"Perimeter: {r.perimeter()}")
""",
        "prog10": """# Program 10: Exception Handling Example
try:
    a = int(input("Enter numerator: "))
    b = int(input("Enter denominator: "))
    result = a / b
    print(f"Result: {result}")
except ZeroDivisionError:
    print("Cannot divide by zero!")
except ValueError:
    print("Please enter valid integers.")
""",
        "prog11": """# Program 11: Set Operations
a = set(map(int, input("Enter numbers for set A (space-separated): ").split()))
b = set(map(int, input("Enter numbers for set B (space-separated): ").split()))
print("A union B:", sorted(a | b))
print("A intersection B:", sorted(a & b))
print("A - B:", sorted(a - b))
""",
        "prog12": """# Program 12: Simple Sorting
arr = list(map(int, input("Enter numbers to sort (space-separated): ").split()))
print("Original:", arr)
print("Sorted:", sorted(arr))
""",
        "prog13": """# Program 13: Using List Comprehensions
n = int(input("Enter n: "))
squares = [i*i for i in range(1, n+1)]
print("Squares:", squares)
""",
        "prog14": """# Program 14: Palindrome Number Check
num = int(input("Enter a number: "))
s = str(num)
if s == s[::-1]:
    print(f"{num} is a palindrome number")
else:
    print(f"{num} is not a palindrome number")
""",
        "prog15": """# Program 15: Simple Math Quiz
import random
a = random.randint(1, 20)
b = random.randint(1, 20)
ans = int(input(f"What is {a} + {b}? "))
if ans == a + b:
    print("Correct!")
else:
    print(f"Wrong — correct answer is {a + b}")
"""
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Compiler of MNMJEC")
        self.setGeometry(150, 80, 1100, 720)

        # ---------- UI ----------
        title = QLabel("Python Compiler of MNMJEC")
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title.setStyleSheet("color:#0b1220;font-size:20px;font-weight:700;")

        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Write Python code here…")
        self.editor.setStyleSheet("""
            background:#001f3f;
            color:#ffd700;
            font-family:Consolas;
            font-size:16px;
            padding:14px;
            border-radius:8px;
            border: 1px solid rgba(11,18,32,0.12);
            selection-background-color: rgba(255,215,0,0.15);
            selection-color: #ffd700;
        """)

        self.output = QPlainTextEdit(readOnly=True)
        self.output.setStyleSheet("""
            background:#071733;
            color:#ffd700;
            font-family:Consolas;
            font-size:14px;
            padding:14px;
            border-radius:8px;
            border: 1px solid rgba(11,18,32,0.12);
            selection-background-color: rgba(255,215,0,0.12);
            selection-color: #071733;
        """)

        self.run_btn = QPushButton("▶ Run")
        self.stop_btn = QPushButton("⛔ Stop")
        self.clear_btn = QPushButton("🧹 Clear")

        for btn in (self.run_btn, self.stop_btn, self.clear_btn):
            btn.setStyleSheet("""
                QPushButton {
                    background:#2563eb;
                    color:white;
                    padding:8px 18px;
                    font-size:14px;
                    border-radius:6px;
                }
                QPushButton:hover { background:#1e40af; }
            """)

        self.stop_btn.setEnabled(False)
        self.run_btn.clicked.connect(self.run_code)
        self.stop_btn.clicked.connect(self.stop_process)
        self.clear_btn.clicked.connect(self.output.clear)

        btns = QHBoxLayout()
        btns.addWidget(self.run_btn)
        btns.addWidget(self.stop_btn)
        btns.addWidget(self.clear_btn)
        btns.addStretch()

        # error banner (hidden initially)
        self.error_banner = QLabel()
        self.error_banner.setVisible(False)
        self.error_banner.setStyleSheet("background:#b91c1c;color:white;padding:6px;border-radius:4px;")
        self.error_banner.setAlignment(Qt.AlignCenter)

        # group timer label to show remaining time for the visible templates (placed top-right)
        self.group_timer_label = QLabel()
        self.group_timer_label.setVisible(False)
        self.group_timer_label.setStyleSheet("background:#0b1220;color:#ffd700;padding:6px;border-radius:6px;")
        self.group_timer_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout = QVBoxLayout(self)

        # ---------- MENU BAR ----------
        self.menu_bar = QMenuBar(self)

        # File menu
        file_menu = self.menu_bar.addMenu("File")
        self.new_act = QAction("New", self)
        self.new_act.setShortcut("Ctrl+N")
        self.new_act.triggered.connect(self.new_file)
        self.open_act = QAction("Open...", self)
        self.open_act.setShortcut("Ctrl+O")
        self.open_act.triggered.connect(self.open_file)
        self.save_act = QAction("Save", self)
        self.save_act.setShortcut("Ctrl+S")
        self.save_act.triggered.connect(self.save_file)
        self.save_as_act = QAction("Save As...", self)
        self.save_as_act.triggered.connect(self.save_file_as)
        self.exit_act = QAction("Exit", self)
        self.exit_act.triggered.connect(self.close)
        for act in (self.new_act, self.open_act, self.save_act, self.save_as_act, self.exit_act):
            file_menu.addAction(act)

        self.file_actions = [self.new_act, self.open_act]

        # Run menu
        run_menu = self.menu_bar.addMenu("Run")
        run_act = QAction("Run", self)
        run_act.setShortcut("F5")
        run_act.triggered.connect(self.run_code)
        stop_act = QAction("Stop", self)
        stop_act.triggered.connect(self.stop_process)
        clear_out_act = QAction("Clear Output", self)
        clear_out_act.triggered.connect(self.output.clear)
        for act in (run_act, stop_act, clear_out_act):
            run_menu.addAction(act)

        # Programs menu: show 5 templates chosen at random (in random order) each run of the IDE
        programs_menu = self.menu_bar.addMenu("Programs")
        all_keys = list(self.PROGRAM_TEMPLATES.keys())
        # choose 5 random templates to show this session
        self.visible_template_keys = random.sample(all_keys, 5)
        random.shuffle(self.visible_template_keys)

        self.prog_actions = []
        for key in self.visible_template_keys:
            i = int(key.replace("prog", ""))
            act = QAction(f"Prog {i}", self)
            act.triggered.connect(lambda checked=False, k=key: self.load_program_template(k))
            programs_menu.addAction(act)
            self.prog_actions.append(act)

        # Help menu
        help_menu = self.menu_bar.addMenu("Help")
        about_act = QAction("About", self)
        about_act.triggered.connect(self.show_about)
        help_menu.addAction(about_act)

        layout.setMenuBar(self.menu_bar)

        # Top row: title (left) and timer (right)
        top_row = QHBoxLayout()
        top_row.addWidget(title)
        top_row.addStretch()
        top_row.addWidget(self.group_timer_label)
        layout.addLayout(top_row)

        layout.addWidget(self.error_banner)
        layout.addWidget(QLabel("📝 Code Editor"))
        layout.addWidget(self.editor, 3)
        layout.addLayout(btns)
        layout.addWidget(QLabel("📤 Output Console"))
        layout.addWidget(self.output, 2)

        self.setStyleSheet("background:#ffffff; color:#0b1220;")

        # ---------- PROCESS ----------
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.read_stdout)
        self.process.readyReadStandardError.connect(self.read_stderr)
        self.process.finished.connect(self.finished)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.force_kill)

        # group timer variables
        self.group_timer_started = False
        self.group_time_left_ms = 0
        self.group_countdown_timer = QTimer(self)
        self.group_countdown_timer.timeout.connect(self._tick_group_timer)

        self.temp_file = None
        self.user_input = ""
        self.current_file = None
        self.runtime_error = False
        self.current_template = None

        # Track whether window was maximized before a run so we can restore it later
        self._pre_run_was_maximized = False
        
        # Track if the last run was initiated by this IDE (used for validation)
        self._last_run_initiated_by_ide = False

        # System hook state and focus protection
        self._system_hook_installed = False
        self._hhook = None
        self._hook_proc_ptr = None
        self._protect_run_active = False
        try:
            app_instance = QApplication.instance()
            if app_instance is not None:
                app_instance.focusChanged.connect(self._on_focus_changed)
        except Exception:
            pass

        # Periodically check whether a debugger is attached; if so, enable protections
        try:
            self._debugger_check_timer = QTimer(self)
            self._debugger_check_timer.setInterval(1000)
            self._debugger_check_timer.timeout.connect(self._check_debugger_and_protect)
            self._debugger_check_timer.start()
        except Exception:
            self._debugger_check_timer = None

        # ========== NEW: ENHANCED WINDOW LOCK PROTECTION ==========
        # (hash and debugger locks removed)

    # ---------- Helpers ----------
    def _on_focus_changed(self, old, now):
        try:
            if getattr(self, '_protect_run_active', False):
                # If focus changed away from this IDE, try to restore it
                if now is not None and now.window() is not self:
                    QTimer.singleShot(50, lambda: (self.raise_(), self.activateWindow()))
        except Exception:
            pass

    def _install_system_key_block(self):
        """Install a low-level keyboard hook on Windows to block Alt+Tab / Win keys / Ctrl+Esc."""
        if os.name != 'nt':
            return False
        if self._system_hook_installed:
            return True
        try:
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32

            WH_KEYBOARD_LL = 13
            WM_KEYDOWN = 0x0100
            WM_KEYUP = 0x0101
            WM_SYSKEYDOWN = 0x0104
            WM_SYSKEYUP = 0x0105

            # KBDLLHOOKSTRUCT
            class KBDLLHOOKSTRUCT(ctypes.Structure):
                _fields_ = [
                    ('vkCode', wintypes.DWORD),
                    ('scanCode', wintypes.DWORD),
                    ('flags', wintypes.DWORD),
                    ('time', wintypes.DWORD),
                    ('dwExtraInfo', wintypes.ULONG_PTR),
                ]

            LowLevelKeyboardProc = ctypes.WINFUNCTYPE(wintypes.LRESULT, wintypes.INT, wintypes.WPARAM, wintypes.LPARAM)

            def _proc(nCode, wParam, lParam):
                try:
                    if nCode == 0:
                        kb = KBDLLHOOKSTRUCT.from_address(lParam)
                        vk = kb.vkCode
                        flags = kb.flags
                        alt_pressed = (flags & 0x20) != 0
                        # Block Win keys
                        if vk in (0x5B, 0x5C):
                            return 1
                        # Block Alt+Tab
                        if (wParam == WM_SYSKEYDOWN or wParam == WM_KEYDOWN) and vk == 0x09 and alt_pressed:
                            return 1
                        # Block Ctrl+Esc
                        if (wParam == WM_KEYDOWN or wParam == WM_SYSKEYDOWN) and vk == 0x1B and (ctypes.windll.user32.GetKeyState(0x11) & 0x8000):
                            return 1
                except Exception:
                    pass
                return user32.CallNextHookEx(self._hhook, nCode, wParam, lParam)

            self._hook_proc_ptr = LowLevelKeyboardProc(_proc)
            hInstance = kernel32.GetModuleHandleW(None)
            hhook = user32.SetWindowsHookExW(WH_KEYBOARD_LL, self._hook_proc_ptr, hInstance, 0)
            if hhook == 0:
                return False
            self._hhook = hhook
            self._system_hook_installed = True
            return True
        except Exception:
            return False

    def _uninstall_system_key_block(self):
        if os.name != 'nt':
            return
        try:
            if self._system_hook_installed and self._hhook:
                ctypes.windll.user32.UnhookWindowsHookEx(self._hhook)
        except Exception:
            pass
        finally:
            self._system_hook_installed = False
            self._hhook = None
            self._hook_proc_ptr = None
    def set_program_actions_enabled(self, enabled: bool):
        try:
            for act in getattr(self, "prog_actions", []):
                act.setEnabled(enabled)
        except Exception:
            pass

    def set_file_actions_enabled(self, enabled: bool):
        try:
            for act in getattr(self, "file_actions", []):
                act.setEnabled(enabled)
        except Exception:
            pass

    # (hash-based validation and external-debugger blocking removed)

    # ---------- Group timer for visible templates ----------
    def start_group_timer_if_needed(self):
        """Start the 20-minute group timer for the visible templates on first template selection."""
        if self.group_timer_started:
            return
        self.group_timer_started = True
        self.group_time_left_ms = self.GROUP_TIMER_MS
        self._update_group_timer_label()
        self.group_timer_label.setVisible(True)
        self.group_countdown_timer.start(1000)
        QTimer.singleShot(self.GROUP_TIMER_MS, self.on_group_time_expired)

    def _tick_group_timer(self):
        self.group_time_left_ms -= 1000
        if self.group_time_left_ms <= 0:
            self.group_time_left_ms = 0
            self.group_countdown_timer.stop()
        self._update_group_timer_label()

    def _update_group_timer_label(self):
        ms = max(0, self.group_time_left_ms)
        seconds = ms // 1000
        mins = seconds // 60
        secs = seconds % 60
        self.group_timer_label.setText(f"⏳ Templates time left: {mins:02d}:{secs:02d}")
        if ms == 0:
            self.group_timer_label.setText("⏱ Templates time expired — editor is read-only")

    def on_group_time_expired(self):
        try:
            self.group_countdown_timer.stop()
        except Exception:
            pass
        self.editor.setReadOnly(True)
        self.run_btn.setEnabled(False)
        self.set_program_actions_enabled(False)
        self.set_file_actions_enabled(False)
        self.set_error_banner(True, "⏱ Time for the displayed templates has expired — editor is now read-only.")
        self.group_timer_label.setVisible(True)
        self._update_group_timer_label()

    # ---------- WINDOW LOCK ----------
    def lock_window(self):
        try:
            self.setWindowFlag(Qt.WindowCloseButtonHint, True)
            self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
            self.raise_()
            self.activateWindow()
            self.show()
        except Exception:
            pass

    def unlock_window(self):
        try:
            self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
            self.show()
        except Exception:
            pass

    # ---------- MIN / MAX CONTROL ----------
    def disable_min_max(self):
        try:
            self.setWindowFlag(Qt.WindowMinimizeButtonHint, False)
            self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
            self.show()
        except Exception:
            pass

    def enable_min_max(self):
        try:
            self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
            self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
            self.show()
        except Exception:
            pass

    # ---------- ERROR BANNER ----------
    def set_error_banner(self, show: bool, text: str = ""):
        try:
            if show:
                self.error_banner.setText(text)
                self.error_banner.setVisible(True)
            else:
                self.error_banner.setVisible(False)
                self.error_banner.setText("")
        except Exception:
            pass

    # ---------- INPUT DETECTION ----------
    def code_needs_input(self, code):
        return "input(" in code

    # ---------- SYNTAX CHECK ----------
    def has_syntax_error(self, code):
        try:
            compile(code, "<contest>", "exec")
            return None
        except Exception:
            return "Error occurred"

    # ---------- RUN ----------
    def run_code(self):
        if self.group_timer_started and self.group_time_left_ms == 0:
            QMessageBox.information(self, "Time Expired", "Template time expired — editor is read-only.")
            return

        code = self.editor.toPlainText().strip()
        if not code:
            QMessageBox.warning(self, "No Code", "Please write some Python code.")
            return

        error = self.has_syntax_error(code)
        if error:
            self.output.clear()
            self.output.appendPlainText("❌ SYNTAX ERROR DETECTED\n")
            self.output.appendPlainText("Error occurred\n")
            self.runtime_error = True
            self.disable_min_max()
            if self.current_template:
                self.set_error_banner(True, f"❌ Syntax error detected — Fix the code in '{self.current_template}' and run successfully to enable minimize/maximize buttons")
            else:
                self.set_error_banner(True, "❌ Syntax error detected — fix code and run to unlock window")
            self.lock_window()
            return

        # (previous code-integrity and external-debugger checks removed)

        self.runtime_error = False
        self.disable_min_max()
        self.set_error_banner(False, "")

        if self.current_template:
            self.start_group_timer_if_needed()

        self.user_input = ""
        if self.code_needs_input(code):
            text, ok = QInputDialog.getMultiLineText(self, "Program Input", "Enter input:")
            if not ok:
                return
            self.user_input = text + "\n"

        # Add a runtime guard to the temporary script so it only executes when
        # launched from this IDE process (parent-PID verification).
        guard = (
            "import os,sys\n"
            "_expected_ppid = os.environ.get('MNMJ_PARENT_PID')\n"
            "try:\n"
            "    if _expected_ppid is None or int(_expected_ppid) != os.getppid():\n"
            "        print('❌ Unauthorized execution: script must be run from the MNMJ IDE')\n"
            "        sys.exit(2)\n"
            "except Exception:\n"
            "    print('❌ Unauthorized execution: script must be run from the MNMJ IDE')\n"
            "    sys.exit(2)\n"
            "sys.setrecursionlimit(10**7)\n"
        )
        code = guard + code

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8") as f:
                f.write(code)
                self.temp_file = f.name
        except Exception as e:
            QMessageBox.critical(self, "Temp File Error", f"Failed to write temp file:\n{e}")
            self.enable_min_max()
            return

        self.output.clear()
        self.output.appendPlainText("▶ Running...\n")

        self.editor.setReadOnly(True)
        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        try:
            self._pre_run_was_maximized = self.isMaximized()
            self.showMaximized()
        except Exception:
            pass

        try:
            # Mark that this run is initiated by the IDE and set a short-lived
            # environment variable the child will check.
            prev_env = os.environ.get('MNMJ_PARENT_PID')
            try:
                os.environ['MNMJ_PARENT_PID'] = str(os.getpid())
                self._last_run_initiated_by_ide = True
                self.process.start(sys.executable, ["-u", self.temp_file])
            finally:
                # restore previous environment variable immediately; child has already inherited it
                try:
                    if prev_env is None:
                        del os.environ['MNMJ_PARENT_PID']
                    else:
                        os.environ['MNMJ_PARENT_PID'] = prev_env
                except Exception:
                    pass
            if not self.process.waitForStarted(1000):
                self.output.appendPlainText("\n❌ Failed to start process.\n")
                self.stop_btn.setEnabled(False)
                self.run_btn.setEnabled(True)
                self.editor.setReadOnly(False)
                try:
                    if not self._pre_run_was_maximized:
                        self.showNormal()
                except Exception:
                    pass
                return
            # install system key block to prevent switching while running
            try:
                if self._install_system_key_block():
                    self._protect_run_active = True
            except Exception:
                pass
        except Exception:
            self.output.appendPlainText("\n❌ Failed to start process.\n")
            self.stop_btn.setEnabled(False)
            self.run_btn.setEnabled(True)
            self.editor.setReadOnly(False)
            try:
                if not self._pre_run_was_maximized:
                    self.showNormal()
            except Exception:
                pass
            return

        if self.user_input and self.process.state() == QProcess.Running:
            try:
                self.process.write(self.user_input.encode())
                self.process.closeWriteChannel()
            except Exception:
                pass

        self.timer.start(self.HARD_TIMEOUT_MS)

    # ---------- OUTPUT ----------
    def read_stdout(self):
        try:
            text = bytes(self.process.readAllStandardOutput()).decode(errors="replace")
            self.output.insertPlainText(text)
            cursor = self.output.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.output.setTextCursor(cursor)
        except Exception:
            pass

    def read_stderr(self):
        try:
            data = bytes(self.process.readAllStandardError()).decode(errors="replace")
            if data.strip() and not self.runtime_error:
                self.runtime_error = True
                self.output.insertPlainText("\n❌ ERROR: Error occurred\n")
                self.disable_min_max()
                if self.current_template:
                    self.set_error_banner(True, f"❌ Runtime error detected — Fix the code in '{self.current_template}' to enable minimize/maximize buttons.")
                else:
                    self.set_error_banner(True, "❌ Runtime error detected — window locked until fixed.")
                self.lock_window()
            else:
                if data.strip():
                    self.output.insertPlainText("\n❌ ERROR: Error occurred\n")
        except Exception:
            pass

    # ---------- CONTROL ----------
    def stop_process(self):
        if self.process.state() == QProcess.Running:
            try:
                self.process.kill()
            except Exception:
                pass
            self.output.appendPlainText("\n⛔ Stopped.")
        # remove protections if any
        try:
            self._uninstall_system_key_block()
        except Exception:
            pass
        try:
            self._protect_run_active = False
        except Exception:
            pass

    def force_kill(self):
        if self.process.state() == QProcess.Running:
            try:
                self.process.kill()
            except Exception:
                pass
            self.output.appendPlainText("\n⏱ Time limit exceeded.")
        # remove protections
        try:
            self._uninstall_system_key_block()
        except Exception:
            pass
        try:
            self._protect_run_active = False
        except Exception:
            pass

    def finished(self):
        try:
            self.timer.stop()
            self.editor.setReadOnly(False)
            self.run_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.output.appendPlainText("\n✅ Finished.")

            try:
                if not self._pre_run_was_maximized:
                    self.showNormal()
            except Exception:
                pass

            if not self.runtime_error:
                if self.current_template:
                    # Only treat the template as "fixed" if this run was initiated
                    # by the IDE itself (prevents marking fixed via external runs).
                    if getattr(self, '_last_run_initiated_by_ide', False):
                        self.enable_min_max()
                        self.unlock_window()
                        self.set_error_banner(False, "")
                        # After successful run, clear template selection
                        self.current_template = None
                    else:
                        # If the run was not initiated by this IDE, do not unlock.
                        self.disable_min_max()
                        self.lock_window()
                        self.set_error_banner(True, "❌ Template run completed outside IDE permission — window remains locked.")
                    if not (self.group_timer_started and self.group_time_left_ms == 0):
                        self.set_program_actions_enabled(True)
                        self.set_file_actions_enabled(True)
                    self.output.appendPlainText(f"\n✅ Code fixed successfully! Minimize/maximize buttons enabled.")
                else:
                    self.enable_min_max()
                    self.unlock_window()
                    self.set_error_banner(False, "")
            else:
                self.disable_min_max()
                self.lock_window()
                if self.current_template:
                    self.set_error_banner(True, f"❌ Run ended with errors — Fix the code in '{self.current_template}' to enable minimize/maximize buttons.")
                else:
                    self.set_error_banner(True, "❌ Run ended with errors — window locked until fixed.")
        finally:
            if self.temp_file and os.path.exists(self.temp_file):
                try:
                    os.remove(self.temp_file)
                except Exception:
                    pass
                self.temp_file = None
            # remove any system-level protections we installed
            try:
                self._uninstall_system_key_block()
            except Exception:
                pass
            try:
                self._protect_run_active = False
            except Exception:
                pass
            # reset internal run marker
            try:
                self._last_run_initiated_by_ide = False
            except Exception:
                pass
            self._pre_run_was_maximized = False

    # ---------- PROGRAM TEMPLATES ----------
    def load_program_template(self, template_name):
        """
        Run the template code (briefly, with a short timeout) BEFORE showing it in the editor.
        If the code errors during that quick run, that's acceptable — we'll show minimal info, then load the template.
        """
        if template_name not in self.PROGRAM_TEMPLATES:
            QMessageBox.warning(self, "Error", f"Template '{template_name}' not found.")
            return

        # If a template is already loaded, prevent loading another one
        if self.current_template:
            QMessageBox.information(self, "Template Locked", "A template is already loaded. Fix it (run successfully) or clear it before loading another template.")
            return

        # If group timer expired, block loading
        if self.group_timer_started and self.group_time_left_ms == 0:
            QMessageBox.information(self, "Time Expired", "Template time expired — cannot load templates.")
            return

        # Stop any running process first
        if self.process.state() == QProcess.Running:
            try:
                self.process.kill()
            except Exception:
                pass
            self.timer.stop()
            self.editor.setReadOnly(False)
            self.run_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

        if self.temp_file and os.path.exists(self.temp_file):
            try:
                os.remove(self.temp_file)
            except Exception:
                pass
            self.temp_file = None

        # Ask user if they want to discard current content
        if self.editor.toPlainText().strip():
            resp = QMessageBox.question(
                self, "Load Template",
                f"Load '{template_name}' template? This will replace current code.",
                QMessageBox.Yes | QMessageBox.No
            )
            if resp != QMessageBox.Yes:
                return

        template_code = self.PROGRAM_TEMPLATES[template_name]

        # --- PRE-RUN: quick, non-interactive execution with timeout ---
        pre_run_result = None
        try:
            # Try compiling first (fast)
            compile(template_code, "<template>", "exec")
            # write to a temporary file for execution
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8") as tf:
                tf.write(template_code)
                tmp_path = tf.name
            # Run the template briefly with no input; timeout quickly to avoid blocking on input()
            try:
                # 2-second timeout for a quick smoke-run (adjustable)
                completed = subprocess.run([sys.executable, "-u", tmp_path],
                                           input=None,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           timeout=2,
                                           check=False,
                                           encoding="utf-8")
                # capture minimal info — do NOT show detailed tracebacks to user
                if completed.returncode != 0 or completed.stderr.strip():
                    pre_run_result = "error"
                else:
                    pre_run_result = "ok"
            except subprocess.TimeoutExpired:
                # If the script waits for input or runs longer, we kill it — that's acceptable
                pre_run_result = "timeout"
            except Exception:
                pre_run_result = "error"
            finally:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
        except Exception:
            # compilation failed — treat as error but continue to show template
            pre_run_result = "compile_error"

        # Show a small note in output about the pre-run (kept minimal)
        if pre_run_result == "ok":
            self.output.clear()
            self.output.appendPlainText("ℹ️ Template pre-run completed (no immediate errors).\n")
        elif pre_run_result in ("timeout", "error", "compile_error"):
            self.output.clear()
            self.output.appendPlainText("ℹ️ Template pre-run detected an issue (will load template for fixing).\n")

        # Now load the template into the editor (as requested: show after pre-run attempt)
        self.editor.setPlainText(template_code)
        self.editor.setReadOnly(False)

        self.current_template = template_name

        # (hash tracking removed for templates)

        # Disable min/max and prevent switching while template is selected
        self.disable_min_max()
        self.set_program_actions_enabled(False)
        self.set_file_actions_enabled(False)

        # Show banner and keep output as-is (pre-run messages remain)
        self.set_error_banner(True, f"📝 Template '{template_name}' loaded — Fix the code and run successfully to enable minimize/maximize buttons")

        # Reset runtime error state and start group timer (if not started) when a visible template is selected
        self.runtime_error = False
        self.user_input = ""
        if template_name in self.visible_template_keys:
            self.start_group_timer_if_needed()

    # ---------- FILE OPERATIONS & HELP ----------
    def new_file(self):
        # Prevent creating a new file while a template is active
        if self.current_template:
            QMessageBox.information(self, "Template Locked", "Cannot create a new file while a template is active. Fix the template (run successfully) or clear it first.")
            return

        if self.editor.toPlainText().strip():
            resp = QMessageBox.question(
                self, "New File", "Discard current contents and create a new file?",
                QMessageBox.Yes | QMessageBox.No
            )
            if resp != QMessageBox.Yes:
                return

        if self.process.state() == QProcess.Running:
            try:
                self.process.kill()
            except Exception:
                pass
            self.timer.stop()
            self.run_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

        if self.temp_file and os.path.exists(self.temp_file):
            try:
                os.remove(self.temp_file)
            except Exception:
                pass
            self.temp_file = None

        self.editor.clear()
        self.editor.setReadOnly(False)
        self.current_file = None
        self.current_template = None
        # template hash tracking removed
        if not (self.group_timer_started and self.group_time_left_ms == 0):
            self.set_program_actions_enabled(True)
            self.set_file_actions_enabled(True)
        self.setWindowTitle("Python Compiler of MNMJEC")
        self.output.clear()
        self.enable_min_max()
        self.set_error_banner(False, "")
        self.runtime_error = False
        self.user_input = ""

    def open_file(self):
        # Prevent opening another file while a template is active
        if self.current_template:
            QMessageBox.information(self, "Template Locked", "Cannot open a file while a template is active. Fix the template (run successfully) or clear it first.")
            return

        if self.group_timer_started and self.group_time_left_ms == 0:
            QMessageBox.information(self, "Time Expired", "Template time expired — cannot open files that would replace templates.")
            return

        path, _ = QFileDialog.getOpenFileName(self, "Open Python file", "", "Python Files (*.py);;All Files (*)")
        if path:
            try:
                if self.process.state() == QProcess.Running:
                    try:
                        self.process.kill()
                    except Exception:
                        pass
                    self.timer.stop()
                    self.run_btn.setEnabled(True)
                    self.stop_btn.setEnabled(False)

                if self.temp_file and os.path.exists(self.temp_file):
                    try:
                        os.remove(self.temp_file)
                    except Exception:
                        pass
                    self.temp_file = None

                with open(path, "r", encoding="utf-8") as f:
                    self.editor.setPlainText(f.read())
                self.editor.setReadOnly(False)
                self.current_file = path
                self.current_template = None
                # template hash tracking removed
                if not (self.group_timer_started and self.group_time_left_ms == 0):
                    self.set_program_actions_enabled(True)
                    self.set_file_actions_enabled(True)
                self.setWindowTitle(f"Python Compiler of MNMJEC - {os.path.basename(path)}")
                self.output.clear()
                self.enable_min_max()
                self.set_error_banner(False, "")
                self.runtime_error = False
                self.user_input = ""
            except Exception as e:
                QMessageBox.critical(self, "Open Error", f"Failed to open file:\n{e}")

    def save_file(self):
        if self.current_file:
            path = self.current_file
        else:
            path, _ = QFileDialog.getSaveFileName(self, "Save Python file", "", "Python Files (*.py);;All Files (*)")
            if not path:
                return
            self.current_file = path
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.editor.toPlainText())
            self.setWindowTitle(f"Python Compiler of MNMJEC - {os.path.basename(path)}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save file:\n{e}")

    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Python file as", "", "Python Files (*.py);;All Files (*)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.editor.toPlainText())
                self.current_file = path
                self.setWindowTitle(f"Python Compiler of MNMJEC - {os.path.basename(path)}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save file:\n{e}")

    def show_about(self):
        QMessageBox.information(self, "About", "Offline Python IDE — MNMJEC\nSimple offline code runner.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ide = OfflinePythonIDE()
    ide.show()
    sys.exit(app.exec_())
