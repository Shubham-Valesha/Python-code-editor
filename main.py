import tkinter as tk
from tkinter import filedialog, simpledialog
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.styles import get_style_by_name
from pygments.token import Token

# Create the main window
root = tk.Tk()
root.title("My Code Editor")
root.geometry("800x600")

# Create a frame to hold line numbers and the text area
frame = tk.Frame(root)
frame.pack(expand=1, fill="both")

# Line numbers canvas
line_numbers = tk.Canvas(frame, width=40, bg="#f0f0f0")
line_numbers.pack(side="left", fill="y")

# Create the text area with undo functionality
text_area = tk.Text(frame, wrap="word", font=("Consolas", 12), undo=True, bg="#ffffff", fg="#000000")
text_area.pack(side="right", expand=1, fill="both")

# Define file operations
def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, 'r') as file:
            text_area.delete(1.0, tk.END)
            text_area.insert(1.0, file.read())

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, 'w') as file:
            file.write(text_area.get(1.0, tk.END))

# Update line numbers dynamically
def update_line_numbers(event=None):
    line_numbers.delete("all")
    i = text_area.index("@0,0")
    while True:
        dline = text_area.dlineinfo(i)
        if dline is None:
            break
        y = dline[1]
        line_number = str(i).split(".")[0]
        line_numbers.create_text(2, y, anchor="nw", text=line_number, font=("Consolas", 10))
        i = text_area.index(f"{i}+1line")

# Syntax highlighting
def apply_syntax_highlighting(event=None):
    text = text_area.get("1.0", "end-1c")
    tokens = lex(text, PythonLexer())
    text_area.tag_remove("Token", "1.0", "end")
    for token_type, value in tokens:
        start = text_area.search(value, "1.0", stopindex="end", nocase=False)
        if start:
            end = f"{start}+{len(value)}c"
            text_area.tag_add(str(token_type), start, end)
            text_area.tag_config(str(token_type), foreground="#ff5733" if str(token_type) == "Token.Keyword" else "#000000")

# Undo/Redo functionality
def undo_action():
    try:
        text_area.edit_undo()
    except tk.TclError:
        pass

def redo_action():
    try:
        text_area.edit_redo()
    except tk.TclError:
        pass

# Theme toggling
def toggle_theme():
    if theme_var.get() == "Dark":
        text_area.config(bg="#2e2e2e", fg="#d3d3d3", insertbackground="#d3d3d3")
        line_numbers.config(bg="#2e2e2e", fg="#d3d3d3")
    else:
        text_area.config(bg="#ffffff", fg="#000000", insertbackground="#000000")
        line_numbers.config(bg="#f0f0f0", fg="#000000")

# Font customization
def set_font():
    font_family = simpledialog.askstring("Font", "Enter Font Family (e.g., Consolas):", initialvalue="Consolas")
    font_size = simpledialog.askinteger("Font Size", "Enter Font Size:", initialvalue=12)
    if font_family and font_size:
        text_area.config(font=(font_family, font_size))
        line_numbers.config(font=(font_family, font_size))

# Create the menu bar
menu = tk.Menu(root)
root.config(menu=menu)

# File menu
file_menu = tk.Menu(menu, tearoff=0)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu.add_cascade(label="File", menu=file_menu)

# Edit menu
edit_menu = tk.Menu(menu, tearoff=0)
edit_menu.add_command(label="Undo", command=undo_action)
edit_menu.add_command(label="Redo", command=redo_action)
menu.add_cascade(label="Edit", menu=edit_menu)

# Theme menu
theme_var = tk.StringVar(value="Light")
theme_menu = tk.Menu(menu, tearoff=0)
theme_menu.add_radiobutton(label="Light", variable=theme_var, value="Light", command=toggle_theme)
theme_menu.add_radiobutton(label="Dark", variable=theme_var, value="Dark", command=toggle_theme)
menu.add_cascade(label="Theme", menu=theme_menu)

# Font menu
font_menu = tk.Menu(menu, tearoff=0)
font_menu.add_command(label="Set Font", command=set_font)
menu.add_cascade(label="Font", menu=font_menu)

# Bindings
text_area.bind("<KeyRelease>", lambda event: (update_line_numbers(), apply_syntax_highlighting()))

def find_text():
    """Open a dialog to find text in the editor."""
    search_term = simpledialog.askstring("Find", "Enter text to search:")
    if search_term:
        text_area.tag_remove("highlight", "1.0", "end")
        start = "1.0"
        while True:
            start = text_area.search(search_term, start, stopindex="end")
            if not start:
                break
            end = f"{start}+{len(search_term)}c"
            text_area.tag_add("highlight", start, end)
            start = end
        text_area.tag_config("highlight", background="yellow", foreground="black")

def replace_text():
    """Open a dialog to replace text in the editor."""
    search_term = simpledialog.askstring("Find", "Enter text to replace:")
    replacement = simpledialog.askstring("Replace", "Enter replacement text:")
    if search_term and replacement:
        content = text_area.get("1.0", "end-1c")
        new_content = content.replace(search_term, replacement)
        text_area.delete("1.0", "end")
        text_area.insert("1.0", new_content)
    
edit_menu.add_separator()
edit_menu.add_command(label="Find", command=find_text)
edit_menu.add_command(label="Replace", command=replace_text)

import os

def auto_save():
    """Automatically save the file at regular intervals."""
    temp_file = os.path.join(os.getcwd(), "autosave.txt")
    with open(temp_file, "w") as file:
        file.write(text_area.get("1.0", "end-1c"))
    root.after(30000, auto_save)  # Save every 30 seconds

auto_save()

def update_status_bar(event=None):
    """Update the word and character count."""
    content = text_area.get("1.0", "end-1c")
    words = len(content.split())
    chars = len(content)
    status_bar.config(text=f"Words: {words} | Characters: {chars}")

# Add a status bar
status_bar = tk.Label(root, text="Words: 0 | Characters: 0", anchor="e")
status_bar.pack(fill="x", side="bottom")

# Bind the update function to key events
text_area.bind("<KeyRelease>", lambda event: (update_line_numbers(), apply_syntax_highlighting(), update_status_bar()))


# Run the application
root.mainloop()