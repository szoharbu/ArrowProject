import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from extract_db import extract, get_unique_values, return_last_modified_date
import yaml

# Create Main Window
root = tk.Tk()
root.title("Instruction Query Explorer")
root.geometry("1000x600")  # Adjusted window size

# 🔹 **Create Sidebar (Left Panel)**
sidebar = tk.Frame(root, width=250, padx=10, pady=10)
sidebar.pack(side=tk.LEFT, fill=tk.Y)

# 🔹 **Create Main Content (Right Panel)**
main_content = tk.Frame(root, padx=10, pady=10)
main_content.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

# ✅ **Project Selection**
tk.Label(sidebar, text="📂 Select Project:").pack(anchor="w")
selected_project = tk.StringVar()
project_dropdown = ttk.Combobox(sidebar, textvariable=selected_project, values=["Olympus", "Rigel"])
project_dropdown.pack(fill=tk.X)
project_dropdown.current(0)  # Default selection

# ✅ **Query Input**
tk.Label(sidebar, text="🔍 Query:").pack(anchor="w")
query_input = scrolledtext.ScrolledText(sidebar, height=4, width=30)
query_input.pack(fill=tk.X)

# ✅ **Dropdowns for Filters**
tk.Label(sidebar, text="⚙️ Mnemonic:").pack(anchor="w")
mnemonic_input = tk.Entry(sidebar)
mnemonic_input.pack(fill=tk.X)

tk.Label(sidebar, text="⚙️ Source Type:").pack(anchor="w")
src_type = ttk.Combobox(sidebar, values=get_unique_values("src1_type"))
src_type.pack(fill=tk.X)

tk.Label(sidebar, text="⚙️ Source Size:").pack(anchor="w")
src_size = ttk.Combobox(sidebar, values=["", "8-bit", "16-bit", "32-bit", "64-bit", "128-bit"])
src_size.pack(fill=tk.X)

tk.Label(sidebar, text="⚙️ Destination Type:").pack(anchor="w")
dest_type = ttk.Combobox(sidebar, values=get_unique_values("dest1_type"))
dest_type.pack(fill=tk.X)

tk.Label(sidebar, text="⚙️ Destination Size:").pack(anchor="w")
dest_size = ttk.Combobox(sidebar, values=["", "8-bit", "16-bit", "32-bit", "64-bit", "128-bit"])
dest_size.pack(fill=tk.X)

tk.Label(sidebar, text="⚙️ Steering Class:").pack(anchor="w")
steering_class = ttk.Combobox(sidebar, values=get_unique_values("steering_class"))
steering_class.pack(fill=tk.X)

tk.Label(sidebar, text="⚙️ Max Latency:").pack(anchor="w")
max_latency_options = get_unique_values("max_latency")
max_latency_options.insert(0, "")  # Add an empty option
max_latency = ttk.Combobox(sidebar, values=max_latency_options)
max_latency.pack(fill=tk.X)

# ✅ Toggle View Button (Table 🆚 Text)
is_table_view = tk.BooleanVar(value=True)  # Default: Table View


def toggle_view():
    """Switch between Table View and Big Text Box."""
    if is_table_view.get():
        text_box.pack_forget()
        results_table.pack(expand=True, fill="both")
        toggle_btn.config(text="🔄 Switch to Text View")
    else:
        results_table.pack_forget()
        text_box.pack(expand=True, fill="both")
        toggle_btn.config(text="🔄 Switch to Table View")
    is_table_view.set(not is_table_view.get())


toggle_btn = tk.Button(sidebar, text="🔄 Switch to Text View", command=toggle_view)
toggle_btn.pack(fill=tk.X, pady=5)

# ✅ **Treeview Table for Results**
columns = ("ID", "Mnemonic", "Description", "Syntax", "Latency", "Steering Class")
results_table = ttk.Treeview(main_content, columns=columns, show="headings")

# Define Column Headers
for col in columns:
    results_table.heading(col, text=col, anchor="w")  # Column Titles
    results_table.column(col, width=150, anchor="w")  # Column Width

# Scrollbars for the Table
scroll_y = ttk.Scrollbar(main_content, orient="vertical", command=results_table.yview)
results_table.configure(yscroll=scroll_y.set)

