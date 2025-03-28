#!/usr/bin/env python3
"""
Nested Skill Tree Application
A simple application that displays a hierarchical skill tree
with the ability to mark skills as completed and collapse/expand subtrees.
"""
import tkinter as tk
from tkinter import ttk
import json
import os
from tkinter import filedialog, messagebox


class SkillTreeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nested Skill Tree")
        self.root.geometry("1000x800")
        
        # Create a title frame
        self.title_frame = ttk.Frame(self.root, padding=10)
        self.title_frame.pack(fill=tk.X)
        
        # Add a title
        title_label = ttk.Label(
            self.title_frame, 
            text="Nested Skill Tree", 
            font=("TkDefaultFont", 16, "bold")
        )
        title_label.pack(pady=5)
        
        # Add instructions
        instructions = (
            "Double-click on a bottom-level skill to mark it as completed/incomplete\n"
            "Click on the arrows to expand/collapse subtrees\n"
            "Only skills without children can be directly marked as completed\n"
            "A parent is automatically completed when all children are completed"
        )
        instructions_label = ttk.Label(
            self.title_frame,
            text=instructions,
            justify=tk.LEFT,
            wraplength=980
        )
        instructions_label.pack(pady=5)
        
        # Add a separator
        separator = ttk.Separator(self.root, orient="horizontal")
        separator.pack(fill=tk.X, padx=10)
        
        # Create a frame for the treeview
        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.pack(fill=tk.BOTH, expand=tk.YES)
        
        # Create scrollbar
        self.scrollbar = ttk.Scrollbar(self.frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create the treeview
        self.tree = ttk.Treeview(
            self.frame, 
            yscrollcommand=self.scrollbar.set,
            selectmode="none",
            columns=("completed",),  # Only keep one hidden column for tracking status
            show="tree"  # Only show the tree part, no headings
        )
        self.tree.column("#0", width=950, stretch=True)  # Increased from 750 to 950
        self.tree.column("completed", width=0, stretch=False)  # Hide this column
        
        # Apply custom tag for alternating row colors
        self.tree.tag_configure('completed', background='#c8f7c5', foreground='#006400')  # Light green bg, dark green text
        self.tree.tag_configure('not_completed', background='#f7f7f7')  # Light gray
        
        self.tree.pack(fill=tk.BOTH, expand=tk.YES)
        
        # Configure the scrollbar
        self.scrollbar.config(command=self.tree.yview)
        
        # Create a button frame at the bottom
        self.button_frame = ttk.Frame(self.root, padding=10)
        self.button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Add buttons
        add_button = ttk.Button(
            self.button_frame,
            text="Add Skill",
            command=self.add_skill_dialog,
            style="Accent.TButton"
        )
        add_button.pack(side=tk.LEFT, padx=5)
        
        # Add a button to expand all
        expand_all_button = ttk.Button(
            self.button_frame,
            text="Expand All",
            command=self.expand_all
        )
        expand_all_button.pack(side=tk.LEFT, padx=5)
        
        # Add a button to collapse all
        collapse_all_button = ttk.Button(
            self.button_frame,
            text="Collapse All",
            command=self.collapse_all
        )
        collapse_all_button.pack(side=tk.LEFT, padx=5)
        
        # Add save and load buttons
        save_button = ttk.Button(
            self.button_frame,
            text="Save Tree",
            command=self.save_tree,
            style="Accent.TButton"
        )
        save_button.pack(side=tk.RIGHT, padx=5)
        
        load_button = ttk.Button(
            self.button_frame,
            text="Load Tree",
            command=self.load_tree,
            style="Accent.TButton"
        )
        load_button.pack(side=tk.RIGHT, padx=5)
        
        # Initialize the skill tree
        self.populate_tree()
        
        # Bind the completion toggle action to double-click
        self.tree.bind("<Double-1>", self.toggle_completion)
    
    def populate_tree(self):
        """Populate the tree with the skill tree structure from math.txt."""
        # Check if math.txt exists
        if os.path.exists("math.txt"):
            print("Loading skill tree from math.txt...")
            self.load_from_text_file("math.txt")
        else:
            print("math.txt not found. Using default skill tree.")
            # Fallback to the simple default tree if math.txt doesn't exist
            self._populate_default_tree()
    
    def _populate_default_tree(self):
        """Populate the tree with a simple default skill tree structure."""
        # Add main categories
        math = self.tree.insert("", "end", text="Arithmetic & Pre-Algebra", values=("False",), tags=('not_completed',))
        algebra = self.tree.insert("", "end", text="Algebra", values=("False",), tags=('not_completed',))
        
        # Add subcategories
        basic_arithmetic = self.tree.insert(math, "end", text="Basic Arithmetic", values=("False",), tags=('not_completed',))
        elem_algebra = self.tree.insert(algebra, "end", text="Elementary Algebra", values=("False",), tags=('not_completed',))
        
        # Add sub-subcategories
        self.tree.insert(basic_arithmetic, "end", text="Counting", values=("False",), tags=('not_completed',))
        self.tree.insert(elem_algebra, "end", text="Linear Equations", values=("False",), tags=('not_completed',))
        
        # Expand top-level categories
        for item in [math, algebra]:
            self.tree.item(item, open=True)
    
    def load_from_text_file(self, file_path):
        """Load a skill tree from a text file with indentation."""
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            # Parse the indented text file
            self._parse_indented_tree(lines)
            
            # Expand top-level items
            for item in self.tree.get_children():
                self.tree.item(item, open=True)
                
                # Also expand second-level items
                for child in self.tree.get_children(item):
                    self.tree.item(child, open=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading from text file: {str(e)}")
            # Fall back to the default tree
            self._populate_default_tree()
    
    def _parse_indented_tree(self, lines):
        """Parse an indented text file and build the tree."""
        # Dictionary to track parent nodes at each indentation level
        parent_map = {}
        
        for line in lines:
            if not line.strip():  # Skip empty lines
                continue
                
            # Calculate indentation level (count spaces at the beginning)
            indent = 0
            for char in line:
                if char == ' ':
                    indent += 1
                elif char == '\t':
                    indent += 4  # Treat tabs as 4 spaces
                else:
                    break
            
            # Normalize indentation to levels
            # If line starts with a dash (after spaces), it's a child of the previous level
            text = line.strip()
            has_dash = text.startswith('- ')
            
            # The text content (remove leading dash if present)
            if has_dash:
                text = text[2:]
            
            # Calculate the actual level based on indentation and dash presence
            if indent == 0 and not has_dash:
                # Main category (like "Arithmetic & Pre-Algebra")
                level = 0
                parent_id = ""
            elif has_dash:
                # Line with a dash is a child of its indentation level
                level = (indent // 2) + 1
                parent_id = parent_map.get(level - 1, "")
            else:
                # Other indented lines without dash
                level = indent // 2
                parent_id = parent_map.get(level - 1, "")
            
            # Insert the node
            node_id = self.tree.insert(
                parent_id, 
                "end", 
                text=text, 
                values=("False",), 
                tags=('not_completed',)
            )
            
            # Update the parent map for this level
            parent_map[level] = node_id
    
    def toggle_completion(self, event):
        """Toggle the completion status of a skill."""
        # Get the item that was clicked
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
            
        # Check if this item has children
        children = self.tree.get_children(item_id)
        if children:
            # This is not a leaf node, show a message and return
            print(f"Cannot directly mark '{self.tree.item(item_id, 'text')}' as completed - only bottom-level skills can be marked")
            return
            
        # Get the current completion status
        current_values = self.tree.item(item_id, "values")
        if len(current_values) < 1:
            return
            
        current_status = str(current_values[0])
        
        # Toggle the status
        if current_status == "True":
            new_status = False
            self.tree.item(item_id, tags=('not_completed',))
        else:
            new_status = True
            self.tree.item(item_id, tags=('completed',))
            
        # Update the item (only store the status, no display character)
        self.tree.item(item_id, values=(str(new_status),))
        
        # Add debugging message
        print(f"Toggled item: {self.tree.item(item_id, 'text')}, new status: {new_status}")
        
        # Check parent status
        parent_id = self.tree.parent(item_id)
        if parent_id:
            self.update_parent(parent_id)
            print(f"Updated parent: {self.tree.item(parent_id, 'text')}, all children completed: {self.tree.item(parent_id, 'values')[0]}")
    
    def update_children(self, parent_id, status):
        """Update all children to match parent's completion status."""
        status_str = str(status)
        
        # Get all children
        children = self.tree.get_children(parent_id)
        if not children:
            return
            
        # Update each child
        for child_id in children:
            # Update child's status
            if status:
                self.tree.item(child_id, tags=('completed',))
            else:
                self.tree.item(child_id, tags=('not_completed',))
                
            self.tree.item(child_id, values=(status_str,))
            
            # Recursively update descendants
            self.update_children(child_id, status)
    
    def update_parent(self, parent_id):
        """Update parent status based on children's statuses."""
        if not parent_id:
            return
            
        # Check if all children are completed
        children = self.tree.get_children(parent_id)
        if not children:
            return
            
        all_completed = True
        for child_id in children:
            child_values = self.tree.item(child_id, "values")
            if len(child_values) < 1:
                all_completed = False
                break
                
            child_status = str(child_values[0])
            if child_status != "True":
                all_completed = False
                break
                
        # Update parent status
        self.tree.item(parent_id, values=(str(all_completed),))
        
        # Update the tag
        if all_completed:
            self.tree.item(parent_id, tags=('completed',))
        else:
            self.tree.item(parent_id, tags=('not_completed',))
            
        # Recursively update ancestors
        self.update_parent(self.tree.parent(parent_id))
    
    def add_skill_dialog(self):
        """Open a dialog to add a new skill."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Skill")
        dialog.geometry("500x250")  # Increased from 400x200
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Add form elements
        ttk.Label(dialog, text="Skill Name:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        skill_name = ttk.Entry(dialog, width=30)
        skill_name.grid(row=0, column=1, padx=10, pady=10)
        skill_name.focus_set()
        
        # Parent selection
        ttk.Label(dialog, text="Parent Skill:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        
        # Get all current items
        all_items = []
        self._get_all_items("", all_items)
        
        # Create a dictionary of item IDs to display names
        self.item_dict = {}
        for item_id in all_items:
            self.item_dict[self.tree.item(item_id, "text")] = item_id
        
        # Add "Root" as an option
        self.item_dict["[Root Level]"] = ""
        
        # Create the combobox with all item names
        parent_combo = ttk.Combobox(dialog, values=list(self.item_dict.keys()), state="readonly")
        parent_combo.current(0)  # Select the first item
        parent_combo.grid(row=1, column=1, padx=10, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            button_frame,
            text="Add",
            style="Accent.TButton",
            command=lambda: self._add_skill(skill_name.get(), parent_combo.get(), dialog)
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=10)
    
    def _add_skill(self, skill_name, parent_name, dialog):
        """Add a new skill to the tree."""
        if not skill_name:
            return
        
        # Get the parent ID from the dictionary
        parent_id = self.item_dict.get(parent_name, "")
        
        # Insert the new skill
        new_item = self.tree.insert(parent_id, "end", text=skill_name, values=("False",), tags=('not_completed',))
        
        # If it's a child, make sure the parent is expanded
        if parent_id:
            self.tree.item(parent_id, open=True)
        
        # Close the dialog
        dialog.destroy()
    
    def _get_all_items(self, parent_id, items_list):
        """Recursively get all items in the tree."""
        for item_id in self.tree.get_children(parent_id):
            items_list.append(item_id)
            self._get_all_items(item_id, items_list)
    
    def expand_all(self):
        """Expand all items in the tree."""
        for item in self.tree.get_children():
            self._expand_item(item)
    
    def _expand_item(self, item):
        """Recursively expand an item and all its children."""
        self.tree.item(item, open=True)
        for child in self.tree.get_children(item):
            self._expand_item(child)
    
    def collapse_all(self):
        """Collapse all items in the tree."""
        for item in self.tree.get_children():
            self._collapse_item(item)
    
    def _collapse_item(self, item):
        """Recursively collapse an item and all its children."""
        for child in self.tree.get_children(item):
            self._collapse_item(child)
        self.tree.item(item, open=False)
    
    def save_tree(self):
        """Save the current skill tree to a JSON file."""
        # Ask for the file to save to
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Skill Tree"
        )
        
        if not file_path:
            return
        
        # Create a dictionary to store the tree structure
        tree_data = self._serialize_tree("")
        
        # Save to the file
        try:
            with open(file_path, 'w') as f:
                json.dump(tree_data, f, indent=4)
            messagebox.showinfo("Success", "Skill tree saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving file: {str(e)}")
    
    def _serialize_tree(self, node_id):
        """Recursively serialize the tree starting from node_id."""
        # Get all children of this node
        children = self.tree.get_children(node_id)
        
        # If this is not the root, get node data
        if node_id:
            is_completed = self.tree.item(node_id, "values")[0] == "True"
            node_text = self.tree.item(node_id, "text")
            is_open = self.tree.item(node_id, "open")
            
            # Create the node data dict
            node_data = {
                "text": node_text,
                "completed": is_completed,
                "open": is_open,
                "children": []
            }
        else:
            # Root node special case
            node_data = {"children": []}
        
        # Add all child nodes
        for child_id in children:
            child_data = self._serialize_tree(child_id)
            node_data["children"].append(child_data)
        
        return node_data
    
    def load_tree(self):
        """Load a skill tree from a JSON file."""
        # Ask for the file to load from
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Skill Tree"
        )
        
        if not file_path:
            return
        
        # Load from the file
        try:
            with open(file_path, 'r') as f:
                tree_data = json.load(f)
            
            # Clear the current tree
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Load the new tree
            self._deserialize_tree("", tree_data)
            messagebox.showinfo("Success", "Skill tree loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading file: {str(e)}")
    
    def _deserialize_tree(self, parent_id, node_data):
        """Recursively build the tree from the serialized data."""
        # Handle root node special case
        if "text" not in node_data:
            # This is the root node special case
            for child_data in node_data["children"]:
                self._deserialize_tree(parent_id, child_data)
            return
        
        # Regular node case
        completed = node_data.get("completed", False)
        tag = 'completed' if completed else 'not_completed'
        
        # Insert this node
        new_id = self.tree.insert(
            parent_id, 
            "end", 
            text=node_data["text"], 
            values=(str(completed),),
            tags=(tag,)
        )
        
        # Set open state
        is_open = node_data.get("open", True)
        self.tree.item(new_id, open=is_open)
        
        # Process all children
        for child_data in node_data.get("children", []):
            self._deserialize_tree(new_id, child_data)


def main():
    root = tk.Tk()
    
    # Set default font for the application
    default_font = ("TkDefaultFont", 12)
    title_font = ("TkDefaultFont", 20, "bold")
    
    # Configure default fonts for different elements
    root.option_add("*Font", default_font)
    root.option_add("*TButton*Font", default_font)
    root.option_add("*TLabel*Font", default_font)
    root.option_add("*TEntry*Font", default_font)
    
    # Create style
    style = ttk.Style()
    style.configure("Accent.TButton", background="#4caf50")
    
    # Increase size of buttons
    style.configure("TButton", padding=(10, 5))
    style.configure("Accent.TButton", padding=(10, 5))
    
    # Configure treeview with larger font
    style.configure("Treeview", rowheight=25, font=default_font)
    style.configure("Treeview.Heading", font=default_font)
    
    app = SkillTreeApp(root)
    
    # Update title font after app creation
    for widget in app.title_frame.winfo_children():
        if isinstance(widget, ttk.Label) and widget.cget("text") == "Nested Skill Tree":
            widget.configure(font=title_font)
    
    root.mainloop()


if __name__ == "__main__":
    main() 