#!/usr/bin/env python3
import sys
import os
import tempfile

from PyQt5.QtWidgets import (
    QApplication, QWidget, QPlainTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QInputDialog,
    QMenuBar, QAction, QFileDialog
)
from PyQt5.QtCore import Qt, QProcess, QTimer
from PyQt5.QtGui import QTextCursor


class OfflinePythonIDE(QWidget):
    HARD_TIMEOUT_MS = 15 * 60 * 1000

    # Template codes for each program
    PROGRAM_TEMPLATES = {
        "prog1": """# Program 1: Basic Input/Output and Arithmetic Operations
# Task: Read two numbers and perform basic operations
# Fix any errors to enable minimize/maximize buttons

# Read two numbers from input
num1 = int(input("Enter first number: "))
num2 = int(input("Enter second number: "))

# Perform operations
sum_result = num1 + num2
difference = num1 - num2
product = num1 * num2

# Display results
print(f"Sum: {sum_result}")
print(f"Difference: {difference}")
print(f"Product: {product}")

# Calculate and display quotient (handle division by zero)
if num2 != 0:
    quotient = num1 / num2
    print(f"Quotient: {quotient}")
else:
    print("Cannot divide by zero!")
""",
        "prog2": """# Program 2: List/Array Operations
# Task: Work with lists - add, remove, and process elements
# Fix any errors to enable minimize/maximize buttons

# Initialize a list
numbers = []

# Add elements to the list
n = int(input("How many numbers do you want to add? "))
for i in range(n):
    num = int(input(f"Enter number {i+1}: "))
    numbers.append(num)

# Display the list
print(f"Original list: {numbers}")

# Find sum and average
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
# Task: Process strings - reverse, count, and analyze
# Fix any errors to enable minimize/maximize buttons

# Get input string
text = input("Enter a string: ")

# String operations
print(f"Original string: {text}")
print(f"Length: {len(text)}")
print(f"Uppercase: {text.upper()}")
print(f"Lowercase: {text.lower()}")

# Count vowels
vowels = "aeiouAEIOU"
vowel_count = sum(1 for char in text if char in vowels)
print(f"Number of vowels: {vowel_count}")

# Reverse the string
reversed_text = text[::-1]
print(f"Reversed: {reversed_text}")

# Check if palindrome
if text.lower().replace(" ", "") == reversed_text.lower().replace(" ", ""):
    print("The string is a palindrome!")
else:
    print("The string is not a palindrome.")
""",
        "prog4": """# Program 4: Mathematical Computations
# Task: Perform mathematical calculations - factorial, prime check, etc.
# Fix any errors to enable minimize/maximize buttons

# Function to calculate factorial
def factorial(n):
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

# Function to check if number is prime
def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(num ** 0.5) + 1):
        if num % i == 0:
            return False
    return True

# Main program
num = int(input("Enter a number: "))

# Calculate factorial
if num >= 0:
    fact = factorial(num)
    print(f"Factorial of {num} is: {fact}")
else:
    print("Factorial is not defined for negative numbers!")

# Check if prime
if is_prime(num):
    print(f"{num} is a prime number.")
else:
    print(f"{num} is not a prime number.")

# Calculate square and cube
print(f"Square: {num ** 2}")
print(f"Cube: {num ** 3}")
""",
        "prog5": """# Program 5: Control Structures and Problem Solving
# Task: Use loops and conditionals to solve a problem
# Fix any errors to enable minimize/maximize buttons

# Program to find all numbers in a range that are divisible by specific numbers
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

# Find numbers divisible by both
print(f"\\nNumbers divisible by both {divisor1} and {divisor2}:")
both_count = 0
for num in range(start, end + 1):
    if num % divisor1 == 0 and num % divisor2 == 0:
        print(num, end=" ")
        both_count += 1

print(f"\\n\\nTotal count: {both_count}")
"""
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Compiler of MNMJEC")
        self.setGeometry(150, 80, 1100, 720)

        # ---------- UI ----------
        title = QLabel("Python Compiler of MNMJEC")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color:#0b1220;font-size:20px;font-weight:700;")

        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Write Python code here…")
        self.editor.setStyleSheet("""
            background:#001f3f;  /* navy blue */
            color:#ffd700;       /* golden yellow text */
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
            background:#071733;  /* darker blue */
            color:#ffd700;       /* golden yellow text */
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

        # Lock-on-error is mandatory: window will be locked on error (min/max disabled)

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

        layout = QVBoxLayout(self)

        # ---------- MENU BAR ----------
        self.menu_bar = QMenuBar(self)

        # File menu
        file_menu = self.menu_bar.addMenu("File")
        new_act = QAction("New", self)
        new_act.setShortcut("Ctrl+N")
        new_act.triggered.connect(self.new_file)
        open_act = QAction("Open...", self)
        open_act.setShortcut("Ctrl+O")
        open_act.triggered.connect(self.open_file)
        save_act = QAction("Save", self)
        save_act.setShortcut("Ctrl+S")
        save_act.triggered.connect(self.save_file)
        save_as_act = QAction("Save As...", self)
        save_as_act.triggered.connect(self.save_file_as)
        exit_act = QAction("Exit", self)
        exit_act.triggered.connect(self.close)
        for act in (new_act, open_act, save_act, save_as_act, exit_act):
            file_menu.addAction(act)

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

        # Programs menu
        programs_menu = self.menu_bar.addMenu("Programs")
        prog1_act = QAction("Prog 1", self)
        prog1_act.triggered.connect(lambda: self.load_program_template("prog1"))
        prog2_act = QAction("Prog 2", self)
        prog2_act.triggered.connect(lambda: self.load_program_template("prog2"))
        prog3_act = QAction("Prog 3", self)
        prog3_act.triggered.connect(lambda: self.load_program_template("prog3"))
        prog4_act = QAction("Prog 4", self)
        prog4_act.triggered.connect(lambda: self.load_program_template("prog4"))
        prog5_act = QAction("Prog 5", self)
        prog5_act.triggered.connect(lambda: self.load_program_template("prog5"))
        for act in (prog1_act, prog2_act, prog3_act, prog4_act, prog5_act):
            programs_menu.addAction(act)

        # Keep a reference to program actions so we can enable/disable them
        self.prog_actions = [prog1_act, prog2_act, prog3_act, prog4_act, prog5_act]

        # Help menu
        help_menu = self.menu_bar.addMenu("Help")
        about_act = QAction("About", self)
        about_act.triggered.connect(self.show_about)
        help_menu.addAction(about_act)

        layout.setMenuBar(self.menu_bar)

        layout.addWidget(title)
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

        self.temp_file = None
        self.user_input = ""
        self.current_file = None
        # Track whether the last or current run has produced a runtime error
        self.runtime_error = False
        # Track if a program template is currently loaded
        self.current_template = None

    # ---------- Helpers ----------
    def set_program_actions_enabled(self, enabled: bool):
        """Enable or disable all program-template actions in the Programs menu."""
        try:
            for act in getattr(self, "prog_actions", []):
                act.setEnabled(enabled)
        except Exception:
            pass

    # ---------- WINDOW LOCK ----------
    def lock_window(self):
        """Keep the window on top and ensure close button remains available."""
        try:
            # Toggle only the flags we need; preserve other flags.
            self.setWindowFlag(Qt.WindowCloseButtonHint, True)
            self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
            # Bring to front
            self.raise_()
            self.activateWindow()
            self.show()
        except Exception:
            pass

    def unlock_window(self):
        """Remove 'stay on top' but preserve other decorations."""
        try:
            self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
            self.show()
        except Exception:
            pass

    # ---------- MIN / MAX CONTROL ----------
    def disable_min_max(self):
        """Remove minimize and maximize buttons from the window (robust toggle)."""
        try:
            # Use setWindowFlag to avoid replacing other flags accidentally.
            self.setWindowFlag(Qt.WindowMinimizeButtonHint, False)
            self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
            self.show()
        except Exception:
            # don't crash UI if platform doesn't support these ops
            pass

    def enable_min_max(self):
        """Restore minimize and maximize buttons on the window."""
        try:
            self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
            self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
            self.show()
        except Exception:
            pass

    # ---------- ERROR BANNER ----------
    def set_error_banner(self, show: bool, text: str = ""):
        """Show or hide a prominent error banner at the top of the UI."""
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
            # Return a generic message only; detailed traceback is intentionally suppressed
            return "Error occurred"

    # ---------- RUN ----------
    def run_code(self):
        code = self.editor.toPlainText().strip()
        if not code:
            QMessageBox.warning(self, "No Code", "Please write some Python code.")
            return

        error = self.has_syntax_error(code)
        if error:
            self.output.clear()
            self.output.appendPlainText("❌ ERROR DETECTED\n")
            # Show only a simple message to the user; do not display traceback details
            self.output.appendPlainText("Error occurred\n")
            # mark error state and disable min/max so user cannot minimize/maximize until fixed
            self.runtime_error = True
            self.disable_min_max()
            # show banner and lock window (mandatory)
            if self.current_template:
                self.set_error_banner(True, f"❌ Error detected — Fix the code in '{self.current_template}' and run successfully...")
            else:
                self.set_error_banner(True, "❌ Error detected — fix code and run to unlock your potential")
            self.lock_window()
            return

        # starting a fresh run: clear runtime error state and disable min/max while running
        self.runtime_error = False
        self.disable_min_max()
        self.set_error_banner(False, "")

        self.user_input = ""
        if self.code_needs_input(code):
            text, ok = QInputDialog.getMultiLineText(
                self, "Program Input", "Enter input:"
            )
            if not ok:
                return
            self.user_input = text + "\n"

        header = "import sys\nsys.setrecursionlimit(10**7)\n"
        code = header + code

        # Save to a temp file so we can run it
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8") as f:
                f.write(code)
                self.temp_file = f.name
        except Exception as e:
            QMessageBox.critical(self, "Temp File Error", f"Failed to write temp file:\n{e}")
            # Ensure UI is reset
            self.enable_min_max()
            return

        self.output.clear()
        self.output.appendPlainText("▶ Running...\n")

        self.editor.setReadOnly(True)
        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        # Start process
        try:
            self.process.start(sys.executable, ["-u", self.temp_file])
            # Quick check: if process fails to start shortly, notify user
            if not self.process.waitForStarted(1000):
                self.output.appendPlainText("\n❌ Failed to start process.\n")
                self.stop_btn.setEnabled(False)
                self.run_btn.setEnabled(True)
                self.editor.setReadOnly(False)
                # keep min/max disabled due to run not completing; leave banner if needed
                return
        except Exception:
            # If starting fails for any reason, restore UI state
            self.output.appendPlainText("\n❌ Failed to start process.\n")
            self.stop_btn.setEnabled(False)
            self.run_btn.setEnabled(True)
            self.editor.setReadOnly(False)
            return

        # Send input if any (only if process is running)
        if self.user_input and self.process.state() == QProcess.Running:
            try:
                self.process.write(self.user_input.encode())
                self.process.closeWriteChannel()
            except Exception:
                # ignore write errors to avoid crashing UI
                pass

        self.timer.start(self.HARD_TIMEOUT_MS)

    # ---------- OUTPUT ----------
    def read_stdout(self):
        try:
            text = bytes(self.process.readAllStandardOutput()).decode(errors="replace")
            self.output.insertPlainText(text)
            # auto-scroll to the end
            cursor = self.output.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.output.setTextCursor(cursor)
        except Exception:
            pass

    def read_stderr(self):
        try:
            data = bytes(self.process.readAllStandardError()).decode(errors="replace")
            # On first runtime error detected during execution, mark state and lock UI controls
            if data.strip() and not self.runtime_error:
                self.runtime_error = True
                # Do not display detailed stderr; show only a generic message to the user.
                self.output.insertPlainText("\n❌ ERROR: Error occurred\n")
                self.disable_min_max()
                # show a banner and lock the window (mandatory)
                if self.current_template:
                    self.set_error_banner(True, f"❌ Runtime error detected — Fix the code in '{self.current_template}' to run sucessfully....")
                else:
                    self.set_error_banner(True, "❌ Runtime error detected — window locked until fixed.")
                self.lock_window()
            else:
                # For any subsequent stderr, still append a minimal message to console
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
            # ensure UI is updated after stop is handled by finished() slot

    def force_kill(self):
        if self.process.state() == QProcess.Running:
            try:
                self.process.kill()
            except Exception:
                pass
            self.output.appendPlainText("\n⏱ Time limit exceeded.")

    def finished(self):
        try:
            self.timer.stop()
            self.editor.setReadOnly(False)
            self.run_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.output.appendPlainText("\n✅ Finished.")

            # Restore window controls only if the run did not produce runtime errors
            if not self.runtime_error:
                # If a template was loaded and code ran successfully, re-enable min/max
                if self.current_template:
                    self.enable_min_max()
                    self.unlock_window()
                    self.set_error_banner(False, "")
                    self.current_template = None  # Clear template tracking after successful run
                    # Re-enable program actions because template is now fixed/cleared
                    self.set_program_actions_enabled(True)
                    self.output.appendPlainText(f"\n✅ Code fixed successfully! Congratulation friend! See you later....")
                else:
                    self.enable_min_max()
                    self.unlock_window()
                    self.set_error_banner(False, "")
            else:
                # keep min/max disabled and show banner; lock window (mandatory)
                self.disable_min_max()
                self.lock_window()
                # Keep program actions disabled while template remains selected (error state)
                if self.current_template:
                    self.set_error_banner(True, f"❌ Run ended with errors — Fix the code in '{self.current_template}' to run successfully...")
                else:
                    self.set_error_banner(True, "❌ Run ended with errors — window locked until fixed.")
        finally:
            # Clean up the temp file
            if self.temp_file and os.path.exists(self.temp_file):
                try:
                    os.remove(self.temp_file)
                except Exception:
                    pass
                self.temp_file = None

    # ---------- PROGRAM TEMPLATES ----------
    def load_program_template(self, template_name):
        """Load a program template into the editor and disable min/max buttons."""
        if template_name not in self.PROGRAM_TEMPLATES:
            QMessageBox.warning(self, "Error", f"Template '{template_name}' not found.")
            return

        # If a template is already selected, prevent loading another one
        if self.current_template:
            QMessageBox.information(self, "Template Locked", "A template is already loaded. Fix it (run successfully) or clear it before loading another template.")
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

        # Clean up temp file if exists
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

        # Load the template code into editor (editable mode)
        template_code = self.PROGRAM_TEMPLATES[template_name]
        self.editor.setPlainText(template_code)
        self.editor.setReadOnly(False)  # Ensure editor is editable

        # Set current template
        self.current_template = template_name

        # Disable minimize and maximize buttons
        self.disable_min_max()

        # Disable other template actions to prevent switching while a template is selected
        self.set_program_actions_enabled(False)

        # Show message banner
        self.set_error_banner(
            True,
            f"📝 Template '{template_name}' loaded — Fix the code and run successfully"
        )

        # Clear output completely - make it clean and neat
        self.output.clear()

        # Reset runtime error state
        self.runtime_error = False
        self.user_input = ""

    # ---------- FILE OPERATIONS & HELP ----------
    def new_file(self):
        if self.editor.toPlainText().strip():
            resp = QMessageBox.question(
                self, "New File", "Discard current contents and create a new file?",
                QMessageBox.Yes | QMessageBox.No
            )
            if resp != QMessageBox.Yes:
                return

        # Stop any running process first
        if self.process.state() == QProcess.Running:
            try:
                self.process.kill()
            except Exception:
                pass
            self.timer.stop()
            self.run_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

        # Clean up temp file if exists
        if self.temp_file and os.path.exists(self.temp_file):
            try:
                os.remove(self.temp_file)
            except Exception:
                pass
            self.temp_file = None

        self.editor.clear()
        self.editor.setReadOnly(False)
        self.current_file = None
        # Clear template tracking
        self.current_template = None
        # Re-enable program actions because template (if any) is now cleared
        self.set_program_actions_enabled(True)
        self.setWindowTitle("Python Compiler of MNMJEC")
        # Clear output completely - make it clean and neat
        self.output.clear()
        # Re-enable min/max buttons when creating new file
        self.enable_min_max()
        self.set_error_banner(False, "")
        self.runtime_error = False
        self.user_input = ""

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Python file", "", "Python Files (*.py);;All Files (*)")
        if path:
            try:
                # Stop any running process first
                if self.process.state() == QProcess.Running:
                    try:
                        self.process.kill()
                    except Exception:
                        pass
                    self.timer.stop()
                    self.run_btn.setEnabled(True)
                    self.stop_btn.setEnabled(False)

                # Clean up temp file if exists
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
                # Clear template tracking when opening external file
                self.current_template = None
                # Re-enable program actions because template (if any) is now cleared
                self.set_program_actions_enabled(True)
                self.setWindowTitle(f"Python Compiler of MNMJEC - {os.path.basename(path)}")
                # Clear output completely - make it clean and neat
                self.output.clear()
                # Re-enable min/max buttons
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