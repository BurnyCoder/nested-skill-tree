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
        self.root.geometry("800x600")
        
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
            "• Double-click on a skill to mark it as completed/incomplete\n"
            "• Click on the arrows to expand/collapse subtrees\n"
            "• Completing a parent skill completes all child skills\n"
            "• A parent is automatically completed when all children are completed"
        )
        instructions_label = ttk.Label(
            self.title_frame,
            text=instructions,
            justify=tk.LEFT,
            wraplength=780
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
            columns=("completed", "display")
        )
        self.tree.heading("#0", text="Skills")
        self.tree.heading("completed", text="Status")
        self.tree.heading("display", text="")
        self.tree.column("#0", width=400)
        self.tree.column("completed", width=0, stretch=False)  # Hide this column
        self.tree.column("display", width=50, anchor=tk.CENTER)
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
        """Populate the tree with the initial skill tree structure."""
        # Add main categories
        math = self.tree.insert("", "end", text="Arithmetic & Pre-Algebra", values=(False, "❌"))
        algebra = self.tree.insert("", "end", text="Algebra", values=(False, "❌"))
        
        # Add subcategories
        basic_arithmetic = self.tree.insert(math, "end", text="Basic Arithmetic", values=(False, "❌"))
        elem_algebra = self.tree.insert(algebra, "end", text="Elementary Algebra", values=(False, "❌"))
        
        # Add sub-subcategories
        self.tree.insert(basic_arithmetic, "end", text="Counting", values=(False, "❌"))
        self.tree.insert(elem_algebra, "end", text="Linear Equations", values=(False, "❌"))
        
        # Expand all initially
        for item in [math, algebra, basic_arithmetic, elem_algebra]:
            self.tree.item(item, open=True)
    
    def toggle_completion(self, event):
        """Toggle the completion status of a skill."""
        # Get the item that was clicked
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
            
        # Get the current completion status
        current_status = self.tree.item(item_id, "values")[0]
        
        # Toggle the status (convert from string representation to boolean and back)
        if current_status == "True":
            new_status = False
            display_value = "❌"
        else:
            new_status = True
            display_value = "✅"
            
        # Update the item
        self.tree.item(item_id, values=(new_status, display_value))
        
        # Update all children if this is a parent node
        self.update_children(item_id, new_status)
        
        # Check parent status
        self.update_parent(self.tree.parent(item_id))
    
    def update_children(self, parent_id, status):
        """Update all children to match parent's completion status."""
        display_value = "✅" if status else "❌"
        for child_id in self.tree.get_children(parent_id):
            self.tree.item(child_id, values=(status, display_value))
            # Recursively update all descendants
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
            if self.tree.item(child_id, "values")[0] != "True":
                all_completed = False
                break
                
        # Update parent status
        display_value = "✅" if all_completed else "❌"
        self.tree.item(parent_id, values=(all_completed, display_value))
        
        # Recursively update ancestors
        self.update_parent(self.tree.parent(parent_id))
    
    def add_skill_dialog(self):
        """Open a dialog to add a new skill."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Skill")
        dialog.geometry("400x200")
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
        new_item = self.tree.insert(parent_id, "end", text=skill_name, values=(False, "❌"))
        
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
        display_value = "✅" if completed else "❌"
        
        # Insert this node
        new_id = self.tree.insert(
            parent_id, 
            "end", 
            text=node_data["text"], 
            values=(completed, display_value)
        )
        
        # Set open state
        is_open = node_data.get("open", True)
        self.tree.item(new_id, open=is_open)
        
        # Process all children
        for child_data in node_data.get("children", []):
            self._deserialize_tree(new_id, child_data)


def main():
    root = tk.Tk()
    style = ttk.Style()
    style.configure("Accent.TButton", background="#4caf50")
    app = SkillTreeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main() 