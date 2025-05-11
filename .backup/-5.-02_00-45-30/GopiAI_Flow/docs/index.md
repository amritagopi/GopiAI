---
layout: default
title: "Home"
nav_order: 1
---

# Pocket Flow

A [100-line](https://github.com/The-Pocket-World/Pocketflow-Framework-Py/blob/main/pocketflow_framework/__init__.py) minimalist LLM framework for *Agents, Task Decomposition, RAG, etc*.


- **Expressive**: Everything you love from larger frameworks—([Multi-](./design_pattern/multi_agent.html))[Agents](./design_pattern/agent.html), [Workflow](./design_pattern/workflow.html), [RAG](./design_pattern/rag.html), and more.  
- **Lightweight**: Just the core graph abstraction in 100 lines. ZERO dependencies, and vendor lock-in.
- **Principled**: Built with modularity and clear separation of concerns at its heart.
- **AI-Friendly**: Intuitive enough for AI agents to assist humans in building complex LLM applications.

<div align="center">
  <img src="https://github.com/The-Pocket-World/Pocketflow-Framework-Py/raw/main/assets/meme.jpg?raw=true" width="400"/>
</div>


## Core Abstraction

We model the LLM workflow as a **Graph + Shared Store**:

- [Node](./core_abstraction/node.md) handles simple (LLM) tasks.
- [Flow](./core_abstraction/flow.md) connects nodes through **Actions** (labeled edges).
- [Shared Store](./core_abstraction/communication.md) enables communication between nodes within flows.
- [Batch](./core_abstraction/batch.md) nodes/flows allow for data-intensive tasks.
- [(Advanced) Async](./core_abstraction/async.md) nodes/flows allow waiting for asynchronous tasks.
- [(Advanced) Parallel](./core_abstraction/parallel.md) nodes/flows handle I/O-bound tasks.

## Design Pattern

From there, it’s easy to implement popular design patterns:

- [Structured Output](./design_pattern/structure.md) formats outputs consistently.
- [Workflow](./design_pattern/workflow.md) chains multiple tasks into pipelines.
- [Map Reduce](./design_pattern/mapreduce.md) splits data tasks into Map and Reduce steps.
- [RAG](./design_pattern/rag.md) integrates data retrieval with generation.
- [Agent](./design_pattern/agent.md) autonomously makes decisions.
- [(Optional) Chat Memory](./design_pattern/memory.md) preserves conversation context.
- [(Advanced) Multi-Agents](./design_pattern/multi_agent.md) coordinate multiple agents.

## Utility Function

We provide utility functions not in *codes*, but in *docs*:

- [LLM Wrapper](./utility_function/llm.md)
- [Tool](./utility_function/tool.md)
- [(Optional) Viz and Debug](./utility_function/viz.md)
- [(Optional) Web Search](./utility_function/websearch.md)
- [(Optional) Chunking](./utility_function/chunking.md)
- [(Optional) Embedding](./utility_function/embedding.md)
- [(Optional) Vector Databases](./utility_function/vector.md)
- [(Optional) Text-to-Speech](./utility_function/text_to_speech.md)

## Read to Develop your LLM Apps? [Read this guide!](./guide.md)