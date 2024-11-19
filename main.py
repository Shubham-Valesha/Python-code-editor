import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
from pygments import lex
from pygments.lexers import PythonLexer
import subprocess
import os
import importlib.util

# Initialize the main window
root = tk.Tk()
root.title("Advanced Code Editor")
root.geometry("1000x700")

# Notebook for tabs
notebook = ttk.Notebook(root)
notebook.pack(expand=1, fill="both")

# Console output frame
console_frame = tk.Frame(root)
console_frame.pack(fill="x", side="bottom")
console_output = tk.Text(console_frame, height=10, bg="#1e1e1e", fg="#d3d3d3", wrap="word", state="disabled")
console_output.pack(fill="x", side="bottom")

# Functions for Tabs and Text Widgets
def add_tab(filename="Untitled"):
    """Add a new tab with a text area."""
    tab = tk.Frame(notebook)
    notebook.add(tab, text=filename)
    text_widget = tk.Text(tab, wrap="word", font=("Consolas", 12), undo=True, bg="#ffffff", fg="#000000")
    text_widget.pack(expand=1, fill="both")
    notebook.select(tab)
    return text_widget
    

def get_current_text_widget():
    """Get the currently active text widget."""
    current_tab = notebook.nametowidget(notebook.select())
    return current_tab.winfo_children()[0]

# Initialize with a default tab
text_area = add_tab()

# File Operations
def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("Python files", "*.py"), ("All files", "*.*")])
    if file_path:
        with open(file_path, 'r') as file:
            text_widget = add_tab(file_path.split("/")[-1])
            text_widget.delete(1.0, tk.END)
            text_widget.insert(1.0, file.read())

def save_file():
    current_text_widget = get_current_text_widget()
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("Python files", "*.py"), ("All files", "*.*")])
    if file_path:
        with open(file_path, 'w') as file:
            file.write(current_text_widget.get(1.0, tk.END))
        notebook.tab(notebook.select(), text=file_path.split("/")[-1])

def auto_save():
    """Automatically save the file at regular intervals."""
    temp_file = os.path.join(os.getcwd(), "autosave.txt")
    with open(temp_file, "w") as file:
        file.write(get_current_text_widget().get(1.0, "end-1c"))
    root.after(30000, auto_save)

# Search and Replace
def find_text():
    search_term = simpledialog.askstring("Find", "Enter text to search:")
    if search_term:
        text_widget = get_current_text_widget()
        text_widget.tag_remove("highlight", "1.0", "end")
        start = "1.0"
        while True:
            start = text_widget.search(search_term, start, stopindex="end")
            if not start:
                break
            end = f"{start}+{len(search_term)}c"
            text_widget.tag_add("highlight", start, end)
            start = end
        text_widget.tag_config("highlight", background="yellow", foreground="black")

def replace_text():
    search_term = simpledialog.askstring("Find", "Enter text to replace:")
    replacement = simpledialog.askstring("Replace", "Enter replacement text:")
    if search_term and replacement:
        text_widget = get_current_text_widget()
        content = text_widget.get("1.0", "end-1c")
        new_content = content.replace(search_term, replacement)
        text_widget.delete("1.0", "end")
        text_widget.insert("1.0", new_content)

# Run Code
def run_code():
    """Execute the Python code in the current tab."""
    code = get_current_text_widget().get(1.0, "end-1c")
    python_command = "python"  # Default command

    # Check if `python3` is needed instead of `python`
    try:
        subprocess.run([python_command, "--version"], capture_output=True, text=True)
    except FileNotFoundError:
        python_command = "python3"

    # Run the code
    try:
        result = subprocess.run([python_command, "-c", code], capture_output=True, text=True)
        console_output.config(state="normal")
        console_output.delete(1.0, tk.END)
        console_output.insert(tk.END, result.stdout if result.returncode == 0 else result.stderr)
        console_output.config(state="disabled")
    except Exception as e:
        console_output.config(state="normal")
        console_output.insert(tk.END, f"Error: {e}")
        console_output.config(state="disabled")

# Auto Indentation
def auto_indent(event=None):
    """Automatically indent the next line."""
    text_widget = get_current_text_widget()
    current_line = text_widget.get("insert linestart", "insert")
    indent = len(current_line) - len(current_line.lstrip())
    text_widget.insert("insert", "\n" + " " * indent)
    return "break"

text_area.bind("<Return>", auto_indent)

# Plugins Support
def load_plugin(plugin_path):
    """Load a Python plugin dynamically."""
    spec = importlib.util.spec_from_file_location("plugin", plugin_path)
    plugin = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(plugin)
    plugin.add_to_editor(root, notebook, get_current_text_widget(), console_output)

def load_plugins():
    """Open file dialog to select a plugin."""
    plugin_path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
    if plugin_path:
        load_plugin(plugin_path)

# Menu Setup
menu = tk.Menu(root)
root.config(menu=menu)

file_menu = tk.Menu(menu, tearoff=0)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu.add_cascade(label="File", menu=file_menu)

edit_menu = tk.Menu(menu, tearoff=0)
edit_menu.add_command(label="Find", command=find_text)
edit_menu.add_command(label="Replace", command=replace_text)
menu.add_cascade(label="Edit", menu=edit_menu)

run_menu = tk.Menu(menu, tearoff=0)
run_menu.add_command(label="Run", command=run_code)
menu.add_cascade(label="Run", menu=run_menu)

plugin_menu = tk.Menu(menu, tearoff=0)
plugin_menu.add_command(label="Load Plugin", command=load_plugins)
menu.add_cascade(label="Plugins", menu=plugin_menu)

# Initialize autosave
auto_save()

# Run the main application
root.mainloop()

