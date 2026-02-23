import tkinter as tk
from tkinter import messagebox
import os
import subprocess

class BrickPi3Troubleshooter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BrickPi3 Troubleshooter")
        self.geometry("500x400")
        self.venv_info = os.environ.get("VENV_INFO", "Virtual environment info not available.")
        self.current_process = None
        self.create_widgets()
        # Set a minimum window size to fit 12 lines of the textbox
        self.update_idletasks()
        min_height = 12 * 20 + 260
        min_width = 800  # Wider window for long lines
        self.minsize(min_width, min_height)
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

    def create_widgets(self):
        # Use grid for better layout control
        self.grid_rowconfigure(8, weight=1)
        self.grid_columnconfigure(0, weight=1)
        row = 0
        tk.Label(self, text=self.venv_info, font=("Arial", 10), fg="blue").grid(row=row, column=0, sticky="w", padx=10, pady=2)
        row += 1
        tk.Label(self, text="BrickPi3 Troubleshooting", font=("Arial", 16)).grid(row=row, column=0, sticky="n", padx=10, pady=10)
        row += 1
        tk.Button(self, text="Check Python Version", command=self.check_python_version).grid(row=row, column=0, sticky="ew", padx=10, pady=2)
        row += 1
        tk.Button(self, text="Check brickpi3 Driver Installation", command=self.check_brickpi3).grid(row=row, column=0, sticky="ew", padx=10, pady=2)
        row += 1
        tk.Button(self, text="Read Hardware Info", command=self.read_info).grid(row=row, column=0, sticky="ew", padx=10, pady=2)
        row += 1
        tk.Button(self, text="Test Touch Sensors", command=self.run_touch_sensor).grid(row=row, column=0, sticky="ew", padx=10, pady=2)
        row += 1
        tk.Button(self, text="Run LEGO-Motors.py", command=self.run_lego_motors).grid(row=row, column=0, sticky="ew", padx=10, pady=2)
        row += 1
        self.feedback_text = tk.Text(self, height=12, width=80, wrap=tk.WORD, font=("Consolas", 10))
        self.feedback_text.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        self.feedback_text.config(height=12)
        self.feedback_text.bind("<Button-3>", self.show_context_menu)
        # Context menu for the feedback_text
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Select All", command=self.select_all_feedback_text)
        self.context_menu.add_command(label="Copy", command=self.copy_selected_text)
        self.context_menu.add_command(label="Copy All", command=self.copy_feedback_text)
        self.context_menu.add_command(label="Clear", command=self.clear_feedback_text)
        # Ensure the feedback_text expands, and the Exit button is always at the bottom right
        self.grid_rowconfigure(row, weight=1)
        row += 1
        exit_btn = tk.Button(self, text="Exit", command=self.on_exit)
        exit_btn.grid(row=row, column=0, sticky="e", padx=10, pady=10)
        self.grid_rowconfigure(row, weight=0)

    def kill_current_process(self):
        if self.current_process and self.current_process.poll() is None:
            try:
                self.current_process.terminate()
            except Exception:
                pass
        self.current_process = None
        self.feedback_text.delete(1.0, tk.END)

    def run_all_tests(self):
        self.kill_current_process()
        messagebox.showinfo("Run Tests", "Running all tests...\n(Implement test logic here)")

    def check_python_version(self):
        self.kill_current_process()
        import sys
        self.feedback_text.delete(1.0, tk.END)
        self.feedback_text.insert(tk.END, f"Python version: {sys.version}\n")

    def check_brickpi3(self):
        self.kill_current_process()
        self.feedback_text.delete(1.0, tk.END)
        try:
            import brickpi3
            brickpi3_path = getattr(brickpi3, '__file__', 'Path not available')
            version = getattr(brickpi3, '__version__', 'unknown')
            self.feedback_text.insert(tk.END, f"brickpi3 import successful!\n")
            self.feedback_text.insert(tk.END, f"Version: {version}\n")
            self.feedback_text.insert(tk.END, f"Library path: {brickpi3_path}\n")
        except Exception as e:
            self.feedback_text.insert(tk.END, f"Failed to import brickpi3:\n{e}\n")

    def read_info(self):
        self.kill_current_process()
        self.feedback_text.delete(1.0, tk.END)
        try:
            examples_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "examples", "Read_Info.py"))
            if not os.path.isfile(examples_path):
                self.feedback_text.insert(tk.END, "Read_Info.py not found in expected location: {}".format(examples_path))
                return
            result = subprocess.run([
                os.environ.get("PYTHON_EXECUTABLE", "python3"),
                examples_path
            ], capture_output=True, text=True, check=True)
            self.feedback_text.insert(tk.END, result.stdout)
            if result.stderr:
                self.feedback_text.insert(tk.END, "\n[stderr]\n" + result.stderr)
        except subprocess.CalledProcessError as e:
            self.feedback_text.insert(tk.END, f"Error running Read_Info.py:\n{e.output}\n{e.stderr}")
        except Exception as e:
            self.feedback_text.insert(tk.END, f"Unexpected error: {e}")

    def run_lego_motors(self):
        import threading
        import re
        self.kill_current_process()
        self.feedback_text.delete(1.0, tk.END)
        def stream_output():
            motors_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "examples", "LEGO-Motors.py"))
            if not os.path.isfile(motors_path):
                self.feedback_text.insert(tk.END, f"LEGO-Motors.py not found in expected location: {motors_path}")
                return
            self.current_process = subprocess.Popen([
                os.environ.get("PYTHON_EXECUTABLE", "python3"),
                "-u",
                motors_path
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            encoder_tag = "Encoder A:"
            encoder_line_index = None
            for line in self.current_process.stdout:
                if line.startswith(encoder_tag):
                    # Always overwrite the same line for Encoder A
                    if encoder_line_index is None:
                        # Insert a blank line and remember its index
                        self.feedback_text.insert(tk.END, "\n")
                        encoder_line_index = int(self.feedback_text.index(tk.END).split('.')[0]) - 1
                    self.feedback_text.delete(f"{encoder_line_index}.0", f"{encoder_line_index}.end")
                    self.feedback_text.insert(f"{encoder_line_index}.0", line.rstrip("\n"))
                else:
                    self.feedback_text.insert(tk.END, line)
                    self.feedback_text.see(tk.END)
            if self.current_process:
                self.current_process.stdout.close()
                self.current_process.wait()
                self.current_process = None
        threading.Thread(target=stream_output, daemon=True).start()

    def run_touch_sensor(self):
        import threading
        self.kill_current_process()
        self.feedback_text.delete(1.0, tk.END)
        def stream_output():
            touch_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "examples", "LEGO-Touch_Sensor.py"))
            if not os.path.isfile(touch_path):
                self.feedback_text.insert(tk.END, f"LEGO-Touch_Sensor.py not found in expected location: {touch_path}")
                return
            self.current_process = subprocess.Popen([
                os.environ.get("PYTHON_EXECUTABLE", "python3"),
                "-u",
                touch_path
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            instruction_line = None
            status_line_index = None
            for line in self.current_process.stdout:
                clean_line = line.rstrip('\r\n')
                if instruction_line is None:
                    # First line: print as instructions
                    self.feedback_text.insert(tk.END, clean_line + "\n")
                    instruction_line = True
                    continue
                if clean_line.strip() == "Press Ctrl+C to exit once done.":
                    continue  # Do not display this line in the GUI
                if clean_line.startswith("PORT_1:"):
                    if status_line_index is None:
                        self.feedback_text.insert(tk.END, "\n")
                        status_line_index = int(self.feedback_text.index(tk.END).split('.')[0]) - 1
                    self.feedback_text.delete(f"{status_line_index}.0", f"{status_line_index}.end")
                    self.feedback_text.insert(f"{status_line_index}.0", clean_line)
                else:
                    # Any other output after the first line, just append
                    self.feedback_text.insert(tk.END, clean_line + "\n")
                self.feedback_text.see(tk.END)
            if self.current_process:
                self.current_process.stdout.close()
                self.current_process.wait()
                self.current_process = None
        threading.Thread(target=stream_output, daemon=True).start()

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def copy_selected_text(self):
        try:
            selected = self.feedback_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(selected)
        except tk.TclError:
            # No text is selected, do nothing
            pass

    def copy_feedback_text(self):
        # First select all text using the same logic as select_all_feedback_text
        self.select_all_feedback_text()
        # Then copy the selected text
        selected = self.feedback_text.get(tk.SEL_FIRST, tk.SEL_LAST)
        self.clipboard_clear()
        self.clipboard_append(selected)

    def select_all_feedback_text(self):
        self.feedback_text.tag_add(tk.SEL, "1.0", tk.END)
        self.feedback_text.mark_set(tk.INSERT, "1.0")
        self.feedback_text.focus_set()

    def clear_feedback_text(self):
        self.feedback_text.delete(1.0, tk.END)

    def on_exit(self):
        self.kill_current_process()
        try:
            import brickpi3
            bp = brickpi3.BrickPi3()
            bp.reset_all()
        except Exception:
            pass
        self.destroy()

if __name__ == "__main__":
    app = BrickPi3Troubleshooter()
    app.mainloop()