scroll_y.pack(side="right", fill="y")
results_table.pack(expand=True, fill="both")  # Default view is Table

# ✅ **Big Text Box for Alternative View**
text_box = tk.Text(main_content, height=20, width=80)
text_box.pack_forget()  # Initially hidden, Table View is default


# ✅ **Run Query Button**
def run_query():
    project = selected_project.get()
    query = query_input.get("1.0", tk.END).strip()

    if not project:
        messagebox.showerror("Error", "Please select a project!")
        return

    # Run extract() function (same as Streamlit)
    instructions = extract(
        project,
        instr_query=query if query else None,
        mnemonic=mnemonic_input.get().strip() or None,
        src_size=src_size.get().split('-')[0] or None,  # Remove "-bit"
        src_type=src_type.get() or None,
        dest_size=dest_size.get().split('-')[0] or None,  # Remove "-bit"
        dest_type=dest_type.get() or None,
        steering_classes=[steering_class.get()] if steering_class.get() else None,
        max_latency=int(max_latency.get()) if max_latency.get() else None
    )

    # Clear previous results
    results_table.delete(*results_table.get_children())
    text_box.delete("1.0", tk.END)

    # Populate Results in Both Views
    if instructions:
        for inst in instructions:
            results_table.insert("", "end", values=(
                inst.id, inst.mnemonic, inst.description, inst.syntax, inst.max_latency, inst.steering_class
            ))

            # Append results to Text Box View
            text_box.insert(tk.END, f"\n🔹 ID: {inst.id}\nMnemonic: {inst.mnemonic}\n")
            text_box.insert(tk.END, f"Description: {inst.description}\nSyntax: {inst.syntax}\n")
            text_box.insert(tk.END, f"Latency: {inst.max_latency}, Steering Class: {inst.steering_class}\n")
            text_box.insert(tk.END, "-" * 50 + "\n")


tk.Button(sidebar, text="🔄 Run Query", command=run_query, bg="green", fg="white").pack(fill=tk.X, pady=5)


# ✅ **YAML Download Buttons**
def save_yaml(filename, data):
    file_path = filedialog.asksaveasfilename(initialfile="arm_isadb.yml", defaultextension=".yml", filetypes=[("YAML Files", "*.yaml")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        #
        # with open(file_path, "w", encoding="utf-8") as f:
        #     yaml.dump(data, f, indent=4)
        messagebox.showinfo("Success", f"File saved as {file_path}")

def download_yaml():
    # Read the YAML file
    arm_asl_instructions_yaml_path = "C:/Users/zbuchris/PycharmProjects/ArrowProject/Externals/db_manager/instruction_jsons/arm_isalib_extended.yml"
    with open(arm_asl_instructions_yaml_path, "r", encoding="utf-8") as f:
        asl_json_yaml = yaml.safe_load(f)  # Returns a Python dict
        #asl_json_yaml = f.read()
    save_yaml("arm_db.yml", asl_json_yaml)

tk.Button(sidebar, text="📥 Download DB YAML", command=download_yaml).pack(fill=tk.X, pady=5)

# # ✅ **JSON Download Buttons**
# def save_json(filename, data):
#     file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")],
#                                              initialfile=filename)
#     if file_path:
#         with open(file_path, "w", encoding="utf-8") as f:
#             json.dump(data, f, indent=4)
#         messagebox.showinfo("Success", f"File saved as {file_path}")
#
#
# def download_asl():
#     asl_data = {"example": "This would be your ASL instruction data"}
#     save_json("arm_asl_instructions.json", asl_data)
#
#
# def download_usl():
#     usl_data = {"example": "This would be your USL instruction data"}
#     save_json("arm_usl_instructions.json", usl_data)
#
#
# tk.Button(sidebar, text="📥 Download ASL JSON", command=download_asl).pack(fill=tk.X, pady=5)
# tk.Button(sidebar, text="📥 Download USL JSON", command=download_usl).pack(fill=tk.X, pady=5)

# ✅ **Show Last Modified Time**
time_label = tk.Label(sidebar, text=f"Last Updated: {return_last_modified_date()}", fg="blue")
time_label.pack(pady=5)

# Run the Tkinter event loop
root.mainloop()

