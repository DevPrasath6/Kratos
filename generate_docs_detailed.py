import sys
import os
import ast
from pathlib import Path

# Add backend to sys.path
sys.path.insert(0, str(Path("backend").absolute()))

try:
    from backend.routes.agents import orchestrator
except ImportError:
    print("Could not import orchestrator. Make sure you run this from the project root.")
    sys.exit(1)

docs_dir = Path("docs")
agents_dir = docs_dir / "agents"
agents_dir.mkdir(parents=True, exist_ok=True)

agents_code_dir = Path("backend/agents")

# Parse all .py files in agents to find docstrings and flows
agent_info_cache = {}

for py_file in agents_code_dir.glob("*.py"):
    with open(py_file, "r", encoding="utf-8") as f:
        source = f.read()
    try:
        tree = ast.parse(source)
    except Exception:
        continue
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            agent_id = None
            for body_item in node.body:
                if isinstance(body_item, ast.AnnAssign) and getattr(body_item.target, "id", None) == "name":
                    if isinstance(body_item.value, ast.Constant):
                        agent_id = body_item.value.value
                elif isinstance(body_item, ast.Assign):
                    for target in body_item.targets:
                        if getattr(target, "id", None) == "name" and isinstance(body_item.value, ast.Constant):
                            agent_id = body_item.value.value
            
            if agent_id:
                run_doc = None
                class_doc = ast.get_docstring(node)
                
                for item in node.body:
                    if isinstance(item, (ast.AsyncFunctionDef, ast.FunctionDef)):
                        if item.name == "run":
                            run_doc = ast.get_docstring(item)
                
                agent_info_cache[agent_id] = {
                    "class_doc": class_doc,
                    "run_doc": run_doc,
                    "file_name": py_file.name
                }

status = orchestrator.get_status()

main_doc = ["# KRATOS Multi-Agent System Detailed Documentation\n"]
main_doc.append("This directory contains the detailed documentation for all the autonomous agents that make up the KRATOS disaster response pipeline.\n")

for name, info in status.items():
    agent_purpose = info.get('purpose', 'No description provided.')
    
    cached = agent_info_cache.get(name, {})
    class_doc = cached.get("class_doc")
    run_doc = cached.get("run_doc")
    file_name = cached.get("file_name", "Unknown File")
    
    agent_file = agents_dir / f"{name}.md"
    
    agent_content = f"# {name.replace('_', ' ').title()}\n\n"
    agent_content += f"**Agent ID:** `{name}`\n"
    agent_content += f"**Source File:** `backend/agents/{file_name}`\n\n"
    
    agent_content += f"## Core Purpose\n{agent_purpose}\n\n"
    
    if class_doc:
        agent_content += f"## Overview\n{class_doc}\n\n"
        
    if run_doc:
        agent_content += f"## Data Flow & I/O Schema\nThe following defines the input parameters expected and output values returned by this agent in the pipeline flow.\n```text\n{run_doc}\n```\n\n"
    else:
        agent_content += f"## Data Flow & I/O Schema\n*No explicit I/O schema provided in the source docstring.* This agent reads properties from the shared pipeline `input_data` dict and appends its own output keys.\n\n"
        
    with open(agent_file, "w", encoding="utf-8") as f:
        f.write(agent_content)
        
    # Append to main doc
    main_doc.append(f"## [{name.replace('_', ' ').title()}](./agents/{name}.md)")
    main_doc.append(f"**Agent ID:** `{name}`\n")
    main_doc.append(f"**Source File:** `backend/agents/{file_name}`\n")
    main_doc.append(f"{agent_purpose}\n")

with open(docs_dir / "README.md", "w", encoding="utf-8") as f:
    f.write("\n".join(main_doc))

print("Successfully generated DETAILED documentation.")
