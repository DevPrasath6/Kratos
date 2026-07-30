import sys
import os
from pathlib import Path

# Add backend to sys.path
sys.path.insert(0, str(Path("backend").absolute()))

try:
    from backend.routes.agents import orchestrator
except ImportError:
    print("Could not import orchestrator. Make sure you run this from the project root.")
    sys.exit(1)

docs_dir = Path("docs")
docs_dir.mkdir(exist_ok=True)
agents_dir = docs_dir / "agents"
agents_dir.mkdir(exist_ok=True)

main_doc = ["# KRATOS Multi-Agent System Documentation\n"]
main_doc.append("This directory contains the detailed documentation for all the autonomous agents that make up the KRATOS disaster response pipeline.\n")

status = orchestrator.get_status()

for name, info in status.items():
    agent_purpose = info.get('purpose', 'No description provided.')
    
    # Write individual agent doc
    agent_file = agents_dir / f"{name}.md"
    agent_content = f"# {name.replace('_', ' ').title()}\n\n"
    agent_content += f"**Agent ID:** `{name}`\n\n"
    agent_content += f"## Description\n{agent_purpose}\n"
    
    with open(agent_file, "w", encoding="utf-8") as f:
        f.write(agent_content)
        
    # Append to main doc
    main_doc.append(f"## [{name.replace('_', ' ').title()}](./agents/{name}.md)")
    main_doc.append(f"**Agent ID:** `{name}`\n")
    main_doc.append(f"{agent_purpose}\n")

with open(docs_dir / "README.md", "w", encoding="utf-8") as f:
    f.write("\n".join(main_doc))

print(f"Successfully generated documentation for {len(status)} agents in the 'docs/' folder.")
