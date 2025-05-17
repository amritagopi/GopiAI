<div align="center">
</div>


![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
[![Docs](https://img.shields.io/badge/docs-latest-blue)](https://the-pocket-world.github.io/Pocketflow-Framework-Py/)
 <a href="https://discord.gg/hUHHE9Sa6T">
    <img src="https://img.shields.io/discord/1346833819172601907?logo=discord&style=flat">
</a>

Pocket Flow is a [100-line](pocketflow_framework/__init__.py) minimalist LLM framework

- **Expressive**: Everything you love from larger frameworks—([Multi-](https://the-pocket-world.github.io/Pocketflow-Framework-Py/design_pattern/multi_agent.html))[Agents](https://the-pocket-world.github.io/Pocketflow-Framework-Py/design_pattern/agent.html), [Workflow](https://the-pocket-world.github.io/Pocketflow-Framework-Py/design_pattern/workflow.html), [RAG](https://the-pocket-world.github.io/Pocketflow-Framework-Py/design_pattern/rag.html), and more.
  
- **Lightweight**: Just the core graph abstraction in 100 lines. Zero bloat, zero dependencies, zero vendor lock-in.
  
- **Principled**: Built with modularity and clear separation of concerns at its heart.

- **AI-Friendly**: Intuitive enough for AI agents to assist humans in building complex LLM applications.
  
- To install, ```pip install pocketflow_framework```or just copy the [source code](pocketflow_framework/__init__.py) (only 100 lines).
  
- To learn more, check out the [documentation](https://the-pocket-world.github.io/Pocketflow-Framework-Py/). For an in-depth design dive, read the [essay](https://github.com/The-Pocket-World/.github/blob/main/profile/pocketflow.md).
  

## What can Pocket Flow build?

</div>

- Want to create your own Python project? Start with  [this template](https://github.com/The-Pocket-World/PocketFlow-Template-Python)

## Why Pocket Flow?

For a new development paradigmn: **Build LLM Apps by Chatting with LLM agents, Not Coding**!

- 🧑 Human **describe LLM App requirements** in a design doc.
- 🤖 The agent (like Cursor AI) **implements App** your code automatically.


  - **For one-time LLM task**:  Create a [ChatGPT](https://help.openai.com/en/articles/10169521-using-projects-in-chatgpt) or [Claude](https://www.anthropic.com/news/projects) project; upload the [docs](docs) to project knowledge.
  - **For LLM App development**: Use [Cursor AI](https://www.cursor.com/).
      - If you already have a project, copy [.cursorrules](.cursorrules) to your project root as [Cursor Rules](https://docs.cursor.com/context/rules-for-ai).

  </details>

  <details>
    <summary>👈 (Click to expand) <b>How does Pocket Flow compare to other frameworks?</b></summary>
<br>

 Pocket Flow is <i>purpose-built for LLM Agents</i>:
1. **🫠 LangChain-like frameworks** overwhelm Cursor AI with *complex* abstractions, *deprecated* functions and *irritating* dependency issues.
2. 😐  **Without a framework**, code is *ad hoc*—suitable only for immediate tasks, *not modular or maintainable*.
3. **🥰 With Pocket Flow**: (1) Minimal and expressive—easy for Cursor AI to pick up. (2) *Nodes and Flows* keep everything *modular*. (3) A *Shared Store* decouples your data structure from compute logic.

In short, the **100 lines** ensures LLM Agents follows *solid coding practices* without sacrificing *flexibility*. 
  </details>

## How does Pocket Flow work?

The few lines](pocketflow_framework/__init__.py) capture what we believe to be the core abstraction of LLM frameworks:
 - **Computation**: A *graph* that breaks down tasks into nodes, with *branching, looping,  and nesting*.
 - **Communication**: A *shared store* that all nodes can read and write to.

<br>
<div align="center">
  <img src="./assets/abstraction.png" width="600"/>
<br>
<div align="center">
  <img src="./assets/design.png" width="600"/>
</div>
<br>
