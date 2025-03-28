# Nested Skill Tree

A simple application that displays a hierarchical skill tree with the ability to mark skills as completed and expand/collapse subtrees. Built with Python's standard tkinter library.

## Features

- Hierarchical display of skills
- Mark skills as completed or incomplete with a double-click
- Expand and collapse subtrees
- Parent skills are automatically marked as completed when all child skills are completed
- Child skills inherit completion status from parent when parent is marked
- Add new skills to any part of the tree
- Expand all or collapse all nodes with a single click
- Save your skill tree to a JSON file
- Load skill trees from JSON files

## Installation

1. Ensure you have Python 3.6+ installed
2. No external dependencies required - uses standard Python libraries

## Usage

Run the application:

```bash
python3 skill_tree.py
```

### How to Use

- **Double-click** on any skill to mark it as completed or incomplete
- **Click** on the arrow next to a skill to expand or collapse its subtree
- **Add Skill** button allows you to add new skills to the tree
- **Expand All** / **Collapse All** buttons to expand or collapse the entire tree
- **Save Tree** / **Load Tree** buttons to save your progress or load existing skill trees

## Sample Skill Tree

The application includes a sample skill tree file (`sample_tree.json`) with a more comprehensive structure that includes:
- Mathematics (Arithmetic, Algebra, Geometry)
- Programming (Web Development, Python)

To load this sample:
1. Start the application
2. Click the "Load Tree" button
3. Navigate to and select the `sample_tree.json` file

## Default Skill Tree

The application comes with a default skill tree structure:

```
Arithmetic & Pre-Algebra
- Basic Arithmetic
  - Counting
Algebra
- Elementary Algebra
  - Linear Equations
```

You can customize this or create your own skill trees.

## Customization

To add or modify skills, edit the `populate_tree` method in the `SkillTreeApp` class in `skill_tree.py`. 