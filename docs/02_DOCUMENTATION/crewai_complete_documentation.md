# CrewAI Documentation - Complete Guide

This documentation was automatically generated and compiled from the official CrewAI documentation.

## Table of Contents

- [Introduction](#introduction)
  - [Introduction](#introduction)
  - [CrewAI Enterprise](#crewai-enterprise)
  - [Introduction](#introduction)
- [Quick Start](#quick-start)
  - [Quickstart](#quickstart)
- [Installation](#installation)
  - [Installation](#installation)
- [Core Concepts](#core-concepts)
  - [Testing](#testing)
  - [Reasoning](#reasoning)
  - [Processes](#processes)
  - [Planning](#planning)
  - [Event Listeners](#event-listeners)
  - [Collaboration](#collaboration)
  - [Knowledge](#knowledge)
  - [CLI](#cli)
  - [Memory](#memory)
  - [Training](#training)
  - [Introduction](#introduction)
- [Agents](#agents)
  - [Custom Manager Agent](#custom-manager-agent)
  - [Using Multimodal Agents](#using-multimodal-agents)
  - [Customize Agents](#customize-agents)
  - [Agents](#agents)
  - [AgentOps Integration](#agentops-integration)
  - [Coding Agents](#coding-agents)
  - [Crafting Effective Agents](#crafting-effective-agents)
- [Tasks](#tasks)
  - [Conditional Tasks](#conditional-tasks)
  - [Tasks](#tasks)
  - [Replay Tasks from Latest Crew Kickoff](#replay-tasks-from-latest-crew-kickoff)
- [Crews](#crews)
  - [Crews](#crews)
  - [Build Your First Crew](#build-your-first-crew)
- [Tools](#tools)
  - [Tools](#tools)
  - [Create Custom Tools](#create-custom-tools)
  - [Force Tool Output as Result](#force-tool-output-as-result)
  - [Tools Overview](#tools-overview)
- [LLMs](#llms)
  - [Custom LLM Implementation](#custom-llm-implementation)
  - [LLMs](#llms)
  - [Connect to any LLM](#connect-to-any-llm)
- [Flows](#flows)
  - [MLflow Integration](#mlflow-integration)
  - [Flows](#flows)
  - [Build Your First Flow](#build-your-first-flow)
  - [Mastering Flow State Management](#mastering-flow-state-management)
- [Guides](#guides)
  - [Customizing Prompts](#customizing-prompts)
  - [Fingerprinting](#fingerprinting)
- [Examples](#examples)
  - [CrewAI Examples](#crewai-examples)
- [How-to Guides](#how-to-guides)
  - [Introduction](#introduction)
- [Other](#other)
  - [Opik Integration](#opik-integration)
  - [Patronus AI Evaluation](#patronus-ai-evaluation)
  - [Telemetry](#telemetry)
  - [Arize Phoenix](#arize-phoenix)
  - [Langtrace Integration](#langtrace-integration)
  - [SSE Transport](#sse-transport)
  - [MCP Security Considerations](#mcp-security-considerations)
  - [Image Generation with DALL-E](#image-generation-with-dall-e)
  - [Overview](#overview)
  - [Hierarchical Process](#hierarchical-process)
  - [Streamable HTTP Transport](#streamable-http-transport)
  - [Kickoff Crew for Each](#kickoff-crew-for-each)
  - [Weave Integration](#weave-integration)
  - [OpenLIT Integration](#openlit-integration)
  - [Stdio Transport](#stdio-transport)
  - [Langfuse Integration](#langfuse-integration)
  - [Using Annotations in crew.py](#using-annotations-in-crew.py)
  - [Overview](#overview)
  - [Connecting to Multiple MCP Servers](#connecting-to-multiple-mcp-servers)
  - [Changelog](#changelog)
  - [MCP Servers as Tools in CrewAI](#mcp-servers-as-tools-in-crewai)
  - [Human Input on Execution](#human-input-on-execution)
  - [Kickoff Crew Asynchronously](#kickoff-crew-asynchronously)
  - [Sequential Processes](#sequential-processes)


## Introduction {#introduction}

### Introduction {#introduction}

**Source:** [https://docs.crewai.com/introduction](https://docs.crewai.com/introduction)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Get Started

Introduction

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Get Started

# Introduction

Copy page

Build AI agent teams that work together to tackle complex tasks

# 

​

What is CrewAI?

**CrewAI is a lean, lightning-fast Python framework built entirely from scratch—completely independent of LangChain or other agent frameworks.**

CrewAI empowers developers with both high-level simplicity and precise low-level control, ideal for creating autonomous AI agents tailored to any scenario:

  * **[CrewAI Crews](/guides/crews/first-crew)** : Optimize for autonomy and collaborative intelligence, enabling you to create AI teams where each agent has specific roles, tools, and goals.
  * **[CrewAI Flows](/guides/flows/first-flow)** : Enable granular, event-driven control, single LLM calls for precise task orchestration and supports Crews natively.



With over 100,000 developers certified through our community courses, CrewAI is rapidly becoming the standard for enterprise-ready AI automation.

## 

​

How Crews Work

Just like a company has departments (Sales, Engineering, Marketing) working together under leadership to achieve business goals, CrewAI helps you create an organization of AI agents with specialized roles collaborating to accomplish complex tasks.

CrewAI Framework Overview

Component| Description| Key Features  
---|---|---  
**Crew**|  The top-level organization| • Manages AI agent teams  
• Oversees workflows  
• Ensures collaboration  
• Delivers outcomes  
**AI Agents**|  Specialized team members| • Have specific roles (researcher, writer)  
• Use designated tools  
• Can delegate tasks  
• Make autonomous decisions  
**Process**|  Workflow management system| • Defines collaboration patterns  
• Controls task assignments  
• Manages interactions  
• Ensures efficient execution  
**Tasks**|  Individual assignments| • Have clear objectives  
• Use specific tools  
• Feed into larger process  
• Produce actionable results  
  
### 

​

How It All Works Together

  1. The **Crew** organizes the overall operation
  2. **AI Agents** work on their specialized tasks
  3. The **Process** ensures smooth collaboration
  4. **Tasks** get completed to achieve the goal



## 

​

Key Features

## Role-Based Agents

Create specialized agents with defined roles, expertise, and goals - from researchers to analysts to writers

## Flexible Tools

Equip agents with custom tools and APIs to interact with external services and data sources

## Intelligent Collaboration

Agents work together, sharing insights and coordinating tasks to achieve complex objectives

## Task Management

Define sequential or parallel workflows, with agents automatically handling task dependencies

## 

​

How Flows Work

While Crews excel at autonomous collaboration, Flows provide structured automations, offering granular control over workflow execution. Flows ensure tasks are executed reliably, securely, and efficiently, handling conditional logic, loops, and dynamic state management with precision. Flows integrate seamlessly with Crews, enabling you to balance high autonomy with exacting control.

CrewAI Framework Overview

Component| Description| Key Features  
---|---|---  
**Flow**|  Structured workflow orchestration| • Manages execution paths  
• Handles state transitions  
• Controls task sequencing  
• Ensures reliable execution  
**Events**|  Triggers for workflow actions| • Initiate specific processes  
• Enable dynamic responses  
• Support conditional branching  
• Allow for real-time adaptation  
**States**|  Workflow execution contexts| • Maintain execution data  
• Enable persistence  
• Support resumability  
• Ensure execution integrity  
**Crew Support**|  Enhances workflow automation| • Injects pockets of agency when needed  
• Complements structured workflows  
• Balances automation with intelligence  
• Enables adaptive decision-making  
  
### 

​

Key Capabilities

## Event-Driven Orchestration

Define precise execution paths responding dynamically to events

## Fine-Grained Control

Manage workflow states and conditional execution securely and efficiently

## Native Crew Integration

Effortlessly combine with Crews for enhanced autonomy and intelligence

## Deterministic Execution

Ensure predictable outcomes with explicit control flow and error handling

## 

​

When to Use Crews vs. Flows

Understanding when to use [Crews](/guides/crews/first-crew) versus [Flows](/guides/flows/first-flow) is key to maximizing the potential of CrewAI in your applications.

Use Case| Recommended Approach| Why?  
---|---|---  
**Open-ended research**| [Crews](/guides/crews/first-crew)| When tasks require creative thinking, exploration, and adaptation  
**Content generation**| [Crews](/guides/crews/first-crew)| For collaborative creation of articles, reports, or marketing materials  
**Decision workflows**| [Flows](/guides/flows/first-flow)| When you need predictable, auditable decision paths with precise control  
**API orchestration**| [Flows](/guides/flows/first-flow)| For reliable integration with multiple external services in a specific sequence  
**Hybrid applications**|  Combined approach| Use [Flows](/guides/flows/first-flow) to orchestrate overall process with [Crews](/guides/crews/first-crew) handling complex subtasks  
  
### 

​

Decision Framework

  * **Choose[Crews](/guides/crews/first-crew) when:** You need autonomous problem-solving, creative collaboration, or exploratory tasks
  * **Choose[Flows](/guides/flows/first-flow) when:** You require deterministic outcomes, auditability, or precise control over execution
  * **Combine both when:** Your application needs both structured processes and pockets of autonomous intelligence



## 

​

Why Choose CrewAI?

  * 🧠 **Autonomous Operation** : Agents make intelligent decisions based on their roles and available tools
  * 📝 **Natural Interaction** : Agents communicate and collaborate like human team members
  * 🛠️ **Extensible Design** : Easy to add new tools, roles, and capabilities
  * 🚀 **Production Ready** : Built for reliability and scalability in real-world applications
  * 🔒 **Security-Focused** : Designed with enterprise security requirements in mind
  * 💰 **Cost-Efficient** : Optimized to minimize token usage and API calls



## 

​

Ready to Start Building?

## [Build Your First CrewStep-by-step tutorial to create a collaborative AI team that works together to solve complex problems.](/guides/crews/first-crew)## [Build Your First FlowLearn how to create structured, event-driven workflows with precise control over execution.](/guides/flows/first-flow)

## [Install CrewAIGet started with CrewAI in your development environment.](/installation)## [Quick StartFollow our quickstart guide to create your first CrewAI agent and get hands-on experience.](/quickstart)## [Join the CommunityConnect with other developers, get help, and share your CrewAI experiences.](https://community.crewai.com)

Was this page helpful?

YesNo

[Installation](/installation)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * What is CrewAI?
  * How Crews Work
  * How It All Works Together
  * Key Features
  * How Flows Work
  * Key Capabilities
  * When to Use Crews vs. Flows
  * Decision Framework
  * Why Choose CrewAI?
  * Ready to Start Building?



Assistant

Responses are generated using AI and may contain mistakes.


---

### CrewAI Enterprise {#crewai-enterprise}

**Source:** [https://docs.crewai.com/enterprise/introduction](https://docs.crewai.com/enterprise/introduction)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Getting Started

CrewAI Enterprise

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Getting Started

  * [CrewAI Enterprise](/enterprise/introduction)



##### Features

  * [Tool Repository](/enterprise/features/tool-repository)
  * [Webhook Streaming](/enterprise/features/webhook-streaming)
  * [Traces](/enterprise/features/traces)
  * [Hallucination Guardrail](/enterprise/features/hallucination-guardrail)



##### How-To Guides

  * [Build Crew](/enterprise/guides/build-crew)
  * [Deploy Crew](/enterprise/guides/deploy-crew)
  * [Kickoff Crew](/enterprise/guides/kickoff-crew)
  * [Update Crew](/enterprise/guides/update-crew)
  * [Enable Crew Studio](/enterprise/guides/enable-crew-studio)
  * [Azure OpenAI Setup](/enterprise/guides/azure-openai-setup)
  * [HubSpot Trigger](/enterprise/guides/hubspot-trigger)
  * [React Component Export](/enterprise/guides/react-component-export)
  * [Salesforce Trigger](/enterprise/guides/salesforce-trigger)
  * [Slack Trigger](/enterprise/guides/slack-trigger)
  * [Team Management](/enterprise/guides/team-management)
  * [Webhook Automation](/enterprise/guides/webhook-automation)
  * [HITL Workflows](/enterprise/guides/human-in-the-loop)
  * [Zapier Trigger](/enterprise/guides/zapier-trigger)



##### Resources

  * [FAQs](/enterprise/resources/frequently-asked-questions)



Getting Started

# CrewAI Enterprise

Copy page

Deploy, monitor, and scale your AI agent workflows

## 

​

Introduction

CrewAI Enterprise provides a platform for deploying, monitoring, and scaling your crews and agents in a production environment.

CrewAI Enterprise extends the power of the open-source framework with features designed for production deployments, collaboration, and scalability. Deploy your crews to a managed infrastructure and monitor their execution in real-time.

## 

​

Key Features

## Crew Deployments

Deploy your crews to a managed infrastructure with a few clicks

## API Access

Access your deployed crews via REST API for integration with existing systems

## Observability

Monitor your crews with detailed execution traces and logs

## Tool Repository

Publish and install tools to enhance your crews’ capabilities

## Webhook Streaming

Stream real-time events and updates to your systems

## Crew Studio

Create and customize crews using a no-code/low-code interface

## 

​

Deployment Options

## GitHub Integration

Connect directly to your GitHub repositories to deploy code

## Crew Studio

Deploy crews created through the no-code Crew Studio interface

## CLI Deployment

Use the CrewAI CLI for more advanced deployment workflows

## 

​

Getting Started

1

Sign up for an account

Create your account at [app.crewai.com](https://app.crewai.com)

## [Sign UpSign Up](https://app.crewai.com/signup)

2

Build your first crew

Use code or Crew Studio to build your crew

## [Build CrewBuild Crew](/enterprise/guides/build-crew)

3

Deploy your crew

Deploy your crew to the Enterprise platform

## [Deploy CrewDeploy Crew](/enterprise/guides/deploy-crew)

4

Access your crew

Integrate with your crew via the generated API endpoints

## [API AccessUse the Crew API](/enterprise/guides/use-crew-api)

For detailed instructions, check out our [deployment guide](/enterprise/guides/deploy-crew) or click the button below to get started.

Was this page helpful?

YesNo

[Tool Repository](/enterprise/features/tool-repository)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Introduction
  * Key Features
  * Deployment Options
  * Getting Started



Assistant

Responses are generated using AI and may contain mistakes.


---

### Introduction {#introduction}

**Source:** [https://docs.crewai.com/api-reference/introduction](https://docs.crewai.com/api-reference/introduction)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Getting Started

Introduction

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Getting Started

  * [Introduction](/api-reference/introduction)



##### Endpoints

  * API Reference




Getting Started

# Introduction

Copy page

Complete reference for the CrewAI Enterprise REST API

# 

​

CrewAI Enterprise API

Welcome to the CrewAI Enterprise API reference. This API allows you to programmatically interact with your deployed crews, enabling integration with your applications, workflows, and services.

## 

​

Quick Start

1

Get Your API Credentials

Navigate to your crew’s detail page in the CrewAI Enterprise dashboard and copy your Bearer Token from the Status tab.

2

Discover Required Inputs

Use the `GET /inputs` endpoint to see what parameters your crew expects.

3

Start a Crew Execution

Call `POST /kickoff` with your inputs to start the crew execution and receive a `kickoff_id`.

4

Monitor Progress

Use `GET /status/{kickoff_id}` to check execution status and retrieve results.

## 

​

Authentication

All API requests require authentication using a Bearer token. Include your token in the `Authorization` header:
    
    
    curl -H "Authorization: Bearer YOUR_CREW_TOKEN" \
      https://your-crew-url.crewai.com/inputs

### 

​

Token Types

Token Type| Scope| Use Case  
---|---|---  
**Bearer Token**|  Organization-level access| Full crew operations, ideal for server-to-server integration  
**User Bearer Token**|  User-scoped access| Limited permissions, suitable for user-specific operations  
  
You can find both token types in the Status tab of your crew’s detail page in the CrewAI Enterprise dashboard.

## 

​

Base URL

Each deployed crew has its own unique API endpoint:
    
    
    https://your-crew-name.crewai.com

Replace `your-crew-name` with your actual crew’s URL from the dashboard.

## 

​

Typical Workflow

  1. **Discovery** : Call `GET /inputs` to understand what your crew needs
  2. **Execution** : Submit inputs via `POST /kickoff` to start processing
  3. **Monitoring** : Poll `GET /status/{kickoff_id}` until completion
  4. **Results** : Extract the final output from the completed response



## 

​

Error Handling

The API uses standard HTTP status codes:

Code| Meaning  
---|---  
`200`| Success  
`400`| Bad Request - Invalid input format  
`401`| Unauthorized - Invalid bearer token  
`404`| Not Found - Resource doesn’t exist  
`422`| Validation Error - Missing required inputs  
`500`| Server Error - Contact support  
  
## 

​

Interactive Testing

**Why no “Send” button?** Since each CrewAI Enterprise user has their own unique crew URL, we use **reference mode** instead of an interactive playground to avoid confusion. This shows you exactly what the requests should look like without non-functional send buttons.

Each endpoint page shows you:

  * ✅ **Exact request format** with all parameters
  * ✅ **Response examples** for success and error cases
  * ✅ **Code samples** in multiple languages (cURL, Python, JavaScript, etc.)
  * ✅ **Authentication examples** with proper Bearer token format



### 

​

**To Test Your Actual API:**

## Copy cURL Examples

Copy the cURL examples and replace the URL + token with your real values

## Use Postman/Insomnia

Import the examples into your preferred API testing tool

**Example workflow:**

  1. **Copy this cURL example** from any endpoint page
  2. **Replace`your-actual-crew-name.crewai.com`** with your real crew URL
  3. **Replace the Bearer token** with your real token from the dashboard
  4. **Run the request** in your terminal or API client



## 

​

Need Help?

## [Enterprise SupportGet help with API integration and troubleshooting](mailto:support@crewai.com)## [Enterprise DashboardManage your crews and view execution logs](https://app.crewai.com)

Was this page helpful?

YesNo

[Get Required Inputs](/api-reference/get-required-inputs)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * CrewAI Enterprise API
  * Quick Start
  * Authentication
  * Token Types
  * Base URL
  * Typical Workflow
  * Error Handling
  * Interactive Testing
  * To Test Your Actual API:
  * Need Help?



Assistant

Responses are generated using AI and may contain mistakes.


---



## Quick Start {#quick-start}

### Quickstart {#quickstart}

**Source:** [https://docs.crewai.com/quickstart](https://docs.crewai.com/quickstart)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Get Started

Quickstart

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Get Started

# Quickstart

Copy page

Build your first AI agent with CrewAI in under 5 minutes.

## 

​

Build your first CrewAI Agent

Let’s create a simple crew that will help us `research` and `report` on the `latest AI developments` for a given topic or subject.

Before we proceed, make sure you have finished installing CrewAI. If you haven’t installed them yet, you can do so by following the [installation guide](/installation).

Follow the steps below to get Crewing! 🚣‍♂️

1

Create your crew

Create a new crew project by running the following command in your terminal. This will create a new directory called `latest-ai-development` with the basic structure for your crew.

Terminal
    
    
    crewai create crew latest-ai-development

2

Navigate to your new crew project

Terminal
    
    
    cd latest-ai-development

3

Modify your `agents.yaml` file

You can also modify the agents as needed to fit your use case or copy and paste as is to your project. Any variable interpolated in your `agents.yaml` and `tasks.yaml` files like `{topic}` will be replaced by the value of the variable in the `main.py` file.

agents.yaml
    
    
    # src/latest_ai_development/config/agents.yaml
    researcher:
      role: >
        {topic} Senior Data Researcher
      goal: >
        Uncover cutting-edge developments in {topic}
      backstory: >
        You're a seasoned researcher with a knack for uncovering the latest
        developments in {topic}. Known for your ability to find the most relevant
        information and present it in a clear and concise manner.
    
    reporting_analyst:
      role: >
        {topic} Reporting Analyst
      goal: >
        Create detailed reports based on {topic} data analysis and research findings
      backstory: >
        You're a meticulous analyst with a keen eye for detail. You're known for
        your ability to turn complex data into clear and concise reports, making
        it easy for others to understand and act on the information you provide.

4

Modify your `tasks.yaml` file

tasks.yaml
    
    
    # src/latest_ai_development/config/tasks.yaml
    research_task:
      description: >
        Conduct a thorough research about {topic}
        Make sure you find any interesting and relevant information given
        the current year is 2025.
      expected_output: >
        A list with 10 bullet points of the most relevant information about {topic}
      agent: researcher
    
    reporting_task:
      description: >
        Review the context you got and expand each topic into a full section for a report.
        Make sure the report is detailed and contains any and all relevant information.
      expected_output: >
        A fully fledge reports with the mains topics, each with a full section of information.
        Formatted as markdown without '```'
      agent: reporting_analyst
      output_file: report.md

5

Modify your `crew.py` file

crew.py
    
    
    # src/latest_ai_development/crew.py
    from crewai import Agent, Crew, Process, Task
    from crewai.project import CrewBase, agent, crew, task
    from crewai_tools import SerperDevTool
    from crewai.agents.agent_builder.base_agent import BaseAgent
    from typing import List
    
    @CrewBase
    class LatestAiDevelopmentCrew():
      """LatestAiDevelopment crew"""
    
      agents: List[BaseAgent]
      tasks: List[Task]
    
      @agent
      def researcher(self) -> Agent:
        return Agent(
          config=self.agents_config['researcher'], # type: ignore[index]
          verbose=True,
          tools=[SerperDevTool()]
        )
    
      @agent
      def reporting_analyst(self) -> Agent:
        return Agent(
          config=self.agents_config['reporting_analyst'], # type: ignore[index]
          verbose=True
        )
    
      @task
      def research_task(self) -> Task:
        return Task(
          config=self.tasks_config['research_task'], # type: ignore[index]
        )
    
      @task
      def reporting_task(self) -> Task:
        return Task(
          config=self.tasks_config['reporting_task'], # type: ignore[index]
          output_file='output/report.md' # This is the file that will be contain the final report.
        )
    
      @crew
      def crew(self) -> Crew:
        """Creates the LatestAiDevelopment crew"""
        return Crew(
          agents=self.agents, # Automatically created by the @agent decorator
          tasks=self.tasks, # Automatically created by the @task decorator
          process=Process.sequential,
          verbose=True,
        )

6

[Optional] Add before and after crew functions

crew.py
    
    
    # src/latest_ai_development/crew.py
    from crewai import Agent, Crew, Process, Task
    from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
    from crewai_tools import SerperDevTool
    
    @CrewBase
    class LatestAiDevelopmentCrew():
      """LatestAiDevelopment crew"""
    
      @before_kickoff
      def before_kickoff_function(self, inputs):
        print(f"Before kickoff function with inputs: {inputs}")
        return inputs # You can return the inputs or modify them as needed
    
      @after_kickoff
      def after_kickoff_function(self, result):
        print(f"After kickoff function with result: {result}")
        return result # You can return the result or modify it as needed
    
      # ... remaining code

7

Feel free to pass custom inputs to your crew

For example, you can pass the `topic` input to your crew to customize the research and reporting.

main.py
    
    
    #!/usr/bin/env python
    # src/latest_ai_development/main.py
    import sys
    from latest_ai_development.crew import LatestAiDevelopmentCrew
    
    def run():
      """
      Run the crew.
      """
      inputs = {
        'topic': 'AI Agents'
      }
      LatestAiDevelopmentCrew().crew().kickoff(inputs=inputs)

8

Set your environment variables

Before running your crew, make sure you have the following keys set as environment variables in your `.env` file:

  * A [Serper.dev](https://serper.dev/) API key: `SERPER_API_KEY=YOUR_KEY_HERE`
  * The configuration for your choice of model, such as an API key. See the [LLM setup guide](/concepts/llms#setting-up-your-llm) to learn how to configure models from any provider.



9

Lock and install the dependencies

  * Lock the dependencies and install them by using the CLI command:

Terminal
        
        crewai install

  * If you have additional packages that you want to install, you can do so by running:

Terminal
        
        uv add <package-name>




10

Run your crew

  * To run your crew, execute the following command in the root of your project:

Terminal
        
        crewai run




11

Enterprise Alternative: Create in Crew Studio

For CrewAI Enterprise users, you can create the same crew without writing code:

  1. Log in to your CrewAI Enterprise account (create a free account at [app.crewai.com](https://app.crewai.com))
  2. Open Crew Studio
  3. Type what is the automation you’re tryign to build
  4. Create your tasks visually and connect them in sequence
  5. Configure your inputs and click “Download Code” or “Deploy”



## [Try CrewAI EnterpriseStart your free account at CrewAI Enterprise](https://app.crewai.com)

12

View your final report

You should see the output in the console and the `report.md` file should be created in the root of your project with the final report.

Here’s an example of what the report should look like:

output/report.md
    
    
    # Comprehensive Report on the Rise and Impact of AI Agents in 2025
    
    ## 1. Introduction to AI Agents
    In 2025, Artificial Intelligence (AI) agents are at the forefront of innovation across various industries. As intelligent systems that can perform tasks typically requiring human cognition, AI agents are paving the way for significant advancements in operational efficiency, decision-making, and overall productivity within sectors like Human Resources (HR) and Finance. This report aims to detail the rise of AI agents, their frameworks, applications, and potential implications on the workforce.
    
    ## 2. Benefits of AI Agents
    AI agents bring numerous advantages that are transforming traditional work environments. Key benefits include:
    
    - **Task Automation**: AI agents can carry out repetitive tasks such as data entry, scheduling, and payroll processing without human intervention, greatly reducing the time and resources spent on these activities.
    - **Improved Efficiency**: By quickly processing large datasets and performing analyses that would take humans significantly longer, AI agents enhance operational efficiency. This allows teams to focus on strategic tasks that require higher-level thinking.
    - **Enhanced Decision-Making**: AI agents can analyze trends and patterns in data, provide insights, and even suggest actions, helping stakeholders make informed decisions based on factual data rather than intuition alone.
    
    ## 3. Popular AI Agent Frameworks
    Several frameworks have emerged to facilitate the development of AI agents, each with its own unique features and capabilities. Some of the most popular frameworks include:
    
    - **Autogen**: A framework designed to streamline the development of AI agents through automation of code generation.
    - **Semantic Kernel**: Focuses on natural language processing and understanding, enabling agents to comprehend user intentions better.
    - **Promptflow**: Provides tools for developers to create conversational agents that can navigate complex interactions seamlessly.
    - **Langchain**: Specializes in leveraging various APIs to ensure agents can access and utilize external data effectively.
    - **CrewAI**: Aimed at collaborative environments, CrewAI strengthens teamwork by facilitating communication through AI-driven insights.
    - **MemGPT**: Combines memory-optimized architectures with generative capabilities, allowing for more personalized interactions with users.
    
    These frameworks empower developers to build versatile and intelligent agents that can engage users, perform advanced analytics, and execute various tasks aligned with organizational goals.
    
    ## 4. AI Agents in Human Resources
    AI agents are revolutionizing HR practices by automating and optimizing key functions:
    
    - **Recruiting**: AI agents can screen resumes, schedule interviews, and even conduct initial assessments, thus accelerating the hiring process while minimizing biases.
    - **Succession Planning**: AI systems analyze employee performance data and potential, helping organizations identify future leaders and plan appropriate training.
    - **Employee Engagement**: Chatbots powered by AI can facilitate feedback loops between employees and management, promoting an open culture and addressing concerns promptly.
    
    As AI continues to evolve, HR departments leveraging these agents can realize substantial improvements in both efficiency and employee satisfaction.
    
    ## 5. AI Agents in Finance
    The finance sector is seeing extensive integration of AI agents that enhance financial practices:
    
    - **Expense Tracking**: Automated systems manage and monitor expenses, flagging anomalies and offering recommendations based on spending patterns.
    - **Risk Assessment**: AI models assess credit risk and uncover potential fraud by analyzing transaction data and behavioral patterns.
    - **Investment Decisions**: AI agents provide stock predictions and analytics based on historical data and current market conditions, empowering investors with informative insights.
    
    The incorporation of AI agents into finance is fostering a more responsive and risk-aware financial landscape.
    
    ## 6. Market Trends and Investments
    The growth of AI agents has attracted significant investment, especially amidst the rising popularity of chatbots and generative AI technologies. Companies and entrepreneurs are eager to explore the potential of these systems, recognizing their ability to streamline operations and improve customer engagement.
    
    Conversely, corporations like Microsoft are taking strides to integrate AI agents into their product offerings, with enhancements to their Copilot 365 applications. This strategic move emphasizes the importance of AI literacy in the modern workplace and indicates the stabilizing of AI agents as essential business tools.
    
    ## 7. Future Predictions and Implications
    Experts predict that AI agents will transform essential aspects of work life. As we look toward the future, several anticipated changes include:
    
    - Enhanced integration of AI agents across all business functions, creating interconnected systems that leverage data from various departmental silos for comprehensive decision-making.
    - Continued advancement of AI technologies, resulting in smarter, more adaptable agents capable of learning and evolving from user interactions.
    - Increased regulatory scrutiny to ensure ethical use, especially concerning data privacy and employee surveillance as AI agents become more prevalent.
    
    To stay competitive and harness the full potential of AI agents, organizations must remain vigilant about latest developments in AI technology and consider continuous learning and adaptation in their strategic planning.
    
    ## 8. Conclusion
    The emergence of AI agents is undeniably reshaping the workplace landscape in 5. With their ability to automate tasks, enhance efficiency, and improve decision-making, AI agents are critical in driving operational success. Organizations must embrace and adapt to AI developments to thrive in an increasingly digital business environment.

Congratulations!

You have successfully set up your crew project and are ready to start building your own agentic workflows!

### 

​

Note on Consistency in Naming

The names you use in your YAML files (`agents.yaml` and `tasks.yaml`) should match the method names in your Python code. For example, you can reference the agent for specific tasks from `tasks.yaml` file. This naming consistency allows CrewAI to automatically link your configurations with your code; otherwise, your task won’t recognize the reference properly.

#### 

​

Example References

Note how we use the same name for the agent in the `agents.yaml` (`email_summarizer`) file as the method name in the `crew.py` (`email_summarizer`) file.

agents.yaml
    
    
    email_summarizer:
        role: >
          Email Summarizer
        goal: >
          Summarize emails into a concise and clear summary
        backstory: >
          You will create a 5 bullet point summary of the report
        llm: provider/model-id  # Add your choice of model here

Note how we use the same name for the task in the `tasks.yaml` (`email_summarizer_task`) file as the method name in the `crew.py` (`email_summarizer_task`) file.

tasks.yaml
    
    
    email_summarizer_task:
        description: >
          Summarize the email into a 5 bullet point summary
        expected_output: >
          A 5 bullet point summary of the email
        agent: email_summarizer
        context:
          - reporting_task
          - research_task

## 

​

Deploying Your Crew

The easiest way to deploy your crew to production is through [CrewAI Enterprise](http://app.crewai.com).

Watch this video tutorial for a step-by-step demonstration of deploying your crew to [CrewAI Enterprise](http://app.crewai.com) using the CLI.

## [Deploy on EnterpriseGet started with CrewAI Enterprise and deploy your crew in a production environment with just a few clicks.](http://app.crewai.com)## [Join the CommunityJoin our open source community to discuss ideas, share your projects, and connect with other CrewAI developers.](https://community.crewai.com)

Was this page helpful?

YesNo

[Installation](/installation)[Evaluating Use Cases for CrewAI](/guides/concepts/evaluating-use-cases)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Build your first CrewAI Agent
  * Note on Consistency in Naming
  * Example References
  * Deploying Your Crew



Assistant

Responses are generated using AI and may contain mistakes.


---



## Installation {#installation}

### Installation {#installation}

**Source:** [https://docs.crewai.com/installation](https://docs.crewai.com/installation)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Get Started

Installation

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Get Started

# Installation

Copy page

Get started with CrewAI - Install, configure, and build your first AI crew

## 

​

Video Tutorial

Watch this video tutorial for a step-by-step demonstration of the installation process:

## 

​

Text Tutorial

**Python Version Requirements**

CrewAI requires `Python >=3.10 and <3.13`. Here’s how to check your version:
    
    
    python3 --version

If you need to update Python, visit [python.org/downloads](https://python.org/downloads)

CrewAI uses the `uv` as its dependency management and package handling tool. It simplifies project setup and execution, offering a seamless experience.

If you haven’t installed `uv` yet, follow **step 1** to quickly get it set up on your system, else you can skip to **step 2**.

1

Install uv

  * **On macOS/Linux:**

Use `curl` to download the script and execute it with `sh`:
        
        curl -LsSf https://astral.sh/uv/install.sh | sh

If your system doesn’t have `curl`, you can use `wget`:
        
        wget -qO- https://astral.sh/uv/install.sh | sh

  * **On Windows:**

Use `irm` to download the script and `iex` to execute it:
        
        powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

If you run into any issues, refer to [UV’s installation guide](https://docs.astral.sh/uv/getting-started/installation/) for more information.




2

Install CrewAI 🚀

  * Run the following command to install `crewai` CLI:
        
        uv tool install crewai

If you encounter a `PATH` warning, run this command to update your shell:
        
        uv tool update-shell

If you encounter the `chroma-hnswlib==0.7.6` build error (`fatal error C1083: Cannot open include file: 'float.h'`) on Windows, install (Visual Studio Build Tools)[<https://visualstudio.microsoft.com/downloads/>] with _Desktop development with C++_.

  * To verify that `crewai` is installed, run:
        
        uv tool list

  * You should see something like:
        
        crewai v0.102.0
        - crewai

  * If you need to update `crewai`, run:
        
        uv tool install crewai --upgrade




Installation successful! You’re ready to create your first crew! 🎉

# 

​

Creating a CrewAI Project

We recommend using the `YAML` template scaffolding for a structured approach to defining agents and tasks. Here’s how to get started:

1

Generate Project Scaffolding

  * Run the `crewai` CLI command:
        
        crewai create crew <your_project_name>

  * This creates a new project with the following structure:
        
        my_project/
        ├── .gitignore
        ├── knowledge/
        ├── pyproject.toml
        ├── README.md
        ├── .env
        └── src/
            └── my_project/
                ├── __init__.py
                ├── main.py
                ├── crew.py
                ├── tools/
                │   ├── custom_tool.py
                │   └── __init__.py
                └── config/
                    ├── agents.yaml
                    └── tasks.yaml




2

Customize Your Project

  * Your project will contain these essential files:

File| Purpose  
---|---  
`agents.yaml`| Define your AI agents and their roles  
`tasks.yaml`| Set up agent tasks and workflows  
`.env`| Store API keys and environment variables  
`main.py`| Project entry point and execution flow  
`crew.py`| Crew orchestration and coordination  
`tools/`| Directory for custom agent tools  
`knowledge/`| Directory for knowledge base  
  * Start by editing `agents.yaml` and `tasks.yaml` to define your crew’s behavior.

  * Keep sensitive information like API keys in `.env`.




3

Run your Crew

  * Before you run your crew, make sure to run:
        
        crewai install

  * If you need to install additional packages, use:
        
        uv add <package-name>

  * To run your crew, execute the following command in the root of your project:
        
        crewai run




## 

​

Enterprise Installation Options

For teams and organizations, CrewAI offers enterprise deployment options that eliminate setup complexity:

### 

​

CrewAI Enterprise (SaaS)

  * Zero installation required - just sign up for free at [app.crewai.com](https://app.crewai.com)
  * Automatic updates and maintenance
  * Managed infrastructure and scaling
  * Build Crews with no Code



### 

​

CrewAI Factory (Self-hosted)

  * Containerized deployment for your infrastructure
  * Supports any hyperscaler including on prem depployments
  * Integration with your existing security systems

## [Explore Enterprise OptionsLearn about CrewAI’s enterprise offerings and schedule a demo](https://crewai.com/enterprise)

## 

​

Next Steps

## [Build Your First AgentFollow our quickstart guide to create your first CrewAI agent and get hands-on experience.](/quickstart)## [Join the CommunityConnect with other developers, get help, and share your CrewAI experiences.](https://community.crewai.com)

Was this page helpful?

YesNo

[Introduction](/introduction)[Quickstart](/quickstart)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Video Tutorial
  * Text Tutorial
  * Creating a CrewAI Project
  * Enterprise Installation Options
  * Next Steps



Assistant

Responses are generated using AI and may contain mistakes.


---



## Core Concepts {#core-concepts}

### Testing {#testing}

**Source:** [https://docs.crewai.com/concepts/testing](https://docs.crewai.com/concepts/testing)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Core Concepts

Testing

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Core Concepts

# Testing

Copy page

Learn how to test your CrewAI Crew and evaluate their performance.

## 

​

Overview

Testing is a crucial part of the development process, and it is essential to ensure that your crew is performing as expected. With crewAI, you can easily test your crew and evaluate its performance using the built-in testing capabilities.

### 

​

Using the Testing Feature

We added the CLI command `crewai test` to make it easy to test your crew. This command will run your crew for a specified number of iterations and provide detailed performance metrics. The parameters are `n_iterations` and `model`, which are optional and default to 2 and `gpt-4o-mini` respectively. For now, the only provider available is OpenAI.
    
    
    crewai test

If you want to run more iterations or use a different model, you can specify the parameters like this:
    
    
    crewai test --n_iterations 5 --model gpt-4o

or using the short forms:
    
    
    crewai test -n 5 -m gpt-4o

When you run the `crewai test` command, the crew will be executed for the specified number of iterations, and the performance metrics will be displayed at the end of the run.

A table of scores at the end will show the performance of the crew in terms of the following metrics:

Tasks/Crew/Agents| Run 1| Run 2| Avg. Total| Agents| Additional Info  
---|---|---|---|---|---  
Task 1| 9.0| 9.5| **9.2**|  Professional Insights|   
| | | | Researcher|   
Task 2| 9.0| 10.0| **9.5**|  Company Profile Investigator|   
Task 3| 9.0| 9.0| **9.0**|  Automation Insights|   
| | | | Specialist|   
Task 4| 9.0| 9.0| **9.0**|  Final Report Compiler| Automation Insights Specialist  
Crew| 9.00| 9.38| **9.2**| |   
Execution Time (s)| 126| 145| **135**| |   
  
The example above shows the test results for two runs of the crew with two tasks, with the average total score for each task and the crew as a whole.

Was this page helpful?

YesNo

[Planning](/concepts/planning)[CLI](/concepts/cli)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Overview
  * Using the Testing Feature



Assistant

Responses are generated using AI and may contain mistakes.


---

### Reasoning {#reasoning}

**Source:** [https://docs.crewai.com/concepts/reasoning](https://docs.crewai.com/concepts/reasoning)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Core Concepts

Reasoning

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Core Concepts

# Reasoning

Copy page

Learn how to enable and use agent reasoning to improve task execution.

## 

​

Overview

Agent reasoning is a feature that allows agents to reflect on a task and create a plan before execution. This helps agents approach tasks more methodically and ensures they’re ready to perform the assigned work.

## 

​

Usage

To enable reasoning for an agent, simply set `reasoning=True` when creating the agent:
    
    
    from crewai import Agent
    
    agent = Agent(
        role="Data Analyst",
        goal="Analyze complex datasets and provide insights",
        backstory="You are an experienced data analyst with expertise in finding patterns in complex data.",
        reasoning=True,  # Enable reasoning
        max_reasoning_attempts=3  # Optional: Set a maximum number of reasoning attempts
    )

## 

​

How It Works

When reasoning is enabled, before executing a task, the agent will:

  1. Reflect on the task and create a detailed plan
  2. Evaluate whether it’s ready to execute the task
  3. Refine the plan as necessary until it’s ready or max_reasoning_attempts is reached
  4. Inject the reasoning plan into the task description before execution



This process helps the agent break down complex tasks into manageable steps and identify potential challenges before starting.

## 

​

Configuration Options

​

reasoning

bool

default:"False"

Enable or disable reasoning

​

max_reasoning_attempts

int

default:"None"

Maximum number of attempts to refine the plan before proceeding with execution. If None (default), the agent will continue refining until it’s ready.

## 

​

Example

Here’s a complete example:
    
    
    from crewai import Agent, Task, Crew
    
    # Create an agent with reasoning enabled
    analyst = Agent(
        role="Data Analyst",
        goal="Analyze data and provide insights",
        backstory="You are an expert data analyst.",
        reasoning=True,
        max_reasoning_attempts=3  # Optional: Set a limit on reasoning attempts
    )
    
    # Create a task
    analysis_task = Task(
        description="Analyze the provided sales data and identify key trends.",
        expected_output="A report highlighting the top 3 sales trends.",
        agent=analyst
    )
    
    # Create a crew and run the task
    crew = Crew(agents=[analyst], tasks=[analysis_task])
    result = crew.kickoff()
    
    print(result)

## 

​

Error Handling

The reasoning process is designed to be robust, with error handling built in. If an error occurs during reasoning, the agent will proceed with executing the task without the reasoning plan. This ensures that tasks can still be executed even if the reasoning process fails.

Here’s how to handle potential errors in your code:
    
    
    from crewai import Agent, Task
    import logging
    
    # Set up logging to capture any reasoning errors
    logging.basicConfig(level=logging.INFO)
    
    # Create an agent with reasoning enabled
    agent = Agent(
        role="Data Analyst",
        goal="Analyze data and provide insights",
        reasoning=True,
        max_reasoning_attempts=3
    )
    
    # Create a task
    task = Task(
        description="Analyze the provided sales data and identify key trends.",
        expected_output="A report highlighting the top 3 sales trends.",
        agent=agent
    )
    
    # Execute the task
    # If an error occurs during reasoning, it will be logged and execution will continue
    result = agent.execute_task(task)

## 

​

Example Reasoning Output

Here’s an example of what a reasoning plan might look like for a data analysis task:
    
    
    Task: Analyze the provided sales data and identify key trends.
    
    Reasoning Plan:
    I'll analyze the sales data to identify the top 3 trends.
    
    1. Understanding of the task:
       I need to analyze sales data to identify key trends that would be valuable for business decision-making.
    
    2. Key steps I'll take:
       - First, I'll examine the data structure to understand what fields are available
       - Then I'll perform exploratory data analysis to identify patterns
       - Next, I'll analyze sales by time periods to identify temporal trends
       - I'll also analyze sales by product categories and customer segments
       - Finally, I'll identify the top 3 most significant trends
    
    3. Approach to challenges:
       - If the data has missing values, I'll decide whether to fill or filter them
       - If the data has outliers, I'll investigate whether they're valid data points or errors
       - If trends aren't immediately obvious, I'll apply statistical methods to uncover patterns
    
    4. Use of available tools:
       - I'll use data analysis tools to explore and visualize the data
       - I'll use statistical tools to identify significant patterns
       - I'll use knowledge retrieval to access relevant information about sales analysis
    
    5. Expected outcome:
       A concise report highlighting the top 3 sales trends with supporting evidence from the data.
    
    READY: I am ready to execute the task.

This reasoning plan helps the agent organize its approach to the task, consider potential challenges, and ensure it delivers the expected output.

Was this page helpful?

YesNo

[Memory](/concepts/memory)[Planning](/concepts/planning)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Overview
  * Usage
  * How It Works
  * Configuration Options
  * Example
  * Error Handling
  * Example Reasoning Output



Assistant

Responses are generated using AI and may contain mistakes.


---

### Processes {#processes}

**Source:** [https://docs.crewai.com/concepts/processes](https://docs.crewai.com/concepts/processes)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Core Concepts

Processes

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Core Concepts

# Processes

Copy page

Detailed guide on workflow management through processes in CrewAI, with updated implementation details.

## 

​

Overview

Processes orchestrate the execution of tasks by agents, akin to project management in human teams. These processes ensure tasks are distributed and executed efficiently, in alignment with a predefined strategy.

## 

​

Process Implementations

  * **Sequential** : Executes tasks sequentially, ensuring tasks are completed in an orderly progression.
  * **Hierarchical** : Organizes tasks in a managerial hierarchy, where tasks are delegated and executed based on a structured chain of command. A manager language model (`manager_llm`) or a custom manager agent (`manager_agent`) must be specified in the crew to enable the hierarchical process, facilitating the creation and management of tasks by the manager.
  * **Consensual Process (Planned)** : Aiming for collaborative decision-making among agents on task execution, this process type introduces a democratic approach to task management within CrewAI. It is planned for future development and is not currently implemented in the codebase.



## 

​

The Role of Processes in Teamwork

Processes enable individual agents to operate as a cohesive unit, streamlining their efforts to achieve common objectives with efficiency and coherence.

## 

​

Assigning Processes to a Crew

To assign a process to a crew, specify the process type upon crew creation to set the execution strategy. For a hierarchical process, ensure to define `manager_llm` or `manager_agent` for the manager agent.
    
    
    from crewai import Crew, Process
    
    # Example: Creating a crew with a sequential process
    crew = Crew(
        agents=my_agents,
        tasks=my_tasks,
        process=Process.sequential
    )
    
    # Example: Creating a crew with a hierarchical process
    # Ensure to provide a manager_llm or manager_agent
    crew = Crew(
        agents=my_agents,
        tasks=my_tasks,
        process=Process.hierarchical,
        manager_llm="gpt-4o"
        # or
        # manager_agent=my_manager_agent
    )

**Note:** Ensure `my_agents` and `my_tasks` are defined prior to creating a `Crew` object, and for the hierarchical process, either `manager_llm` or `manager_agent` is also required.

## 

​

Sequential Process

This method mirrors dynamic team workflows, progressing through tasks in a thoughtful and systematic manner. Task execution follows the predefined order in the task list, with the output of one task serving as context for the next.

To customize task context, utilize the `context` parameter in the `Task` class to specify outputs that should be used as context for subsequent tasks.

## 

​

Hierarchical Process

Emulates a corporate hierarchy, CrewAI allows specifying a custom manager agent or automatically creates one, requiring the specification of a manager language model (`manager_llm`). This agent oversees task execution, including planning, delegation, and validation. Tasks are not pre-assigned; the manager allocates tasks to agents based on their capabilities, reviews outputs, and assesses task completion.

## 

​

Process Class: Detailed Overview

The `Process` class is implemented as an enumeration (`Enum`), ensuring type safety and restricting process values to the defined types (`sequential`, `hierarchical`). The consensual process is planned for future inclusion, emphasizing our commitment to continuous development and innovation.

## 

​

Conclusion

The structured collaboration facilitated by processes within CrewAI is crucial for enabling systematic teamwork among agents. This documentation has been updated to reflect the latest features, enhancements, and the planned integration of the Consensual Process, ensuring users have access to the most current and comprehensive information.

Was this page helpful?

YesNo

[LLMs](/concepts/llms)[Collaboration](/concepts/collaboration)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Overview
  * Process Implementations
  * The Role of Processes in Teamwork
  * Assigning Processes to a Crew
  * Sequential Process
  * Hierarchical Process
  * Process Class: Detailed Overview
  * Conclusion



Assistant

Responses are generated using AI and may contain mistakes.


---

### Planning {#planning}

**Source:** [https://docs.crewai.com/concepts/planning](https://docs.crewai.com/concepts/planning)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Core Concepts

Planning

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Core Concepts

# Planning

Copy page

Learn how to add planning to your CrewAI Crew and improve their performance.

## 

​

Overview

The planning feature in CrewAI allows you to add planning capability to your crew. When enabled, before each Crew iteration, all Crew information is sent to an AgentPlanner that will plan the tasks step by step, and this plan will be added to each task description.

### 

​

Using the Planning Feature

Getting started with the planning feature is very easy, the only step required is to add `planning=True` to your Crew:

Code
    
    
    from crewai import Crew, Agent, Task, Process
    
    # Assemble your crew with planning capabilities
    my_crew = Crew(
        agents=self.agents,
        tasks=self.tasks,
        process=Process.sequential,
        planning=True,
    )

From this point on, your crew will have planning enabled, and the tasks will be planned before each iteration.

#### 

​

Planning LLM

Now you can define the LLM that will be used to plan the tasks.

When running the base case example, you will see something like the output below, which represents the output of the `AgentPlanner` responsible for creating the step-by-step logic to add to the Agents’ tasks.

Code

Result
    
    
    from crewai import Crew, Agent, Task, Process
    
    # Assemble your crew with planning capabilities and custom LLM
    my_crew = Crew(
        agents=self.agents,
        tasks=self.tasks,
        process=Process.sequential,
        planning=True,
        planning_llm="gpt-4o"
    )
    
    # Run the crew
    my_crew.kickoff()

Was this page helpful?

YesNo

[Reasoning](/concepts/reasoning)[Testing](/concepts/testing)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Overview
  * Using the Planning Feature
  * Planning LLM



Assistant

Responses are generated using AI and may contain mistakes.


---

### Event Listeners {#event-listeners}

**Source:** [https://docs.crewai.com/concepts/event-listener](https://docs.crewai.com/concepts/event-listener)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Core Concepts

Event Listeners

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Core Concepts

# Event Listeners

Copy page

Tap into CrewAI events to build custom integrations and monitoring

## 

​

Overview

CrewAI provides a powerful event system that allows you to listen for and react to various events that occur during the execution of your Crew. This feature enables you to build custom integrations, monitoring solutions, logging systems, or any other functionality that needs to be triggered based on CrewAI’s internal events.

## 

​

How It Works

CrewAI uses an event bus architecture to emit events throughout the execution lifecycle. The event system is built on the following components:

  1. **CrewAIEventsBus** : A singleton event bus that manages event registration and emission
  2. **BaseEvent** : Base class for all events in the system
  3. **BaseEventListener** : Abstract base class for creating custom event listeners



When specific actions occur in CrewAI (like a Crew starting execution, an Agent completing a task, or a tool being used), the system emits corresponding events. You can register handlers for these events to execute custom code when they occur.

CrewAI Enterprise provides a built-in Prompt Tracing feature that leverages the event system to track, store, and visualize all prompts, completions, and associated metadata. This provides powerful debugging capabilities and transparency into your agent operations.

With Prompt Tracing you can:

  * View the complete history of all prompts sent to your LLM
  * Track token usage and costs
  * Debug agent reasoning failures
  * Share prompt sequences with your team
  * Compare different prompt strategies
  * Export traces for compliance and auditing



## 

​

Creating a Custom Event Listener

To create a custom event listener, you need to:

  1. Create a class that inherits from `BaseEventListener`
  2. Implement the `setup_listeners` method
  3. Register handlers for the events you’re interested in
  4. Create an instance of your listener in the appropriate file



Here’s a simple example of a custom event listener class:
    
    
    from crewai.utilities.events import (
        CrewKickoffStartedEvent,
        CrewKickoffCompletedEvent,
        AgentExecutionCompletedEvent,
    )
    from crewai.utilities.events.base_event_listener import BaseEventListener
    
    class MyCustomListener(BaseEventListener):
        def __init__(self):
            super().__init__()
    
        def setup_listeners(self, crewai_event_bus):
            @crewai_event_bus.on(CrewKickoffStartedEvent)
            def on_crew_started(source, event):
                print(f"Crew '{event.crew_name}' has started execution!")
    
            @crewai_event_bus.on(CrewKickoffCompletedEvent)
            def on_crew_completed(source, event):
                print(f"Crew '{event.crew_name}' has completed execution!")
                print(f"Output: {event.output}")
    
            @crewai_event_bus.on(AgentExecutionCompletedEvent)
            def on_agent_execution_completed(source, event):
                print(f"Agent '{event.agent.role}' completed task")
                print(f"Output: {event.output}")

## 

​

Properly Registering Your Listener

Simply defining your listener class isn’t enough. You need to create an instance of it and ensure it’s imported in your application. This ensures that:

  1. The event handlers are registered with the event bus
  2. The listener instance remains in memory (not garbage collected)
  3. The listener is active when events are emitted



### 

​

Option 1: Import and Instantiate in Your Crew or Flow Implementation

The most important thing is to create an instance of your listener in the file where your Crew or Flow is defined and executed:

#### 

​

For Crew-based Applications

Create and import your listener at the top of your Crew implementation file:
    
    
    # In your crew.py file
    from crewai import Agent, Crew, Task
    from my_listeners import MyCustomListener
    
    # Create an instance of your listener
    my_listener = MyCustomListener()
    
    class MyCustomCrew:
        # Your crew implementation...
    
        def crew(self):
            return Crew(
                agents=[...],
                tasks=[...],
                # ...
            )

#### 

​

For Flow-based Applications

Create and import your listener at the top of your Flow implementation file:
    
    
    # In your main.py or flow.py file
    from crewai.flow import Flow, listen, start
    from my_listeners import MyCustomListener
    
    # Create an instance of your listener
    my_listener = MyCustomListener()
    
    class MyCustomFlow(Flow):
        # Your flow implementation...
    
        @start()
        def first_step(self):
            # ...

This ensures that your listener is loaded and active when your Crew or Flow is executed.

### 

​

Option 2: Create a Package for Your Listeners

For a more structured approach, especially if you have multiple listeners:

  1. Create a package for your listeners:


    
    
    my_project/
      ├── listeners/
      │   ├── __init__.py
      │   ├── my_custom_listener.py
      │   └── another_listener.py

  2. In `my_custom_listener.py`, define your listener class and create an instance:


    
    
    # my_custom_listener.py
    from crewai.utilities.events.base_event_listener import BaseEventListener
    # ... import events ...
    
    class MyCustomListener(BaseEventListener):
        # ... implementation ...
    
    # Create an instance of your listener
    my_custom_listener = MyCustomListener()

  3. In `__init__.py`, import the listener instances to ensure they’re loaded:


    
    
    # __init__.py
    from .my_custom_listener import my_custom_listener
    from .another_listener import another_listener
    
    # Optionally export them if you need to access them elsewhere
    __all__ = ['my_custom_listener', 'another_listener']

  4. Import your listeners package in your Crew or Flow file:


    
    
    # In your crew.py or flow.py file
    import my_project.listeners  # This loads all your listeners
    
    class MyCustomCrew:
        # Your crew implementation...

This is exactly how CrewAI’s built-in `agentops_listener` is registered. In the CrewAI codebase, you’ll find:
    
    
    # src/crewai/utilities/events/third_party/__init__.py
    from .agentops_listener import agentops_listener

This ensures the `agentops_listener` is loaded when the `crewai.utilities.events` package is imported.

## 

​

Available Event Types

CrewAI provides a wide range of events that you can listen for:

### 

​

Crew Events

  * **CrewKickoffStartedEvent** : Emitted when a Crew starts execution
  * **CrewKickoffCompletedEvent** : Emitted when a Crew completes execution
  * **CrewKickoffFailedEvent** : Emitted when a Crew fails to complete execution
  * **CrewTestStartedEvent** : Emitted when a Crew starts testing
  * **CrewTestCompletedEvent** : Emitted when a Crew completes testing
  * **CrewTestFailedEvent** : Emitted when a Crew fails to complete testing
  * **CrewTrainStartedEvent** : Emitted when a Crew starts training
  * **CrewTrainCompletedEvent** : Emitted when a Crew completes training
  * **CrewTrainFailedEvent** : Emitted when a Crew fails to complete training



### 

​

Agent Events

  * **AgentExecutionStartedEvent** : Emitted when an Agent starts executing a task
  * **AgentExecutionCompletedEvent** : Emitted when an Agent completes executing a task
  * **AgentExecutionErrorEvent** : Emitted when an Agent encounters an error during execution



### 

​

Task Events

  * **TaskStartedEvent** : Emitted when a Task starts execution
  * **TaskCompletedEvent** : Emitted when a Task completes execution
  * **TaskFailedEvent** : Emitted when a Task fails to complete execution
  * **TaskEvaluationEvent** : Emitted when a Task is evaluated



### 

​

Tool Usage Events

  * **ToolUsageStartedEvent** : Emitted when a tool execution is started
  * **ToolUsageFinishedEvent** : Emitted when a tool execution is completed
  * **ToolUsageErrorEvent** : Emitted when a tool execution encounters an error
  * **ToolValidateInputErrorEvent** : Emitted when a tool input validation encounters an error
  * **ToolExecutionErrorEvent** : Emitted when a tool execution encounters an error
  * **ToolSelectionErrorEvent** : Emitted when there’s an error selecting a tool



### 

​

Knowledge Events

  * **KnowledgeRetrievalStartedEvent** : Emitted when a knowledge retrieval is started
  * **KnowledgeRetrievalCompletedEvent** : Emitted when a knowledge retrieval is completed
  * **KnowledgeQueryStartedEvent** : Emitted when a knowledge query is started
  * **KnowledgeQueryCompletedEvent** : Emitted when a knowledge query is completed
  * **KnowledgeQueryFailedEvent** : Emitted when a knowledge query fails
  * **KnowledgeSearchQueryFailedEvent** : Emitted when a knowledge search query fails



### 

​

Flow Events

  * **FlowCreatedEvent** : Emitted when a Flow is created
  * **FlowStartedEvent** : Emitted when a Flow starts execution
  * **FlowFinishedEvent** : Emitted when a Flow completes execution
  * **FlowPlotEvent** : Emitted when a Flow is plotted
  * **MethodExecutionStartedEvent** : Emitted when a Flow method starts execution
  * **MethodExecutionFinishedEvent** : Emitted when a Flow method completes execution
  * **MethodExecutionFailedEvent** : Emitted when a Flow method fails to complete execution



### 

​

LLM Events

  * **LLMCallStartedEvent** : Emitted when an LLM call starts
  * **LLMCallCompletedEvent** : Emitted when an LLM call completes
  * **LLMCallFailedEvent** : Emitted when an LLM call fails
  * **LLMStreamChunkEvent** : Emitted for each chunk received during streaming LLM responses



## 

​

Event Handler Structure

Each event handler receives two parameters:

  1. **source** : The object that emitted the event
  2. **event** : The event instance, containing event-specific data



The structure of the event object depends on the event type, but all events inherit from `BaseEvent` and include:

  * **timestamp** : The time when the event was emitted
  * **type** : A string identifier for the event type



Additional fields vary by event type. For example, `CrewKickoffCompletedEvent` includes `crew_name` and `output` fields.

## 

​

Real-World Example: Integration with AgentOps

CrewAI includes an example of a third-party integration with [AgentOps](https://github.com/AgentOps-AI/agentops), a monitoring and observability platform for AI agents. Here’s how it’s implemented:
    
    
    from typing import Optional
    
    from crewai.utilities.events import (
        CrewKickoffCompletedEvent,
        ToolUsageErrorEvent,
        ToolUsageStartedEvent,
    )
    from crewai.utilities.events.base_event_listener import BaseEventListener
    from crewai.utilities.events.crew_events import CrewKickoffStartedEvent
    from crewai.utilities.events.task_events import TaskEvaluationEvent
    
    try:
        import agentops
        AGENTOPS_INSTALLED = True
    except ImportError:
        AGENTOPS_INSTALLED = False
    
    class AgentOpsListener(BaseEventListener):
        tool_event: Optional["agentops.ToolEvent"] = None
        session: Optional["agentops.Session"] = None
    
        def __init__(self):
            super().__init__()
    
        def setup_listeners(self, crewai_event_bus):
            if not AGENTOPS_INSTALLED:
                return
    
            @crewai_event_bus.on(CrewKickoffStartedEvent)
            def on_crew_kickoff_started(source, event: CrewKickoffStartedEvent):
                self.session = agentops.init()
                for agent in source.agents:
                    if self.session:
                        self.session.create_agent(
                            name=agent.role,
                            agent_id=str(agent.id),
                        )
    
            @crewai_event_bus.on(CrewKickoffCompletedEvent)
            def on_crew_kickoff_completed(source, event: CrewKickoffCompletedEvent):
                if self.session:
                    self.session.end_session(
                        end_state="Success",
                        end_state_reason="Finished Execution",
                    )
    
            @crewai_event_bus.on(ToolUsageStartedEvent)
            def on_tool_usage_started(source, event: ToolUsageStartedEvent):
                self.tool_event = agentops.ToolEvent(name=event.tool_name)
                if self.session:
                    self.session.record(self.tool_event)
    
            @crewai_event_bus.on(ToolUsageErrorEvent)
            def on_tool_usage_error(source, event: ToolUsageErrorEvent):
                agentops.ErrorEvent(exception=event.error, trigger_event=self.tool_event)

This listener initializes an AgentOps session when a Crew starts, registers agents with AgentOps, tracks tool usage, and ends the session when the Crew completes.

The AgentOps listener is registered in CrewAI’s event system through the import in `src/crewai/utilities/events/third_party/__init__.py`:
    
    
    from .agentops_listener import agentops_listener

This ensures the `agentops_listener` is loaded when the `crewai.utilities.events` package is imported.

## 

​

Advanced Usage: Scoped Handlers

For temporary event handling (useful for testing or specific operations), you can use the `scoped_handlers` context manager:
    
    
    from crewai.utilities.events import crewai_event_bus, CrewKickoffStartedEvent
    
    with crewai_event_bus.scoped_handlers():
        @crewai_event_bus.on(CrewKickoffStartedEvent)
        def temp_handler(source, event):
            print("This handler only exists within this context")
    
        # Do something that emits events
    
    # Outside the context, the temporary handler is removed

## 

​

Use Cases

Event listeners can be used for a variety of purposes:

  1. **Logging and Monitoring** : Track the execution of your Crew and log important events
  2. **Analytics** : Collect data about your Crew’s performance and behavior
  3. **Debugging** : Set up temporary listeners to debug specific issues
  4. **Integration** : Connect CrewAI with external systems like monitoring platforms, databases, or notification services
  5. **Custom Behavior** : Trigger custom actions based on specific events



## 

​

Best Practices

  1. **Keep Handlers Light** : Event handlers should be lightweight and avoid blocking operations
  2. **Error Handling** : Include proper error handling in your event handlers to prevent exceptions from affecting the main execution
  3. **Cleanup** : If your listener allocates resources, ensure they’re properly cleaned up
  4. **Selective Listening** : Only listen for events you actually need to handle
  5. **Testing** : Test your event listeners in isolation to ensure they behave as expected



By leveraging CrewAI’s event system, you can extend its functionality and integrate it seamlessly with your existing infrastructure.

Was this page helpful?

YesNo

[Tools](/concepts/tools)[MCP Servers as Tools in CrewAI](/mcp/overview)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Overview
  * How It Works
  * Creating a Custom Event Listener
  * Properly Registering Your Listener
  * Option 1: Import and Instantiate in Your Crew or Flow Implementation
  * For Crew-based Applications
  * For Flow-based Applications
  * Option 2: Create a Package for Your Listeners
  * Available Event Types
  * Crew Events
  * Agent Events
  * Task Events
  * Tool Usage Events
  * Knowledge Events
  * Flow Events
  * LLM Events
  * Event Handler Structure
  * Real-World Example: Integration with AgentOps
  * Advanced Usage: Scoped Handlers
  * Use Cases
  * Best Practices



Assistant

Responses are generated using AI and may contain mistakes.


---

### Collaboration {#collaboration}

**Source:** [https://docs.crewai.com/concepts/collaboration](https://docs.crewai.com/concepts/collaboration)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Core Concepts

Collaboration

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Core Concepts

# Collaboration

Copy page

How to enable agents to work together, delegate tasks, and communicate effectively within CrewAI teams.

## 

​

Overview

Collaboration in CrewAI enables agents to work together as a team by delegating tasks and asking questions to leverage each other’s expertise. When `allow_delegation=True`, agents automatically gain access to powerful collaboration tools.

## 

​

Quick Start: Enable Collaboration
    
    
    from crewai import Agent, Crew, Task
    
    # Enable collaboration for agents
    researcher = Agent(
        role="Research Specialist",
        goal="Conduct thorough research on any topic",
        backstory="Expert researcher with access to various sources",
        allow_delegation=True,  # 🔑 Key setting for collaboration
        verbose=True
    )
    
    writer = Agent(
        role="Content Writer", 
        goal="Create engaging content based on research",
        backstory="Skilled writer who transforms research into compelling content",
        allow_delegation=True,  # 🔑 Enables asking questions to other agents
        verbose=True
    )
    
    # Agents can now collaborate automatically
    crew = Crew(
        agents=[researcher, writer],
        tasks=[...],
        verbose=True
    )

## 

​

How Agent Collaboration Works

When `allow_delegation=True`, CrewAI automatically provides agents with two powerful tools:

### 

​

1\. **Delegate Work Tool**

Allows agents to assign tasks to teammates with specific expertise.
    
    
    # Agent automatically gets this tool:
    # Delegate work to coworker(task: str, context: str, coworker: str)

### 

​

2\. **Ask Question Tool**

Enables agents to ask specific questions to gather information from colleagues.
    
    
    # Agent automatically gets this tool:
    # Ask question to coworker(question: str, context: str, coworker: str)

## 

​

Collaboration in Action

Here’s a complete example showing agents collaborating on a content creation task:
    
    
    from crewai import Agent, Crew, Task, Process
    
    # Create collaborative agents
    researcher = Agent(
        role="Research Specialist",
        goal="Find accurate, up-to-date information on any topic",
        backstory="""You're a meticulous researcher with expertise in finding 
        reliable sources and fact-checking information across various domains.""",
        allow_delegation=True,
        verbose=True
    )
    
    writer = Agent(
        role="Content Writer",
        goal="Create engaging, well-structured content",
        backstory="""You're a skilled content writer who excels at transforming 
        research into compelling, readable content for different audiences.""",
        allow_delegation=True,
        verbose=True
    )
    
    editor = Agent(
        role="Content Editor",
        goal="Ensure content quality and consistency",
        backstory="""You're an experienced editor with an eye for detail, 
        ensuring content meets high standards for clarity and accuracy.""",
        allow_delegation=True,
        verbose=True
    )
    
    # Create a task that encourages collaboration
    article_task = Task(
        description="""Write a comprehensive 1000-word article about 'The Future of AI in Healthcare'.
        
        The article should include:
        - Current AI applications in healthcare
        - Emerging trends and technologies  
        - Potential challenges and ethical considerations
        - Expert predictions for the next 5 years
        
        Collaborate with your teammates to ensure accuracy and quality.""",
        expected_output="A well-researched, engaging 1000-word article with proper structure and citations",
        agent=writer  # Writer leads, but can delegate research to researcher
    )
    
    # Create collaborative crew
    crew = Crew(
        agents=[researcher, writer, editor],
        tasks=[article_task],
        process=Process.sequential,
        verbose=True
    )
    
    result = crew.kickoff()

## 

​

Collaboration Patterns

### 

​

Pattern 1: Research → Write → Edit
    
    
    research_task = Task(
        description="Research the latest developments in quantum computing",
        expected_output="Comprehensive research summary with key findings and sources",
        agent=researcher
    )
    
    writing_task = Task(
        description="Write an article based on the research findings",
        expected_output="Engaging 800-word article about quantum computing",
        agent=writer,
        context=[research_task]  # Gets research output as context
    )
    
    editing_task = Task(
        description="Edit and polish the article for publication",
        expected_output="Publication-ready article with improved clarity and flow",
        agent=editor,
        context=[writing_task]  # Gets article draft as context
    )

### 

​

Pattern 2: Collaborative Single Task
    
    
    collaborative_task = Task(
        description="""Create a marketing strategy for a new AI product.
        
        Writer: Focus on messaging and content strategy
        Researcher: Provide market analysis and competitor insights
        
        Work together to create a comprehensive strategy.""",
        expected_output="Complete marketing strategy with research backing",
        agent=writer  # Lead agent, but can delegate to researcher
    )

## 

​

Hierarchical Collaboration

For complex projects, use a hierarchical process with a manager agent:
    
    
    from crewai import Agent, Crew, Task, Process
    
    # Manager agent coordinates the team
    manager = Agent(
        role="Project Manager",
        goal="Coordinate team efforts and ensure project success",
        backstory="Experienced project manager skilled at delegation and quality control",
        allow_delegation=True,
        verbose=True
    )
    
    # Specialist agents
    researcher = Agent(
        role="Researcher",
        goal="Provide accurate research and analysis",
        backstory="Expert researcher with deep analytical skills",
        allow_delegation=False,  # Specialists focus on their expertise
        verbose=True
    )
    
    writer = Agent(
        role="Writer", 
        goal="Create compelling content",
        backstory="Skilled writer who creates engaging content",
        allow_delegation=False,
        verbose=True
    )
    
    # Manager-led task
    project_task = Task(
        description="Create a comprehensive market analysis report with recommendations",
        expected_output="Executive summary, detailed analysis, and strategic recommendations",
        agent=manager  # Manager will delegate to specialists
    )
    
    # Hierarchical crew
    crew = Crew(
        agents=[manager, researcher, writer],
        tasks=[project_task],
        process=Process.hierarchical,  # Manager coordinates everything
        manager_llm="gpt-4o",  # Specify LLM for manager
        verbose=True
    )

## 

​

Best Practices for Collaboration

### 

​

1\. **Clear Role Definition**
    
    
    # ✅ Good: Specific, complementary roles
    researcher = Agent(role="Market Research Analyst", ...)
    writer = Agent(role="Technical Content Writer", ...)
    
    # ❌ Avoid: Overlapping or vague roles  
    agent1 = Agent(role="General Assistant", ...)
    agent2 = Agent(role="Helper", ...)

### 

​

2\. **Strategic Delegation Enabling**
    
    
    # ✅ Enable delegation for coordinators and generalists
    lead_agent = Agent(
        role="Content Lead",
        allow_delegation=True,  # Can delegate to specialists
        ...
    )
    
    # ✅ Disable for focused specialists (optional)
    specialist_agent = Agent(
        role="Data Analyst", 
        allow_delegation=False,  # Focuses on core expertise
        ...
    )

### 

​

3\. **Context Sharing**
    
    
    # ✅ Use context parameter for task dependencies
    writing_task = Task(
        description="Write article based on research",
        agent=writer,
        context=[research_task],  # Shares research results
        ...
    )

### 

​

4\. **Clear Task Descriptions**
    
    
    # ✅ Specific, actionable descriptions
    Task(
        description="""Research competitors in the AI chatbot space.
        Focus on: pricing models, key features, target markets.
        Provide data in a structured format.""",
        ...
    )
    
    # ❌ Vague descriptions that don't guide collaboration
    Task(description="Do some research about chatbots", ...)

## 

​

Troubleshooting Collaboration

### 

​

Issue: Agents Not Collaborating

**Symptoms:** Agents work in isolation, no delegation occurs
    
    
    # ✅ Solution: Ensure delegation is enabled
    agent = Agent(
        role="...",
        allow_delegation=True,  # This is required!
        ...
    )

### 

​

Issue: Too Much Back-and-Forth

**Symptoms:** Agents ask excessive questions, slow progress
    
    
    # ✅ Solution: Provide better context and specific roles
    Task(
        description="""Write a technical blog post about machine learning.
        
        Context: Target audience is software developers with basic ML knowledge.
        Length: 1200 words
        Include: code examples, practical applications, best practices
        
        If you need specific technical details, delegate research to the researcher.""",
        ...
    )

### 

​

Issue: Delegation Loops

**Symptoms:** Agents delegate back and forth indefinitely
    
    
    # ✅ Solution: Clear hierarchy and responsibilities
    manager = Agent(role="Manager", allow_delegation=True)
    specialist1 = Agent(role="Specialist A", allow_delegation=False)  # No re-delegation
    specialist2 = Agent(role="Specialist B", allow_delegation=False)

## 

​

Advanced Collaboration Features

### 

​

Custom Collaboration Rules
    
    
    # Set specific collaboration guidelines in agent backstory
    agent = Agent(
        role="Senior Developer",
        backstory="""You lead development projects and coordinate with team members.
        
        Collaboration guidelines:
        - Delegate research tasks to the Research Analyst
        - Ask the Designer for UI/UX guidance  
        - Consult the QA Engineer for testing strategies
        - Only escalate blocking issues to the Project Manager""",
        allow_delegation=True
    )

### 

​

Monitoring Collaboration
    
    
    def track_collaboration(output):
        """Track collaboration patterns"""
        if "Delegate work to coworker" in output.raw:
            print("🤝 Delegation occurred")
        if "Ask question to coworker" in output.raw:
            print("❓ Question asked")
    
    crew = Crew(
        agents=[...],
        tasks=[...],
        step_callback=track_collaboration,  # Monitor collaboration
        verbose=True
    )

## 

​

Memory and Learning

Enable agents to remember past collaborations:
    
    
    agent = Agent(
        role="Content Lead",
        memory=True,  # Remembers past interactions
        allow_delegation=True,
        verbose=True
    )

With memory enabled, agents learn from previous collaborations and improve their delegation decisions over time.

## 

​

Next Steps

  * **Try the examples** : Start with the basic collaboration example
  * **Experiment with roles** : Test different agent role combinations
  * **Monitor interactions** : Use `verbose=True` to see collaboration in action
  * **Optimize task descriptions** : Clear tasks lead to better collaboration
  * **Scale up** : Try hierarchical processes for complex projects



Collaboration transforms individual AI agents into powerful teams that can tackle complex, multi-faceted challenges together.

Was this page helpful?

YesNo

[Processes](/concepts/processes)[Training](/concepts/training)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Overview
  * Quick Start: Enable Collaboration
  * How Agent Collaboration Works
  * 1\. Delegate Work Tool
  * 2\. Ask Question Tool
  * Collaboration in Action
  * Collaboration Patterns
  * Pattern 1: Research → Write → Edit
  * Pattern 2: Collaborative Single Task
  * Hierarchical Collaboration
  * Best Practices for Collaboration
  * 1\. Clear Role Definition
  * 2\. Strategic Delegation Enabling
  * 3\. Context Sharing
  * 4\. Clear Task Descriptions
  * Troubleshooting Collaboration
  * Issue: Agents Not Collaborating
  * Issue: Too Much Back-and-Forth
  * Issue: Delegation Loops
  * Advanced Collaboration Features
  * Custom Collaboration Rules
  * Monitoring Collaboration
  * Memory and Learning
  * Next Steps



Assistant

Responses are generated using AI and may contain mistakes.


---

### Knowledge {#knowledge}

**Source:** [https://docs.crewai.com/concepts/knowledge](https://docs.crewai.com/concepts/knowledge)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Core Concepts

Knowledge

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Core Concepts

# Knowledge

Copy page

What is knowledge in CrewAI and how to use it.

## 

​

Overview

Knowledge in CrewAI is a powerful system that allows AI agents to access and utilize external information sources during their tasks. Think of it as giving your agents a reference library they can consult while working.

Key benefits of using Knowledge:

  * Enhance agents with domain-specific information
  * Support decisions with real-world data
  * Maintain context across conversations
  * Ground responses in factual information



## 

​

Quickstart Examples

For file-based Knowledge Sources, make sure to place your files in a `knowledge` directory at the root of your project. Also, use relative paths from the `knowledge` directory when creating the source.

### 

​

Basic String Knowledge Example

Code
    
    
    from crewai import Agent, Task, Crew, Process, LLM
    from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
    
    # Create a knowledge source
    content = "Users name is John. He is 30 years old and lives in San Francisco."
    string_source = StringKnowledgeSource(content=content)
    
    # Create an LLM with a temperature of 0 to ensure deterministic outputs
    llm = LLM(model="gpt-4o-mini", temperature=0)
    
    # Create an agent with the knowledge store
    agent = Agent(
        role="About User",
        goal="You know everything about the user.",
        backstory="You are a master at understanding people and their preferences.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )
    
    task = Task(
        description="Answer the following questions about the user: {question}",
        expected_output="An answer to the question.",
        agent=agent,
    )
    
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True,
        process=Process.sequential,
        knowledge_sources=[string_source], # Enable knowledge by adding the sources here
    )
    
    result = crew.kickoff(inputs={"question": "What city does John live in and how old is he?"})

### 

​

Web Content Knowledge Example

You need to install `docling` for the following example to work: `uv add docling`

Code
    
    
    from crewai import LLM, Agent, Crew, Process, Task
    from crewai.knowledge.source.crew_docling_source import CrewDoclingSource
    
    # Create a knowledge source from web content
    content_source = CrewDoclingSource(
        file_paths=[
            "https://lilianweng.github.io/posts/2024-11-28-reward-hacking",
            "https://lilianweng.github.io/posts/2024-07-07-hallucination",
        ],
    )
    
    # Create an LLM with a temperature of 0 to ensure deterministic outputs
    llm = LLM(model="gpt-4o-mini", temperature=0)
    
    # Create an agent with the knowledge store
    agent = Agent(
        role="About papers",
        goal="You know everything about the papers.",
        backstory="You are a master at understanding papers and their content.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )
    
    task = Task(
        description="Answer the following questions about the papers: {question}",
        expected_output="An answer to the question.",
        agent=agent,
    )
    
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True,
        process=Process.sequential,
        knowledge_sources=[content_source],
    )
    
    result = crew.kickoff(
        inputs={"question": "What is the reward hacking paper about? Be sure to provide sources."}
    )

## 

​

Supported Knowledge Sources

CrewAI supports various types of knowledge sources out of the box:

## Text Sources

  * Raw strings
  * Text files (.txt)
  * PDF documents



## Structured Data

  * CSV files
  * Excel spreadsheets
  * JSON documents



### 

​

Text File Knowledge Source
    
    
    from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
    
    text_source = TextFileKnowledgeSource(
        file_paths=["document.txt", "another.txt"]
    )

### 

​

PDF Knowledge Source
    
    
    from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
    
    pdf_source = PDFKnowledgeSource(
        file_paths=["document.pdf", "another.pdf"]
    )

### 

​

CSV Knowledge Source
    
    
    from crewai.knowledge.source.csv_knowledge_source import CSVKnowledgeSource
    
    csv_source = CSVKnowledgeSource(
        file_paths=["data.csv"]
    )

### 

​

Excel Knowledge Source
    
    
    from crewai.knowledge.source.excel_knowledge_source import ExcelKnowledgeSource
    
    excel_source = ExcelKnowledgeSource(
        file_paths=["spreadsheet.xlsx"]
    )

### 

​

JSON Knowledge Source
    
    
    from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource
    
    json_source = JSONKnowledgeSource(
        file_paths=["data.json"]
    )

Please ensure that you create the ./knowledge folder. All source files (e.g., .txt, .pdf, .xlsx, .json) should be placed in this folder for centralized management.

## 

​

Agent vs Crew Knowledge: Complete Guide

**Understanding Knowledge Levels** : CrewAI supports knowledge at both agent and crew levels. This section clarifies exactly how each works, when they’re initialized, and addresses common misconceptions about dependencies.

### 

​

How Knowledge Initialization Actually Works

Here’s exactly what happens when you use knowledge:

#### 

​

Agent-Level Knowledge (Independent)
    
    
    from crewai import Agent, Task, Crew
    from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
    
    # Agent with its own knowledge - NO crew knowledge needed
    specialist_knowledge = StringKnowledgeSource(
        content="Specialized technical information for this agent only"
    )
    
    specialist_agent = Agent(
        role="Technical Specialist",
        goal="Provide technical expertise",
        backstory="Expert in specialized technical domains",
        knowledge_sources=[specialist_knowledge]  # Agent-specific knowledge
    )
    
    task = Task(
        description="Answer technical questions",
        agent=specialist_agent,
        expected_output="Technical answer"
    )
    
    # No crew-level knowledge required
    crew = Crew(
        agents=[specialist_agent],
        tasks=[task]
    )
    
    result = crew.kickoff()  # Agent knowledge works independently

#### 

​

What Happens During `crew.kickoff()`

When you call `crew.kickoff()`, here’s the exact sequence:
    
    
    # During kickoff
    for agent in self.agents:
        agent.crew = self  # Agent gets reference to crew
        agent.set_knowledge(crew_embedder=self.embedder)  # Agent knowledge initialized
        agent.create_agent_executor()

#### 

​

Storage Independence

Each knowledge level uses independent storage collections:
    
    
    # Agent knowledge storage
    agent_collection_name = agent.role  # e.g., "Technical Specialist"
    
    # Crew knowledge storage  
    crew_collection_name = "crew"
    
    # Both stored in same ChromaDB instance but different collections
    # Path: ~/.local/share/CrewAI/{project}/knowledge/
    #   ├── crew/                    # Crew knowledge collection
    #   ├── Technical Specialist/    # Agent knowledge collection
    #   └── Another Agent Role/      # Another agent's collection

### 

​

Complete Working Examples

#### 

​

Example 1: Agent-Only Knowledge
    
    
    from crewai import Agent, Task, Crew
    from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
    
    # Agent-specific knowledge
    agent_knowledge = StringKnowledgeSource(
        content="Agent-specific information that only this agent needs"
    )
    
    agent = Agent(
        role="Specialist",
        goal="Use specialized knowledge",
        backstory="Expert with specific knowledge",
        knowledge_sources=[agent_knowledge],
        embedder={  # Agent can have its own embedder
            "provider": "openai",
            "config": {"model": "text-embedding-3-small"}
        }
    )
    
    task = Task(
        description="Answer using your specialized knowledge",
        agent=agent,
        expected_output="Answer based on agent knowledge"
    )
    
    # No crew knowledge needed
    crew = Crew(agents=[agent], tasks=[task])
    result = crew.kickoff()  # Works perfectly

#### 

​

Example 2: Both Agent and Crew Knowledge
    
    
    # Crew-wide knowledge (shared by all agents)
    crew_knowledge = StringKnowledgeSource(
        content="Company policies and general information for all agents"
    )
    
    # Agent-specific knowledge
    specialist_knowledge = StringKnowledgeSource(
        content="Technical specifications only the specialist needs"
    )
    
    specialist = Agent(
        role="Technical Specialist",
        goal="Provide technical expertise",
        backstory="Technical expert",
        knowledge_sources=[specialist_knowledge]  # Agent-specific
    )
    
    generalist = Agent(
        role="General Assistant", 
        goal="Provide general assistance",
        backstory="General helper"
        # No agent-specific knowledge
    )
    
    crew = Crew(
        agents=[specialist, generalist],
        tasks=[...],
        knowledge_sources=[crew_knowledge]  # Crew-wide knowledge
    )
    
    # Result:
    # - specialist gets: crew_knowledge + specialist_knowledge
    # - generalist gets: crew_knowledge only

#### 

​

Example 3: Multiple Agents with Different Knowledge
    
    
    # Different knowledge for different agents
    sales_knowledge = StringKnowledgeSource(content="Sales procedures and pricing")
    tech_knowledge = StringKnowledgeSource(content="Technical documentation")
    support_knowledge = StringKnowledgeSource(content="Support procedures")
    
    sales_agent = Agent(
        role="Sales Representative",
        knowledge_sources=[sales_knowledge],
        embedder={"provider": "openai", "config": {"model": "text-embedding-3-small"}}
    )
    
    tech_agent = Agent(
        role="Technical Expert", 
        knowledge_sources=[tech_knowledge],
        embedder={"provider": "ollama", "config": {"model": "mxbai-embed-large"}}
    )
    
    support_agent = Agent(
        role="Support Specialist",
        knowledge_sources=[support_knowledge]
        # Will use crew embedder as fallback
    )
    
    crew = Crew(
        agents=[sales_agent, tech_agent, support_agent],
        tasks=[...],
        embedder={  # Fallback embedder for agents without their own
            "provider": "google",
            "config": {"model": "text-embedding-004"}
        }
    )
    
    # Each agent gets only their specific knowledge
    # Each can use different embedding providers

Unlike retrieval from a vector database using a tool, agents preloaded with knowledge will not need a retrieval persona or task. Simply add the relevant knowledge sources your agent or crew needs to function.

Knowledge sources can be added at the agent or crew level. Crew level knowledge sources will be used by **all agents** in the crew. Agent level knowledge sources will be used by the **specific agent** that is preloaded with the knowledge.

## 

​

Knowledge Configuration

You can configure the knowledge configuration for the crew or agent.

Code
    
    
    from crewai.knowledge.knowledge_config import KnowledgeConfig
    
    knowledge_config = KnowledgeConfig(results_limit=10, score_threshold=0.5)
    
    agent = Agent(
        ...
        knowledge_config=knowledge_config
    )

`results_limit`: is the number of relevant documents to return. Default is 3. `score_threshold`: is the minimum score for a document to be considered relevant. Default is 0.35.

## 

​

Supported Knowledge Parameters

​

sources

List[BaseKnowledgeSource]

required

List of knowledge sources that provide content to be stored and queried. Can include PDF, CSV, Excel, JSON, text files, or string content.

​

collection_name

str

Name of the collection where the knowledge will be stored. Used to identify different sets of knowledge. Defaults to “knowledge” if not provided.

​

storage

Optional[KnowledgeStorage]

Custom storage configuration for managing how the knowledge is stored and retrieved. If not provided, a default storage will be created.

## 

​

Knowledge Storage Transparency

**Understanding Knowledge Storage** : CrewAI automatically stores knowledge sources in platform-specific directories using ChromaDB for vector storage. Understanding these locations and defaults helps with production deployments, debugging, and storage management.

### 

​

Where CrewAI Stores Knowledge Files

By default, CrewAI uses the same storage system as memory, storing knowledge in platform-specific directories:

#### 

​

Default Storage Locations by Platform

**macOS:**
    
    
    ~/Library/Application Support/CrewAI/{project_name}/
    └── knowledge/                    # Knowledge ChromaDB files
        ├── chroma.sqlite3           # ChromaDB metadata
        ├── {collection_id}/         # Vector embeddings
        └── knowledge_{collection}/  # Named collections

**Linux:**
    
    
    ~/.local/share/CrewAI/{project_name}/
    └── knowledge/
        ├── chroma.sqlite3
        ├── {collection_id}/
        └── knowledge_{collection}/

**Windows:**
    
    
    C:\Users\{username}\AppData\Local\CrewAI\{project_name}\
    └── knowledge\
        ├── chroma.sqlite3
        ├── {collection_id}\
        └── knowledge_{collection}\

### 

​

Finding Your Knowledge Storage Location

To see exactly where CrewAI is storing your knowledge files:
    
    
    from crewai.utilities.paths import db_storage_path
    import os
    
    # Get the knowledge storage path
    knowledge_path = os.path.join(db_storage_path(), "knowledge")
    print(f"Knowledge storage location: {knowledge_path}")
    
    # List knowledge collections and files
    if os.path.exists(knowledge_path):
        print("\nKnowledge storage contents:")
        for item in os.listdir(knowledge_path):
            item_path = os.path.join(knowledge_path, item)
            if os.path.isdir(item_path):
                print(f"📁 Collection: {item}/")
                # Show collection contents
                try:
                    for subitem in os.listdir(item_path):
                        print(f"   └── {subitem}")
                except PermissionError:
                    print(f"   └── (permission denied)")
            else:
                print(f"📄 {item}")
    else:
        print("No knowledge storage found yet.")

### 

​

Controlling Knowledge Storage Locations

#### 

​

Option 1: Environment Variable (Recommended)
    
    
    import os
    from crewai import Crew
    
    # Set custom storage location for all CrewAI data
    os.environ["CREWAI_STORAGE_DIR"] = "./my_project_storage"
    
    # All knowledge will now be stored in ./my_project_storage/knowledge/
    crew = Crew(
        agents=[...],
        tasks=[...],
        knowledge_sources=[...]
    )

#### 

​

Option 2: Custom Knowledge Storage
    
    
    from crewai.knowledge.storage.knowledge_storage import KnowledgeStorage
    from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
    
    # Create custom storage with specific embedder
    custom_storage = KnowledgeStorage(
        embedder={
            "provider": "ollama",
            "config": {"model": "mxbai-embed-large"}
        },
        collection_name="my_custom_knowledge"
    )
    
    # Use with knowledge sources
    knowledge_source = StringKnowledgeSource(
        content="Your knowledge content here"
    )
    knowledge_source.storage = custom_storage

#### 

​

Option 3: Project-Specific Knowledge Storage
    
    
    import os
    from pathlib import Path
    
    # Store knowledge in project directory
    project_root = Path(__file__).parent
    knowledge_dir = project_root / "knowledge_storage"
    
    os.environ["CREWAI_STORAGE_DIR"] = str(knowledge_dir)
    
    # Now all knowledge will be stored in your project directory

### 

​

Default Embedding Provider Behavior

**Default Embedding Provider** : CrewAI defaults to OpenAI embeddings (`text-embedding-3-small`) for knowledge storage, even when using different LLM providers. You can easily customize this to match your setup.

#### 

​

Understanding Default Behavior
    
    
    from crewai import Agent, Crew, LLM
    from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
    
    # When using Claude as your LLM...
    agent = Agent(
        role="Researcher",
        goal="Research topics",
        backstory="Expert researcher",
        llm=LLM(provider="anthropic", model="claude-3-sonnet")  # Using Claude
    )
    
    # CrewAI will still use OpenAI embeddings by default for knowledge
    # This ensures consistency but may not match your LLM provider preference
    knowledge_source = StringKnowledgeSource(content="Research data...")
    
    crew = Crew(
        agents=[agent],
        tasks=[...],
        knowledge_sources=[knowledge_source]
        # Default: Uses OpenAI embeddings even with Claude LLM
    )

#### 

​

Customizing Knowledge Embedding Providers
    
    
    # Option 1: Use Voyage AI (recommended by Anthropic for Claude users)
    crew = Crew(
        agents=[agent],
        tasks=[...],
        knowledge_sources=[knowledge_source],
        embedder={
            "provider": "voyageai",  # Recommended for Claude users
            "config": {
                "api_key": "your-voyage-api-key",
                "model": "voyage-3"  # or "voyage-3-large" for best quality
            }
        }
    )
    
    # Option 2: Use local embeddings (no external API calls)
    crew = Crew(
        agents=[agent],
        tasks=[...],
        knowledge_sources=[knowledge_source],
        embedder={
            "provider": "ollama",
            "config": {
                "model": "mxbai-embed-large",
                "url": "http://localhost:11434/api/embeddings"
            }
        }
    )
    
    # Option 3: Agent-level embedding customization
    agent = Agent(
        role="Researcher",
        goal="Research topics",
        backstory="Expert researcher",
        knowledge_sources=[knowledge_source],
        embedder={
            "provider": "google",
            "config": {
                "model": "models/text-embedding-004",
                "api_key": "your-google-key"
            }
        }
    )

## 

​

Advanced Features

### 

​

Query Rewriting

CrewAI implements an intelligent query rewriting mechanism to optimize knowledge retrieval. When an agent needs to search through knowledge sources, the raw task prompt is automatically transformed into a more effective search query.

#### 

​

How Query Rewriting Works

  1. When an agent executes a task with knowledge sources available, the `_get_knowledge_search_query` method is triggered
  2. The agent’s LLM is used to transform the original task prompt into an optimized search query
  3. This optimized query is then used to retrieve relevant information from knowledge sources



#### 

​

Benefits of Query Rewriting

## Improved Retrieval Accuracy

By focusing on key concepts and removing irrelevant content, query rewriting helps retrieve more relevant information.

## Context Awareness

The rewritten queries are designed to be more specific and context-aware for vector database retrieval.

#### 

​

Example
    
    
    # Original task prompt
    task_prompt = "Answer the following questions about the user's favorite movies: What movie did John watch last week? Format your answer in JSON."
    
    # Behind the scenes, this might be rewritten as:
    rewritten_query = "What movies did John watch last week?"

The rewritten query is more focused on the core information need and removes irrelevant instructions about output formatting.

This mechanism is fully automatic and requires no configuration from users. The agent’s LLM is used to perform the query rewriting, so using a more capable LLM can improve the quality of rewritten queries.

### 

​

Knowledge Events

CrewAI emits events during the knowledge retrieval process that you can listen for using the event system. These events allow you to monitor, debug, and analyze how knowledge is being retrieved and used by your agents.

#### 

​

Available Knowledge Events

  * **KnowledgeRetrievalStartedEvent** : Emitted when an agent starts retrieving knowledge from sources
  * **KnowledgeRetrievalCompletedEvent** : Emitted when knowledge retrieval is completed, including the query used and the retrieved content
  * **KnowledgeQueryStartedEvent** : Emitted when a query to knowledge sources begins
  * **KnowledgeQueryCompletedEvent** : Emitted when a query completes successfully
  * **KnowledgeQueryFailedEvent** : Emitted when a query to knowledge sources fails
  * **KnowledgeSearchQueryFailedEvent** : Emitted when a search query fails



#### 

​

Example: Monitoring Knowledge Retrieval
    
    
    from crewai.utilities.events import (
        KnowledgeRetrievalStartedEvent,
        KnowledgeRetrievalCompletedEvent,
    )
    from crewai.utilities.events.base_event_listener import BaseEventListener
    
    class KnowledgeMonitorListener(BaseEventListener):
        def setup_listeners(self, crewai_event_bus):
            @crewai_event_bus.on(KnowledgeRetrievalStartedEvent)
            def on_knowledge_retrieval_started(source, event):
                print(f"Agent '{event.agent.role}' started retrieving knowledge")
                
            @crewai_event_bus.on(KnowledgeRetrievalCompletedEvent)
            def on_knowledge_retrieval_completed(source, event):
                print(f"Agent '{event.agent.role}' completed knowledge retrieval")
                print(f"Query: {event.query}")
                print(f"Retrieved {len(event.retrieved_knowledge)} knowledge chunks")
    
    # Create an instance of your listener
    knowledge_monitor = KnowledgeMonitorListener()

For more information on using events, see the [Event Listeners](https://docs.crewai.com/concepts/event-listener) documentation.

### 

​

Custom Knowledge Sources

CrewAI allows you to create custom knowledge sources for any type of data by extending the `BaseKnowledgeSource` class. Let’s create a practical example that fetches and processes space news articles.

#### 

​

Space News Knowledge Source Example

Code

Output
    
    
    from crewai import Agent, Task, Crew, Process, LLM
    from crewai.knowledge.source.base_knowledge_source import BaseKnowledgeSource
    import requests
    from datetime import datetime
    from typing import Dict, Any
    from pydantic import BaseModel, Field
    
    class SpaceNewsKnowledgeSource(BaseKnowledgeSource):
        """Knowledge source that fetches data from Space News API."""
    
        api_endpoint: str = Field(description="API endpoint URL")
        limit: int = Field(default=10, description="Number of articles to fetch")
    
        def load_content(self) -> Dict[Any, str]:
            """Fetch and format space news articles."""
            try:
                response = requests.get(
                    f"{self.api_endpoint}?limit={self.limit}"
                )
                response.raise_for_status()
    
                data = response.json()
                articles = data.get('results', [])
    
                formatted_data = self.validate_content(articles)
                return {self.api_endpoint: formatted_data}
            except Exception as e:
                raise ValueError(f"Failed to fetch space news: {str(e)}")
    
        def validate_content(self, articles: list) -> str:
            """Format articles into readable text."""
            formatted = "Space News Articles:\n\n"
            for article in articles:
                formatted += f"""
                    Title: {article['title']}
                    Published: {article['published_at']}
                    Summary: {article['summary']}
                    News Site: {article['news_site']}
                    URL: {article['url']}
                    -------------------"""
            return formatted
    
        def add(self) -> None:
            """Process and store the articles."""
            content = self.load_content()
            for _, text in content.items():
                chunks = self._chunk_text(text)
                self.chunks.extend(chunks)
    
            self._save_documents()
    
    # Create knowledge source
    recent_news = SpaceNewsKnowledgeSource(
        api_endpoint="https://api.spaceflightnewsapi.net/v4/articles",
        limit=10,
    )
    
    # Create specialized agent
    space_analyst = Agent(
        role="Space News Analyst",
        goal="Answer questions about space news accurately and comprehensively",
        backstory="""You are a space industry analyst with expertise in space exploration,
        satellite technology, and space industry trends. You excel at answering questions
        about space news and providing detailed, accurate information.""",
        knowledge_sources=[recent_news],
        llm=LLM(model="gpt-4", temperature=0.0)
    )
    
    # Create task that handles user questions
    analysis_task = Task(
        description="Answer this question about space news: {user_question}",
        expected_output="A detailed answer based on the recent space news articles",
        agent=space_analyst
    )
    
    # Create and run the crew
    crew = Crew(
        agents=[space_analyst],
        tasks=[analysis_task],
        verbose=True,
        process=Process.sequential
    )
    
    # Example usage
    result = crew.kickoff(
        inputs={"user_question": "What are the latest developments in space exploration?"}
    )

## 

​

Debugging and Troubleshooting

### 

​

Debugging Knowledge Issues

#### 

​

Check Agent Knowledge Initialization
    
    
    from crewai import Agent, Crew, Task
    from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
    
    knowledge_source = StringKnowledgeSource(content="Test knowledge")
    
    agent = Agent(
        role="Test Agent",
        goal="Test knowledge",
        backstory="Testing",
        knowledge_sources=[knowledge_source]
    )
    
    crew = Crew(agents=[agent], tasks=[Task(...)])
    
    # Before kickoff - knowledge not initialized
    print(f"Before kickoff - Agent knowledge: {getattr(agent, 'knowledge', None)}")
    
    crew.kickoff()
    
    # After kickoff - knowledge initialized
    print(f"After kickoff - Agent knowledge: {agent.knowledge}")
    print(f"Agent knowledge collection: {agent.knowledge.storage.collection_name}")
    print(f"Number of sources: {len(agent.knowledge.sources)}")

#### 

​

Verify Knowledge Storage Locations
    
    
    import os
    from crewai.utilities.paths import db_storage_path
    
    # Check storage structure
    storage_path = db_storage_path()
    knowledge_path = os.path.join(storage_path, "knowledge")
    
    if os.path.exists(knowledge_path):
        print("Knowledge collections found:")
        for collection in os.listdir(knowledge_path):
            collection_path = os.path.join(knowledge_path, collection)
            if os.path.isdir(collection_path):
                print(f"  - {collection}/")
                # Show collection contents
                for item in os.listdir(collection_path):
                    print(f"    └── {item}")

#### 

​

Test Knowledge Retrieval
    
    
    # Test agent knowledge retrieval
    if hasattr(agent, 'knowledge') and agent.knowledge:
        test_query = ["test query"]
        results = agent.knowledge.query(test_query)
        print(f"Agent knowledge results: {len(results)} documents found")
        
        # Test crew knowledge retrieval (if exists)
        if hasattr(crew, 'knowledge') and crew.knowledge:
            crew_results = crew.query_knowledge(test_query)
            print(f"Crew knowledge results: {len(crew_results)} documents found")

#### 

​

Inspect Knowledge Collections
    
    
    import chromadb
    from crewai.utilities.paths import db_storage_path
    import os
    
    # Connect to CrewAI's knowledge ChromaDB
    knowledge_path = os.path.join(db_storage_path(), "knowledge")
    
    if os.path.exists(knowledge_path):
        client = chromadb.PersistentClient(path=knowledge_path)
        collections = client.list_collections()
        
        print("Knowledge Collections:")
        for collection in collections:
            print(f"  - {collection.name}: {collection.count()} documents")
            
            # Sample a few documents to verify content
            if collection.count() > 0:
                sample = collection.peek(limit=2)
                print(f"    Sample content: {sample['documents'][0][:100]}...")
    else:
        print("No knowledge storage found")

#### 

​

Check Knowledge Processing
    
    
    from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
    
    # Create a test knowledge source
    test_source = StringKnowledgeSource(
        content="Test knowledge content for debugging",
        chunk_size=100,  # Small chunks for testing
        chunk_overlap=20
    )
    
    # Check chunking behavior
    print(f"Original content length: {len(test_source.content)}")
    print(f"Chunk size: {test_source.chunk_size}")
    print(f"Chunk overlap: {test_source.chunk_overlap}")
    
    # Process and inspect chunks
    test_source.add()
    print(f"Number of chunks created: {len(test_source.chunks)}")
    for i, chunk in enumerate(test_source.chunks[:3]):  # Show first 3 chunks
        print(f"Chunk {i+1}: {chunk[:50]}...")

### 

​

Common Knowledge Storage Issues

**“File not found” errors:**
    
    
    # Ensure files are in the correct location
    from crewai.utilities.constants import KNOWLEDGE_DIRECTORY
    import os
    
    knowledge_dir = KNOWLEDGE_DIRECTORY  # Usually "knowledge"
    file_path = os.path.join(knowledge_dir, "your_file.pdf")
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Expected knowledge directory: {os.path.abspath(knowledge_dir)}")

**“Embedding dimension mismatch” errors:**
    
    
    # This happens when switching embedding providers
    # Reset knowledge storage to clear old embeddings
    crew.reset_memories(command_type='knowledge')
    
    # Or use consistent embedding providers
    crew = Crew(
        agents=[...],
        tasks=[...],
        knowledge_sources=[...],
        embedder={"provider": "openai", "config": {"model": "text-embedding-3-small"}}
    )

**“ChromaDB permission denied” errors:**
    
    
    # Fix storage permissions
    chmod -R 755 ~/.local/share/CrewAI/

**Knowledge not persisting between runs:**
    
    
    # Verify storage location consistency
    import os
    from crewai.utilities.paths import db_storage_path
    
    print("CREWAI_STORAGE_DIR:", os.getenv("CREWAI_STORAGE_DIR"))
    print("Computed storage path:", db_storage_path())
    print("Knowledge path:", os.path.join(db_storage_path(), "knowledge"))

### 

​

Knowledge Reset Commands
    
    
    # Reset only agent-specific knowledge
    crew.reset_memories(command_type='agent_knowledge')
    
    # Reset both crew and agent knowledge  
    crew.reset_memories(command_type='knowledge')
    
    # CLI commands
    # crewai reset-memories --agent-knowledge  # Agent knowledge only
    # crewai reset-memories --knowledge        # All knowledge

### 

​

Clearing Knowledge

If you need to clear the knowledge stored in CrewAI, you can use the `crewai reset-memories` command with the `--knowledge` option.

Command
    
    
    crewai reset-memories --knowledge

This is useful when you’ve updated your knowledge sources and want to ensure that the agents are using the most recent information.

## 

​

Best Practices

Content Organization

  * Keep chunk sizes appropriate for your content type
  * Consider content overlap for context preservation
  * Organize related information into separate knowledge sources



Performance Tips

  * Adjust chunk sizes based on content complexity
  * Configure appropriate embedding models
  * Consider using local embedding providers for faster processing



One Time Knowledge

  * With the typical file structure provided by CrewAI, knowledge sources are embedded every time the kickoff is triggered.
  * If the knowledge sources are large, this leads to inefficiency and increased latency, as the same data is embedded each time.
  * To resolve this, directly initialize the knowledge parameter instead of the knowledge_sources parameter.
  * Link to the issue to get complete idea [Github Issue](https://github.com/crewAIInc/crewAI/issues/2755)



Knowledge Management

  * Use agent-level knowledge for role-specific information
  * Use crew-level knowledge for shared information all agents need
  * Set embedders at agent level if you need different embedding strategies
  * Use consistent collection naming by keeping agent roles descriptive
  * Test knowledge initialization by checking agent.knowledge after kickoff
  * Monitor storage locations to understand where knowledge is stored
  * Reset knowledge appropriately using the correct command types



Production Best Practices

  * Set `CREWAI_STORAGE_DIR` to a known location in production
  * Choose explicit embedding providers to match your LLM setup and avoid API key conflicts
  * Monitor knowledge storage size as it grows with document additions
  * Organize knowledge sources by domain or purpose using collection names
  * Include knowledge directories in your backup and deployment strategies
  * Set appropriate file permissions for knowledge files and storage directories
  * Use environment variables for API keys and sensitive configuration



Was this page helpful?

YesNo

[Flows](/concepts/flows)[LLMs](/concepts/llms)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Overview
  * Quickstart Examples
  * Basic String Knowledge Example
  * Web Content Knowledge Example
  * Supported Knowledge Sources
  * Text File Knowledge Source
  * PDF Knowledge Source
  * CSV Knowledge Source
  * Excel Knowledge Source
  * JSON Knowledge Source
  * Agent vs Crew Knowledge: Complete Guide
  * How Knowledge Initialization Actually Works
  * Agent-Level Knowledge (Independent)
  * What Happens During crew.kickoff()
  * Storage Independence
  * Complete Working Examples
  * Example 1: Agent-Only Knowledge
  * Example 2: Both Agent and Crew Knowledge
  * Example 3: Multiple Agents with Different Knowledge
  * Knowledge Configuration
  * Supported Knowledge Parameters
  * Knowledge Storage Transparency
  * Where CrewAI Stores Knowledge Files
  * Default Storage Locations by Platform
  * Finding Your Knowledge Storage Location
  * Controlling Knowledge Storage Locations
  * Option 1: Environment Variable (Recommended)
  * Option 2: Custom Knowledge Storage
  * Option 3: Project-Specific Knowledge Storage
  * Default Embedding Provider Behavior
  * Understanding Default Behavior
  * Customizing Knowledge Embedding Providers
  * Advanced Features
  * Query Rewriting
  * How Query Rewriting Works
  * Benefits of Query Rewriting
  * Example
  * Knowledge Events
  * Available Knowledge Events
  * Example: Monitoring Knowledge Retrieval
  * Custom Knowledge Sources
  * Space News Knowledge Source Example
  * Debugging and Troubleshooting
  * Debugging Knowledge Issues
  * Check Agent Knowledge Initialization
  * Verify Knowledge Storage Locations
  * Test Knowledge Retrieval
  * Inspect Knowledge Collections
  * Check Knowledge Processing
  * Common Knowledge Storage Issues
  * Knowledge Reset Commands
  * Clearing Knowledge
  * Best Practices



Assistant

Responses are generated using AI and may contain mistakes.


---

### CLI {#cli}

**Source:** [https://docs.crewai.com/concepts/cli](https://docs.crewai.com/concepts/cli)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Core Concepts

CLI

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Core Concepts

# CLI

Copy page

Learn how to use the CrewAI CLI to interact with CrewAI.

## 

​

Overview

The CrewAI CLI provides a set of commands to interact with CrewAI, allowing you to create, train, run, and manage crews & flows.

## 

​

Installation

To use the CrewAI CLI, make sure you have CrewAI installed:

Terminal
    
    
    pip install crewai

## 

​

Basic Usage

The basic structure of a CrewAI CLI command is:

Terminal
    
    
    crewai [COMMAND] [OPTIONS] [ARGUMENTS]

## 

​

Available Commands

### 

​

1\. Create

Create a new crew or flow.

Terminal
    
    
    crewai create [OPTIONS] TYPE NAME

  * `TYPE`: Choose between “crew” or “flow”
  * `NAME`: Name of the crew or flow



Example:

Terminal
    
    
    crewai create crew my_new_crew
    crewai create flow my_new_flow

### 

​

2\. Version

Show the installed version of CrewAI.

Terminal
    
    
    crewai version [OPTIONS]

  * `--tools`: (Optional) Show the installed version of CrewAI tools



Example:

Terminal
    
    
    crewai version
    crewai version --tools

### 

​

3\. Train

Train the crew for a specified number of iterations.

Terminal
    
    
    crewai train [OPTIONS]

  * `-n, --n_iterations INTEGER`: Number of iterations to train the crew (default: 5)
  * `-f, --filename TEXT`: Path to a custom file for training (default: “trained_agents_data.pkl”)



Example:

Terminal
    
    
    crewai train -n 10 -f my_training_data.pkl

### 

​

4\. Replay

Replay the crew execution from a specific task.

Terminal
    
    
    crewai replay [OPTIONS]

  * `-t, --task_id TEXT`: Replay the crew from this task ID, including all subsequent tasks



Example:

Terminal
    
    
    crewai replay -t task_123456

### 

​

5\. Log-tasks-outputs

Retrieve your latest crew.kickoff() task outputs.

Terminal
    
    
    crewai log-tasks-outputs

### 

​

6\. Reset-memories

Reset the crew memories (long, short, entity, latest_crew_kickoff_outputs).

Terminal
    
    
    crewai reset-memories [OPTIONS]

  * `-l, --long`: Reset LONG TERM memory
  * `-s, --short`: Reset SHORT TERM memory
  * `-e, --entities`: Reset ENTITIES memory
  * `-k, --kickoff-outputs`: Reset LATEST KICKOFF TASK OUTPUTS
  * `-kn, --knowledge`: Reset KNOWLEDGE storage
  * `-akn, --agent-knowledge`: Reset AGENT KNOWLEDGE storage
  * `-a, --all`: Reset ALL memories



Example:

Terminal
    
    
    crewai reset-memories --long --short
    crewai reset-memories --all

### 

​

7\. Test

Test the crew and evaluate the results.

Terminal
    
    
    crewai test [OPTIONS]

  * `-n, --n_iterations INTEGER`: Number of iterations to test the crew (default: 3)
  * `-m, --model TEXT`: LLM Model to run the tests on the Crew (default: “gpt-4o-mini”)



Example:

Terminal
    
    
    crewai test -n 5 -m gpt-3.5-turbo

### 

​

8\. Run

Run the crew or flow.

Terminal
    
    
    crewai run

Starting from version 0.103.0, the `crewai run` command can be used to run both standard crews and flows. For flows, it automatically detects the type from pyproject.toml and runs the appropriate command. This is now the recommended way to run both crews and flows.

Make sure to run these commands from the directory where your CrewAI project is set up. Some commands may require additional configuration or setup within your project structure.

### 

​

9\. Chat

Starting in version `0.98.0`, when you run the `crewai chat` command, you start an interactive session with your crew. The AI assistant will guide you by asking for necessary inputs to execute the crew. Once all inputs are provided, the crew will execute its tasks.

After receiving the results, you can continue interacting with the assistant for further instructions or questions.

Terminal
    
    
    crewai chat

Ensure you execute these commands from your CrewAI project’s root directory.

IMPORTANT: Set the `chat_llm` property in your `crew.py` file to enable this command.
    
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            chat_llm="gpt-4o",  # LLM for chat orchestration
        )

### 

​

10\. Deploy

Deploy the crew or flow to [CrewAI Enterprise](https://app.crewai.com).

  * **Authentication** : You need to be authenticated to deploy to CrewAI Enterprise.

Terminal
        
        crewai signup

If you already have an account, you can login with:

Terminal
        
        crewai login

  * **Create a deployment** : Once you are authenticated, you can create a deployment for your crew or flow from the root of your localproject.

Terminal
        
        crewai deploy create

    * Reads your local project configuration.
    * Prompts you to confirm the environment variables (like `OPENAI_API_KEY`, `SERPER_API_KEY`) found locally. These will be securely stored with the deployment on the Enterprise platform. Ensure your sensitive keys are correctly configured locally (e.g., in a `.env` file) before running this.
    * Links the deployment to the corresponding remote GitHub repository (it usually detects this automatically).
  * **Deploy the Crew** : Once you are authenticated, you can deploy your crew or flow to CrewAI Enterprise.

Terminal
        
        crewai deploy push

    * Initiates the deployment process on the CrewAI Enterprise platform.
    * Upon successful initiation, it will output the Deployment created successfully! message along with the Deployment Name and a unique Deployment ID (UUID).
  * **Deployment Status** : You can check the status of your deployment with:

Terminal
        
        crewai deploy status

This fetches the latest deployment status of your most recent deployment attempt (e.g., `Building Images for Crew`, `Deploy Enqueued`, `Online`).

  * **Deployment Logs** : You can check the logs of your deployment with:

Terminal
        
        crewai deploy logs

This streams the deployment logs to your terminal.

  * **List deployments** : You can list all your deployments with:

Terminal
        
        crewai deploy list

This lists all your deployments.

  * **Delete a deployment** : You can delete a deployment with:

Terminal
        
        crewai deploy remove

This deletes the deployment from the CrewAI Enterprise platform.

  * **Help Command** : You can get help with the CLI with:

Terminal
        
        crewai deploy --help

This shows the help message for the CrewAI Deploy CLI.




Watch this video tutorial for a step-by-step demonstration of deploying your crew to [CrewAI Enterprise](http://app.crewai.com) using the CLI.

### 

​

11\. API Keys

When running `crewai create crew` command, the CLI will first show you the top 5 most common LLM providers and ask you to select one.

Once you’ve selected an LLM provider, you will be prompted for API keys.

#### 

​

Initial API key providers

The CLI will initially prompt for API keys for the following services:

  * OpenAI
  * Groq
  * Anthropic
  * Google Gemini
  * SambaNova



When you select a provider, the CLI will prompt you to enter your API key.

#### 

​

Other Options

If you select option 6, you will be able to select from a list of LiteLLM supported providers.

When you select a provider, the CLI will prompt you to enter the Key name and the API key.

See the following link for each provider’s key name:

  * [LiteLLM Providers](https://docs.litellm.ai/docs/providers)



Was this page helpful?

YesNo

[Testing](/concepts/testing)[Tools](/concepts/tools)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Overview
  * Installation
  * Basic Usage
  * Available Commands
  * 1\. Create
  * 2\. Version
  * 3\. Train
  * 4\. Replay
  * 5\. Log-tasks-outputs
  * 6\. Reset-memories
  * 7\. Test
  * 8\. Run
  * 9\. Chat
  * 10\. Deploy
  * 11\. API Keys
  * Initial API key providers
  * Other Options



Assistant

Responses are generated using AI and may contain mistakes.


---

### Memory {#memory}

**Source:** [https://docs.crewai.com/concepts/memory](https://docs.crewai.com/concepts/memory)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Core Concepts

Memory

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Core Concepts

# Memory

Copy page

Leveraging memory systems in the CrewAI framework to enhance agent capabilities.

## 

​

Overview

The CrewAI framework provides a sophisticated memory system designed to significantly enhance AI agent capabilities. CrewAI offers **three distinct memory approaches** that serve different use cases:

  1. **Basic Memory System** \- Built-in short-term, long-term, and entity memory
  2. **User Memory** \- User-specific memory with Mem0 integration (legacy approach)
  3. **External Memory** \- Standalone external memory providers (new approach)



## 

​

Memory System Components

Component| Description  
---|---  
**Short-Term Memory**|  Temporarily stores recent interactions and outcomes using `RAG`, enabling agents to recall and utilize information relevant to their current context during the current executions.  
**Long-Term Memory**|  Preserves valuable insights and learnings from past executions, allowing agents to build and refine their knowledge over time.  
**Entity Memory**|  Captures and organizes information about entities (people, places, concepts) encountered during tasks, facilitating deeper understanding and relationship mapping. Uses `RAG` for storing entity information.  
**Contextual Memory**|  Maintains the context of interactions by combining `ShortTermMemory`, `LongTermMemory`, and `EntityMemory`, aiding in the coherence and relevance of agent responses over a sequence of tasks or a conversation.  
  
## 

​

1\. Basic Memory System (Recommended)

The simplest and most commonly used approach. Enable memory for your crew with a single parameter:

### 

​

Quick Start
    
    
    from crewai import Crew, Agent, Task, Process
    
    # Enable basic memory system
    crew = Crew(
        agents=[...],
        tasks=[...],
        process=Process.sequential,
        memory=True,  # Enables short-term, long-term, and entity memory
        verbose=True
    )

### 

​

How It Works

  * **Short-Term Memory** : Uses ChromaDB with RAG for current context
  * **Long-Term Memory** : Uses SQLite3 to store task results across sessions
  * **Entity Memory** : Uses RAG to track entities (people, places, concepts)
  * **Storage Location** : Platform-specific location via `appdirs` package
  * **Custom Storage Directory** : Set `CREWAI_STORAGE_DIR` environment variable



## 

​

Storage Location Transparency

**Understanding Storage Locations** : CrewAI uses platform-specific directories to store memory and knowledge files following OS conventions. Understanding these locations helps with production deployments, backups, and debugging.

### 

​

Where CrewAI Stores Files

By default, CrewAI uses the `appdirs` library to determine storage locations following platform conventions. Here’s exactly where your files are stored:

#### 

​

Default Storage Locations by Platform

**macOS:**
    
    
    ~/Library/Application Support/CrewAI/{project_name}/
    ├── knowledge/           # Knowledge base ChromaDB files
    ├── short_term_memory/   # Short-term memory ChromaDB files  
    ├── long_term_memory/    # Long-term memory ChromaDB files
    ├── entities/            # Entity memory ChromaDB files
    └── long_term_memory_storage.db  # SQLite database

**Linux:**
    
    
    ~/.local/share/CrewAI/{project_name}/
    ├── knowledge/
    ├── short_term_memory/
    ├── long_term_memory/
    ├── entities/
    └── long_term_memory_storage.db

**Windows:**
    
    
    C:\Users\{username}\AppData\Local\CrewAI\{project_name}\
    ├── knowledge\
    ├── short_term_memory\
    ├── long_term_memory\
    ├── entities\
    └── long_term_memory_storage.db

### 

​

Finding Your Storage Location

To see exactly where CrewAI is storing files on your system:
    
    
    from crewai.utilities.paths import db_storage_path
    import os
    
    # Get the base storage path
    storage_path = db_storage_path()
    print(f"CrewAI storage location: {storage_path}")
    
    # List all CrewAI storage directories
    if os.path.exists(storage_path):
        print("\nStored files and directories:")
        for item in os.listdir(storage_path):
            item_path = os.path.join(storage_path, item)
            if os.path.isdir(item_path):
                print(f"📁 {item}/")
                # Show ChromaDB collections
                if os.path.exists(item_path):
                    for subitem in os.listdir(item_path):
                        print(f"   └── {subitem}")
            else:
                print(f"📄 {item}")
    else:
        print("No CrewAI storage directory found yet.")

### 

​

Controlling Storage Locations

#### 

​

Option 1: Environment Variable (Recommended)
    
    
    import os
    from crewai import Crew
    
    # Set custom storage location
    os.environ["CREWAI_STORAGE_DIR"] = "./my_project_storage"
    
    # All memory and knowledge will now be stored in ./my_project_storage/
    crew = Crew(
        agents=[...],
        tasks=[...],
        memory=True
    )

#### 

​

Option 2: Custom Storage Paths
    
    
    import os
    from crewai import Crew
    from crewai.memory import LongTermMemory
    from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
    
    # Configure custom storage location
    custom_storage_path = "./storage"
    os.makedirs(custom_storage_path, exist_ok=True)
    
    crew = Crew(
        memory=True,
        long_term_memory=LongTermMemory(
            storage=LTMSQLiteStorage(
                db_path=f"{custom_storage_path}/memory.db"
            )
        )
    )

#### 

​

Option 3: Project-Specific Storage
    
    
    import os
    from pathlib import Path
    
    # Store in project directory
    project_root = Path(__file__).parent
    storage_dir = project_root / "crewai_storage"
    
    os.environ["CREWAI_STORAGE_DIR"] = str(storage_dir)
    
    # Now all storage will be in your project directory

### 

​

Embedding Provider Defaults

**Default Embedding Provider** : CrewAI defaults to OpenAI embeddings for consistency and reliability. You can easily customize this to match your LLM provider or use local embeddings.

#### 

​

Understanding Default Behavior
    
    
    # When using Claude as your LLM...
    from crewai import Agent, LLM
    
    agent = Agent(
        role="Analyst",
        goal="Analyze data",
        backstory="Expert analyst",
        llm=LLM(provider="anthropic", model="claude-3-sonnet")  # Using Claude
    )
    
    # CrewAI will use OpenAI embeddings by default for consistency
    # You can easily customize this to match your preferred provider

#### 

​

Customizing Embedding Providers
    
    
    from crewai import Crew
    
    # Option 1: Match your LLM provider
    crew = Crew(
        agents=[agent],
        tasks=[task],
        memory=True,
        embedder={
            "provider": "anthropic",  # Match your LLM provider
            "config": {
                "api_key": "your-anthropic-key",
                "model": "text-embedding-3-small"
            }
        }
    )
    
    # Option 2: Use local embeddings (no external API calls)
    crew = Crew(
        agents=[agent],
        tasks=[task],
        memory=True,
        embedder={
            "provider": "ollama",
            "config": {"model": "mxbai-embed-large"}
        }
    )

### 

​

Debugging Storage Issues

#### 

​

Check Storage Permissions
    
    
    import os
    from crewai.utilities.paths import db_storage_path
    
    storage_path = db_storage_path()
    print(f"Storage path: {storage_path}")
    print(f"Path exists: {os.path.exists(storage_path)}")
    print(f"Is writable: {os.access(storage_path, os.W_OK) if os.path.exists(storage_path) else 'Path does not exist'}")
    
    # Create with proper permissions
    if not os.path.exists(storage_path):
        os.makedirs(storage_path, mode=0o755, exist_ok=True)
        print(f"Created storage directory: {storage_path}")

#### 

​

Inspect ChromaDB Collections
    
    
    import chromadb
    from crewai.utilities.paths import db_storage_path
    
    # Connect to CrewAI's ChromaDB
    storage_path = db_storage_path()
    chroma_path = os.path.join(storage_path, "knowledge")
    
    if os.path.exists(chroma_path):
        client = chromadb.PersistentClient(path=chroma_path)
        collections = client.list_collections()
        
        print("ChromaDB Collections:")
        for collection in collections:
            print(f"  - {collection.name}: {collection.count()} documents")
    else:
        print("No ChromaDB storage found")

#### 

​

Reset Storage (Debugging)
    
    
    from crewai import Crew
    
    # Reset all memory storage
    crew = Crew(agents=[...], tasks=[...], memory=True)
    
    # Reset specific memory types
    crew.reset_memories(command_type='short')     # Short-term memory
    crew.reset_memories(command_type='long')      # Long-term memory  
    crew.reset_memories(command_type='entity')    # Entity memory
    crew.reset_memories(command_type='knowledge') # Knowledge storage

### 

​

Production Best Practices

  1. **Set`CREWAI_STORAGE_DIR`** to a known location in production for better control
  2. **Choose explicit embedding providers** to match your LLM setup
  3. **Monitor storage directory size** for large-scale deployments
  4. **Include storage directories** in your backup strategy
  5. **Set appropriate file permissions** (0o755 for directories, 0o644 for files)
  6. **Use project-relative paths** for containerized deployments



### 

​

Common Storage Issues

**“ChromaDB permission denied” errors:**
    
    
    # Fix permissions
    chmod -R 755 ~/.local/share/CrewAI/

**“Database is locked” errors:**
    
    
    # Ensure only one CrewAI instance accesses storage
    import fcntl
    import os
    
    storage_path = db_storage_path()
    lock_file = os.path.join(storage_path, ".crewai.lock")
    
    with open(lock_file, 'w') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        # Your CrewAI code here

**Storage not persisting between runs:**
    
    
    # Verify storage location is consistent
    import os
    print("CREWAI_STORAGE_DIR:", os.getenv("CREWAI_STORAGE_DIR"))
    print("Current working directory:", os.getcwd())
    print("Computed storage path:", db_storage_path())

## 

​

Custom Embedder Configuration

CrewAI supports multiple embedding providers to give you flexibility in choosing the best option for your use case. Here’s a comprehensive guide to configuring different embedding providers for your memory system.

### 

​

Why Choose Different Embedding Providers?

  * **Cost Optimization** : Local embeddings (Ollama) are free after initial setup
  * **Privacy** : Keep your data local with Ollama or use your preferred cloud provider
  * **Performance** : Some models work better for specific domains or languages
  * **Consistency** : Match your embedding provider with your LLM provider
  * **Compliance** : Meet specific regulatory or organizational requirements



### 

​

OpenAI Embeddings (Default)

OpenAI provides reliable, high-quality embeddings that work well for most use cases.
    
    
    from crewai import Crew
    
    # Basic OpenAI configuration (uses environment OPENAI_API_KEY)
    crew = Crew(
        agents=[...],
        tasks=[...],
        memory=True,
        embedder={
            "provider": "openai",
            "config": {
                "model": "text-embedding-3-small"  # or "text-embedding-3-large"
            }
        }
    )
    
    # Advanced OpenAI configuration
    crew = Crew(
        memory=True,
        embedder={
            "provider": "openai",
            "config": {
                "api_key": "your-openai-api-key",  # Optional: override env var
                "model": "text-embedding-3-large",
                "dimensions": 1536,  # Optional: reduce dimensions for smaller storage
                "organization_id": "your-org-id"  # Optional: for organization accounts
            }
        }
    )

### 

​

Azure OpenAI Embeddings

For enterprise users with Azure OpenAI deployments.
    
    
    crew = Crew(
        memory=True,
        embedder={
            "provider": "openai",  # Use openai provider for Azure
            "config": {
                "api_key": "your-azure-api-key",
                "api_base": "https://your-resource.openai.azure.com/",
                "api_type": "azure",
                "api_version": "2023-05-15",
                "model": "text-embedding-3-small",
                "deployment_id": "your-deployment-name"  # Azure deployment name
            }
        }
    )

### 

​

Google AI Embeddings

Use Google’s text embedding models for integration with Google Cloud services.
    
    
    crew = Crew(
        memory=True,
        embedder={
            "provider": "google",
            "config": {
                "api_key": "your-google-api-key",
                "model": "text-embedding-004"  # or "text-embedding-preview-0409"
            }
        }
    )

### 

​

Vertex AI Embeddings

For Google Cloud users with Vertex AI access.
    
    
    crew = Crew(
        memory=True,
        embedder={
            "provider": "vertexai",
            "config": {
                "project_id": "your-gcp-project-id",
                "region": "us-central1",  # or your preferred region
                "api_key": "your-service-account-key",
                "model_name": "textembedding-gecko"
            }
        }
    )

### 

​

Ollama Embeddings (Local)

Run embeddings locally for privacy and cost savings.
    
    
    # First, install and run Ollama locally, then pull an embedding model:
    # ollama pull mxbai-embed-large
    
    crew = Crew(
        memory=True,
        embedder={
            "provider": "ollama",
            "config": {
                "model": "mxbai-embed-large",  # or "nomic-embed-text"
                "url": "http://localhost:11434/api/embeddings"  # Default Ollama URL
            }
        }
    )
    
    # For custom Ollama installations
    crew = Crew(
        memory=True,
        embedder={
            "provider": "ollama",
            "config": {
                "model": "mxbai-embed-large",
                "url": "http://your-ollama-server:11434/api/embeddings"
            }
        }
    )

### 

​

Cohere Embeddings

Use Cohere’s embedding models for multilingual support.
    
    
    crew = Crew(
        memory=True,
        embedder={
            "provider": "cohere",
            "config": {
                "api_key": "your-cohere-api-key",
                "model": "embed-english-v3.0"  # or "embed-multilingual-v3.0"
            }
        }
    )

### 

​

VoyageAI Embeddings

High-performance embeddings optimized for retrieval tasks.
    
    
    crew = Crew(
        memory=True,
        embedder={
            "provider": "voyageai",
            "config": {
                "api_key": "your-voyage-api-key",
                "model": "voyage-large-2",  # or "voyage-code-2" for code
                "input_type": "document"  # or "query"
            }
        }
    )

### 

​

AWS Bedrock Embeddings

For AWS users with Bedrock access.
    
    
    crew = Crew(
        memory=True,
        embedder={
            "provider": "bedrock",
            "config": {
                "aws_access_key_id": "your-access-key",
                "aws_secret_access_key": "your-secret-key",
                "region_name": "us-east-1",
                "model": "amazon.titan-embed-text-v1"
            }
        }
    )

### 

​

Hugging Face Embeddings

Use open-source models from Hugging Face.
    
    
    crew = Crew(
        memory=True,
        embedder={
            "provider": "huggingface",
            "config": {
                "api_key": "your-hf-token",  # Optional for public models
                "model": "sentence-transformers/all-MiniLM-L6-v2",
                "api_url": "https://api-inference.huggingface.co"  # or your custom endpoint
            }
        }
    )

### 

​

IBM Watson Embeddings

For IBM Cloud users.
    
    
    crew = Crew(
        memory=True,
        embedder={
            "provider": "watson",
            "config": {
                "api_key": "your-watson-api-key",
                "url": "your-watson-instance-url",
                "model": "ibm/slate-125m-english-rtrvr"
            }
        }
    )

### 

​

Choosing the Right Embedding Provider

Provider| Best For| Pros| Cons  
---|---|---|---  
**OpenAI**|  General use, reliability| High quality, well-tested| Cost, requires API key  
**Ollama**|  Privacy, cost savings| Free, local, private| Requires local setup  
**Google AI**|  Google ecosystem| Good performance| Requires Google account  
**Azure OpenAI**|  Enterprise, compliance| Enterprise features| Complex setup  
**Cohere**|  Multilingual content| Great language support| Specialized use case  
**VoyageAI**|  Retrieval tasks| Optimized for search| Newer provider  
  
### 

​

Environment Variable Configuration

For security, store API keys in environment variables:
    
    
    import os
    
    # Set environment variables
    os.environ["OPENAI_API_KEY"] = "your-openai-key"
    os.environ["GOOGLE_API_KEY"] = "your-google-key"
    os.environ["COHERE_API_KEY"] = "your-cohere-key"
    
    # Use without exposing keys in code
    crew = Crew(
        memory=True,
        embedder={
            "provider": "openai",
            "config": {
                "model": "text-embedding-3-small"
                # API key automatically loaded from environment
            }
        }
    )

### 

​

Testing Different Embedding Providers

Compare embedding providers for your specific use case:
    
    
    from crewai import Crew
    from crewai.utilities.paths import db_storage_path
    
    # Test different providers with the same data
    providers_to_test = [
        {
            "name": "OpenAI",
            "config": {
                "provider": "openai",
                "config": {"model": "text-embedding-3-small"}
            }
        },
        {
            "name": "Ollama",
            "config": {
                "provider": "ollama", 
                "config": {"model": "mxbai-embed-large"}
            }
        }
    ]
    
    for provider in providers_to_test:
        print(f"\nTesting {provider['name']} embeddings...")
        
        # Create crew with specific embedder
        crew = Crew(
            agents=[...],
            tasks=[...],
            memory=True,
            embedder=provider['config']
        )
        
        # Run your test and measure performance
        result = crew.kickoff()
        print(f"{provider['name']} completed successfully")

### 

​

Troubleshooting Embedding Issues

**Model not found errors:**
    
    
    # Verify model availability
    from crewai.utilities.embedding_configurator import EmbeddingConfigurator
    
    configurator = EmbeddingConfigurator()
    try:
        embedder = configurator.configure_embedder({
            "provider": "ollama",
            "config": {"model": "mxbai-embed-large"}
        })
        print("Embedder configured successfully")
    except Exception as e:
        print(f"Configuration error: {e}")

**API key issues:**
    
    
    import os
    
    # Check if API keys are set
    required_keys = ["OPENAI_API_KEY", "GOOGLE_API_KEY", "COHERE_API_KEY"]
    for key in required_keys:
        if os.getenv(key):
            print(f"✅ {key} is set")
        else:
            print(f"❌ {key} is not set")

**Performance comparison:**
    
    
    import time
    
    def test_embedding_performance(embedder_config, test_text="This is a test document"):
        start_time = time.time()
        
        crew = Crew(
            agents=[...],
            tasks=[...],
            memory=True,
            embedder=embedder_config
        )
        
        # Simulate memory operation
        crew.kickoff()
        
        end_time = time.time()
        return end_time - start_time
    
    # Compare performance
    openai_time = test_embedding_performance({
        "provider": "openai",
        "config": {"model": "text-embedding-3-small"}
    })
    
    ollama_time = test_embedding_performance({
        "provider": "ollama", 
        "config": {"model": "mxbai-embed-large"}
    })
    
    print(f"OpenAI: {openai_time:.2f}s")
    print(f"Ollama: {ollama_time:.2f}s")

## 

​

2\. User Memory with Mem0 (Legacy)

**Legacy Approach** : While fully functional, this approach is considered legacy. For new projects requiring user-specific memory, consider using External Memory instead.

User Memory integrates with [Mem0](https://mem0.ai/) to provide user-specific memory that persists across sessions and integrates with the crew’s contextual memory system.

### 

​

Prerequisites
    
    
    pip install mem0ai

### 

​

Mem0 Cloud Configuration
    
    
    import os
    from crewai import Crew, Process
    
    # Set your Mem0 API key
    os.environ["MEM0_API_KEY"] = "m0-your-api-key"
    
    crew = Crew(
        agents=[...],
        tasks=[...],
        memory=True,  # Required for contextual memory integration
        memory_config={
            "provider": "mem0",
            "config": {"user_id": "john"},
            "user_memory": {}  # Required - triggers user memory initialization
        },
        process=Process.sequential,
        verbose=True
    )

### 

​

Advanced Mem0 Configuration
    
    
    crew = Crew(
        agents=[...],
        tasks=[...],
        memory=True,
        memory_config={
            "provider": "mem0",
            "config": {
                "user_id": "john",
                "org_id": "my_org_id",        # Optional
                "project_id": "my_project_id", # Optional
                "api_key": "custom-api-key"    # Optional - overrides env var
            },
            "user_memory": {}
        }
    )

### 

​

Local Mem0 Configuration
    
    
    crew = Crew(
        agents=[...],
        tasks=[...],
        memory=True,
        memory_config={
            "provider": "mem0",
            "config": {
                "user_id": "john",
                "local_mem0_config": {
                    "vector_store": {
                        "provider": "qdrant",
                        "config": {"host": "localhost", "port": 6333}
                    },
                    "llm": {
                        "provider": "openai",
                        "config": {"api_key": "your-api-key", "model": "gpt-4"}
                    },
                    "embedder": {
                        "provider": "openai",
                        "config": {"api_key": "your-api-key", "model": "text-embedding-3-small"}
                    }
                }
            },
            "user_memory": {}
        }
    )

## 

​

3\. External Memory (New Approach)

External Memory provides a standalone memory system that operates independently from the crew’s built-in memory. This is ideal for specialized memory providers or cross-application memory sharing.

### 

​

Basic External Memory with Mem0
    
    
    import os
    from crewai import Agent, Crew, Process, Task
    from crewai.memory.external.external_memory import ExternalMemory
    
    os.environ["MEM0_API_KEY"] = "your-api-key"
    
    # Create external memory instance
    external_memory = ExternalMemory(
        embedder_config={
            "provider": "mem0", 
            "config": {"user_id": "U-123"}
        }
    )
    
    crew = Crew(
        agents=[...],
        tasks=[...],
        external_memory=external_memory,  # Separate from basic memory
        process=Process.sequential,
        verbose=True
    )

### 

​

Custom Storage Implementation
    
    
    from crewai.memory.external.external_memory import ExternalMemory
    from crewai.memory.storage.interface import Storage
    
    class CustomStorage(Storage):
        def __init__(self):
            self.memories = []
    
        def save(self, value, metadata=None, agent=None):
            self.memories.append({
                "value": value, 
                "metadata": metadata, 
                "agent": agent
            })
    
        def search(self, query, limit=10, score_threshold=0.5):
            # Implement your search logic here
            return [m for m in self.memories if query.lower() in str(m["value"]).lower()]
    
        def reset(self):
            self.memories = []
    
    # Use custom storage
    external_memory = ExternalMemory(storage=CustomStorage())
    
    crew = Crew(
        agents=[...],
        tasks=[...],
        external_memory=external_memory
    )

## 

​

Memory System Comparison

Feature| Basic Memory| User Memory (Legacy)| External Memory  
---|---|---|---  
**Setup Complexity**|  Simple| Medium| Medium  
**Integration**|  Built-in contextual| Contextual + User-specific| Standalone  
**Storage**|  Local files| Mem0 Cloud/Local| Custom/Mem0  
**Cross-session**|  ✅| ✅| ✅  
**User-specific**|  ❌| ✅| ✅  
**Custom providers**|  Limited| Mem0 only| Any provider  
**Recommended for**|  Most use cases| Legacy projects| Specialized needs  
  
## 

​

Supported Embedding Providers

### 

​

OpenAI (Default)
    
    
    crew = Crew(
        memory=True,
        embedder={
            "provider": "openai",
            "config": {"model": "text-embedding-3-small"}
        }
    )

### 

​

Ollama
    
    
    crew = Crew(
        memory=True,
        embedder={
            "provider": "ollama",
            "config": {"model": "mxbai-embed-large"}
        }
    )

### 

​

Google AI
    
    
    crew = Crew(
        memory=True,
        embedder={
            "provider": "google",
            "config": {
                "api_key": "your-api-key",
                "model": "text-embedding-004"
            }
        }
    )

### 

​

Azure OpenAI
    
    
    crew = Crew(
        memory=True,
        embedder={
            "provider": "openai",
            "config": {
                "api_key": "your-api-key",
                "api_base": "https://your-resource.openai.azure.com/",
                "api_version": "2023-05-15",
                "model_name": "text-embedding-3-small"
            }
        }
    )

### 

​

Vertex AI
    
    
    crew = Crew(
        memory=True,
        embedder={
            "provider": "vertexai",
            "config": {
                "project_id": "your-project-id",
                "region": "your-region",
                "api_key": "your-api-key",
                "model_name": "textembedding-gecko"
            }
        }
    )

## 

​

Security Best Practices

### 

​

Environment Variables
    
    
    import os
    from crewai import Crew
    
    # Store sensitive data in environment variables
    crew = Crew(
        memory=True,
        embedder={
            "provider": "openai",
            "config": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "model": "text-embedding-3-small"
            }
        }
    )

### 

​

Storage Security
    
    
    import os
    from crewai import Crew
    from crewai.memory import LongTermMemory
    from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
    
    # Use secure storage paths
    storage_path = os.getenv("CREWAI_STORAGE_DIR", "./storage")
    os.makedirs(storage_path, mode=0o700, exist_ok=True)  # Restricted permissions
    
    crew = Crew(
        memory=True,
        long_term_memory=LongTermMemory(
            storage=LTMSQLiteStorage(
                db_path=f"{storage_path}/memory.db"
            )
        )
    )

## 

​

Troubleshooting

### 

​

Common Issues

**Memory not persisting between sessions?**

  * Check `CREWAI_STORAGE_DIR` environment variable
  * Ensure write permissions to storage directory
  * Verify memory is enabled with `memory=True`



**Mem0 authentication errors?**

  * Verify `MEM0_API_KEY` environment variable is set
  * Check API key permissions on Mem0 dashboard
  * Ensure `mem0ai` package is installed



**High memory usage with large datasets?**

  * Consider using External Memory with custom storage
  * Implement pagination in custom storage search methods
  * Use smaller embedding models for reduced memory footprint



### 

​

Performance Tips

  * Use `memory=True` for most use cases (simplest and fastest)
  * Only use User Memory if you need user-specific persistence
  * Consider External Memory for high-scale or specialized requirements
  * Choose smaller embedding models for faster processing
  * Set appropriate search limits to control memory retrieval size



## 

​

Benefits of Using CrewAI’s Memory System

  * 🦾 **Adaptive Learning:** Crews become more efficient over time, adapting to new information and refining their approach to tasks.
  * 🫡 **Enhanced Personalization:** Memory enables agents to remember user preferences and historical interactions, leading to personalized experiences.
  * 🧠 **Improved Problem Solving:** Access to a rich memory store aids agents in making more informed decisions, drawing on past learnings and contextual insights.



## 

​

Conclusion

Integrating CrewAI’s memory system into your projects is straightforward. By leveraging the provided memory components and configurations, you can quickly empower your agents with the ability to remember, reason, and learn from their interactions, unlocking new levels of intelligence and capability.

Was this page helpful?

YesNo

[Training](/concepts/training)[Reasoning](/concepts/reasoning)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Overview
  * Memory System Components
  * 1\. Basic Memory System (Recommended)
  * Quick Start
  * How It Works
  * Storage Location Transparency
  * Where CrewAI Stores Files
  * Default Storage Locations by Platform
  * Finding Your Storage Location
  * Controlling Storage Locations
  * Option 1: Environment Variable (Recommended)
  * Option 2: Custom Storage Paths
  * Option 3: Project-Specific Storage
  * Embedding Provider Defaults
  * Understanding Default Behavior
  * Customizing Embedding Providers
  * Debugging Storage Issues
  * Check Storage Permissions
  * Inspect ChromaDB Collections
  * Reset Storage (Debugging)
  * Production Best Practices
  * Common Storage Issues
  * Custom Embedder Configuration
  * Why Choose Different Embedding Providers?
  * OpenAI Embeddings (Default)
  * Azure OpenAI Embeddings
  * Google AI Embeddings
  * Vertex AI Embeddings
  * Ollama Embeddings (Local)
  * Cohere Embeddings
  * VoyageAI Embeddings
  * AWS Bedrock Embeddings
  * Hugging Face Embeddings
  * IBM Watson Embeddings
  * Choosing the Right Embedding Provider
  * Environment Variable Configuration
  * Testing Different Embedding Providers
  * Troubleshooting Embedding Issues
  * 2\. User Memory with Mem0 (Legacy)
  * Prerequisites
  * Mem0 Cloud Configuration
  * Advanced Mem0 Configuration
  * Local Mem0 Configuration
  * 3\. External Memory (New Approach)
  * Basic External Memory with Mem0
  * Custom Storage Implementation
  * Memory System Comparison
  * Supported Embedding Providers
  * OpenAI (Default)
  * Ollama
  * Google AI
  * Azure OpenAI
  * Vertex AI
  * Security Best Practices
  * Environment Variables
  * Storage Security
  * Troubleshooting
  * Common Issues
  * Performance Tips
  * Benefits of Using CrewAI’s Memory System
  * Conclusion



Assistant

Responses are generated using AI and may contain mistakes.


---

### Training {#training}

**Source:** [https://docs.crewai.com/concepts/training](https://docs.crewai.com/concepts/training)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Core Concepts

Training

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Core Concepts

# Training

Copy page

Learn how to train your CrewAI agents by giving them feedback early on and get consistent results.

## 

​

Overview

The training feature in CrewAI allows you to train your AI agents using the command-line interface (CLI). By running the command `crewai train -n <n_iterations>`, you can specify the number of iterations for the training process.

During training, CrewAI utilizes techniques to optimize the performance of your agents along with human feedback. This helps the agents improve their understanding, decision-making, and problem-solving abilities.

### 

​

Training Your Crew Using the CLI

To use the training feature, follow these steps:

  1. Open your terminal or command prompt.
  2. Navigate to the directory where your CrewAI project is located.
  3. Run the following command:


    
    
    crewai train -n <n_iterations> <filename> (optional)

Replace `<n_iterations>` with the desired number of training iterations and `<filename>` with the appropriate filename ending with `.pkl`.

### 

​

Training Your Crew Programmatically

To train your crew programmatically, use the following steps:

  1. Define the number of iterations for training.
  2. Specify the input parameters for the training process.
  3. Execute the training command within a try-except block to handle potential errors.



Code
    
    
    n_iterations = 2
    inputs = {"topic": "CrewAI Training"}
    filename = "your_model.pkl"
    
    try:
        YourCrewName_Crew().crew().train(
          n_iterations=n_iterations, 
          inputs=inputs, 
          filename=filename
        )
    
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

### 

​

Key Points to Note

  * **Positive Integer Requirement:** Ensure that the number of iterations (`n_iterations`) is a positive integer. The code will raise a `ValueError` if this condition is not met.
  * **Filename Requirement:** Ensure that the filename ends with `.pkl`. The code will raise a `ValueError` if this condition is not met.
  * **Error Handling:** The code handles subprocess errors and unexpected exceptions, providing error messages to the user.



It is important to note that the training process may take some time, depending on the complexity of your agents and will also require your feedback on each iteration.

Once the training is complete, your agents will be equipped with enhanced capabilities and knowledge, ready to tackle complex tasks and provide more consistent and valuable insights.

Remember to regularly update and retrain your agents to ensure they stay up-to-date with the latest information and advancements in the field.

Happy training with CrewAI! 🚀

Was this page helpful?

YesNo

[Collaboration](/concepts/collaboration)[Memory](/concepts/memory)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Overview
  * Training Your Crew Using the CLI
  * Training Your Crew Programmatically
  * Key Points to Note



Assistant

Responses are generated using AI and may contain mistakes.


---

### Introduction {#introduction}

**Source:** [https://docs.crewai.com/core-concepts](https://docs.crewai.com/core-concepts)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Get Started

Introduction

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Get Started

# Introduction

Copy page

Build AI agent teams that work together to tackle complex tasks

# 

​

What is CrewAI?

**CrewAI is a lean, lightning-fast Python framework built entirely from scratch—completely independent of LangChain or other agent frameworks.**

CrewAI empowers developers with both high-level simplicity and precise low-level control, ideal for creating autonomous AI agents tailored to any scenario:

  * **[CrewAI Crews](/guides/crews/first-crew)** : Optimize for autonomy and collaborative intelligence, enabling you to create AI teams where each agent has specific roles, tools, and goals.
  * **[CrewAI Flows](/guides/flows/first-flow)** : Enable granular, event-driven control, single LLM calls for precise task orchestration and supports Crews natively.



With over 100,000 developers certified through our community courses, CrewAI is rapidly becoming the standard for enterprise-ready AI automation.

## 

​

How Crews Work

Just like a company has departments (Sales, Engineering, Marketing) working together under leadership to achieve business goals, CrewAI helps you create an organization of AI agents with specialized roles collaborating to accomplish complex tasks.

CrewAI Framework Overview

Component| Description| Key Features  
---|---|---  
**Crew**|  The top-level organization| • Manages AI agent teams  
• Oversees workflows  
• Ensures collaboration  
• Delivers outcomes  
**AI Agents**|  Specialized team members| • Have specific roles (researcher, writer)  
• Use designated tools  
• Can delegate tasks  
• Make autonomous decisions  
**Process**|  Workflow management system| • Defines collaboration patterns  
• Controls task assignments  
• Manages interactions  
• Ensures efficient execution  
**Tasks**|  Individual assignments| • Have clear objectives  
• Use specific tools  
• Feed into larger process  
• Produce actionable results  
  
### 

​

How It All Works Together

  1. The **Crew** organizes the overall operation
  2. **AI Agents** work on their specialized tasks
  3. The **Process** ensures smooth collaboration
  4. **Tasks** get completed to achieve the goal



## 

​

Key Features

## Role-Based Agents

Create specialized agents with defined roles, expertise, and goals - from researchers to analysts to writers

## Flexible Tools

Equip agents with custom tools and APIs to interact with external services and data sources

## Intelligent Collaboration

Agents work together, sharing insights and coordinating tasks to achieve complex objectives

## Task Management

Define sequential or parallel workflows, with agents automatically handling task dependencies

## 

​

How Flows Work

While Crews excel at autonomous collaboration, Flows provide structured automations, offering granular control over workflow execution. Flows ensure tasks are executed reliably, securely, and efficiently, handling conditional logic, loops, and dynamic state management with precision. Flows integrate seamlessly with Crews, enabling you to balance high autonomy with exacting control.

CrewAI Framework Overview

Component| Description| Key Features  
---|---|---  
**Flow**|  Structured workflow orchestration| • Manages execution paths  
• Handles state transitions  
• Controls task sequencing  
• Ensures reliable execution  
**Events**|  Triggers for workflow actions| • Initiate specific processes  
• Enable dynamic responses  
• Support conditional branching  
• Allow for real-time adaptation  
**States**|  Workflow execution contexts| • Maintain execution data  
• Enable persistence  
• Support resumability  
• Ensure execution integrity  
**Crew Support**|  Enhances workflow automation| • Injects pockets of agency when needed  
• Complements structured workflows  
• Balances automation with intelligence  
• Enables adaptive decision-making  
  
### 

​

Key Capabilities

## Event-Driven Orchestration

Define precise execution paths responding dynamically to events

## Fine-Grained Control

Manage workflow states and conditional execution securely and efficiently

## Native Crew Integration

Effortlessly combine with Crews for enhanced autonomy and intelligence

## Deterministic Execution

Ensure predictable outcomes with explicit control flow and error handling

## 

​

When to Use Crews vs. Flows

Understanding when to use [Crews](/guides/crews/first-crew) versus [Flows](/guides/flows/first-flow) is key to maximizing the potential of CrewAI in your applications.

Use Case| Recommended Approach| Why?  
---|---|---  
**Open-ended research**| [Crews](/guides/crews/first-crew)| When tasks require creative thinking, exploration, and adaptation  
**Content generation**| [Crews](/guides/crews/first-crew)| For collaborative creation of articles, reports, or marketing materials  
**Decision workflows**| [Flows](/guides/flows/first-flow)| When you need predictable, auditable decision paths with precise control  
**API orchestration**| [Flows](/guides/flows/first-flow)| For reliable integration with multiple external services in a specific sequence  
**Hybrid applications**|  Combined approach| Use [Flows](/guides/flows/first-flow) to orchestrate overall process with [Crews](/guides/crews/first-crew) handling complex subtasks  
  
### 

​

Decision Framework

  * **Choose[Crews](/guides/crews/first-crew) when:** You need autonomous problem-solving, creative collaboration, or exploratory tasks
  * **Choose[Flows](/guides/flows/first-flow) when:** You require deterministic outcomes, auditability, or precise control over execution
  * **Combine both when:** Your application needs both structured processes and pockets of autonomous intelligence



## 

​

Why Choose CrewAI?

  * 🧠 **Autonomous Operation** : Agents make intelligent decisions based on their roles and available tools
  * 📝 **Natural Interaction** : Agents communicate and collaborate like human team members
  * 🛠️ **Extensible Design** : Easy to add new tools, roles, and capabilities
  * 🚀 **Production Ready** : Built for reliability and scalability in real-world applications
  * 🔒 **Security-Focused** : Designed with enterprise security requirements in mind
  * 💰 **Cost-Efficient** : Optimized to minimize token usage and API calls



## 

​

Ready to Start Building?

## [Build Your First CrewStep-by-step tutorial to create a collaborative AI team that works together to solve complex problems.](/guides/crews/first-crew)## [Build Your First FlowLearn how to create structured, event-driven workflows with precise control over execution.](/guides/flows/first-flow)

## [Install CrewAIGet started with CrewAI in your development environment.](/installation)## [Quick StartFollow our quickstart guide to create your first CrewAI agent and get hands-on experience.](/quickstart)## [Join the CommunityConnect with other developers, get help, and share your CrewAI experiences.](https://community.crewai.com)

Was this page helpful?

YesNo

[Installation](/installation)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * What is CrewAI?
  * How Crews Work
  * How It All Works Together
  * Key Features
  * How Flows Work
  * Key Capabilities
  * When to Use Crews vs. Flows
  * Decision Framework
  * Why Choose CrewAI?
  * Ready to Start Building?



Assistant

Responses are generated using AI and may contain mistakes.


---



## Agents {#agents}

### Custom Manager Agent {#custom-manager-agent}

**Source:** [https://docs.crewai.com/learn/custom-manager-agent](https://docs.crewai.com/learn/custom-manager-agent)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Learn

Custom Manager Agent

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Learn

# Custom Manager Agent

Copy page

Learn how to set a custom agent as the manager in CrewAI, providing more control over task management and coordination.

# 

​

Setting a Specific Agent as Manager in CrewAI

CrewAI allows users to set a specific agent as the manager of the crew, providing more control over the management and coordination of tasks. This feature enables the customization of the managerial role to better fit your project’s requirements.

## 

​

Using the `manager_agent` Attribute

### 

​

Custom Manager Agent

The `manager_agent` attribute allows you to define a custom agent to manage the crew. This agent will oversee the entire process, ensuring that tasks are completed efficiently and to the highest standard.

### 

​

Example

Code
    
    
    import os
    from crewai import Agent, Task, Crew, Process
    
    # Define your agents
    researcher = Agent(
        role="Researcher",
        goal="Conduct thorough research and analysis on AI and AI agents",
        backstory="You're an expert researcher, specialized in technology, software engineering, AI, and startups. You work as a freelancer and are currently researching for a new client.",
        allow_delegation=False,
    )
    
    writer = Agent(
        role="Senior Writer",
        goal="Create compelling content about AI and AI agents",
        backstory="You're a senior writer, specialized in technology, software engineering, AI, and startups. You work as a freelancer and are currently writing content for a new client.",
        allow_delegation=False,
    )
    
    # Define your task
    task = Task(
        description="Generate a list of 5 interesting ideas for an article, then write one captivating paragraph for each idea that showcases the potential of a full article on this topic. Return the list of ideas with their paragraphs and your notes.",
        expected_output="5 bullet points, each with a paragraph and accompanying notes.",
    )
    
    # Define the manager agent
    manager = Agent(
        role="Project Manager",
        goal="Efficiently manage the crew and ensure high-quality task completion",
        backstory="You're an experienced project manager, skilled in overseeing complex projects and guiding teams to success. Your role is to coordinate the efforts of the crew members, ensuring that each task is completed on time and to the highest standard.",
        allow_delegation=True,
    )
    
    # Instantiate your crew with a custom manager
    crew = Crew(
        agents=[researcher, writer],
        tasks=[task],
        manager_agent=manager,
        process=Process.hierarchical,
    )
    
    # Start the crew's work
    result = crew.kickoff()

## 

​

Benefits of a Custom Manager Agent

  * **Enhanced Control** : Tailor the management approach to fit the specific needs of your project.
  * **Improved Coordination** : Ensure efficient task coordination and management by an experienced agent.
  * **Customizable Management** : Define managerial roles and responsibilities that align with your project’s goals.



## 

​

Setting a Manager LLM

If you’re using the hierarchical process and don’t want to set a custom manager agent, you can specify the language model for the manager:

Code
    
    
    from crewai import LLM
    
    manager_llm = LLM(model="gpt-4o")
    
    crew = Crew(
        agents=[researcher, writer],
        tasks=[task],
        process=Process.hierarchical,
        manager_llm=manager_llm
    )

Either `manager_agent` or `manager_llm` must be set when using the hierarchical process.

Was this page helpful?

YesNo

[Custom LLM Implementation](/learn/custom-llm)[Customize Agents](/learn/customizing-agents)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Setting a Specific Agent as Manager in CrewAI
  * Using the manager_agent Attribute
  * Custom Manager Agent
  * Example
  * Benefits of a Custom Manager Agent
  * Setting a Manager LLM



Assistant

Responses are generated using AI and may contain mistakes.


---

### Using Multimodal Agents {#using-multimodal-agents}

**Source:** [https://docs.crewai.com/learn/multimodal-agents](https://docs.crewai.com/learn/multimodal-agents)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Learn

Using Multimodal Agents

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Learn

# Using Multimodal Agents

Copy page

Learn how to enable and use multimodal capabilities in your agents for processing images and other non-text content within the CrewAI framework.

## 

​

Using Multimodal Agents

CrewAI supports multimodal agents that can process both text and non-text content like images. This guide will show you how to enable and use multimodal capabilities in your agents.

### 

​

Enabling Multimodal Capabilities

To create a multimodal agent, simply set the `multimodal` parameter to `True` when initializing your agent:
    
    
    from crewai import Agent
    
    agent = Agent(
        role="Image Analyst",
        goal="Analyze and extract insights from images",
        backstory="An expert in visual content interpretation with years of experience in image analysis",
        multimodal=True  # This enables multimodal capabilities
    )

When you set `multimodal=True`, the agent is automatically configured with the necessary tools for handling non-text content, including the `AddImageTool`.

### 

​

Working with Images

The multimodal agent comes pre-configured with the `AddImageTool`, which allows it to process images. You don’t need to manually add this tool - it’s automatically included when you enable multimodal capabilities.

Here’s a complete example showing how to use a multimodal agent to analyze an image:
    
    
    from crewai import Agent, Task, Crew
    
    # Create a multimodal agent
    image_analyst = Agent(
        role="Product Analyst",
        goal="Analyze product images and provide detailed descriptions",
        backstory="Expert in visual product analysis with deep knowledge of design and features",
        multimodal=True
    )
    
    # Create a task for image analysis
    task = Task(
        description="Analyze the product image at https://example.com/product.jpg and provide a detailed description",
        expected_output="A detailed description of the product image",
        agent=image_analyst
    )
    
    # Create and run the crew
    crew = Crew(
        agents=[image_analyst],
        tasks=[task]
    )
    
    result = crew.kickoff()

### 

​

Advanced Usage with Context

You can provide additional context or specific questions about the image when creating tasks for multimodal agents. The task description can include specific aspects you want the agent to focus on:
    
    
    from crewai import Agent, Task, Crew
    
    # Create a multimodal agent for detailed analysis
    expert_analyst = Agent(
        role="Visual Quality Inspector",
        goal="Perform detailed quality analysis of product images",
        backstory="Senior quality control expert with expertise in visual inspection",
        multimodal=True  # AddImageTool is automatically included
    )
    
    # Create a task with specific analysis requirements
    inspection_task = Task(
        description="""
        Analyze the product image at https://example.com/product.jpg with focus on:
        1. Quality of materials
        2. Manufacturing defects
        3. Compliance with standards
        Provide a detailed report highlighting any issues found.
        """,
        expected_output="A detailed report highlighting any issues found",
        agent=expert_analyst
    )
    
    # Create and run the crew
    crew = Crew(
        agents=[expert_analyst],
        tasks=[inspection_task]
    )
    
    result = crew.kickoff()

### 

​

Tool Details

When working with multimodal agents, the `AddImageTool` is automatically configured with the following schema:
    
    
    class AddImageToolSchema:
        image_url: str  # Required: The URL or path of the image to process
        action: Optional[str] = None  # Optional: Additional context or specific questions about the image

The multimodal agent will automatically handle the image processing through its built-in tools, allowing it to:

  * Access images via URLs or local file paths
  * Process image content with optional context or specific questions
  * Provide analysis and insights based on the visual information and task requirements



### 

​

Best Practices

When working with multimodal agents, keep these best practices in mind:

  1. **Image Access**

     * Ensure your images are accessible via URLs that the agent can reach
     * For local images, consider hosting them temporarily or using absolute file paths
     * Verify that image URLs are valid and accessible before running tasks
  2. **Task Description**

     * Be specific about what aspects of the image you want the agent to analyze
     * Include clear questions or requirements in the task description
     * Consider using the optional `action` parameter for focused analysis
  3. **Resource Management**

     * Image processing may require more computational resources than text-only tasks
     * Some language models may require base64 encoding for image data
     * Consider batch processing for multiple images to optimize performance
  4. **Environment Setup**

     * Verify that your environment has the necessary dependencies for image processing
     * Ensure your language model supports multimodal capabilities
     * Test with small images first to validate your setup
  5. **Error Handling**

     * Implement proper error handling for image loading failures
     * Have fallback strategies for when image processing fails
     * Monitor and log image processing operations for debugging



Was this page helpful?

YesNo

[Connect to any LLM](/learn/llm-connections)[Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Using Multimodal Agents
  * Enabling Multimodal Capabilities
  * Working with Images
  * Advanced Usage with Context
  * Tool Details
  * Best Practices



Assistant

Responses are generated using AI and may contain mistakes.


---

### Customize Agents {#customize-agents}

**Source:** [https://docs.crewai.com/learn/customizing-agents](https://docs.crewai.com/learn/customizing-agents)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Learn

Customize Agents

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Learn

# Customize Agents

Copy page

A comprehensive guide to tailoring agents for specific roles, tasks, and advanced customizations within the CrewAI framework.

## 

​

Customizable Attributes

Crafting an efficient CrewAI team hinges on the ability to dynamically tailor your AI agents to meet the unique requirements of any project. This section covers the foundational attributes you can customize.

### 

​

Key Attributes for Customization

Attribute| Description  
---|---  
**Role**|  Specifies the agent’s job within the crew, such as ‘Analyst’ or ‘Customer Service Rep’.  
**Goal**|  Defines the agent’s objectives, aligned with its role and the crew’s overarching mission.  
**Backstory**|  Provides depth to the agent’s persona, enhancing motivations and engagements within the crew.  
**Tools** _(Optional)_|  Represents the capabilities or methods the agent uses for tasks, from simple functions to complex integrations.  
**Cache** _(Optional)_|  Determines if the agent should use a cache for tool usage.  
**Max RPM**|  Sets the maximum requests per minute (`max_rpm`). Can be set to `None` for unlimited requests to external services.  
**Verbose** _(Optional)_|  Enables detailed logging for debugging and optimization, providing insights into execution processes.  
**Allow Delegation** _(Optional)_|  Controls task delegation to other agents, default is `False`.  
**Max Iter** _(Optional)_|  Limits the maximum number of iterations (`max_iter`) for a task to prevent infinite loops, with a default of 25.  
**Max Execution Time** _(Optional)_|  Sets the maximum time allowed for an agent to complete a task.  
**System Template** _(Optional)_|  Defines the system format for the agent.  
**Prompt Template** _(Optional)_|  Defines the prompt format for the agent.  
**Response Template** _(Optional)_|  Defines the response format for the agent.  
**Use System Prompt** _(Optional)_|  Controls whether the agent will use a system prompt during task execution.  
**Respect Context Window**|  Enables a sliding context window by default, maintaining context size.  
**Max Retry Limit**|  Sets the maximum number of retries (`max_retry_limit`) for an agent in case of errors.  
  
## 

​

Advanced Customization Options

Beyond the basic attributes, CrewAI allows for deeper customization to enhance an agent’s behavior and capabilities significantly.

### 

​

Language Model Customization

Agents can be customized with specific language models (`llm`) and function-calling language models (`function_calling_llm`), offering advanced control over their processing and decision-making abilities. It’s important to note that setting the `function_calling_llm` allows for overriding the default crew function-calling language model, providing a greater degree of customization.

## 

​

Performance and Debugging Settings

Adjusting an agent’s performance and monitoring its operations are crucial for efficient task execution.

### 

​

Verbose Mode and RPM Limit

  * **Verbose Mode** : Enables detailed logging of an agent’s actions, useful for debugging and optimization. Specifically, it provides insights into agent execution processes, aiding in the optimization of performance.
  * **RPM Limit** : Sets the maximum number of requests per minute (`max_rpm`). This attribute is optional and can be set to `None` for no limit, allowing for unlimited queries to external services if needed.



### 

​

Maximum Iterations for Task Execution

The `max_iter` attribute allows users to define the maximum number of iterations an agent can perform for a single task, preventing infinite loops or excessively long executions. The default value is set to 25, providing a balance between thoroughness and efficiency. Once the agent approaches this number, it will try its best to give a good answer.

## 

​

Customizing Agents and Tools

Agents are customized by defining their attributes and tools during initialization. Tools are critical for an agent’s functionality, enabling them to perform specialized tasks. The `tools` attribute should be an array of tools the agent can utilize, and it’s initialized as an empty list by default. Tools can be added or modified post-agent initialization to adapt to new requirements.
    
    
    pip install 'crewai[tools]'

### 

​

Example: Assigning Tools to an Agent

Code
    
    
    import os
    from crewai import Agent
    from crewai_tools import SerperDevTool
    
    # Set API keys for tool initialization
    os.environ["OPENAI_API_KEY"] = "Your Key"
    os.environ["SERPER_API_KEY"] = "Your Key"
    
    # Initialize a search tool
    search_tool = SerperDevTool()
    
    # Initialize the agent with advanced options
    agent = Agent(
      role='Research Analyst',
      goal='Provide up-to-date market analysis',
      backstory='An expert analyst with a keen eye for market trends.',
      tools=[search_tool],
      memory=True, # Enable memory
      verbose=True,
      max_rpm=None, # No limit on requests per minute
      max_iter=25, # Default value for maximum iterations
    )

## 

​

Delegation and Autonomy

Controlling an agent’s ability to delegate tasks or ask questions is vital for tailoring its autonomy and collaborative dynamics within the CrewAI framework. By default, the `allow_delegation` attribute is now set to `False`, disabling agents to seek assistance or delegate tasks as needed. This default behavior can be changed to promote collaborative problem-solving and efficiency within the CrewAI ecosystem. If needed, delegation can be enabled to suit specific operational requirements.

### 

​

Example: Disabling Delegation for an Agent

Code
    
    
    agent = Agent(
      role='Content Writer',
      goal='Write engaging content on market trends',
      backstory='A seasoned writer with expertise in market analysis.',
      allow_delegation=True # Enabling delegation
    )

## 

​

Conclusion

Customizing agents in CrewAI by setting their roles, goals, backstories, and tools, alongside advanced options like language model customization, memory, performance settings, and delegation preferences, equips a nuanced and capable AI team ready for complex challenges.

Was this page helpful?

YesNo

[Custom Manager Agent](/learn/custom-manager-agent)[Image Generation with DALL-E](/learn/dalle-image-generation)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Customizable Attributes
  * Key Attributes for Customization
  * Advanced Customization Options
  * Language Model Customization
  * Performance and Debugging Settings
  * Verbose Mode and RPM Limit
  * Maximum Iterations for Task Execution
  * Customizing Agents and Tools
  * Example: Assigning Tools to an Agent
  * Delegation and Autonomy
  * Example: Disabling Delegation for an Agent
  * Conclusion



Assistant

Responses are generated using AI and may contain mistakes.


---

### Agents {#agents}

**Source:** [https://docs.crewai.com/concepts/agents](https://docs.crewai.com/concepts/agents)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Core Concepts

Agents

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Core Concepts

# Agents

Copy page

Detailed guide on creating and managing agents within the CrewAI framework.

## 

​

Overview of an Agent

In the CrewAI framework, an `Agent` is an autonomous unit that can:

  * Perform specific tasks
  * Make decisions based on its role and goal
  * Use tools to accomplish objectives
  * Communicate and collaborate with other agents
  * Maintain memory of interactions
  * Delegate tasks when allowed



Think of an agent as a specialized team member with specific skills, expertise, and responsibilities. For example, a `Researcher` agent might excel at gathering and analyzing information, while a `Writer` agent might be better at creating content.

CrewAI Enterprise includes a Visual Agent Builder that simplifies agent creation and configuration without writing code. Design your agents visually and test them in real-time.

The Visual Agent Builder enables:

  * Intuitive agent configuration with form-based interfaces
  * Real-time testing and validation
  * Template library with pre-configured agent types
  * Easy customization of agent attributes and behaviors



## 

​

Agent Attributes

Attribute| Parameter| Type| Description  
---|---|---|---  
**Role**| `role`| `str`| Defines the agent’s function and expertise within the crew.  
**Goal**| `goal`| `str`| The individual objective that guides the agent’s decision-making.  
**Backstory**| `backstory`| `str`| Provides context and personality to the agent, enriching interactions.  
**LLM** _(optional)_| `llm`| `Union[str, LLM, Any]`| Language model that powers the agent. Defaults to the model specified in `OPENAI_MODEL_NAME` or “gpt-4”.  
**Tools** _(optional)_| `tools`| `List[BaseTool]`| Capabilities or functions available to the agent. Defaults to an empty list.  
**Function Calling LLM** _(optional)_| `function_calling_llm`| `Optional[Any]`| Language model for tool calling, overrides crew’s LLM if specified.  
**Max Iterations** _(optional)_| `max_iter`| `int`| Maximum iterations before the agent must provide its best answer. Default is 20.  
**Max RPM** _(optional)_| `max_rpm`| `Optional[int]`| Maximum requests per minute to avoid rate limits.  
**Max Execution Time** _(optional)_| `max_execution_time`| `Optional[int]`| Maximum time (in seconds) for task execution.  
**Memory** _(optional)_| `memory`| `bool`| Whether the agent should maintain memory of interactions. Default is True.  
**Verbose** _(optional)_| `verbose`| `bool`| Enable detailed execution logs for debugging. Default is False.  
**Allow Delegation** _(optional)_| `allow_delegation`| `bool`| Allow the agent to delegate tasks to other agents. Default is False.  
**Step Callback** _(optional)_| `step_callback`| `Optional[Any]`| Function called after each agent step, overrides crew callback.  
**Cache** _(optional)_| `cache`| `bool`| Enable caching for tool usage. Default is True.  
**System Template** _(optional)_| `system_template`| `Optional[str]`| Custom system prompt template for the agent.  
**Prompt Template** _(optional)_| `prompt_template`| `Optional[str]`| Custom prompt template for the agent.  
**Response Template** _(optional)_| `response_template`| `Optional[str]`| Custom response template for the agent.  
**Allow Code Execution** _(optional)_| `allow_code_execution`| `Optional[bool]`| Enable code execution for the agent. Default is False.  
**Max Retry Limit** _(optional)_| `max_retry_limit`| `int`| Maximum number of retries when an error occurs. Default is 2.  
**Respect Context Window** _(optional)_| `respect_context_window`| `bool`| Keep messages under context window size by summarizing. Default is True.  
**Code Execution Mode** _(optional)_| `code_execution_mode`| `Literal["safe", "unsafe"]`| Mode for code execution: ‘safe’ (using Docker) or ‘unsafe’ (direct). Default is ‘safe’.  
**Multimodal** _(optional)_| `multimodal`| `bool`| Whether the agent supports multimodal capabilities. Default is False.  
**Inject Date** _(optional)_| `inject_date`| `bool`| Whether to automatically inject the current date into tasks. Default is False.  
**Date Format** _(optional)_| `date_format`| `str`| Format string for date when inject_date is enabled. Default is “%Y-%m-%d” (ISO format).  
**Reasoning** _(optional)_| `reasoning`| `bool`| Whether the agent should reflect and create a plan before executing a task. Default is False.  
**Max Reasoning Attempts** _(optional)_| `max_reasoning_attempts`| `Optional[int]`| Maximum number of reasoning attempts before executing the task. If None, will try until ready.  
**Embedder** _(optional)_| `embedder`| `Optional[Dict[str, Any]]`| Configuration for the embedder used by the agent.  
**Knowledge Sources** _(optional)_| `knowledge_sources`| `Optional[List[BaseKnowledgeSource]]`| Knowledge sources available to the agent.  
**Use System Prompt** _(optional)_| `use_system_prompt`| `Optional[bool]`| Whether to use system prompt (for o1 model support). Default is True.  
  
## 

​

Creating Agents

There are two ways to create agents in CrewAI: using **YAML configuration (recommended)** or defining them **directly in code**.

### 

​

YAML Configuration (Recommended)

Using YAML configuration provides a cleaner, more maintainable way to define agents. We strongly recommend using this approach in your CrewAI projects.

After creating your CrewAI project as outlined in the [Installation](/installation) section, navigate to the `src/latest_ai_development/config/agents.yaml` file and modify the template to match your requirements.

Variables in your YAML files (like `{topic}`) will be replaced with values from your inputs when running the crew:

Code
    
    
    crew.kickoff(inputs={'topic': 'AI Agents'})

Here’s an example of how to configure agents using YAML:

agents.yaml
    
    
    # src/latest_ai_development/config/agents.yaml
    researcher:
      role: >
        {topic} Senior Data Researcher
      goal: >
        Uncover cutting-edge developments in {topic}
      backstory: >
        You're a seasoned researcher with a knack for uncovering the latest
        developments in {topic}. Known for your ability to find the most relevant
        information and present it in a clear and concise manner.
    
    reporting_analyst:
      role: >
        {topic} Reporting Analyst
      goal: >
        Create detailed reports based on {topic} data analysis and research findings
      backstory: >
        You're a meticulous analyst with a keen eye for detail. You're known for
        your ability to turn complex data into clear and concise reports, making
        it easy for others to understand and act on the information you provide.

To use this YAML configuration in your code, create a crew class that inherits from `CrewBase`:

Code
    
    
    # src/latest_ai_development/crew.py
    from crewai import Agent, Crew, Process
    from crewai.project import CrewBase, agent, crew
    from crewai_tools import SerperDevTool
    
    @CrewBase
    class LatestAiDevelopmentCrew():
      """LatestAiDevelopment crew"""
    
      agents_config = "config/agents.yaml"
    
      @agent
      def researcher(self) -> Agent:
        return Agent(
          config=self.agents_config['researcher'], # type: ignore[index]
          verbose=True,
          tools=[SerperDevTool()]
        )
    
      @agent
      def reporting_analyst(self) -> Agent:
        return Agent(
          config=self.agents_config['reporting_analyst'], # type: ignore[index]
          verbose=True
        )

The names you use in your YAML files (`agents.yaml`) should match the method names in your Python code.

### 

​

Direct Code Definition

You can create agents directly in code by instantiating the `Agent` class. Here’s a comprehensive example showing all available parameters:

Code
    
    
    from crewai import Agent
    from crewai_tools import SerperDevTool
    
    # Create an agent with all available parameters
    agent = Agent(
        role="Senior Data Scientist",
        goal="Analyze and interpret complex datasets to provide actionable insights",
        backstory="With over 10 years of experience in data science and machine learning, "
                  "you excel at finding patterns in complex datasets.",
        llm="gpt-4",  # Default: OPENAI_MODEL_NAME or "gpt-4"
        function_calling_llm=None,  # Optional: Separate LLM for tool calling
        memory=True,  # Default: True
        verbose=False,  # Default: False
        allow_delegation=False,  # Default: False
        max_iter=20,  # Default: 20 iterations
        max_rpm=None,  # Optional: Rate limit for API calls
        max_execution_time=None,  # Optional: Maximum execution time in seconds
        max_retry_limit=2,  # Default: 2 retries on error
        allow_code_execution=False,  # Default: False
        code_execution_mode="safe",  # Default: "safe" (options: "safe", "unsafe")
        respect_context_window=True,  # Default: True
        use_system_prompt=True,  # Default: True
        multimodal=False,  # Default: False
        inject_date=False,  # Default: False
        date_format="%Y-%m-%d",  # Default: ISO format
        reasoning=False,  # Default: False
        max_reasoning_attempts=None,  # Default: None
        tools=[SerperDevTool()],  # Optional: List of tools
        knowledge_sources=None,  # Optional: List of knowledge sources
        embedder=None,  # Optional: Custom embedder configuration
        system_template=None,  # Optional: Custom system prompt template
        prompt_template=None,  # Optional: Custom prompt template
        response_template=None,  # Optional: Custom response template
        step_callback=None,  # Optional: Callback function for monitoring
    )

Let’s break down some key parameter combinations for common use cases:

#### 

​

Basic Research Agent

Code
    
    
    research_agent = Agent(
        role="Research Analyst",
        goal="Find and summarize information about specific topics",
        backstory="You are an experienced researcher with attention to detail",
        tools=[SerperDevTool()],
        verbose=True  # Enable logging for debugging
    )

#### 

​

Code Development Agent

Code
    
    
    dev_agent = Agent(
        role="Senior Python Developer",
        goal="Write and debug Python code",
        backstory="Expert Python developer with 10 years of experience",
        allow_code_execution=True,
        code_execution_mode="safe",  # Uses Docker for safety
        max_execution_time=300,  # 5-minute timeout
        max_retry_limit=3  # More retries for complex code tasks
    )

#### 

​

Long-Running Analysis Agent

Code
    
    
    analysis_agent = Agent(
        role="Data Analyst",
        goal="Perform deep analysis of large datasets",
        backstory="Specialized in big data analysis and pattern recognition",
        memory=True,
        respect_context_window=True,
        max_rpm=10,  # Limit API calls
        function_calling_llm="gpt-4o-mini"  # Cheaper model for tool calls
    )

#### 

​

Custom Template Agent

Code
    
    
    custom_agent = Agent(
        role="Customer Service Representative",
        goal="Assist customers with their inquiries",
        backstory="Experienced in customer support with a focus on satisfaction",
        system_template="""<|start_header_id|>system<|end_header_id|>
                            {{ .System }}<|eot_id|>""",
        prompt_template="""<|start_header_id|>user<|end_header_id|>
                            {{ .Prompt }}<|eot_id|>""",
        response_template="""<|start_header_id|>assistant<|end_header_id|>
                            {{ .Response }}<|eot_id|>""",
    )

#### 

​

Date-Aware Agent with Reasoning

Code
    
    
    strategic_agent = Agent(
        role="Market Analyst",
        goal="Track market movements with precise date references and strategic planning",
        backstory="Expert in time-sensitive financial analysis and strategic reporting",
        inject_date=True,  # Automatically inject current date into tasks
        date_format="%B %d, %Y",  # Format as "May 21, 2025"
        reasoning=True,  # Enable strategic planning
        max_reasoning_attempts=2,  # Limit planning iterations
        verbose=True
    )

#### 

​

Reasoning Agent

Code
    
    
    reasoning_agent = Agent(
        role="Strategic Planner",
        goal="Analyze complex problems and create detailed execution plans",
        backstory="Expert strategic planner who methodically breaks down complex challenges",
        reasoning=True,  # Enable reasoning and planning
        max_reasoning_attempts=3,  # Limit reasoning attempts
        max_iter=30,  # Allow more iterations for complex planning
        verbose=True
    )

#### 

​

Multimodal Agent

Code
    
    
    multimodal_agent = Agent(
        role="Visual Content Analyst",
        goal="Analyze and process both text and visual content",
        backstory="Specialized in multimodal analysis combining text and image understanding",
        multimodal=True,  # Enable multimodal capabilities
        verbose=True
    )

### 

​

Parameter Details

#### 

​

Critical Parameters

  * `role`, `goal`, and `backstory` are required and shape the agent’s behavior
  * `llm` determines the language model used (default: OpenAI’s GPT-4)



#### 

​

Memory and Context

  * `memory`: Enable to maintain conversation history
  * `respect_context_window`: Prevents token limit issues
  * `knowledge_sources`: Add domain-specific knowledge bases



#### 

​

Execution Control

  * `max_iter`: Maximum attempts before giving best answer
  * `max_execution_time`: Timeout in seconds
  * `max_rpm`: Rate limiting for API calls
  * `max_retry_limit`: Retries on error



#### 

​

Code Execution

  * `allow_code_execution`: Must be True to run code
  * `code_execution_mode`:
    * `"safe"`: Uses Docker (recommended for production)
    * `"unsafe"`: Direct execution (use only in trusted environments)



#### 

​

Advanced Features

  * `multimodal`: Enable multimodal capabilities for processing text and visual content
  * `reasoning`: Enable agent to reflect and create plans before executing tasks
  * `inject_date`: Automatically inject current date into task descriptions



#### 

​

Templates

  * `system_template`: Defines agent’s core behavior
  * `prompt_template`: Structures input format
  * `response_template`: Formats agent responses



When using custom templates, ensure that both `system_template` and `prompt_template` are defined. The `response_template` is optional but recommended for consistent output formatting.

When using custom templates, you can use variables like `{role}`, `{goal}`, and `{backstory}` in your templates. These will be automatically populated during execution.

## 

​

Agent Tools

Agents can be equipped with various tools to enhance their capabilities. CrewAI supports tools from:

  * [CrewAI Toolkit](https://github.com/joaomdmoura/crewai-tools)
  * [LangChain Tools](https://python.langchain.com/docs/integrations/tools)



Here’s how to add tools to an agent:

Code
    
    
    from crewai import Agent
    from crewai_tools import SerperDevTool, WikipediaTools
    
    # Create tools
    search_tool = SerperDevTool()
    wiki_tool = WikipediaTools()
    
    # Add tools to agent
    researcher = Agent(
        role="AI Technology Researcher",
        goal="Research the latest AI developments",
        tools=[search_tool, wiki_tool],
        verbose=True
    )

## 

​

Agent Memory and Context

Agents can maintain memory of their interactions and use context from previous tasks. This is particularly useful for complex workflows where information needs to be retained across multiple tasks.

Code
    
    
    from crewai import Agent
    
    analyst = Agent(
        role="Data Analyst",
        goal="Analyze and remember complex data patterns",
        memory=True,  # Enable memory
        verbose=True
    )

When `memory` is enabled, the agent will maintain context across multiple interactions, improving its ability to handle complex, multi-step tasks.

## 

​

Context Window Management

CrewAI includes sophisticated automatic context window management to handle situations where conversations exceed the language model’s token limits. This powerful feature is controlled by the `respect_context_window` parameter.

### 

​

How Context Window Management Works

When an agent’s conversation history grows too large for the LLM’s context window, CrewAI automatically detects this situation and can either:

  1. **Automatically summarize content** (when `respect_context_window=True`)
  2. **Stop execution with an error** (when `respect_context_window=False`)



### 

​

Automatic Context Handling (`respect_context_window=True`)

This is the **default and recommended setting** for most use cases. When enabled, CrewAI will:

Code
    
    
    # Agent with automatic context management (default)
    smart_agent = Agent(
        role="Research Analyst",
        goal="Analyze large documents and datasets",
        backstory="Expert at processing extensive information",
        respect_context_window=True,  # 🔑 Default: auto-handle context limits
        verbose=True
    )

**What happens when context limits are exceeded:**

  * ⚠️ **Warning message** : `"Context length exceeded. Summarizing content to fit the model context window."`
  * 🔄 **Automatic summarization** : CrewAI intelligently summarizes the conversation history
  * ✅ **Continued execution** : Task execution continues seamlessly with the summarized context
  * 📝 **Preserved information** : Key information is retained while reducing token count



### 

​

Strict Context Limits (`respect_context_window=False`)

When you need precise control and prefer execution to stop rather than lose any information:

Code
    
    
    # Agent with strict context limits
    strict_agent = Agent(
        role="Legal Document Reviewer",
        goal="Provide precise legal analysis without information loss",
        backstory="Legal expert requiring complete context for accurate analysis",
        respect_context_window=False,  # ❌ Stop execution on context limit
        verbose=True
    )

**What happens when context limits are exceeded:**

  * ❌ **Error message** : `"Context length exceeded. Consider using smaller text or RAG tools from crewai_tools."`
  * 🛑 **Execution stops** : Task execution halts immediately
  * 🔧 **Manual intervention required** : You need to modify your approach



### 

​

Choosing the Right Setting

#### 

​

Use `respect_context_window=True` (Default) when:

  * **Processing large documents** that might exceed context limits
  * **Long-running conversations** where some summarization is acceptable
  * **Research tasks** where general context is more important than exact details
  * **Prototyping and development** where you want robust execution



Code
    
    
    # Perfect for document processing
    document_processor = Agent(
        role="Document Analyst", 
        goal="Extract insights from large research papers",
        backstory="Expert at analyzing extensive documentation",
        respect_context_window=True,  # Handle large documents gracefully
        max_iter=50,  # Allow more iterations for complex analysis
        verbose=True
    )

#### 

​

Use `respect_context_window=False` when:

  * **Precision is critical** and information loss is unacceptable
  * **Legal or medical tasks** requiring complete context
  * **Code review** where missing details could introduce bugs
  * **Financial analysis** where accuracy is paramount



Code
    
    
    # Perfect for precision tasks
    precision_agent = Agent(
        role="Code Security Auditor",
        goal="Identify security vulnerabilities in code",
        backstory="Security expert requiring complete code context",
        respect_context_window=False,  # Prefer failure over incomplete analysis
        max_retry_limit=1,  # Fail fast on context issues
        verbose=True
    )

### 

​

Alternative Approaches for Large Data

When dealing with very large datasets, consider these strategies:

#### 

​

1\. Use RAG Tools

Code
    
    
    from crewai_tools import RagTool
    
    # Create RAG tool for large document processing
    rag_tool = RagTool()
    
    rag_agent = Agent(
        role="Research Assistant",
        goal="Query large knowledge bases efficiently",
        backstory="Expert at using RAG tools for information retrieval",
        tools=[rag_tool],  # Use RAG instead of large context windows
        respect_context_window=True,
        verbose=True
    )

#### 

​

2\. Use Knowledge Sources

Code
    
    
    # Use knowledge sources instead of large prompts
    knowledge_agent = Agent(
        role="Knowledge Expert",
        goal="Answer questions using curated knowledge",
        backstory="Expert at leveraging structured knowledge sources",
        knowledge_sources=[your_knowledge_sources],  # Pre-processed knowledge
        respect_context_window=True,
        verbose=True
    )

### 

​

Context Window Best Practices

  1. **Monitor Context Usage** : Enable `verbose=True` to see context management in action
  2. **Design for Efficiency** : Structure tasks to minimize context accumulation
  3. **Use Appropriate Models** : Choose LLMs with context windows suitable for your tasks
  4. **Test Both Settings** : Try both `True` and `False` to see which works better for your use case
  5. **Combine with RAG** : Use RAG tools for very large datasets instead of relying solely on context windows



### 

​

Troubleshooting Context Issues

**If you’re getting context limit errors:**

Code
    
    
    # Quick fix: Enable automatic handling
    agent.respect_context_window = True
    
    # Better solution: Use RAG tools for large data
    from crewai_tools import RagTool
    agent.tools = [RagTool()]
    
    # Alternative: Break tasks into smaller pieces
    # Or use knowledge sources instead of large prompts

**If automatic summarization loses important information:**

Code
    
    
    # Disable auto-summarization and use RAG instead
    agent = Agent(
        role="Detailed Analyst",
        goal="Maintain complete information accuracy",
        backstory="Expert requiring full context",
        respect_context_window=False,  # No summarization
        tools=[RagTool()],  # Use RAG for large data
        verbose=True
    )

The context window management feature works automatically in the background. You don’t need to call any special functions - just set `respect_context_window` to your preferred behavior and CrewAI handles the rest!

## 

​

Important Considerations and Best Practices

### 

​

Security and Code Execution

  * When using `allow_code_execution`, be cautious with user input and always validate it
  * Use `code_execution_mode: "safe"` (Docker) in production environments
  * Consider setting appropriate `max_execution_time` limits to prevent infinite loops



### 

​

Performance Optimization

  * Use `respect_context_window: true` to prevent token limit issues
  * Set appropriate `max_rpm` to avoid rate limiting
  * Enable `cache: true` to improve performance for repetitive tasks
  * Adjust `max_iter` and `max_retry_limit` based on task complexity



### 

​

Memory and Context Management

  * Use `memory: true` for tasks requiring historical context
  * Leverage `knowledge_sources` for domain-specific information
  * Configure `embedder` when using custom embedding models
  * Use custom templates (`system_template`, `prompt_template`, `response_template`) for fine-grained control over agent behavior



### 

​

Advanced Features

  * Enable `reasoning: true` for agents that need to plan and reflect before executing complex tasks
  * Set appropriate `max_reasoning_attempts` to control planning iterations (None for unlimited attempts)
  * Use `inject_date: true` to provide agents with current date awareness for time-sensitive tasks
  * Customize the date format with `date_format` using standard Python datetime format codes
  * Enable `multimodal: true` for agents that need to process both text and visual content



### 

​

Agent Collaboration

  * Enable `allow_delegation: true` when agents need to work together
  * Use `step_callback` to monitor and log agent interactions
  * Consider using different LLMs for different purposes:
    * Main `llm` for complex reasoning
    * `function_calling_llm` for efficient tool usage



### 

​

Date Awareness and Reasoning

  * Use `inject_date: true` to provide agents with current date awareness for time-sensitive tasks
  * Customize the date format with `date_format` using standard Python datetime format codes
  * Valid format codes include: %Y (year), %m (month), %d (day), %B (full month name), etc.
  * Invalid date formats will be logged as warnings and will not modify the task description
  * Enable `reasoning: true` for complex tasks that benefit from upfront planning and reflection



### 

​

Model Compatibility

  * Set `use_system_prompt: false` for older models that don’t support system messages
  * Ensure your chosen `llm` supports the features you need (like function calling)



## 

​

Troubleshooting Common Issues

  1. **Rate Limiting** : If you’re hitting API rate limits:

     * Implement appropriate `max_rpm`
     * Use caching for repetitive operations
     * Consider batching requests
  2. **Context Window Errors** : If you’re exceeding context limits:

     * Enable `respect_context_window`
     * Use more efficient prompts
     * Clear agent memory periodically
  3. **Code Execution Issues** : If code execution fails:

     * Verify Docker is installed for safe mode
     * Check execution permissions
     * Review code sandbox settings
  4. **Memory Issues** : If agent responses seem inconsistent:

     * Verify memory is enabled
     * Check knowledge source configuration
     * Review conversation history management



Remember that agents are most effective when configured according to their specific use case. Take time to understand your requirements and adjust these parameters accordingly.

Was this page helpful?

YesNo

[Fingerprinting](/guides/advanced/fingerprinting)[Tasks](/concepts/tasks)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Overview of an Agent
  * Agent Attributes
  * Creating Agents
  * YAML Configuration (Recommended)
  * Direct Code Definition
  * Basic Research Agent
  * Code Development Agent
  * Long-Running Analysis Agent
  * Custom Template Agent
  * Date-Aware Agent with Reasoning
  * Reasoning Agent
  * Multimodal Agent
  * Parameter Details
  * Critical Parameters
  * Memory and Context
  * Execution Control
  * Code Execution
  * Advanced Features
  * Templates
  * Agent Tools
  * Agent Memory and Context
  * Context Window Management
  * How Context Window Management Works
  * Automatic Context Handling (respect_context_window=True)
  * Strict Context Limits (respect_context_window=False)
  * Choosing the Right Setting
  * Use respect_context_window=True (Default) when:
  * Use respect_context_window=False when:
  * Alternative Approaches for Large Data
  * 1\. Use RAG Tools
  * 2\. Use Knowledge Sources
  * Context Window Best Practices
  * Troubleshooting Context Issues
  * Important Considerations and Best Practices
  * Security and Code Execution
  * Performance Optimization
  * Memory and Context Management
  * Advanced Features
  * Agent Collaboration
  * Date Awareness and Reasoning
  * Model Compatibility
  * Troubleshooting Common Issues



Assistant

Responses are generated using AI and may contain mistakes.


---

### AgentOps Integration {#agentops-integration}

**Source:** [https://docs.crewai.com/observability/agentops](https://docs.crewai.com/observability/agentops)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Observability

AgentOps Integration

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Observability

# AgentOps Integration

Copy page

Understanding and logging your agent performance with AgentOps.

# 

​

Introduction

Observability is a key aspect of developing and deploying conversational AI agents. It allows developers to understand how their agents are performing, how their agents are interacting with users, and how their agents use external tools and APIs. AgentOps is a product independent of CrewAI that provides a comprehensive observability solution for agents.

## 

​

AgentOps

[AgentOps](https://agentops.ai/?=crew) provides session replays, metrics, and monitoring for agents.

At a high level, AgentOps gives you the ability to monitor cost, token usage, latency, agent failures, session-wide statistics, and more. For more info, check out the [AgentOps Repo](https://github.com/AgentOps-AI/agentops).

### 

​

Overview

AgentOps provides monitoring for agents in development and production. It provides a dashboard for tracking agent performance, session replays, and custom reporting.

Additionally, AgentOps provides session drilldowns for viewing Crew agent interactions, LLM calls, and tool usage in real-time. This feature is useful for debugging and understanding how agents interact with users as well as other agents.

### 

​

Features

  * **LLM Cost Management and Tracking** : Track spend with foundation model providers.
  * **Replay Analytics** : Watch step-by-step agent execution graphs.
  * **Recursive Thought Detection** : Identify when agents fall into infinite loops.
  * **Custom Reporting** : Create custom analytics on agent performance.
  * **Analytics Dashboard** : Monitor high-level statistics about agents in development and production.
  * **Public Model Testing** : Test your agents against benchmarks and leaderboards.
  * **Custom Tests** : Run your agents against domain-specific tests.
  * **Time Travel Debugging** : Restart your sessions from checkpoints.
  * **Compliance and Security** : Create audit logs and detect potential threats such as profanity and PII leaks.
  * **Prompt Injection Detection** : Identify potential code injection and secret leaks.



### 

​

Using AgentOps

1

Create an API Key

Create a user API key here: [Create API Key](https://app.agentops.ai/account)

2

Configure Your Environment

Add your API key to your environment variables:
    
    
    AGENTOPS_API_KEY=<YOUR_AGENTOPS_API_KEY>

3

Install AgentOps

Install AgentOps with:
    
    
    pip install 'crewai[agentops]'

or
    
    
    pip install agentops

4

Initialize AgentOps

Before using `Crew` in your script, include these lines:
    
    
    import agentops
    agentops.init()

This will initiate an AgentOps session as well as automatically track Crew agents. For further info on how to outfit more complex agentic systems, check out the [AgentOps documentation](https://docs.agentops.ai) or join the [Discord](https://discord.gg/j4f3KbeH).

### 

​

Crew + AgentOps Examples

## [Job PostingExample of a Crew agent that generates job posts.](https://github.com/joaomdmoura/crewAI-examples/tree/main/job-posting)## [Markdown ValidatorExample of a Crew agent that validates Markdown files.](https://github.com/joaomdmoura/crewAI-examples/tree/main/markdown_validator)## [Instagram PostExample of a Crew agent that generates Instagram posts.](https://github.com/joaomdmoura/crewAI-examples/tree/main/instagram_post)

### 

​

Further Information

To get started, create an [AgentOps account](https://agentops.ai/?=crew).

For feature requests or bug reports, please reach out to the AgentOps team on the [AgentOps Repo](https://github.com/AgentOps-AI/agentops).

#### 

​

Extra links

[🐦 Twitter](https://twitter.com/agentopsai/) •  [📢 Discord](https://discord.gg/JHPt4C7r) •  [🖇️ AgentOps Dashboard](https://app.agentops.ai/?=crew) •  [📙 Documentation](https://docs.agentops.ai/introduction)

Was this page helpful?

YesNo

[Overview](/observability/overview)[Arize Phoenix](/observability/arize-phoenix)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Introduction
  * AgentOps
  * Overview
  * Features
  * Using AgentOps
  * Crew + AgentOps Examples
  * Further Information
  * Extra links



Assistant

Responses are generated using AI and may contain mistakes.


---

### Coding Agents {#coding-agents}

**Source:** [https://docs.crewai.com/learn/coding-agents](https://docs.crewai.com/learn/coding-agents)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Learn

Coding Agents

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Learn

# Coding Agents

Copy page

Learn how to enable your CrewAI Agents to write and execute code, and explore advanced features for enhanced functionality.

## 

​

Introduction

CrewAI Agents now have the powerful ability to write and execute code, significantly enhancing their problem-solving capabilities. This feature is particularly useful for tasks that require computational or programmatic solutions.

## 

​

Enabling Code Execution

To enable code execution for an agent, set the `allow_code_execution` parameter to `True` when creating the agent.

Here’s an example:

Code
    
    
    from crewai import Agent
    
    coding_agent = Agent(
        role="Senior Python Developer",
        goal="Craft well-designed and thought-out code",
        backstory="You are a senior Python developer with extensive experience in software architecture and best practices.",
        allow_code_execution=True
    )

Note that `allow_code_execution` parameter defaults to `False`.

## 

​

Important Considerations

  1. **Model Selection** : It is strongly recommended to use more capable models like Claude 3.5 Sonnet and GPT-4 when enabling code execution. These models have a better understanding of programming concepts and are more likely to generate correct and efficient code.

  2. **Error Handling** : The code execution feature includes error handling. If executed code raises an exception, the agent will receive the error message and can attempt to correct the code or provide alternative solutions. The `max_retry_limit` parameter, which defaults to 2, controls the maximum number of retries for a task.

  3. **Dependencies** : To use the code execution feature, you need to install the `crewai_tools` package. If not installed, the agent will log an info message: “Coding tools not available. Install crewai_tools.”




## 

​

Code Execution Process

When an agent with code execution enabled encounters a task requiring programming:

1

Task Analysis

The agent analyzes the task and determines that code execution is necessary.

2

Code Formulation

It formulates the Python code needed to solve the problem.

3

Code Execution

The code is sent to the internal code execution tool (`CodeInterpreterTool`).

4

Result Interpretation

The agent interprets the result and incorporates it into its response or uses it for further problem-solving.

## 

​

Example Usage

Here’s a detailed example of creating an agent with code execution capabilities and using it in a task:

Code
    
    
    from crewai import Agent, Task, Crew
    
    # Create an agent with code execution enabled
    coding_agent = Agent(
        role="Python Data Analyst",
        goal="Analyze data and provide insights using Python",
        backstory="You are an experienced data analyst with strong Python skills.",
        allow_code_execution=True
    )
    
    # Create a task that requires code execution
    data_analysis_task = Task(
        description="Analyze the given dataset and calculate the average age of participants.",
        agent=coding_agent
    )
    
    # Create a crew and add the task
    analysis_crew = Crew(
        agents=[coding_agent],
        tasks=[data_analysis_task]
    )
    
    # Execute the crew
    result = analysis_crew.kickoff()
    
    print(result)

In this example, the `coding_agent` can write and execute Python code to perform data analysis tasks.

Was this page helpful?

YesNo

[Conditional Tasks](/learn/conditional-tasks)[Create Custom Tools](/learn/create-custom-tools)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Introduction
  * Enabling Code Execution
  * Important Considerations
  * Code Execution Process
  * Example Usage



Assistant

Responses are generated using AI and may contain mistakes.


---

### Crafting Effective Agents {#crafting-effective-agents}

**Source:** [https://docs.crewai.com/guides/agents/crafting-effective-agents](https://docs.crewai.com/guides/agents/crafting-effective-agents)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Agents

Crafting Effective Agents

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

    * [Crafting Effective Agents](/guides/agents/crafting-effective-agents)
  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Agents

# Crafting Effective Agents

Copy page

Learn best practices for designing powerful, specialized AI agents that collaborate effectively to solve complex problems.

## 

​

The Art and Science of Agent Design

At the heart of CrewAI lies the agent - a specialized AI entity designed to perform specific roles within a collaborative framework. While creating basic agents is simple, crafting truly effective agents that produce exceptional results requires understanding key design principles and best practices.

This guide will help you master the art of agent design, enabling you to create specialized AI personas that collaborate effectively, think critically, and produce high-quality outputs tailored to your specific needs.

### 

​

Why Agent Design Matters

The way you define your agents significantly impacts:

  1. **Output quality** : Well-designed agents produce more relevant, high-quality results
  2. **Collaboration effectiveness** : Agents with complementary skills work together more efficiently
  3. **Task performance** : Agents with clear roles and goals execute tasks more effectively
  4. **System scalability** : Thoughtfully designed agents can be reused across multiple crews and contexts



Let’s explore best practices for creating agents that excel in these dimensions.

## 

​

The 80/20 Rule: Focus on Tasks Over Agents

When building effective AI systems, remember this crucial principle: **80% of your effort should go into designing tasks, and only 20% into defining agents**.

Why? Because even the most perfectly defined agent will fail with poorly designed tasks, but well-designed tasks can elevate even a simple agent. This means:

  * Spend most of your time writing clear task instructions
  * Define detailed inputs and expected outputs
  * Add examples and context to guide execution
  * Dedicate the remaining time to agent role, goal, and backstory



This doesn’t mean agent design isn’t important - it absolutely is. But task design is where most execution failures occur, so prioritize accordingly.

## 

​

Core Principles of Effective Agent Design

### 

​

1\. The Role-Goal-Backstory Framework

The most powerful agents in CrewAI are built on a strong foundation of three key elements:

#### 

​

Role: The Agent’s Specialized Function

The role defines what the agent does and their area of expertise. When crafting roles:

  * **Be specific and specialized** : Instead of “Writer,” use “Technical Documentation Specialist” or “Creative Storyteller”
  * **Align with real-world professions** : Base roles on recognizable professional archetypes
  * **Include domain expertise** : Specify the agent’s field of knowledge (e.g., “Financial Analyst specializing in market trends”)



**Examples of effective roles:**
    
    
    role: "Senior UX Researcher specializing in user interview analysis"
    role: "Full-Stack Software Architect with expertise in distributed systems"
    role: "Corporate Communications Director specializing in crisis management"

#### 

​

Goal: The Agent’s Purpose and Motivation

The goal directs the agent’s efforts and shapes their decision-making process. Effective goals should:

  * **Be clear and outcome-focused** : Define what the agent is trying to achieve
  * **Emphasize quality standards** : Include expectations about the quality of work
  * **Incorporate success criteria** : Help the agent understand what “good” looks like



**Examples of effective goals:**
    
    
    goal: "Uncover actionable user insights by analyzing interview data and identifying recurring patterns, unmet needs, and improvement opportunities"
    goal: "Design robust, scalable system architectures that balance performance, maintainability, and cost-effectiveness"
    goal: "Craft clear, empathetic crisis communications that address stakeholder concerns while protecting organizational reputation"

#### 

​

Backstory: The Agent’s Experience and Perspective

The backstory gives depth to the agent, influencing how they approach problems and interact with others. Good backstories:

  * **Establish expertise and experience** : Explain how the agent gained their skills
  * **Define working style and values** : Describe how the agent approaches their work
  * **Create a cohesive persona** : Ensure all elements of the backstory align with the role and goal



**Examples of effective backstories:**
    
    
    backstory: "You have spent 15 years conducting and analyzing user research for top tech companies. You have a talent for reading between the lines and identifying patterns that others miss. You believe that good UX is invisible and that the best insights come from listening to what users don't say as much as what they do say."
    
    backstory: "With 20+ years of experience building distributed systems at scale, you've developed a pragmatic approach to software architecture. You've seen both successful and failed systems and have learned valuable lessons from each. You balance theoretical best practices with practical constraints and always consider the maintenance and operational aspects of your designs."
    
    backstory: "As a seasoned communications professional who has guided multiple organizations through high-profile crises, you understand the importance of transparency, speed, and empathy in crisis response. You have a methodical approach to crafting messages that address concerns while maintaining organizational credibility."

### 

​

2\. Specialists Over Generalists

Agents perform significantly better when given specialized roles rather than general ones. A highly focused agent delivers more precise, relevant outputs:

**Generic (Less Effective):**
    
    
    role: "Writer"

**Specialized (More Effective):**
    
    
    role: "Technical Blog Writer specializing in explaining complex AI concepts to non-technical audiences"

**Specialist Benefits:**

  * Clearer understanding of expected output
  * More consistent performance
  * Better alignment with specific tasks
  * Improved ability to make domain-specific judgments



### 

​

3\. Balancing Specialization and Versatility

Effective agents strike the right balance between specialization (doing one thing extremely well) and versatility (being adaptable to various situations):

  * **Specialize in role, versatile in application** : Create agents with specialized skills that can be applied across multiple contexts
  * **Avoid overly narrow definitions** : Ensure agents can handle variations within their domain of expertise
  * **Consider the collaborative context** : Design agents whose specializations complement the other agents they’ll work with



### 

​

4\. Setting Appropriate Expertise Levels

The expertise level you assign to your agent shapes how they approach tasks:

  * **Novice agents** : Good for straightforward tasks, brainstorming, or initial drafts
  * **Intermediate agents** : Suitable for most standard tasks with reliable execution
  * **Expert agents** : Best for complex, specialized tasks requiring depth and nuance
  * **World-class agents** : Reserved for critical tasks where exceptional quality is needed



Choose the appropriate expertise level based on task complexity and quality requirements. For most collaborative crews, a mix of expertise levels often works best, with higher expertise assigned to core specialized functions.

## 

​

Practical Examples: Before and After

Let’s look at some examples of agent definitions before and after applying these best practices:

### 

​

Example 1: Content Creation Agent

**Before:**
    
    
    role: "Writer"
    goal: "Write good content"
    backstory: "You are a writer who creates content for websites."

**After:**
    
    
    role: "B2B Technology Content Strategist"
    goal: "Create compelling, technically accurate content that explains complex topics in accessible language while driving reader engagement and supporting business objectives"
    backstory: "You have spent a decade creating content for leading technology companies, specializing in translating technical concepts for business audiences. You excel at research, interviewing subject matter experts, and structuring information for maximum clarity and impact. You believe that the best B2B content educates first and sells second, building trust through genuine expertise rather than marketing hype."

### 

​

Example 2: Research Agent

**Before:**
    
    
    role: "Researcher"
    goal: "Find information"
    backstory: "You are good at finding information online."

**After:**
    
    
    role: "Academic Research Specialist in Emerging Technologies"
    goal: "Discover and synthesize cutting-edge research, identifying key trends, methodologies, and findings while evaluating the quality and reliability of sources"
    backstory: "With a background in both computer science and library science, you've mastered the art of digital research. You've worked with research teams at prestigious universities and know how to navigate academic databases, evaluate research quality, and synthesize findings across disciplines. You're methodical in your approach, always cross-referencing information and tracing claims to primary sources before drawing conclusions."

## 

​

Crafting Effective Tasks for Your Agents

While agent design is important, task design is critical for successful execution. Here are best practices for designing tasks that set your agents up for success:

### 

​

The Anatomy of an Effective Task

A well-designed task has two key components that serve different purposes:

#### 

​

Task Description: The Process

The description should focus on what to do and how to do it, including:

  * Detailed instructions for execution
  * Context and background information
  * Scope and constraints
  * Process steps to follow



#### 

​

Expected Output: The Deliverable

The expected output should define what the final result should look like:

  * Format specifications (markdown, JSON, etc.)
  * Structure requirements
  * Quality criteria
  * Examples of good outputs (when possible)



### 

​

Task Design Best Practices

#### 

​

1\. Single Purpose, Single Output

Tasks perform best when focused on one clear objective:

**Bad Example (Too Broad):**
    
    
    task_description: "Research market trends, analyze the data, and create a visualization."

**Good Example (Focused):**
    
    
    # Task 1
    research_task:
      description: "Research the top 5 market trends in the AI industry for 2024."
      expected_output: "A markdown list of the 5 trends with supporting evidence."
    
    # Task 2
    analysis_task:
      description: "Analyze the identified trends to determine potential business impacts."
      expected_output: "A structured analysis with impact ratings (High/Medium/Low)."
    
    # Task 3
    visualization_task:
      description: "Create a visual representation of the analyzed trends."
      expected_output: "A description of a chart showing trends and their impact ratings."

#### 

​

2\. Be Explicit About Inputs and Outputs

Always clearly specify what inputs the task will use and what the output should look like:

**Example:**
    
    
    analysis_task:
      description: >
        Analyze the customer feedback data from the CSV file.
        Focus on identifying recurring themes related to product usability.
        Consider sentiment and frequency when determining importance.
      expected_output: >
        A markdown report with the following sections:
        1. Executive summary (3-5 bullet points)
        2. Top 3 usability issues with supporting data
        3. Recommendations for improvement

#### 

​

3\. Include Purpose and Context

Explain why the task matters and how it fits into the larger workflow:

**Example:**
    
    
    competitor_analysis_task:
      description: >
        Analyze our three main competitors' pricing strategies.
        This analysis will inform our upcoming pricing model revision.
        Focus on identifying patterns in how they price premium features
        and how they structure their tiered offerings.

#### 

​

4\. Use Structured Output Tools

For machine-readable outputs, specify the format clearly:

**Example:**
    
    
    data_extraction_task:
      description: "Extract key metrics from the quarterly report."
      expected_output: "JSON object with the following keys: revenue, growth_rate, customer_acquisition_cost, and retention_rate."

## 

​

Common Mistakes to Avoid

Based on lessons learned from real-world implementations, here are the most common pitfalls in agent and task design:

### 

​

1\. Unclear Task Instructions

**Problem:** Tasks lack sufficient detail, making it difficult for agents to execute effectively.

**Example of Poor Design:**
    
    
    research_task:
      description: "Research AI trends."
      expected_output: "A report on AI trends."

**Improved Version:**
    
    
    research_task:
      description: >
        Research the top emerging AI trends for 2024 with a focus on:
        1. Enterprise adoption patterns
        2. Technical breakthroughs in the past 6 months
        3. Regulatory developments affecting implementation
    
        For each trend, identify key companies, technologies, and potential business impacts.
      expected_output: >
        A comprehensive markdown report with:
        - Executive summary (5 bullet points)
        - 5-7 major trends with supporting evidence
        - For each trend: definition, examples, and business implications
        - References to authoritative sources

### 

​

2\. “God Tasks” That Try to Do Too Much

**Problem:** Tasks that combine multiple complex operations into one instruction set.

**Example of Poor Design:**
    
    
    comprehensive_task:
      description: "Research market trends, analyze competitor strategies, create a marketing plan, and design a launch timeline."

**Improved Version:** Break this into sequential, focused tasks:
    
    
    # Task 1: Research
    market_research_task:
      description: "Research current market trends in the SaaS project management space."
      expected_output: "A markdown summary of key market trends."
    
    # Task 2: Competitive Analysis
    competitor_analysis_task:
      description: "Analyze strategies of the top 3 competitors based on the market research."
      expected_output: "A comparison table of competitor strategies."
      context: [market_research_task]
    
    # Continue with additional focused tasks...

### 

​

3\. Misaligned Description and Expected Output

**Problem:** The task description asks for one thing while the expected output specifies something different.

**Example of Poor Design:**
    
    
    analysis_task:
      description: "Analyze customer feedback to find areas of improvement."
      expected_output: "A marketing plan for the next quarter."

**Improved Version:**
    
    
    analysis_task:
      description: "Analyze customer feedback to identify the top 3 areas for product improvement."
      expected_output: "A report listing the 3 priority improvement areas with supporting customer quotes and data points."

### 

​

4\. Not Understanding the Process Yourself

**Problem:** Asking agents to execute tasks that you yourself don’t fully understand.

**Solution:**

  1. Try to perform the task manually first
  2. Document your process, decision points, and information sources
  3. Use this documentation as the basis for your task description



### 

​

5\. Premature Use of Hierarchical Structures

**Problem:** Creating unnecessarily complex agent hierarchies where sequential processes would work better.

**Solution:** Start with sequential processes and only move to hierarchical models when the workflow complexity truly requires it.

### 

​

6\. Vague or Generic Agent Definitions

**Problem:** Generic agent definitions lead to generic outputs.

**Example of Poor Design:**
    
    
    agent:
      role: "Business Analyst"
      goal: "Analyze business data"
      backstory: "You are good at business analysis."

**Improved Version:**
    
    
    agent:
      role: "SaaS Metrics Specialist focusing on growth-stage startups"
      goal: "Identify actionable insights from business data that can directly impact customer retention and revenue growth"
      backstory: "With 10+ years analyzing SaaS business models, you've developed a keen eye for the metrics that truly matter for sustainable growth. You've helped numerous companies identify the leverage points that turned around their business trajectory. You believe in connecting data to specific, actionable recommendations rather than general observations."

## 

​

Advanced Agent Design Strategies

### 

​

Designing for Collaboration

When creating agents that will work together in a crew, consider:

  * **Complementary skills** : Design agents with distinct but complementary abilities
  * **Handoff points** : Define clear interfaces for how work passes between agents
  * **Constructive tension** : Sometimes, creating agents with slightly different perspectives can lead to better outcomes through productive dialogue



For example, a content creation crew might include:
    
    
    # Research Agent
    role: "Research Specialist for technical topics"
    goal: "Gather comprehensive, accurate information from authoritative sources"
    backstory: "You are a meticulous researcher with a background in library science..."
    
    # Writer Agent
    role: "Technical Content Writer"
    goal: "Transform research into engaging, clear content that educates and informs"
    backstory: "You are an experienced writer who excels at explaining complex concepts..."
    
    # Editor Agent
    role: "Content Quality Editor"
    goal: "Ensure content is accurate, well-structured, and polished while maintaining consistency"
    backstory: "With years of experience in publishing, you have a keen eye for detail..."

### 

​

Creating Specialized Tool Users

Some agents can be designed specifically to leverage certain tools effectively:
    
    
    role: "Data Analysis Specialist"
    goal: "Derive meaningful insights from complex datasets through statistical analysis"
    backstory: "With a background in data science, you excel at working with structured and unstructured data..."
    tools: [PythonREPLTool, DataVisualizationTool, CSVAnalysisTool]

### 

​

Tailoring Agents to LLM Capabilities

Different LLMs have different strengths. Design your agents with these capabilities in mind:
    
    
    # For complex reasoning tasks
    analyst:
      role: "Data Insights Analyst"
      goal: "..."
      backstory: "..."
      llm: openai/gpt-4o
    
    # For creative content
    writer:
      role: "Creative Content Writer"
      goal: "..."
      backstory: "..."
      llm: anthropic/claude-3-opus

## 

​

Testing and Iterating on Agent Design

Agent design is often an iterative process. Here’s a practical approach:

  1. **Start with a prototype** : Create an initial agent definition
  2. **Test with sample tasks** : Evaluate performance on representative tasks
  3. **Analyze outputs** : Identify strengths and weaknesses
  4. **Refine the definition** : Adjust role, goal, and backstory based on observations
  5. **Test in collaboration** : Evaluate how the agent performs in a crew setting



## 

​

Conclusion

Crafting effective agents is both an art and a science. By carefully defining roles, goals, and backstories that align with your specific needs, and combining them with well-designed tasks, you can create specialized AI collaborators that produce exceptional results.

Remember that agent and task design is an iterative process. Start with these best practices, observe your agents in action, and refine your approach based on what you learn. And always keep in mind the 80/20 rule - focus most of your effort on creating clear, focused tasks to get the best results from your agents.

Congratulations! You now understand the principles and practices of effective agent design. Apply these techniques to create powerful, specialized agents that work together seamlessly to accomplish complex tasks.

## 

​

Next Steps

  * Experiment with different agent configurations for your specific use case
  * Learn about [building your first crew](/guides/crews/first-crew) to see how agents work together
  * Explore [CrewAI Flows](/guides/flows/first-flow) for more advanced orchestration



Was this page helpful?

YesNo

[Evaluating Use Cases for CrewAI](/guides/concepts/evaluating-use-cases)[Build Your First Crew](/guides/crews/first-crew)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * The Art and Science of Agent Design
  * Why Agent Design Matters
  * The 80/20 Rule: Focus on Tasks Over Agents
  * Core Principles of Effective Agent Design
  * 1\. The Role-Goal-Backstory Framework
  * Role: The Agent’s Specialized Function
  * Goal: The Agent’s Purpose and Motivation
  * Backstory: The Agent’s Experience and Perspective
  * 2\. Specialists Over Generalists
  * 3\. Balancing Specialization and Versatility
  * 4\. Setting Appropriate Expertise Levels
  * Practical Examples: Before and After
  * Example 1: Content Creation Agent
  * Example 2: Research Agent
  * Crafting Effective Tasks for Your Agents
  * The Anatomy of an Effective Task
  * Task Description: The Process
  * Expected Output: The Deliverable
  * Task Design Best Practices
  * 1\. Single Purpose, Single Output
  * 2\. Be Explicit About Inputs and Outputs
  * 3\. Include Purpose and Context
  * 4\. Use Structured Output Tools
  * Common Mistakes to Avoid
  * 1\. Unclear Task Instructions
  * 2\. “God Tasks” That Try to Do Too Much
  * 3\. Misaligned Description and Expected Output
  * 4\. Not Understanding the Process Yourself
  * 5\. Premature Use of Hierarchical Structures
  * 6\. Vague or Generic Agent Definitions
  * Advanced Agent Design Strategies
  * Designing for Collaboration
  * Creating Specialized Tool Users
  * Tailoring Agents to LLM Capabilities
  * Testing and Iterating on Agent Design
  * Conclusion
  * Next Steps



Assistant

Responses are generated using AI and may contain mistakes.


---



## Tasks {#tasks}

### Conditional Tasks {#conditional-tasks}

**Source:** [https://docs.crewai.com/learn/conditional-tasks](https://docs.crewai.com/learn/conditional-tasks)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Learn

Conditional Tasks

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Learn

# Conditional Tasks

Copy page

Learn how to use conditional tasks in a crewAI kickoff

## 

​

Introduction

Conditional Tasks in crewAI allow for dynamic workflow adaptation based on the outcomes of previous tasks. This powerful feature enables crews to make decisions and execute tasks selectively, enhancing the flexibility and efficiency of your AI-driven processes.

## 

​

Example Usage

Code
    
    
    from typing import List
    from pydantic import BaseModel
    from crewai import Agent, Crew
    from crewai.tasks.conditional_task import ConditionalTask
    from crewai.tasks.task_output import TaskOutput
    from crewai.task import Task
    from crewai_tools import SerperDevTool
    
    # Define a condition function for the conditional task
    # If false, the task will be skipped, if true, then execute the task.
    def is_data_missing(output: TaskOutput) -> bool:
        return len(output.pydantic.events) < 10  # this will skip this task
    
    # Define the agents
    data_fetcher_agent = Agent(
        role="Data Fetcher",
        goal="Fetch data online using Serper tool",
        backstory="Backstory 1",
        verbose=True,
        tools=[SerperDevTool()]
    )
    
    data_processor_agent = Agent(
        role="Data Processor",
        goal="Process fetched data",
        backstory="Backstory 2",
        verbose=True
    )
    
    summary_generator_agent = Agent(
        role="Summary Generator",
        goal="Generate summary from fetched data",
        backstory="Backstory 3",
        verbose=True
    )
    
    class EventOutput(BaseModel):
        events: List[str]
    
    task1 = Task(
        description="Fetch data about events in San Francisco using Serper tool",
        expected_output="List of 10 things to do in SF this week",
        agent=data_fetcher_agent,
        output_pydantic=EventOutput,
    )
    
    conditional_task = ConditionalTask(
        description="""
            Check if data is missing. If we have less than 10 events,
            fetch more events using Serper tool so that
            we have a total of 10 events in SF this week..
            """,
        expected_output="List of 10 Things to do in SF this week",
        condition=is_data_missing,
        agent=data_processor_agent,
    )
    
    task3 = Task(
        description="Generate summary of events in San Francisco from fetched data",
        expected_output="A complete report on the customer and their customers and competitors, including their demographics, preferences, market positioning and audience engagement.",
        agent=summary_generator_agent,
    )
    
    # Create a crew with the tasks
    crew = Crew(
        agents=[data_fetcher_agent, data_processor_agent, summary_generator_agent],
        tasks=[task1, conditional_task, task3],
        verbose=True,
        planning=True
    )
    
    # Run the crew
    result = crew.kickoff()
    print("results", result)

Was this page helpful?

YesNo

[Overview](/learn/overview)[Coding Agents](/learn/coding-agents)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Introduction
  * Example Usage



Assistant

Responses are generated using AI and may contain mistakes.


---

### Tasks {#tasks}

**Source:** [https://docs.crewai.com/concepts/tasks](https://docs.crewai.com/concepts/tasks)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Core Concepts

Tasks

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Core Concepts

# Tasks

Copy page

Detailed guide on managing and creating tasks within the CrewAI framework.

## 

​

Overview

In the CrewAI framework, a `Task` is a specific assignment completed by an `Agent`.

Tasks provide all necessary details for execution, such as a description, the agent responsible, required tools, and more, facilitating a wide range of action complexities.

Tasks within CrewAI can be collaborative, requiring multiple agents to work together. This is managed through the task properties and orchestrated by the Crew’s process, enhancing teamwork and efficiency.

CrewAI Enterprise includes a Visual Task Builder in Crew Studio that simplifies complex task creation and chaining. Design your task flows visually and test them in real-time without writing code.

The Visual Task Builder enables:

  * Drag-and-drop task creation
  * Visual task dependencies and flow
  * Real-time testing and validation
  * Easy sharing and collaboration



### 

​

Task Execution Flow

Tasks can be executed in two ways:

  * **Sequential** : Tasks are executed in the order they are defined
  * **Hierarchical** : Tasks are assigned to agents based on their roles and expertise



The execution flow is defined when creating the crew:

Code
    
    
    crew = Crew(
        agents=[agent1, agent2],
        tasks=[task1, task2],
        process=Process.sequential  # or Process.hierarchical
    )

## 

​

Task Attributes

Attribute| Parameters| Type| Description  
---|---|---|---  
**Description**| `description`| `str`| A clear, concise statement of what the task entails.  
**Expected Output**| `expected_output`| `str`| A detailed description of what the task’s completion looks like.  
**Name** _(optional)_| `name`| `Optional[str]`| A name identifier for the task.  
**Agent** _(optional)_| `agent`| `Optional[BaseAgent]`| The agent responsible for executing the task.  
**Tools** _(optional)_| `tools`| `List[BaseTool]`| The tools/resources the agent is limited to use for this task.  
**Context** _(optional)_| `context`| `Optional[List["Task"]]`| Other tasks whose outputs will be used as context for this task.  
**Async Execution** _(optional)_| `async_execution`| `Optional[bool]`| Whether the task should be executed asynchronously. Defaults to False.  
**Human Input** _(optional)_| `human_input`| `Optional[bool]`| Whether the task should have a human review the final answer of the agent. Defaults to False.  
**Markdown** _(optional)_| `markdown`| `Optional[bool]`| Whether the task should instruct the agent to return the final answer formatted in Markdown. Defaults to False.  
**Config** _(optional)_| `config`| `Optional[Dict[str, Any]]`| Task-specific configuration parameters.  
**Output File** _(optional)_| `output_file`| `Optional[str]`| File path for storing the task output.  
**Output JSON** _(optional)_| `output_json`| `Optional[Type[BaseModel]]`| A Pydantic model to structure the JSON output.  
**Output Pydantic** _(optional)_| `output_pydantic`| `Optional[Type[BaseModel]]`| A Pydantic model for task output.  
**Callback** _(optional)_| `callback`| `Optional[Any]`| Function/object to be executed after task completion.  
  
## 

​

Creating Tasks

There are two ways to create tasks in CrewAI: using **YAML configuration (recommended)** or defining them **directly in code**.

### 

​

YAML Configuration (Recommended)

Using YAML configuration provides a cleaner, more maintainable way to define tasks. We strongly recommend using this approach to define tasks in your CrewAI projects.

After creating your CrewAI project as outlined in the [Installation](/installation) section, navigate to the `src/latest_ai_development/config/tasks.yaml` file and modify the template to match your specific task requirements.

Variables in your YAML files (like `{topic}`) will be replaced with values from your inputs when running the crew:

Code
    
    
    crew.kickoff(inputs={'topic': 'AI Agents'})

Here’s an example of how to configure tasks using YAML:

tasks.yaml
    
    
    research_task:
      description: >
        Conduct a thorough research about {topic}
        Make sure you find any interesting and relevant information given
        the current year is 2025.
      expected_output: >
        A list with 10 bullet points of the most relevant information about {topic}
      agent: researcher
    
    reporting_task:
      description: >
        Review the context you got and expand each topic into a full section for a report.
        Make sure the report is detailed and contains any and all relevant information.
      expected_output: >
        A fully fledge reports with the mains topics, each with a full section of information.
        Formatted as markdown without '```'
      agent: reporting_analyst
      markdown: true
      output_file: report.md

To use this YAML configuration in your code, create a crew class that inherits from `CrewBase`:

crew.py
    
    
    # src/latest_ai_development/crew.py
    
    from crewai import Agent, Crew, Process, Task
    from crewai.project import CrewBase, agent, crew, task
    from crewai_tools import SerperDevTool
    
    @CrewBase
    class LatestAiDevelopmentCrew():
      """LatestAiDevelopment crew"""
    
      @agent
      def researcher(self) -> Agent:
        return Agent(
          config=self.agents_config['researcher'], # type: ignore[index]
          verbose=True,
          tools=[SerperDevTool()]
        )
    
      @agent
      def reporting_analyst(self) -> Agent:
        return Agent(
          config=self.agents_config['reporting_analyst'], # type: ignore[index]
          verbose=True
        )
    
      @task
      def research_task(self) -> Task:
        return Task(
          config=self.tasks_config['research_task'] # type: ignore[index]
        )
    
      @task
      def reporting_task(self) -> Task:
        return Task(
          config=self.tasks_config['reporting_task'] # type: ignore[index]
        )
    
      @crew
      def crew(self) -> Crew:
        return Crew(
          agents=[
            self.researcher(),
            self.reporting_analyst()
          ],
          tasks=[
            self.research_task(),
            self.reporting_task()
          ],
          process=Process.sequential
        )

The names you use in your YAML files (`agents.yaml` and `tasks.yaml`) should match the method names in your Python code.

### 

​

Direct Code Definition (Alternative)

Alternatively, you can define tasks directly in your code without using YAML configuration:

task.py
    
    
    from crewai import Task
    
    research_task = Task(
        description="""
            Conduct a thorough research about AI Agents.
            Make sure you find any interesting and relevant information given
            the current year is 2025.
        """,
        expected_output="""
            A list with 10 bullet points of the most relevant information about AI Agents
        """,
        agent=researcher
    )
    
    reporting_task = Task(
        description="""
            Review the context you got and expand each topic into a full section for a report.
            Make sure the report is detailed and contains any and all relevant information.
        """,
        expected_output="""
            A fully fledge reports with the mains topics, each with a full section of information.
        """,
        agent=reporting_analyst,
        markdown=True,  # Enable markdown formatting for the final output
        output_file="report.md"
    )

Directly specify an `agent` for assignment or let the `hierarchical` CrewAI’s process decide based on roles, availability, etc.

## 

​

Task Output

Understanding task outputs is crucial for building effective AI workflows. CrewAI provides a structured way to handle task results through the `TaskOutput` class, which supports multiple output formats and can be easily passed between tasks.

The output of a task in CrewAI framework is encapsulated within the `TaskOutput` class. This class provides a structured way to access results of a task, including various formats such as raw output, JSON, and Pydantic models.

By default, the `TaskOutput` will only include the `raw` output. A `TaskOutput` will only include the `pydantic` or `json_dict` output if the original `Task` object was configured with `output_pydantic` or `output_json`, respectively.

### 

​

Task Output Attributes

Attribute| Parameters| Type| Description  
---|---|---|---  
**Description**| `description`| `str`| Description of the task.  
**Summary**| `summary`| `Optional[str]`| Summary of the task, auto-generated from the first 10 words of the description.  
**Raw**| `raw`| `str`| The raw output of the task. This is the default format for the output.  
**Pydantic**| `pydantic`| `Optional[BaseModel]`| A Pydantic model object representing the structured output of the task.  
**JSON Dict**| `json_dict`| `Optional[Dict[str, Any]]`| A dictionary representing the JSON output of the task.  
**Agent**| `agent`| `str`| The agent that executed the task.  
**Output Format**| `output_format`| `OutputFormat`| The format of the task output, with options including RAW, JSON, and Pydantic. The default is RAW.  
  
### 

​

Task Methods and Properties

Method/Property| Description  
---|---  
**json**|  Returns the JSON string representation of the task output if the output format is JSON.  
**to_dict**|  Converts the JSON and Pydantic outputs to a dictionary.  
**str**|  Returns the string representation of the task output, prioritizing Pydantic, then JSON, then raw.  
  
### 

​

Accessing Task Outputs

Once a task has been executed, its output can be accessed through the `output` attribute of the `Task` object. The `TaskOutput` class provides various ways to interact with and present this output.

#### 

​

Example

Code
    
    
    # Example task
    task = Task(
        description='Find and summarize the latest AI news',
        expected_output='A bullet list summary of the top 5 most important AI news',
        agent=research_agent,
        tools=[search_tool]
    )
    
    # Execute the crew
    crew = Crew(
        agents=[research_agent],
        tasks=[task],
        verbose=True
    )
    
    result = crew.kickoff()
    
    # Accessing the task output
    task_output = task.output
    
    print(f"Task Description: {task_output.description}")
    print(f"Task Summary: {task_output.summary}")
    print(f"Raw Output: {task_output.raw}")
    if task_output.json_dict:
        print(f"JSON Output: {json.dumps(task_output.json_dict, indent=2)}")
    if task_output.pydantic:
        print(f"Pydantic Output: {task_output.pydantic}")

## 

​

Markdown Output Formatting

The `markdown` parameter enables automatic markdown formatting for task outputs. When set to `True`, the task will instruct the agent to format the final answer using proper Markdown syntax.

### 

​

Using Markdown Formatting

Code
    
    
    # Example task with markdown formatting enabled
    formatted_task = Task(
        description="Create a comprehensive report on AI trends",
        expected_output="A well-structured report with headers, sections, and bullet points",
        agent=reporter_agent,
        markdown=True  # Enable automatic markdown formatting
    )

When `markdown=True`, the agent will receive additional instructions to format the output using:

  * `#` for headers
  * `**text**` for bold text
  * `*text*` for italic text
  * `-` or `*` for bullet points
  * ``code`` for inline code
  * ` `language ``` for code blocks



### 

​

YAML Configuration with Markdown

tasks.yaml
    
    
    analysis_task:
      description: >
        Analyze the market data and create a detailed report
      expected_output: >
        A comprehensive analysis with charts and key findings
      agent: analyst
      markdown: true  # Enable markdown formatting
      output_file: analysis.md

### 

​

Benefits of Markdown Output

  * **Consistent Formatting** : Ensures all outputs follow proper markdown conventions
  * **Better Readability** : Structured content with headers, lists, and emphasis
  * **Documentation Ready** : Output can be directly used in documentation systems
  * **Cross-Platform Compatibility** : Markdown is universally supported



The markdown formatting instructions are automatically added to the task prompt when `markdown=True`, so you don’t need to specify formatting requirements in your task description.

## 

​

Task Dependencies and Context

Tasks can depend on the output of other tasks using the `context` attribute. For example:

Code
    
    
    research_task = Task(
        description="Research the latest developments in AI",
        expected_output="A list of recent AI developments",
        agent=researcher
    )
    
    analysis_task = Task(
        description="Analyze the research findings and identify key trends",
        expected_output="Analysis report of AI trends",
        agent=analyst,
        context=[research_task]  # This task will wait for research_task to complete
    )

## 

​

Task Guardrails

Task guardrails provide a way to validate and transform task outputs before they are passed to the next task. This feature helps ensure data quality and provides feedback to agents when their output doesn’t meet specific criteria.

### 

​

Using Task Guardrails

To add a guardrail to a task, provide a validation function through the `guardrail` parameter:

Code
    
    
    from typing import Tuple, Union, Dict, Any
    from crewai import TaskOutput
    
    def validate_blog_content(result: TaskOutput) -> Tuple[bool, Any]:
        """Validate blog content meets requirements."""
        try:
            # Check word count
            word_count = len(result.split())
            if word_count > 200:
                return (False, "Blog content exceeds 200 words")
    
            # Additional validation logic here
            return (True, result.strip())
        except Exception as e:
            return (False, "Unexpected error during validation")
    
    blog_task = Task(
        description="Write a blog post about AI",
        expected_output="A blog post under 200 words",
        agent=blog_agent,
        guardrail=validate_blog_content  # Add the guardrail function
    )

### 

​

Guardrail Function Requirements

  1. **Function Signature** :

     * Must accept exactly one parameter (the task output)
     * Should return a tuple of `(bool, Any)`
     * Type hints are recommended but optional
  2. **Return Values** :

     * On success: it returns a tuple of `(bool, Any)`. For example: `(True, validated_result)`
     * On Failure: it returns a tuple of `(bool, str)`. For example: `(False, "Error message explain the failure")`



### 

​

LLMGuardrail

The `LLMGuardrail` class offers a robust mechanism for validating task outputs.

### 

​

Error Handling Best Practices

  1. **Structured Error Responses** :



Code
    
    
    from crewai import TaskOutput, LLMGuardrail
    
    def validate_with_context(result: TaskOutput) -> Tuple[bool, Any]:
        try:
            # Main validation logic
            validated_data = perform_validation(result)
            return (True, validated_data)
        except ValidationError as e:
            return (False, f"VALIDATION_ERROR: {str(e)}")
        except Exception as e:
            return (False, str(e))

  2. **Error Categories** :

     * Use specific error codes
     * Include relevant context
     * Provide actionable feedback
  3. **Validation Chain** :




Code
    
    
    from typing import Any, Dict, List, Tuple, Union
    from crewai import TaskOutput
    
    def complex_validation(result: TaskOutput) -> Tuple[bool, Any]:
        """Chain multiple validation steps."""
        # Step 1: Basic validation
        if not result:
            return (False, "Empty result")
    
        # Step 2: Content validation
        try:
            validated = validate_content(result)
            if not validated:
                return (False, "Invalid content")
    
            # Step 3: Format validation
            formatted = format_output(validated)
            return (True, formatted)
        except Exception as e:
            return (False, str(e))

### 

​

Handling Guardrail Results

When a guardrail returns `(False, error)`:

  1. The error is sent back to the agent
  2. The agent attempts to fix the issue
  3. The process repeats until:
     * The guardrail returns `(True, result)`
     * Maximum retries are reached



Example with retry handling:

Code
    
    
    from typing import Optional, Tuple, Union
    from crewai import TaskOutput, Task
    
    def validate_json_output(result: TaskOutput) -> Tuple[bool, Any]:
        """Validate and parse JSON output."""
        try:
            # Try to parse as JSON
            data = json.loads(result)
            return (True, data)
        except json.JSONDecodeError as e:
            return (False, "Invalid JSON format")
    
    task = Task(
        description="Generate a JSON report",
        expected_output="A valid JSON object",
        agent=analyst,
        guardrail=validate_json_output,
        max_retries=3  # Limit retry attempts
    )

## 

​

Getting Structured Consistent Outputs from Tasks

It’s also important to note that the output of the final task of a crew becomes the final output of the actual crew itself.

### 

​

Using `output_pydantic`

The `output_pydantic` property allows you to define a Pydantic model that the task output should conform to. This ensures that the output is not only structured but also validated according to the Pydantic model.

Here’s an example demonstrating how to use output_pydantic:

Code
    
    
    import json
    
    from crewai import Agent, Crew, Process, Task
    from pydantic import BaseModel
    
    
    class Blog(BaseModel):
        title: str
        content: str
    
    
    blog_agent = Agent(
        role="Blog Content Generator Agent",
        goal="Generate a blog title and content",
        backstory="""You are an expert content creator, skilled in crafting engaging and informative blog posts.""",
        verbose=False,
        allow_delegation=False,
        llm="gpt-4o",
    )
    
    task1 = Task(
        description="""Create a blog title and content on a given topic. Make sure the content is under 200 words.""",
        expected_output="A compelling blog title and well-written content.",
        agent=blog_agent,
        output_pydantic=Blog,
    )
    
    # Instantiate your crew with a sequential process
    crew = Crew(
        agents=[blog_agent],
        tasks=[task1],
        verbose=True,
        process=Process.sequential,
    )
    
    result = crew.kickoff()
    
    # Option 1: Accessing Properties Using Dictionary-Style Indexing
    print("Accessing Properties - Option 1")
    title = result["title"]
    content = result["content"]
    print("Title:", title)
    print("Content:", content)
    
    # Option 2: Accessing Properties Directly from the Pydantic Model
    print("Accessing Properties - Option 2")
    title = result.pydantic.title
    content = result.pydantic.content
    print("Title:", title)
    print("Content:", content)
    
    # Option 3: Accessing Properties Using the to_dict() Method
    print("Accessing Properties - Option 3")
    output_dict = result.to_dict()
    title = output_dict["title"]
    content = output_dict["content"]
    print("Title:", title)
    print("Content:", content)
    
    # Option 4: Printing the Entire Blog Object
    print("Accessing Properties - Option 5")
    print("Blog:", result)

In this example:

  * A Pydantic model Blog is defined with title and content fields.
  * The task task1 uses the output_pydantic property to specify that its output should conform to the Blog model.
  * After executing the crew, you can access the structured output in multiple ways as shown.



#### 

​

Explanation of Accessing the Output

  1. Dictionary-Style Indexing: You can directly access the fields using result[“field_name”]. This works because the CrewOutput class implements the **getitem** method.
  2. Directly from Pydantic Model: Access the attributes directly from the result.pydantic object.
  3. Using to_dict() Method: Convert the output to a dictionary and access the fields.
  4. Printing the Entire Object: Simply print the result object to see the structured output.



### 

​

Using `output_json`

The `output_json` property allows you to define the expected output in JSON format. This ensures that the task’s output is a valid JSON structure that can be easily parsed and used in your application.

Here’s an example demonstrating how to use `output_json`:

Code
    
    
    import json
    
    from crewai import Agent, Crew, Process, Task
    from pydantic import BaseModel
    
    
    # Define the Pydantic model for the blog
    class Blog(BaseModel):
        title: str
        content: str
    
    
    # Define the agent
    blog_agent = Agent(
        role="Blog Content Generator Agent",
        goal="Generate a blog title and content",
        backstory="""You are an expert content creator, skilled in crafting engaging and informative blog posts.""",
        verbose=False,
        allow_delegation=False,
        llm="gpt-4o",
    )
    
    # Define the task with output_json set to the Blog model
    task1 = Task(
        description="""Create a blog title and content on a given topic. Make sure the content is under 200 words.""",
        expected_output="A JSON object with 'title' and 'content' fields.",
        agent=blog_agent,
        output_json=Blog,
    )
    
    # Instantiate the crew with a sequential process
    crew = Crew(
        agents=[blog_agent],
        tasks=[task1],
        verbose=True,
        process=Process.sequential,
    )
    
    # Kickoff the crew to execute the task
    result = crew.kickoff()
    
    # Option 1: Accessing Properties Using Dictionary-Style Indexing
    print("Accessing Properties - Option 1")
    title = result["title"]
    content = result["content"]
    print("Title:", title)
    print("Content:", content)
    
    # Option 2: Printing the Entire Blog Object
    print("Accessing Properties - Option 2")
    print("Blog:", result)

In this example:

  * A Pydantic model Blog is defined with title and content fields, which is used to specify the structure of the JSON output.
  * The task task1 uses the output_json property to indicate that it expects a JSON output conforming to the Blog model.
  * After executing the crew, you can access the structured JSON output in two ways as shown.



#### 

​

Explanation of Accessing the Output

  1. Accessing Properties Using Dictionary-Style Indexing: You can access the fields directly using result[“field_name”]. This is possible because the CrewOutput class implements the **getitem** method, allowing you to treat the output like a dictionary. In this option, we’re retrieving the title and content from the result.
  2. Printing the Entire Blog Object: By printing result, you get the string representation of the CrewOutput object. Since the **str** method is implemented to return the JSON output, this will display the entire output as a formatted string representing the Blog object.



* * *

By using output_pydantic or output_json, you ensure that your tasks produce outputs in a consistent and structured format, making it easier to process and utilize the data within your application or across multiple tasks.

## 

​

Integrating Tools with Tasks

Leverage tools from the [CrewAI Toolkit](https://github.com/joaomdmoura/crewai-tools) and [LangChain Tools](https://python.langchain.com/docs/integrations/tools) for enhanced task performance and agent interaction.

## 

​

Creating a Task with Tools

Code
    
    
    import os
    os.environ["OPENAI_API_KEY"] = "Your Key"
    os.environ["SERPER_API_KEY"] = "Your Key" # serper.dev API key
    
    from crewai import Agent, Task, Crew
    from crewai_tools import SerperDevTool
    
    research_agent = Agent(
      role='Researcher',
      goal='Find and summarize the latest AI news',
      backstory="""You're a researcher at a large company.
      You're responsible for analyzing data and providing insights
      to the business.""",
      verbose=True
    )
    
    # to perform a semantic search for a specified query from a text's content across the internet
    search_tool = SerperDevTool()
    
    task = Task(
      description='Find and summarize the latest AI news',
      expected_output='A bullet list summary of the top 5 most important AI news',
      agent=research_agent,
      tools=[search_tool]
    )
    
    crew = Crew(
        agents=[research_agent],
        tasks=[task],
        verbose=True
    )
    
    result = crew.kickoff()
    print(result)

This demonstrates how tasks with specific tools can override an agent’s default set for tailored task execution.

## 

​

Referring to Other Tasks

In CrewAI, the output of one task is automatically relayed into the next one, but you can specifically define what tasks’ output, including multiple, should be used as context for another task.

This is useful when you have a task that depends on the output of another task that is not performed immediately after it. This is done through the `context` attribute of the task:

Code
    
    
    # ...
    
    research_ai_task = Task(
        description="Research the latest developments in AI",
        expected_output="A list of recent AI developments",
        async_execution=True,
        agent=research_agent,
        tools=[search_tool]
    )
    
    research_ops_task = Task(
        description="Research the latest developments in AI Ops",
        expected_output="A list of recent AI Ops developments",
        async_execution=True,
        agent=research_agent,
        tools=[search_tool]
    )
    
    write_blog_task = Task(
        description="Write a full blog post about the importance of AI and its latest news",
        expected_output="Full blog post that is 4 paragraphs long",
        agent=writer_agent,
        context=[research_ai_task, research_ops_task]
    )
    
    #...

## 

​

Asynchronous Execution

You can define a task to be executed asynchronously. This means that the crew will not wait for it to be completed to continue with the next task. This is useful for tasks that take a long time to be completed, or that are not crucial for the next tasks to be performed.

You can then use the `context` attribute to define in a future task that it should wait for the output of the asynchronous task to be completed.

Code
    
    
    #...
    
    list_ideas = Task(
        description="List of 5 interesting ideas to explore for an article about AI.",
        expected_output="Bullet point list of 5 ideas for an article.",
        agent=researcher,
        async_execution=True # Will be executed asynchronously
    )
    
    list_important_history = Task(
        description="Research the history of AI and give me the 5 most important events.",
        expected_output="Bullet point list of 5 important events.",
        agent=researcher,
        async_execution=True # Will be executed asynchronously
    )
    
    write_article = Task(
        description="Write an article about AI, its history, and interesting ideas.",
        expected_output="A 4 paragraph article about AI.",
        agent=writer,
        context=[list_ideas, list_important_history] # Will wait for the output of the two tasks to be completed
    )
    
    #...

## 

​

Callback Mechanism

The callback function is executed after the task is completed, allowing for actions or notifications to be triggered based on the task’s outcome.

Code
    
    
    # ...
    
    def callback_function(output: TaskOutput):
        # Do something after the task is completed
        # Example: Send an email to the manager
        print(f"""
            Task completed!
            Task: {output.description}
            Output: {output.raw}
        """)
    
    research_task = Task(
        description='Find and summarize the latest AI news',
        expected_output='A bullet list summary of the top 5 most important AI news',
        agent=research_agent,
        tools=[search_tool],
        callback=callback_function
    )
    
    #...

## 

​

Accessing a Specific Task Output

Once a crew finishes running, you can access the output of a specific task by using the `output` attribute of the task object:

Code
    
    
    # ...
    task1 = Task(
        description='Find and summarize the latest AI news',
        expected_output='A bullet list summary of the top 5 most important AI news',
        agent=research_agent,
        tools=[search_tool]
    )
    
    #...
    
    crew = Crew(
        agents=[research_agent],
        tasks=[task1, task2, task3],
        verbose=True
    )
    
    result = crew.kickoff()
    
    # Returns a TaskOutput object with the description and results of the task
    print(f"""
        Task completed!
        Task: {task1.output.description}
        Output: {task1.output.raw}
    """)

## 

​

Tool Override Mechanism

Specifying tools in a task allows for dynamic adaptation of agent capabilities, emphasizing CrewAI’s flexibility.

## 

​

Error Handling and Validation Mechanisms

While creating and executing tasks, certain validation mechanisms are in place to ensure the robustness and reliability of task attributes. These include but are not limited to:

  * Ensuring only one output type is set per task to maintain clear output expectations.
  * Preventing the manual assignment of the `id` attribute to uphold the integrity of the unique identifier system.



These validations help in maintaining the consistency and reliability of task executions within the crewAI framework.

## 

​

Task Guardrails

Task guardrails provide a powerful way to validate, transform, or filter task outputs before they are passed to the next task. Guardrails are optional functions that execute before the next task starts, allowing you to ensure that task outputs meet specific requirements or formats.

### 

​

Basic Usage

#### 

​

Define your own logic to validate

Code
    
    
    from typing import Tuple, Union
    from crewai import Task
    
    def validate_json_output(result: str) -> Tuple[bool, Union[dict, str]]:
        """Validate that the output is valid JSON."""
        try:
            json_data = json.loads(result)
            return (True, json_data)
        except json.JSONDecodeError:
            return (False, "Output must be valid JSON")
    
    task = Task(
        description="Generate JSON data",
        expected_output="Valid JSON object",
        guardrail=validate_json_output
    )

#### 

​

Leverage a no-code approach for validation

Code
    
    
    from crewai import Task
    
    task = Task(
        description="Generate JSON data",
        expected_output="Valid JSON object",
        guardrail="Ensure the response is a valid JSON object"
    )

#### 

​

Using YAML
    
    
    research_task:
      ...
      guardrail: make sure each bullet contains a minimum of 100 words
      ...

Code
    
    
    @CrewBase
    class InternalCrew:
        agents_config = "config/agents.yaml"
        tasks_config = "config/tasks.yaml"
    
        ...
        @task
        def research_task(self):
            return Task(config=self.tasks_config["research_task"])  # type: ignore[index]
        ...

#### 

​

Use custom models for code generation

Code
    
    
    from crewai import Task
    from crewai.llm import LLM
    
    task = Task(
        description="Generate JSON data",
        expected_output="Valid JSON object",
        guardrail=LLMGuardrail(
            description="Ensure the response is a valid JSON object",
            llm=LLM(model="gpt-4o-mini"),
        )
    )

### 

​

How Guardrails Work

  1. **Optional Attribute** : Guardrails are an optional attribute at the task level, allowing you to add validation only where needed.
  2. **Execution Timing** : The guardrail function is executed before the next task starts, ensuring valid data flow between tasks.
  3. **Return Format** : Guardrails must return a tuple of `(success, data)`:
     * If `success` is `True`, `data` is the validated/transformed result
     * If `success` is `False`, `data` is the error message
  4. **Result Routing** :
     * On success (`True`), the result is automatically passed to the next task
     * On failure (`False`), the error is sent back to the agent to generate a new answer



### 

​

Common Use Cases

#### 

​

Data Format Validation

Code
    
    
    def validate_email_format(result: str) -> Tuple[bool, Union[str, str]]:
        """Ensure the output contains a valid email address."""
        import re
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if re.match(email_pattern, result.strip()):
            return (True, result.strip())
        return (False, "Output must be a valid email address")

#### 

​

Content Filtering

Code
    
    
    def filter_sensitive_info(result: str) -> Tuple[bool, Union[str, str]]:
        """Remove or validate sensitive information."""
        sensitive_patterns = ['SSN:', 'password:', 'secret:']
        for pattern in sensitive_patterns:
            if pattern.lower() in result.lower():
                return (False, f"Output contains sensitive information ({pattern})")
        return (True, result)

#### 

​

Data Transformation

Code
    
    
    def normalize_phone_number(result: str) -> Tuple[bool, Union[str, str]]:
        """Ensure phone numbers are in a consistent format."""
        import re
        digits = re.sub(r'\D', '', result)
        if len(digits) == 10:
            formatted = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            return (True, formatted)
        return (False, "Output must be a 10-digit phone number")

### 

​

Advanced Features

#### 

​

Chaining Multiple Validations

Code
    
    
    def chain_validations(*validators):
        """Chain multiple validators together."""
        def combined_validator(result):
            for validator in validators:
                success, data = validator(result)
                if not success:
                    return (False, data)
                result = data
            return (True, result)
        return combined_validator
    
    # Usage
    task = Task(
        description="Get user contact info",
        expected_output="Email and phone",
        guardrail=chain_validations(
            validate_email_format,
            filter_sensitive_info
        )
    )

#### 

​

Custom Retry Logic

Code
    
    
    task = Task(
        description="Generate data",
        expected_output="Valid data",
        guardrail=validate_data,
        max_retries=5  # Override default retry limit
    )

## 

​

Creating Directories when Saving Files

You can now specify if a task should create directories when saving its output to a file. This is particularly useful for organizing outputs and ensuring that file paths are correctly structured.

Code
    
    
    # ...
    
    save_output_task = Task(
        description='Save the summarized AI news to a file',
        expected_output='File saved successfully',
        agent=research_agent,
        tools=[file_save_tool],
        output_file='outputs/ai_news_summary.txt',
        create_directory=True
    )
    
    #...

Check out the video below to see how to use structured outputs in CrewAI:

## 

​

Conclusion

Tasks are the driving force behind the actions of agents in CrewAI. By properly defining tasks and their outcomes, you set the stage for your AI agents to work effectively, either independently or as a collaborative unit. Equipping tasks with appropriate tools, understanding the execution process, and following robust validation practices are crucial for maximizing CrewAI’s potential, ensuring agents are effectively prepared for their assignments and that tasks are executed as intended.

Was this page helpful?

YesNo

[Agents](/concepts/agents)[Crews](/concepts/crews)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Overview
  * Task Execution Flow
  * Task Attributes
  * Creating Tasks
  * YAML Configuration (Recommended)
  * Direct Code Definition (Alternative)
  * Task Output
  * Task Output Attributes
  * Task Methods and Properties
  * Accessing Task Outputs
  * Example
  * Markdown Output Formatting
  * Using Markdown Formatting
  * YAML Configuration with Markdown
  * Benefits of Markdown Output
  * Task Dependencies and Context
  * Task Guardrails
  * Using Task Guardrails
  * Guardrail Function Requirements
  * LLMGuardrail
  * Error Handling Best Practices
  * Handling Guardrail Results
  * Getting Structured Consistent Outputs from Tasks
  * Using output_pydantic
  * Explanation of Accessing the Output
  * Using output_json
  * Explanation of Accessing the Output
  * Integrating Tools with Tasks
  * Creating a Task with Tools
  * Referring to Other Tasks
  * Asynchronous Execution
  * Callback Mechanism
  * Accessing a Specific Task Output
  * Tool Override Mechanism
  * Error Handling and Validation Mechanisms
  * Task Guardrails
  * Basic Usage
  * Define your own logic to validate
  * Leverage a no-code approach for validation
  * Using YAML
  * Use custom models for code generation
  * How Guardrails Work
  * Common Use Cases
  * Data Format Validation
  * Content Filtering
  * Data Transformation
  * Advanced Features
  * Chaining Multiple Validations
  * Custom Retry Logic
  * Creating Directories when Saving Files
  * Conclusion



Assistant

Responses are generated using AI and may contain mistakes.


---

### Replay Tasks from Latest Crew Kickoff {#replay-tasks-from-latest-crew-kickoff}

**Source:** [https://docs.crewai.com/learn/replay-tasks-from-latest-crew-kickoff](https://docs.crewai.com/learn/replay-tasks-from-latest-crew-kickoff)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Learn

Replay Tasks from Latest Crew Kickoff

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Learn

# Replay Tasks from Latest Crew Kickoff

Copy page

Replay tasks from the latest crew.kickoff(…)

## 

​

Introduction

CrewAI provides the ability to replay from a task specified from the latest crew kickoff. This feature is particularly useful when you’ve finished a kickoff and may want to retry certain tasks or don’t need to refetch data over and your agents already have the context saved from the kickoff execution so you just need to replay the tasks you want to.

You must run `crew.kickoff()` before you can replay a task. Currently, only the latest kickoff is supported, so if you use `kickoff_for_each`, it will only allow you to replay from the most recent crew run.

Here’s an example of how to replay from a task:

### 

​

Replaying from Specific Task Using the CLI

To use the replay feature, follow these steps:

1

Open your terminal or command prompt.

2

Navigate to the directory where your CrewAI project is located.

3

Run the following commands:

To view the latest kickoff task_ids use:
    
    
    crewai log-tasks-outputs

Once you have your `task_id` to replay, use:
    
    
    crewai replay -t <task_id>

Ensure `crewai` is installed and configured correctly in your development environment.

### 

​

Replaying from a Task Programmatically

To replay from a task programmatically, use the following steps:

1

Specify the `task_id` and input parameters for the replay process.

Specify the `task_id` and input parameters for the replay process.

2

Execute the replay command within a try-except block to handle potential errors.

Execute the replay command within a try-except block to handle potential errors.

Code
    
    
    def replay():
      """
      Replay the crew execution from a specific task.
      """
      task_id = '<task_id>'
      inputs = {"topic": "CrewAI Training"}  # This is optional; you can pass in the inputs you want to replay; otherwise, it uses the previous kickoff's inputs.
      try:
          YourCrewName_Crew().crew().replay(task_id=task_id, inputs=inputs)
    
      except subprocess.CalledProcessError as e:
          raise Exception(f"An error occurred while replaying the crew: {e}")
    
      except Exception as e:
          raise Exception(f"An unexpected error occurred: {e}")

## 

​

Conclusion

With the above enhancements and detailed functionality, replaying specific tasks in CrewAI has been made more efficient and robust. Ensure you follow the commands and steps precisely to make the most of these features.

Was this page helpful?

YesNo

[Using Multimodal Agents](/learn/multimodal-agents)[Sequential Processes](/learn/sequential-process)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Introduction
  * Replaying from Specific Task Using the CLI
  * Replaying from a Task Programmatically
  * Conclusion



Assistant

Responses are generated using AI and may contain mistakes.


---



## Crews {#crews}

### Crews {#crews}

**Source:** [https://docs.crewai.com/concepts/crews](https://docs.crewai.com/concepts/crews)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Core Concepts

Crews

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Core Concepts

# Crews

Copy page

Understanding and utilizing crews in the crewAI framework with comprehensive attributes and functionalities.

## 

​

Overview

A crew in crewAI represents a collaborative group of agents working together to achieve a set of tasks. Each crew defines the strategy for task execution, agent collaboration, and the overall workflow.

## 

​

Crew Attributes

Attribute| Parameters| Description  
---|---|---  
**Tasks**| `tasks`| A list of tasks assigned to the crew.  
**Agents**| `agents`| A list of agents that are part of the crew.  
**Process** _(optional)_| `process`| The process flow (e.g., sequential, hierarchical) the crew follows. Default is `sequential`.  
**Verbose** _(optional)_| `verbose`| The verbosity level for logging during execution. Defaults to `False`.  
**Manager LLM** _(optional)_| `manager_llm`| The language model used by the manager agent in a hierarchical process. **Required when using a hierarchical process.**  
**Function Calling LLM** _(optional)_| `function_calling_llm`| If passed, the crew will use this LLM to do function calling for tools for all agents in the crew. Each agent can have its own LLM, which overrides the crew’s LLM for function calling.  
**Config** _(optional)_| `config`| Optional configuration settings for the crew, in `Json` or `Dict[str, Any]` format.  
**Max RPM** _(optional)_| `max_rpm`| Maximum requests per minute the crew adheres to during execution. Defaults to `None`.  
**Memory** _(optional)_| `memory`| Utilized for storing execution memories (short-term, long-term, entity memory).  
**Memory Config** _(optional)_| `memory_config`| Configuration for the memory provider to be used by the crew.  
**Cache** _(optional)_| `cache`| Specifies whether to use a cache for storing the results of tools’ execution. Defaults to `True`.  
**Embedder** _(optional)_| `embedder`| Configuration for the embedder to be used by the crew. Mostly used by memory for now. Default is `{"provider": "openai"}`.  
**Step Callback** _(optional)_| `step_callback`| A function that is called after each step of every agent. This can be used to log the agent’s actions or to perform other operations; it won’t override the agent-specific `step_callback`.  
**Task Callback** _(optional)_| `task_callback`| A function that is called after the completion of each task. Useful for monitoring or additional operations post-task execution.  
**Share Crew** _(optional)_| `share_crew`| Whether you want to share the complete crew information and execution with the crewAI team to make the library better, and allow us to train models.  
**Output Log File** _(optional)_| `output_log_file`| Set to True to save logs as logs.txt in the current directory or provide a file path. Logs will be in JSON format if the filename ends in .json, otherwise .txt. Defaults to `None`.  
**Manager Agent** _(optional)_| `manager_agent`| `manager` sets a custom agent that will be used as a manager.  
**Prompt File** _(optional)_| `prompt_file`| Path to the prompt JSON file to be used for the crew.  
**Planning** _(optional)_| `planning`| Adds planning ability to the Crew. When activated before each Crew iteration, all Crew data is sent to an AgentPlanner that will plan the tasks and this plan will be added to each task description.  
**Planning LLM** _(optional)_| `planning_llm`| The language model used by the AgentPlanner in a planning process.  
  
**Crew Max RPM** : The `max_rpm` attribute sets the maximum number of requests per minute the crew can perform to avoid rate limits and will override individual agents’ `max_rpm` settings if you set it.

## 

​

Creating Crews

There are two ways to create crews in CrewAI: using **YAML configuration (recommended)** or defining them **directly in code**.

### 

​

YAML Configuration (Recommended)

Using YAML configuration provides a cleaner, more maintainable way to define crews and is consistent with how agents and tasks are defined in CrewAI projects.

After creating your CrewAI project as outlined in the [Installation](/installation) section, you can define your crew in a class that inherits from `CrewBase` and uses decorators to define agents, tasks, and the crew itself.

#### 

​

Example Crew Class with Decorators

code
    
    
    from crewai import Agent, Crew, Task, Process
    from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
    from crewai.agents.agent_builder.base_agent import BaseAgent
    from typing import List
    
    @CrewBase
    class YourCrewName:
        """Description of your crew"""
    
        agents: List[BaseAgent]
        tasks: List[Task]
    
        # Paths to your YAML configuration files
        # To see an example agent and task defined in YAML, checkout the following:
        # - Task: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
        # - Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
        agents_config = 'config/agents.yaml' 
        tasks_config = 'config/tasks.yaml' 
    
        @before_kickoff
        def prepare_inputs(self, inputs):
            # Modify inputs before the crew starts
            inputs['additional_data'] = "Some extra information"
            return inputs
    
        @after_kickoff
        def process_output(self, output):
            # Modify output after the crew finishes
            output.raw += "\nProcessed after kickoff."
            return output
    
        @agent
        def agent_one(self) -> Agent:
            return Agent(
                config=self.agents_config['agent_one'], # type: ignore[index]
                verbose=True
            )
    
        @agent
        def agent_two(self) -> Agent:
            return Agent(
                config=self.agents_config['agent_two'], # type: ignore[index]
                verbose=True
            )
    
        @task
        def task_one(self) -> Task:
            return Task(
                config=self.tasks_config['task_one'] # type: ignore[index]
            )
    
        @task
        def task_two(self) -> Task:
            return Task(
                config=self.tasks_config['task_two'] # type: ignore[index]
            )
    
        @crew
        def crew(self) -> Crew:
            return Crew(
                agents=self.agents,  # Automatically collected by the @agent decorator
                tasks=self.tasks,    # Automatically collected by the @task decorator. 
                process=Process.sequential,
                verbose=True,
            )

How to run the above code:

code
    
    
    YourCrewName().crew().kickoff(inputs={"any": "input here"})

Tasks will be executed in the order they are defined.

The `CrewBase` class, along with these decorators, automates the collection of agents and tasks, reducing the need for manual management.

#### 

​

Decorators overview from `annotations.py`

CrewAI provides several decorators in the `annotations.py` file that are used to mark methods within your crew class for special handling:

  * `@CrewBase`: Marks the class as a crew base class.
  * `@agent`: Denotes a method that returns an `Agent` object.
  * `@task`: Denotes a method that returns a `Task` object.
  * `@crew`: Denotes the method that returns the `Crew` object.
  * `@before_kickoff`: (Optional) Marks a method to be executed before the crew starts.
  * `@after_kickoff`: (Optional) Marks a method to be executed after the crew finishes.



These decorators help in organizing your crew’s structure and automatically collecting agents and tasks without manually listing them.

### 

​

Direct Code Definition (Alternative)

Alternatively, you can define the crew directly in code without using YAML configuration files.

code
    
    
    from crewai import Agent, Crew, Task, Process
    from crewai_tools import YourCustomTool
    
    class YourCrewName:
        def agent_one(self) -> Agent:
            return Agent(
                role="Data Analyst",
                goal="Analyze data trends in the market",
                backstory="An experienced data analyst with a background in economics",
                verbose=True,
                tools=[YourCustomTool()]
            )
    
        def agent_two(self) -> Agent:
            return Agent(
                role="Market Researcher",
                goal="Gather information on market dynamics",
                backstory="A diligent researcher with a keen eye for detail",
                verbose=True
            )
    
        def task_one(self) -> Task:
            return Task(
                description="Collect recent market data and identify trends.",
                expected_output="A report summarizing key trends in the market.",
                agent=self.agent_one()
            )
    
        def task_two(self) -> Task:
            return Task(
                description="Research factors affecting market dynamics.",
                expected_output="An analysis of factors influencing the market.",
                agent=self.agent_two()
            )
    
        def crew(self) -> Crew:
            return Crew(
                agents=[self.agent_one(), self.agent_two()],
                tasks=[self.task_one(), self.task_two()],
                process=Process.sequential,
                verbose=True
            )

How to run the above code:

code
    
    
    YourCrewName().crew().kickoff(inputs={})

In this example:

  * Agents and tasks are defined directly within the class without decorators.
  * We manually create and manage the list of agents and tasks.
  * This approach provides more control but can be less maintainable for larger projects.



## 

​

Crew Output

The output of a crew in the CrewAI framework is encapsulated within the `CrewOutput` class. This class provides a structured way to access results of the crew’s execution, including various formats such as raw strings, JSON, and Pydantic models. The `CrewOutput` includes the results from the final task output, token usage, and individual task outputs.

### 

​

Crew Output Attributes

Attribute| Parameters| Type| Description  
---|---|---|---  
**Raw**| `raw`| `str`| The raw output of the crew. This is the default format for the output.  
**Pydantic**| `pydantic`| `Optional[BaseModel]`| A Pydantic model object representing the structured output of the crew.  
**JSON Dict**| `json_dict`| `Optional[Dict[str, Any]]`| A dictionary representing the JSON output of the crew.  
**Tasks Output**| `tasks_output`| `List[TaskOutput]`| A list of `TaskOutput` objects, each representing the output of a task in the crew.  
**Token Usage**| `token_usage`| `Dict[str, Any]`| A summary of token usage, providing insights into the language model’s performance during execution.  
  
### 

​

Crew Output Methods and Properties

Method/Property| Description  
---|---  
**json**|  Returns the JSON string representation of the crew output if the output format is JSON.  
**to_dict**|  Converts the JSON and Pydantic outputs to a dictionary.  
* ***str****|  Returns the string representation of the crew output, prioritizing Pydantic, then JSON, then raw.  
  
### 

​

Accessing Crew Outputs

Once a crew has been executed, its output can be accessed through the `output` attribute of the `Crew` object. The `CrewOutput` class provides various ways to interact with and present this output.

#### 

​

Example

Code
    
    
    # Example crew execution
    crew = Crew(
        agents=[research_agent, writer_agent],
        tasks=[research_task, write_article_task],
        verbose=True
    )
    
    crew_output = crew.kickoff()
    
    # Accessing the crew output
    print(f"Raw Output: {crew_output.raw}")
    if crew_output.json_dict:
        print(f"JSON Output: {json.dumps(crew_output.json_dict, indent=2)}")
    if crew_output.pydantic:
        print(f"Pydantic Output: {crew_output.pydantic}")
    print(f"Tasks Output: {crew_output.tasks_output}")
    print(f"Token Usage: {crew_output.token_usage}")

## 

​

Accessing Crew Logs

You can see real time log of the crew execution, by setting `output_log_file` as a `True(Boolean)` or a `file_name(str)`. Supports logging of events as both `file_name.txt` and `file_name.json`. In case of `True(Boolean)` will save as `logs.txt`.

In case of `output_log_file` is set as `False(Boolean)` or `None`, the logs will not be populated.

Code
    
    
    # Save crew logs
    crew = Crew(output_log_file = True)  # Logs will be saved as logs.txt
    crew = Crew(output_log_file = file_name)  # Logs will be saved as file_name.txt
    crew = Crew(output_log_file = file_name.txt)  # Logs will be saved as file_name.txt
    crew = Crew(output_log_file = file_name.json)  # Logs will be saved as file_name.json

## 

​

Memory Utilization

Crews can utilize memory (short-term, long-term, and entity memory) to enhance their execution and learning over time. This feature allows crews to store and recall execution memories, aiding in decision-making and task execution strategies.

## 

​

Cache Utilization

Caches can be employed to store the results of tools’ execution, making the process more efficient by reducing the need to re-execute identical tasks.

## 

​

Crew Usage Metrics

After the crew execution, you can access the `usage_metrics` attribute to view the language model (LLM) usage metrics for all tasks executed by the crew. This provides insights into operational efficiency and areas for improvement.

Code
    
    
    # Access the crew's usage metrics
    crew = Crew(agents=[agent1, agent2], tasks=[task1, task2])
    crew.kickoff()
    print(crew.usage_metrics)

## 

​

Crew Execution Process

  * **Sequential Process** : Tasks are executed one after another, allowing for a linear flow of work.
  * **Hierarchical Process** : A manager agent coordinates the crew, delegating tasks and validating outcomes before proceeding. **Note** : A `manager_llm` or `manager_agent` is required for this process and it’s essential for validating the process flow.



### 

​

Kicking Off a Crew

Once your crew is assembled, initiate the workflow with the `kickoff()` method. This starts the execution process according to the defined process flow.

Code
    
    
    # Start the crew's task execution
    result = my_crew.kickoff()
    print(result)

### 

​

Different Ways to Kick Off a Crew

Once your crew is assembled, initiate the workflow with the appropriate kickoff method. CrewAI provides several methods for better control over the kickoff process: `kickoff()`, `kickoff_for_each()`, `kickoff_async()`, and `kickoff_for_each_async()`.

  * `kickoff()`: Starts the execution process according to the defined process flow.
  * `kickoff_for_each()`: Executes tasks sequentially for each provided input event or item in the collection.
  * `kickoff_async()`: Initiates the workflow asynchronously.
  * `kickoff_for_each_async()`: Executes tasks concurrently for each provided input event or item, leveraging asynchronous processing.



Code
    
    
    # Start the crew's task execution
    result = my_crew.kickoff()
    print(result)
    
    # Example of using kickoff_for_each
    inputs_array = [{'topic': 'AI in healthcare'}, {'topic': 'AI in finance'}]
    results = my_crew.kickoff_for_each(inputs=inputs_array)
    for result in results:
        print(result)
    
    # Example of using kickoff_async
    inputs = {'topic': 'AI in healthcare'}
    async_result = my_crew.kickoff_async(inputs=inputs)
    print(async_result)
    
    # Example of using kickoff_for_each_async
    inputs_array = [{'topic': 'AI in healthcare'}, {'topic': 'AI in finance'}]
    async_results = my_crew.kickoff_for_each_async(inputs=inputs_array)
    for async_result in async_results:
        print(async_result)

These methods provide flexibility in how you manage and execute tasks within your crew, allowing for both synchronous and asynchronous workflows tailored to your needs.

### 

​

Replaying from a Specific Task

You can now replay from a specific task using our CLI command `replay`.

The replay feature in CrewAI allows you to replay from a specific task using the command-line interface (CLI). By running the command `crewai replay -t <task_id>`, you can specify the `task_id` for the replay process.

Kickoffs will now save the latest kickoffs returned task outputs locally for you to be able to replay from.

### 

​

Replaying from a Specific Task Using the CLI

To use the replay feature, follow these steps:

  1. Open your terminal or command prompt.
  2. Navigate to the directory where your CrewAI project is located.
  3. Run the following command:



To view the latest kickoff task IDs, use:
    
    
    crewai log-tasks-outputs

Then, to replay from a specific task, use:
    
    
    crewai replay -t <task_id>

These commands let you replay from your latest kickoff tasks, still retaining context from previously executed tasks.

Was this page helpful?

YesNo

[Tasks](/concepts/tasks)[Flows](/concepts/flows)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Overview
  * Crew Attributes
  * Creating Crews
  * YAML Configuration (Recommended)
  * Example Crew Class with Decorators
  * Decorators overview from annotations.py
  * Direct Code Definition (Alternative)
  * Crew Output
  * Crew Output Attributes
  * Crew Output Methods and Properties
  * Accessing Crew Outputs
  * Example
  * Accessing Crew Logs
  * Memory Utilization
  * Cache Utilization
  * Crew Usage Metrics
  * Crew Execution Process
  * Kicking Off a Crew
  * Different Ways to Kick Off a Crew
  * Replaying from a Specific Task
  * Replaying from a Specific Task Using the CLI



Assistant

Responses are generated using AI and may contain mistakes.


---

### Build Your First Crew {#build-your-first-crew}

**Source:** [https://docs.crewai.com/guides/crews/first-crew](https://docs.crewai.com/guides/crews/first-crew)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Crews

Build Your First Crew

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

    * [Build Your First Crew](/guides/crews/first-crew)
  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Crews

# Build Your First Crew

Copy page

Step-by-step tutorial to create a collaborative AI team that works together to solve complex problems.

## 

​

Unleashing the Power of Collaborative AI

Imagine having a team of specialized AI agents working together seamlessly to solve complex problems, each contributing their unique skills to achieve a common goal. This is the power of CrewAI - a framework that enables you to create collaborative AI systems that can accomplish tasks far beyond what a single AI could achieve alone.

In this guide, we’ll walk through creating a research crew that will help us research and analyze a topic, then create a comprehensive report. This practical example demonstrates how AI agents can collaborate to accomplish complex tasks, but it’s just the beginning of what’s possible with CrewAI.

### 

​

What You’ll Build and Learn

By the end of this guide, you’ll have:

  1. **Created a specialized AI research team** with distinct roles and responsibilities
  2. **Orchestrated collaboration** between multiple AI agents
  3. **Automated a complex workflow** that involves gathering information, analysis, and report generation
  4. **Built foundational skills** that you can apply to more ambitious projects



While we’re building a simple research crew in this guide, the same patterns and techniques can be applied to create much more sophisticated teams for tasks like:

  * Multi-stage content creation with specialized writers, editors, and fact-checkers
  * Complex customer service systems with tiered support agents
  * Autonomous business analysts that gather data, create visualizations, and generate insights
  * Product development teams that ideate, design, and plan implementation



Let’s get started building your first crew!

### 

​

Prerequisites

Before starting, make sure you have:

  1. Installed CrewAI following the [installation guide](/installation)
  2. Set up your LLM API key in your environment, following the [LLM setup guide](/concepts/llms#setting-up-your-llm)
  3. Basic understanding of Python



## 

​

Step 1: Create a New CrewAI Project

First, let’s create a new CrewAI project using the CLI. This command will set up a complete project structure with all the necessary files, allowing you to focus on defining your agents and their tasks rather than setting up boilerplate code.
    
    
    crewai create crew research_crew
    cd research_crew

This will generate a project with the basic structure needed for your crew. The CLI automatically creates:

  * A project directory with the necessary files
  * Configuration files for agents and tasks
  * A basic crew implementation
  * A main script to run the crew



CrewAI Framework Overview

## 

​

Step 2: Explore the Project Structure

Let’s take a moment to understand the project structure created by the CLI. CrewAI follows best practices for Python projects, making it easy to maintain and extend your code as your crews become more complex.
    
    
    research_crew/
    ├── .gitignore
    ├── pyproject.toml
    ├── README.md
    ├── .env
    └── src/
        └── research_crew/
            ├── __init__.py
            ├── main.py
            ├── crew.py
            ├── tools/
            │   ├── custom_tool.py
            │   └── __init__.py
            └── config/
                ├── agents.yaml
                └── tasks.yaml

This structure follows best practices for Python projects and makes it easy to organize your code. The separation of configuration files (in YAML) from implementation code (in Python) makes it easy to modify your crew’s behavior without changing the underlying code.

## 

​

Step 3: Configure Your Agents

Now comes the fun part - defining your AI agents! In CrewAI, agents are specialized entities with specific roles, goals, and backstories that shape their behavior. Think of them as characters in a play, each with their own personality and purpose.

For our research crew, we’ll create two agents:

  1. A **researcher** who excels at finding and organizing information
  2. An **analyst** who can interpret research findings and create insightful reports



Let’s modify the `agents.yaml` file to define these specialized agents. Be sure to set `llm` to the provider you are using.
    
    
    # src/research_crew/config/agents.yaml
    researcher:
      role: >
        Senior Research Specialist for {topic}
      goal: >
        Find comprehensive and accurate information about {topic}
        with a focus on recent developments and key insights
      backstory: >
        You are an experienced research specialist with a talent for
        finding relevant information from various sources. You excel at
        organizing information in a clear and structured manner, making
        complex topics accessible to others.
      llm: provider/model-id  # e.g. openai/gpt-4o, google/gemini-2.0-flash, anthropic/claude...
    
    analyst:
      role: >
        Data Analyst and Report Writer for {topic}
      goal: >
        Analyze research findings and create a comprehensive, well-structured
        report that presents insights in a clear and engaging way
      backstory: >
        You are a skilled analyst with a background in data interpretation
        and technical writing. You have a talent for identifying patterns
        and extracting meaningful insights from research data, then
        communicating those insights effectively through well-crafted reports.
      llm: provider/model-id  # e.g. openai/gpt-4o, google/gemini-2.0-flash, anthropic/claude...

Notice how each agent has a distinct role, goal, and backstory. These elements aren’t just descriptive - they actively shape how the agent approaches its tasks. By crafting these carefully, you can create agents with specialized skills and perspectives that complement each other.

## 

​

Step 4: Define Your Tasks

With our agents defined, we now need to give them specific tasks to perform. Tasks in CrewAI represent the concrete work that agents will perform, with detailed instructions and expected outputs.

For our research crew, we’ll define two main tasks:

  1. A **research task** for gathering comprehensive information
  2. An **analysis task** for creating an insightful report



Let’s modify the `tasks.yaml` file:
    
    
    # src/research_crew/config/tasks.yaml
    research_task:
      description: >
        Conduct thorough research on {topic}. Focus on:
        1. Key concepts and definitions
        2. Historical development and recent trends
        3. Major challenges and opportunities
        4. Notable applications or case studies
        5. Future outlook and potential developments
    
        Make sure to organize your findings in a structured format with clear sections.
      expected_output: >
        A comprehensive research document with well-organized sections covering
        all the requested aspects of {topic}. Include specific facts, figures,
        and examples where relevant.
      agent: researcher
    
    analysis_task:
      description: >
        Analyze the research findings and create a comprehensive report on {topic}.
        Your report should:
        1. Begin with an executive summary
        2. Include all key information from the research
        3. Provide insightful analysis of trends and patterns
        4. Offer recommendations or future considerations
        5. Be formatted in a professional, easy-to-read style with clear headings
      expected_output: >
        A polished, professional report on {topic} that presents the research
        findings with added analysis and insights. The report should be well-structured
        with an executive summary, main sections, and conclusion.
      agent: analyst
      context:
        - research_task
      output_file: output/report.md

Note the `context` field in the analysis task - this is a powerful feature that allows the analyst to access the output of the research task. This creates a workflow where information flows naturally between agents, just as it would in a human team.

## 

​

Step 5: Configure Your Crew

Now it’s time to bring everything together by configuring our crew. The crew is the container that orchestrates how agents work together to complete tasks.

Let’s modify the `crew.py` file:
    
    
    # src/research_crew/crew.py
    from crewai import Agent, Crew, Process, Task
    from crewai.project import CrewBase, agent, crew, task
    from crewai_tools import SerperDevTool
    from crewai.agents.agent_builder.base_agent import BaseAgent
    from typing import List
    
    @CrewBase
    class ResearchCrew():
        """Research crew for comprehensive topic analysis and reporting"""
    
        agents: List[BaseAgent]
        tasks: List[Task]
    
        @agent
        def researcher(self) -> Agent:
            return Agent(
                config=self.agents_config['researcher'], # type: ignore[index]
                verbose=True,
                tools=[SerperDevTool()]
            )
    
        @agent
        def analyst(self) -> Agent:
            return Agent(
                config=self.agents_config['analyst'], # type: ignore[index]
                verbose=True
            )
    
        @task
        def research_task(self) -> Task:
            return Task(
                config=self.tasks_config['research_task'] # type: ignore[index]
            )
    
        @task
        def analysis_task(self) -> Task:
            return Task(
                config=self.tasks_config['analysis_task'], # type: ignore[index]
                output_file='output/report.md'
            )
    
        @crew
        def crew(self) -> Crew:
            """Creates the research crew"""
            return Crew(
                agents=self.agents,
                tasks=self.tasks,
                process=Process.sequential,
                verbose=True,
            )

In this code, we’re:

  1. Creating the researcher agent and equipping it with the SerperDevTool to search the web
  2. Creating the analyst agent
  3. Setting up the research and analysis tasks
  4. Configuring the crew to run tasks sequentially (the analyst will wait for the researcher to finish)



This is where the magic happens - with just a few lines of code, we’ve defined a collaborative AI system where specialized agents work together in a coordinated process.

## 

​

Step 6: Set Up Your Main Script

Now, let’s set up the main script that will run our crew. This is where we provide the specific topic we want our crew to research.
    
    
    #!/usr/bin/env python
    # src/research_crew/main.py
    import os
    from research_crew.crew import ResearchCrew
    
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    def run():
        """
        Run the research crew.
        """
        inputs = {
            'topic': 'Artificial Intelligence in Healthcare'
        }
    
        # Create and run the crew
        result = ResearchCrew().crew().kickoff(inputs=inputs)
    
        # Print the result
        print("\n\n=== FINAL REPORT ===\n\n")
        print(result.raw)
    
        print("\n\nReport has been saved to output/report.md")
    
    if __name__ == "__main__":
        run()

This script prepares the environment, specifies our research topic, and kicks off the crew’s work. The power of CrewAI is evident in how simple this code is - all the complexity of managing multiple AI agents is handled by the framework.

## 

​

Step 7: Set Up Your Environment Variables

Create a `.env` file in your project root with your API keys:
    
    
    SERPER_API_KEY=your_serper_api_key
    # Add your provider's API key here too.

See the [LLM Setup guide](/concepts/llms#setting-up-your-llm) for details on configuring your provider of choice. You can get a Serper API key from [Serper.dev](https://serper.dev/).

## 

​

Step 8: Install Dependencies

Install the required dependencies using the CrewAI CLI:
    
    
    crewai install

This command will:

  1. Read the dependencies from your project configuration
  2. Create a virtual environment if needed
  3. Install all required packages



## 

​

Step 9: Run Your Crew

Now for the exciting moment - it’s time to run your crew and see AI collaboration in action!
    
    
    crewai run

When you run this command, you’ll see your crew spring to life. The researcher will gather information about the specified topic, and the analyst will then create a comprehensive report based on that research. You’ll see the agents’ thought processes, actions, and outputs in real-time as they work together to complete their tasks.

## 

​

Step 10: Review the Output

Once the crew completes its work, you’ll find the final report in the `output/report.md` file. The report will include:

  1. An executive summary
  2. Detailed information about the topic
  3. Analysis and insights
  4. Recommendations or future considerations



Take a moment to appreciate what you’ve accomplished - you’ve created a system where multiple AI agents collaborated on a complex task, each contributing their specialized skills to produce a result that’s greater than what any single agent could achieve alone.

## 

​

Exploring Other CLI Commands

CrewAI offers several other useful CLI commands for working with crews:
    
    
    # View all available commands
    crewai --help
    
    # Run the crew
    crewai run
    
    # Test the crew
    crewai test
    
    # Reset crew memories
    crewai reset-memories
    
    # Replay from a specific task
    crewai replay -t <task_id>

## 

​

The Art of the Possible: Beyond Your First Crew

What you’ve built in this guide is just the beginning. The skills and patterns you’ve learned can be applied to create increasingly sophisticated AI systems. Here are some ways you could extend this basic research crew:

### 

​

Expanding Your Crew

You could add more specialized agents to your crew:

  * A **fact-checker** to verify research findings
  * A **data visualizer** to create charts and graphs
  * A **domain expert** with specialized knowledge in a particular area
  * A **critic** to identify weaknesses in the analysis



### 

​

Adding Tools and Capabilities

You could enhance your agents with additional tools:

  * Web browsing tools for real-time research
  * CSV/database tools for data analysis
  * Code execution tools for data processing
  * API connections to external services



### 

​

Creating More Complex Workflows

You could implement more sophisticated processes:

  * Hierarchical processes where manager agents delegate to worker agents
  * Iterative processes with feedback loops for refinement
  * Parallel processes where multiple agents work simultaneously
  * Dynamic processes that adapt based on intermediate results



### 

​

Applying to Different Domains

The same patterns can be applied to create crews for:

  * **Content creation** : Writers, editors, fact-checkers, and designers working together
  * **Customer service** : Triage agents, specialists, and quality control working together
  * **Product development** : Researchers, designers, and planners collaborating
  * **Data analysis** : Data collectors, analysts, and visualization specialists



## 

​

Next Steps

Now that you’ve built your first crew, you can:

  1. Experiment with different agent configurations and personalities
  2. Try more complex task structures and workflows
  3. Implement custom tools to give your agents new capabilities
  4. Apply your crew to different topics or problem domains
  5. Explore [CrewAI Flows](/guides/flows/first-flow) for more advanced workflows with procedural programming



Congratulations! You’ve successfully built your first CrewAI crew that can research and analyze any topic you provide. This foundational experience has equipped you with the skills to create increasingly sophisticated AI systems that can tackle complex, multi-stage problems through collaborative intelligence.

Was this page helpful?

YesNo

[Crafting Effective Agents](/guides/agents/crafting-effective-agents)[Build Your First Flow](/guides/flows/first-flow)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Unleashing the Power of Collaborative AI
  * What You’ll Build and Learn
  * Prerequisites
  * Step 1: Create a New CrewAI Project
  * Step 2: Explore the Project Structure
  * Step 3: Configure Your Agents
  * Step 4: Define Your Tasks
  * Step 5: Configure Your Crew
  * Step 6: Set Up Your Main Script
  * Step 7: Set Up Your Environment Variables
  * Step 8: Install Dependencies
  * Step 9: Run Your Crew
  * Step 10: Review the Output
  * Exploring Other CLI Commands
  * The Art of the Possible: Beyond Your First Crew
  * Expanding Your Crew
  * Adding Tools and Capabilities
  * Creating More Complex Workflows
  * Applying to Different Domains
  * Next Steps



Assistant

Responses are generated using AI and may contain mistakes.


---



## Tools {#tools}

### Tools {#tools}

**Source:** [https://docs.crewai.com/concepts/tools](https://docs.crewai.com/concepts/tools)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Core Concepts

Tools

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Core Concepts

# Tools

Copy page

Understanding and leveraging tools within the CrewAI framework for agent collaboration and task execution.

## 

​

Overview

CrewAI tools empower agents with capabilities ranging from web searching and data analysis to collaboration and delegating tasks among coworkers. This documentation outlines how to create, integrate, and leverage these tools within the CrewAI framework, including a new focus on collaboration tools.

## 

​

What is a Tool?

A tool in CrewAI is a skill or function that agents can utilize to perform various actions. This includes tools from the [CrewAI Toolkit](https://github.com/joaomdmoura/crewai-tools) and [LangChain Tools](https://python.langchain.com/docs/integrations/tools), enabling everything from simple searches to complex interactions and effective teamwork among agents.

CrewAI Enterprise provides a comprehensive Tools Repository with pre-built integrations for common business systems and APIs. Deploy agents with enterprise tools in minutes instead of days.

The Enterprise Tools Repository includes:

  * Pre-built connectors for popular enterprise systems
  * Custom tool creation interface
  * Version control and sharing capabilities
  * Security and compliance features



## 

​

Key Characteristics of Tools

  * **Utility** : Crafted for tasks such as web searching, data analysis, content generation, and agent collaboration.
  * **Integration** : Boosts agent capabilities by seamlessly integrating tools into their workflow.
  * **Customizability** : Provides the flexibility to develop custom tools or utilize existing ones, catering to the specific needs of agents.
  * **Error Handling** : Incorporates robust error handling mechanisms to ensure smooth operation.
  * **Caching Mechanism** : Features intelligent caching to optimize performance and reduce redundant operations.



## 

​

Using CrewAI Tools

To enhance your agents’ capabilities with crewAI tools, begin by installing our extra tools package:
    
    
    pip install 'crewai[tools]'

Here’s an example demonstrating their use:

Code
    
    
    import os
    from crewai import Agent, Task, Crew
    # Importing crewAI tools
    from crewai_tools import (
        DirectoryReadTool,
        FileReadTool,
        SerperDevTool,
        WebsiteSearchTool
    )
    
    # Set up API keys
    os.environ["SERPER_API_KEY"] = "Your Key" # serper.dev API key
    os.environ["OPENAI_API_KEY"] = "Your Key"
    
    # Instantiate tools
    docs_tool = DirectoryReadTool(directory='./blog-posts')
    file_tool = FileReadTool()
    search_tool = SerperDevTool()
    web_rag_tool = WebsiteSearchTool()
    
    # Create agents
    researcher = Agent(
        role='Market Research Analyst',
        goal='Provide up-to-date market analysis of the AI industry',
        backstory='An expert analyst with a keen eye for market trends.',
        tools=[search_tool, web_rag_tool],
        verbose=True
    )
    
    writer = Agent(
        role='Content Writer',
        goal='Craft engaging blog posts about the AI industry',
        backstory='A skilled writer with a passion for technology.',
        tools=[docs_tool, file_tool],
        verbose=True
    )
    
    # Define tasks
    research = Task(
        description='Research the latest trends in the AI industry and provide a summary.',
        expected_output='A summary of the top 3 trending developments in the AI industry with a unique perspective on their significance.',
        agent=researcher
    )
    
    write = Task(
        description='Write an engaging blog post about the AI industry, based on the research analyst's summary. Draw inspiration from the latest blog posts in the directory.',
        expected_output='A 4-paragraph blog post formatted in markdown with engaging, informative, and accessible content, avoiding complex jargon.',
        agent=writer,
        output_file='blog-posts/new_post.md'  # The final blog post will be saved here
    )
    
    # Assemble a crew with planning enabled
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research, write],
        verbose=True,
        planning=True,  # Enable planning feature
    )
    
    # Execute tasks
    crew.kickoff()

## 

​

Available CrewAI Tools

  * **Error Handling** : All tools are built with error handling capabilities, allowing agents to gracefully manage exceptions and continue their tasks.
  * **Caching Mechanism** : All tools support caching, enabling agents to efficiently reuse previously obtained results, reducing the load on external resources and speeding up the execution time. You can also define finer control over the caching mechanism using the `cache_function` attribute on the tool.



Here is a list of the available tools and their descriptions:

Tool| Description  
---|---  
**ApifyActorsTool**|  A tool that integrates Apify Actors with your workflows for web scraping and automation tasks.  
**BrowserbaseLoadTool**|  A tool for interacting with and extracting data from web browsers.  
**CodeDocsSearchTool**|  A RAG tool optimized for searching through code documentation and related technical documents.  
**CodeInterpreterTool**|  A tool for interpreting python code.  
**ComposioTool**|  Enables use of Composio tools.  
**CSVSearchTool**|  A RAG tool designed for searching within CSV files, tailored to handle structured data.  
**DALL-E Tool**|  A tool for generating images using the DALL-E API.  
**DirectorySearchTool**|  A RAG tool for searching within directories, useful for navigating through file systems.  
**DOCXSearchTool**|  A RAG tool aimed at searching within DOCX documents, ideal for processing Word files.  
**DirectoryReadTool**|  Facilitates reading and processing of directory structures and their contents.  
**EXASearchTool**|  A tool designed for performing exhaustive searches across various data sources.  
**FileReadTool**|  Enables reading and extracting data from files, supporting various file formats.  
**FirecrawlSearchTool**|  A tool to search webpages using Firecrawl and return the results.  
**FirecrawlCrawlWebsiteTool**|  A tool for crawling webpages using Firecrawl.  
**FirecrawlScrapeWebsiteTool**|  A tool for scraping webpages URL using Firecrawl and returning its contents.  
**GithubSearchTool**|  A RAG tool for searching within GitHub repositories, useful for code and documentation search.  
**SerperDevTool**|  A specialized tool for development purposes, with specific functionalities under development.  
**TXTSearchTool**|  A RAG tool focused on searching within text (.txt) files, suitable for unstructured data.  
**JSONSearchTool**|  A RAG tool designed for searching within JSON files, catering to structured data handling.  
**LlamaIndexTool**|  Enables the use of LlamaIndex tools.  
**MDXSearchTool**|  A RAG tool tailored for searching within Markdown (MDX) files, useful for documentation.  
**PDFSearchTool**|  A RAG tool aimed at searching within PDF documents, ideal for processing scanned documents.  
**PGSearchTool**|  A RAG tool optimized for searching within PostgreSQL databases, suitable for database queries.  
**Vision Tool**|  A tool for generating images using the DALL-E API.  
**RagTool**|  A general-purpose RAG tool capable of handling various data sources and types.  
**ScrapeElementFromWebsiteTool**|  Enables scraping specific elements from websites, useful for targeted data extraction.  
**ScrapeWebsiteTool**|  Facilitates scraping entire websites, ideal for comprehensive data collection.  
**WebsiteSearchTool**|  A RAG tool for searching website content, optimized for web data extraction.  
**XMLSearchTool**|  A RAG tool designed for searching within XML files, suitable for structured data formats.  
**YoutubeChannelSearchTool**|  A RAG tool for searching within YouTube channels, useful for video content analysis.  
**YoutubeVideoSearchTool**|  A RAG tool aimed at searching within YouTube videos, ideal for video data extraction.  
  
## 

​

Creating your own Tools

Developers can craft `custom tools` tailored for their agent’s needs or utilize pre-built options.

There are two main ways for one to create a CrewAI tool:

### 

​

Subclassing `BaseTool`

Code
    
    
    from crewai.tools import BaseTool
    from pydantic import BaseModel, Field
    
    class MyToolInput(BaseModel):
        """Input schema for MyCustomTool."""
        argument: str = Field(..., description="Description of the argument.")
    
    class MyCustomTool(BaseTool):
        name: str = "Name of my tool"
        description: str = "What this tool does. It's vital for effective utilization."
        args_schema: Type[BaseModel] = MyToolInput
    
        def _run(self, argument: str) -> str:
            # Your tool's logic here
            return "Tool's result"

### 

​

Utilizing the `tool` Decorator

Code
    
    
    from crewai.tools import tool
    @tool("Name of my tool")
    def my_tool(question: str) -> str:
        """Clear description for what this tool is useful for, your agent will need this information to use it."""
        # Function logic here
        return "Result from your custom tool"

### 

​

Custom Caching Mechanism

Tools can optionally implement a `cache_function` to fine-tune caching behavior. This function determines when to cache results based on specific conditions, offering granular control over caching logic.

Code
    
    
    from crewai.tools import tool
    
    @tool
    def multiplication_tool(first_number: int, second_number: int) -> str:
        """Useful for when you need to multiply two numbers together."""
        return first_number * second_number
    
    def cache_func(args, result):
        # In this case, we only cache the result if it's a multiple of 2
        cache = result % 2 == 0
        return cache
    
    multiplication_tool.cache_function = cache_func
    
    writer1 = Agent(
            role="Writer",
            goal="You write lessons of math for kids.",
            backstory="You're an expert in writing and you love to teach kids but you know nothing of math.",
            tools=[multiplication_tool],
            allow_delegation=False,
        )
        #...

## 

​

Conclusion

Tools are pivotal in extending the capabilities of CrewAI agents, enabling them to undertake a broad spectrum of tasks and collaborate effectively. When building solutions with CrewAI, leverage both custom and existing tools to empower your agents and enhance the AI ecosystem. Consider utilizing error handling, caching mechanisms, and the flexibility of tool arguments to optimize your agents’ performance and capabilities.

Was this page helpful?

YesNo

[CLI](/concepts/cli)[Event Listeners](/concepts/event-listener)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Overview
  * What is a Tool?
  * Key Characteristics of Tools
  * Using CrewAI Tools
  * Available CrewAI Tools
  * Creating your own Tools
  * Subclassing BaseTool
  * Utilizing the tool Decorator
  * Custom Caching Mechanism
  * Conclusion



Assistant

Responses are generated using AI and may contain mistakes.


---

### Create Custom Tools {#create-custom-tools}

**Source:** [https://docs.crewai.com/learn/create-custom-tools](https://docs.crewai.com/learn/create-custom-tools)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Learn

Create Custom Tools

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Learn

# Create Custom Tools

Copy page

Comprehensive guide on crafting, using, and managing custom tools within the CrewAI framework, including new functionalities and error handling.

## 

​

Creating and Utilizing Tools in CrewAI

This guide provides detailed instructions on creating custom tools for the CrewAI framework and how to efficiently manage and utilize these tools, incorporating the latest functionalities such as tool delegation, error handling, and dynamic tool calling. It also highlights the importance of collaboration tools, enabling agents to perform a wide range of actions.

### 

​

Subclassing `BaseTool`

To create a personalized tool, inherit from `BaseTool` and define the necessary attributes, including the `args_schema` for input validation, and the `_run` method.

Code
    
    
    from typing import Type
    from crewai.tools import BaseTool
    from pydantic import BaseModel, Field
    
    class MyToolInput(BaseModel):
        """Input schema for MyCustomTool."""
        argument: str = Field(..., description="Description of the argument.")
    
    class MyCustomTool(BaseTool):
        name: str = "Name of my tool"
        description: str = "What this tool does. It's vital for effective utilization."
        args_schema: Type[BaseModel] = MyToolInput
    
        def _run(self, argument: str) -> str:
            # Your tool's logic here
            return "Tool's result"

### 

​

Using the `tool` Decorator

Alternatively, you can use the tool decorator `@tool`. This approach allows you to define the tool’s attributes and functionality directly within a function, offering a concise and efficient way to create specialized tools tailored to your needs.

Code
    
    
    from crewai.tools import tool
    
    @tool("Tool Name")
    def my_simple_tool(question: str) -> str:
        """Tool description for clarity."""
        # Tool logic here
        return "Tool output"

### 

​

Defining a Cache Function for the Tool

To optimize tool performance with caching, define custom caching strategies using the `cache_function` attribute.

Code
    
    
    @tool("Tool with Caching")
    def cached_tool(argument: str) -> str:
        """Tool functionality description."""
        return "Cacheable result"
    
    def my_cache_strategy(arguments: dict, result: str) -> bool:
        # Define custom caching logic
        return True if some_condition else False
    
    cached_tool.cache_function = my_cache_strategy

By adhering to these guidelines and incorporating new functionalities and collaboration tools into your tool creation and management processes, you can leverage the full capabilities of the CrewAI framework, enhancing both the development experience and the efficiency of your AI agents.

Was this page helpful?

YesNo

[Coding Agents](/learn/coding-agents)[Custom LLM Implementation](/learn/custom-llm)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Creating and Utilizing Tools in CrewAI
  * Subclassing BaseTool
  * Using the tool Decorator
  * Defining a Cache Function for the Tool



Assistant

Responses are generated using AI and may contain mistakes.


---

### Force Tool Output as Result {#force-tool-output-as-result}

**Source:** [https://docs.crewai.com/learn/force-tool-output-as-result](https://docs.crewai.com/learn/force-tool-output-as-result)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Learn

Force Tool Output as Result

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Learn

# Force Tool Output as Result

Copy page

Learn how to force tool output as the result in an Agent’s task in CrewAI.

## 

​

Introduction

In CrewAI, you can force the output of a tool as the result of an agent’s task. This feature is useful when you want to ensure that the tool output is captured and returned as the task result, avoiding any agent modification during the task execution.

## 

​

Forcing Tool Output as Result

To force the tool output as the result of an agent’s task, you need to set the `result_as_answer` parameter to `True` when adding a tool to the agent. This parameter ensures that the tool output is captured and returned as the task result, without any modifications by the agent.

Here’s an example of how to force the tool output as the result of an agent’s task:

Code
    
    
    from crewai.agent import Agent
    from my_tool import MyCustomTool
    
    # Create a coding agent with the custom tool
    coding_agent = Agent(
            role="Data Scientist",
            goal="Produce amazing reports on AI",
            backstory="You work with data and AI",
            tools=[MyCustomTool(result_as_answer=True)],
        )
    
    # Assuming the tool's execution and result population occurs within the system
    task_result = coding_agent.execute_task(task)

## 

​

Workflow in Action

1

Task Execution

The agent executes the task using the tool provided.

2

Tool Output

The tool generates the output, which is captured as the task result.

3

Agent Interaction

The agent may reflect and take learnings from the tool but the output is not modified.

4

Result Return

The tool output is returned as the task result without any modifications.

Was this page helpful?

YesNo

[Image Generation with DALL-E](/learn/dalle-image-generation)[Hierarchical Process](/learn/hierarchical-process)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Introduction
  * Forcing Tool Output as Result
  * Workflow in Action



Assistant

Responses are generated using AI and may contain mistakes.


---

### Tools Overview {#tools-overview}

**Source:** [https://docs.crewai.com/tools/overview](https://docs.crewai.com/tools/overview)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Tools

Tools Overview

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Tools

# Tools Overview

Copy page

Discover CrewAI’s extensive library of 40+ tools to supercharge your AI agents

CrewAI provides an extensive library of pre-built tools to enhance your agents’ capabilities. From file processing to web scraping, database queries to AI services - we’ve got you covered.

## 

​

**Tool Categories**

## [File & DocumentRead, write, and search through various file formats including PDF, DOCX, JSON, CSV, and more. Perfect for document processing workflows.](/tools/file-document/overview)## [Web Scraping & BrowsingExtract data from websites, automate browser interactions, and scrape content at scale with tools like Firecrawl, Selenium, and more.](/tools/web-scraping/overview)## [Search & ResearchPerform web searches, find code repositories, research YouTube content, and discover information across the internet.](/tools/search-research/overview)## [Database & DataConnect to SQL databases, vector stores, and data warehouses. Query MySQL, PostgreSQL, Snowflake, Qdrant, and Weaviate.](/tools/database-data/overview)## [AI & Machine LearningGenerate images with DALL-E, process vision tasks, integrate with LangChain, build RAG systems, and leverage code interpreters.](/tools/ai-ml/overview)## [Cloud & StorageInteract with cloud services including AWS S3, Amazon Bedrock, and other cloud storage and AI services.](/tools/cloud-storage/overview)## [Automation & IntegrationAutomate workflows with Apify, Composio, and other integration platforms to connect your agents with external services.](/tools/automation/overview)

## 

​

**Quick Access**

Need a specific tool? Here are some popular choices:

## [RAG ToolImplement Retrieval-Augmented Generation](/tools/ai-ml/ragtool)## [Serper DevGoogle search API](/tools/search-research/serperdevtool)## [File ReadRead any file type](/tools/file-document/filereadtool)## [Scrape WebsiteExtract web content](/tools/web-scraping/scrapewebsitetool)## [Code InterpreterExecute Python code](/tools/ai-ml/codeinterpretertool)## [S3 ReaderAccess AWS S3 files](/tools/cloud-storage/s3readertool)

## 

​

**Getting Started**

To use any tool in your CrewAI project:

  1. **Import** the tool in your crew configuration
  2. **Add** it to your agent’s tools list
  3. **Configure** any required API keys or settings


    
    
    from crewai_tools import FileReadTool, SerperDevTool
    
    # Add tools to your agent
    agent = Agent(
        role="Research Analyst",
        tools=[FileReadTool(), SerperDevTool()],
        # ... other configuration
    )

Ready to explore? Pick a category above to discover tools that fit your use case!

Was this page helpful?

YesNo

[MCP Security Considerations](/mcp/security)[Overview](/tools/file-document/overview)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Tool Categories
  * Quick Access
  * Getting Started



Assistant

Responses are generated using AI and may contain mistakes.


---



## LLMs {#llms}

### Custom LLM Implementation {#custom-llm-implementation}

**Source:** [https://docs.crewai.com/learn/custom-llm](https://docs.crewai.com/learn/custom-llm)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Learn

Custom LLM Implementation

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Learn

# Custom LLM Implementation

Copy page

Learn how to create custom LLM implementations in CrewAI.

## 

​

Overview

CrewAI supports custom LLM implementations through the `BaseLLM` abstract base class. This allows you to integrate any LLM provider that doesn’t have built-in support in LiteLLM, or implement custom authentication mechanisms.

## 

​

Quick Start

Here’s a minimal custom LLM implementation:
    
    
    from crewai import BaseLLM
    from typing import Any, Dict, List, Optional, Union
    import requests
    
    class CustomLLM(BaseLLM):
        def __init__(self, model: str, api_key: str, endpoint: str, temperature: Optional[float] = None):
            # IMPORTANT: Call super().__init__() with required parameters
            super().__init__(model=model, temperature=temperature)
            
            self.api_key = api_key
            self.endpoint = endpoint
            
        def call(
            self,
            messages: Union[str, List[Dict[str, str]]],
            tools: Optional[List[dict]] = None,
            callbacks: Optional[List[Any]] = None,
            available_functions: Optional[Dict[str, Any]] = None,
        ) -> Union[str, Any]:
            """Call the LLM with the given messages."""
            # Convert string to message format if needed
            if isinstance(messages, str):
                messages = [{"role": "user", "content": messages}]
            
            # Prepare request
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
            }
            
            # Add tools if provided and supported
            if tools and self.supports_function_calling():
                payload["tools"] = tools
            
            # Make API call
            response = requests.post(
                self.endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        def supports_function_calling(self) -> bool:
            """Override if your LLM supports function calling."""
            return True  # Change to False if your LLM doesn't support tools
            
        def get_context_window_size(self) -> int:
            """Return the context window size of your LLM."""
            return 8192  # Adjust based on your model's actual context window

## 

​

Using Your Custom LLM
    
    
    from crewai import Agent, Task, Crew
    
    # Assuming you have the CustomLLM class defined above
    # Create your custom LLM
    custom_llm = CustomLLM(
        model="my-custom-model",
        api_key="your-api-key",
        endpoint="https://api.example.com/v1/chat/completions",
        temperature=0.7
    )
    
    # Use with an agent
    agent = Agent(
        role="Research Assistant",
        goal="Find and analyze information",
        backstory="You are a research assistant.",
        llm=custom_llm
    )
    
    # Create and execute tasks
    task = Task(
        description="Research the latest developments in AI",
        expected_output="A comprehensive summary",
        agent=agent
    )
    
    crew = Crew(agents=[agent], tasks=[task])
    result = crew.kickoff()

## 

​

Required Methods

### 

​

Constructor: `__init__()`

**Critical** : You must call `super().__init__(model, temperature)` with the required parameters:
    
    
    def __init__(self, model: str, api_key: str, temperature: Optional[float] = None):
        # REQUIRED: Call parent constructor with model and temperature
        super().__init__(model=model, temperature=temperature)
        
        # Your custom initialization
        self.api_key = api_key

### 

​

Abstract Method: `call()`

The `call()` method is the heart of your LLM implementation. It must:

  * Accept messages (string or list of dicts with ‘role’ and ‘content’)
  * Return a string response
  * Handle tools and function calling if supported
  * Raise appropriate exceptions for errors



### 

​

Optional Methods
    
    
    def supports_function_calling(self) -> bool:
        """Return True if your LLM supports function calling."""
        return True  # Default is True
    
    def supports_stop_words(self) -> bool:
        """Return True if your LLM supports stop sequences."""
        return True  # Default is True
    
    def get_context_window_size(self) -> int:
        """Return the context window size."""
        return 4096  # Default is 4096

## 

​

Common Patterns

### 

​

Error Handling
    
    
    import requests
    
    def call(self, messages, tools=None, callbacks=None, available_functions=None):
        try:
            response = requests.post(
                self.endpoint,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
            
        except requests.Timeout:
            raise TimeoutError("LLM request timed out")
        except requests.RequestException as e:
            raise RuntimeError(f"LLM request failed: {str(e)}")
        except (KeyError, IndexError) as e:
            raise ValueError(f"Invalid response format: {str(e)}")

### 

​

Custom Authentication
    
    
    from crewai import BaseLLM
    from typing import Optional
    
    class CustomAuthLLM(BaseLLM):
        def __init__(self, model: str, auth_token: str, endpoint: str, temperature: Optional[float] = None):
            super().__init__(model=model, temperature=temperature)
            self.auth_token = auth_token
            self.endpoint = endpoint
        
        def call(self, messages, tools=None, callbacks=None, available_functions=None):
            headers = {
                "Authorization": f"Custom {self.auth_token}",  # Custom auth format
                "Content-Type": "application/json"
            }
            # Rest of implementation...

### 

​

Stop Words Support

CrewAI automatically adds `"\nObservation:"` as a stop word to control agent behavior. If your LLM supports stop words:
    
    
    def call(self, messages, tools=None, callbacks=None, available_functions=None):
        payload = {
            "model": self.model,
            "messages": messages,
            "stop": self.stop  # Include stop words in API call
        }
        # Make API call...
    
    def supports_stop_words(self) -> bool:
        return True  # Your LLM supports stop sequences

If your LLM doesn’t support stop words natively:
    
    
    def call(self, messages, tools=None, callbacks=None, available_functions=None):
        response = self._make_api_call(messages, tools)
        content = response["choices"][0]["message"]["content"]
        
        # Manually truncate at stop words
        if self.stop:
            for stop_word in self.stop:
                if stop_word in content:
                    content = content.split(stop_word)[0]
                    break
        
        return content
    
    def supports_stop_words(self) -> bool:
        return False  # Tell CrewAI we handle stop words manually

## 

​

Function Calling

If your LLM supports function calling, implement the complete flow:
    
    
    import json
    
    def call(self, messages, tools=None, callbacks=None, available_functions=None):
        # Convert string to message format
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        # Make API call
        response = self._make_api_call(messages, tools)
        message = response["choices"][0]["message"]
        
        # Check for function calls
        if "tool_calls" in message and available_functions:
            return self._handle_function_calls(
                message["tool_calls"], messages, tools, available_functions
            )
        
        return message["content"]
    
    def _handle_function_calls(self, tool_calls, messages, tools, available_functions):
        """Handle function calling with proper message flow."""
        for tool_call in tool_calls:
            function_name = tool_call["function"]["name"]
            
            if function_name in available_functions:
                # Parse and execute function
                function_args = json.loads(tool_call["function"]["arguments"])
                function_result = available_functions[function_name](**function_args)
                
                # Add function call and result to message history
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call]
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": function_name,
                    "content": str(function_result)
                })
                
                # Call LLM again with updated context
                return self.call(messages, tools, None, available_functions)
        
        return "Function call failed"

## 

​

Troubleshooting

### 

​

Common Issues

**Constructor Errors**
    
    
    # ❌ Wrong - missing required parameters
    def __init__(self, api_key: str):
        super().__init__()
    
    # ✅ Correct
    def __init__(self, model: str, api_key: str, temperature: Optional[float] = None):
        super().__init__(model=model, temperature=temperature)

**Function Calling Not Working**

  * Ensure `supports_function_calling()` returns `True`
  * Check that you handle `tool_calls` in the response
  * Verify `available_functions` parameter is used correctly



**Authentication Failures**

  * Verify API key format and permissions
  * Check authentication header format
  * Ensure endpoint URLs are correct



**Response Parsing Errors**

  * Validate response structure before accessing nested fields
  * Handle cases where content might be None
  * Add proper error handling for malformed responses



## 

​

Testing Your Custom LLM
    
    
    from crewai import Agent, Task, Crew
    
    def test_custom_llm():
        llm = CustomLLM(
            model="test-model",
            api_key="test-key",
            endpoint="https://api.test.com"
        )
        
        # Test basic call
        result = llm.call("Hello, world!")
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Test with CrewAI agent
        agent = Agent(
            role="Test Agent",
            goal="Test custom LLM",
            backstory="A test agent.",
            llm=llm
        )
        
        task = Task(
            description="Say hello",
            expected_output="A greeting",
            agent=agent
        )
        
        crew = Crew(agents=[agent], tasks=[task])
        result = crew.kickoff()
        assert "hello" in result.raw.lower()

This guide covers the essentials of implementing custom LLMs in CrewAI.

Was this page helpful?

YesNo

[Create Custom Tools](/learn/create-custom-tools)[Custom Manager Agent](/learn/custom-manager-agent)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Overview
  * Quick Start
  * Using Your Custom LLM
  * Required Methods
  * Constructor: __init__()
  * Abstract Method: call()
  * Optional Methods
  * Common Patterns
  * Error Handling
  * Custom Authentication
  * Stop Words Support
  * Function Calling
  * Troubleshooting
  * Common Issues
  * Testing Your Custom LLM



Assistant

Responses are generated using AI and may contain mistakes.


---

### LLMs {#llms}

**Source:** [https://docs.crewai.com/concepts/llms](https://docs.crewai.com/concepts/llms)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Core Concepts

LLMs

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Core Concepts

# LLMs

Copy page

A comprehensive guide to configuring and using Large Language Models (LLMs) in your CrewAI projects

## 

​

Overview

CrewAI integrates with multiple LLM providers through LiteLLM, giving you the flexibility to choose the right model for your specific use case. This guide will help you understand how to configure and use different LLM providers in your CrewAI projects.

## 

​

What are LLMs?

Large Language Models (LLMs) are the core intelligence behind CrewAI agents. They enable agents to understand context, make decisions, and generate human-like responses. Here’s what you need to know:

## LLM Basics

Large Language Models are AI systems trained on vast amounts of text data. They power the intelligence of your CrewAI agents, enabling them to understand and generate human-like text.

## Context Window

The context window determines how much text an LLM can process at once. Larger windows (e.g., 128K tokens) allow for more context but may be more expensive and slower.

## Temperature

Temperature (0.0 to 1.0) controls response randomness. Lower values (e.g., 0.2) produce more focused, deterministic outputs, while higher values (e.g., 0.8) increase creativity and variability.

## Provider Selection

Each LLM provider (e.g., OpenAI, Anthropic, Google) offers different models with varying capabilities, pricing, and features. Choose based on your needs for accuracy, speed, and cost.

## 

​

Setting up your LLM

There are different places in CrewAI code where you can specify the model to use. Once you specify the model you are using, you will need to provide the configuration (like an API key) for each of the model providers you use. See the [provider configuration examples](/_sites/docs.crewai.com/concepts/llms#provider-configuration-examples) section for your provider.

  * 1\. Environment Variables
  * 2\. YAML Configuration
  * 3\. Direct Code



The simplest way to get started. Set the model in your environment directly, through an `.env` file or in your app code. If you used `crewai create` to bootstrap your project, it will be set already.

.env
    
    
    MODEL=model-id  # e.g. gpt-4o, gemini-2.0-flash, claude-3-sonnet-...
    
    # Be sure to set your API keys here too. See the Provider
    # section below.

Never commit API keys to version control. Use environment files (.env) or your system’s secret management.

The simplest way to get started. Set the model in your environment directly, through an `.env` file or in your app code. If you used `crewai create` to bootstrap your project, it will be set already.

.env
    
    
    MODEL=model-id  # e.g. gpt-4o, gemini-2.0-flash, claude-3-sonnet-...
    
    # Be sure to set your API keys here too. See the Provider
    # section below.

Never commit API keys to version control. Use environment files (.env) or your system’s secret management.

Create a YAML file to define your agent configurations. This method is great for version control and team collaboration:

agents.yaml
    
    
    researcher:
        role: Research Specialist
        goal: Conduct comprehensive research and analysis
        backstory: A dedicated research professional with years of experience
        verbose: true
        llm: provider/model-id  # e.g. openai/gpt-4o, google/gemini-2.0-flash, anthropic/claude...
        # (see provider configuration examples below for more)

The YAML configuration allows you to:

  * Version control your agent settings
  * Easily switch between different models
  * Share configurations across team members
  * Document model choices and their purposes



For maximum flexibility, configure LLMs directly in your Python code:
    
    
    from crewai import LLM
    
    # Basic configuration
    llm = LLM(model="model-id-here")  # gpt-4o, gemini-2.0-flash, anthropic/claude...
    
    # Advanced configuration with detailed parameters
    llm = LLM(
        model="model-id-here",  # gpt-4o, gemini-2.0-flash, anthropic/claude...
        temperature=0.7,        # Higher for more creative outputs
        timeout=120,            # Seconds to wait for response
        max_tokens=4000,        # Maximum length of response
        top_p=0.9,              # Nucleus sampling parameter
        frequency_penalty=0.1 , # Reduce repetition
        presence_penalty=0.1,   # Encourage topic diversity
        response_format={"type": "json"},  # For structured outputs
        seed=42                 # For reproducible results
    )

Parameter explanations:

  * `temperature`: Controls randomness (0.0-1.0)
  * `timeout`: Maximum wait time for response
  * `max_tokens`: Limits response length
  * `top_p`: Alternative to temperature for sampling
  * `frequency_penalty`: Reduces word repetition
  * `presence_penalty`: Encourages new topics
  * `response_format`: Specifies output structure
  * `seed`: Ensures consistent outputs



## 

​

Provider Configuration Examples

CrewAI supports a multitude of LLM providers, each offering unique features, authentication methods, and model capabilities. In this section, you’ll find detailed examples that help you select, configure, and optimize the LLM that best fits your project’s needs.

OpenAI

Set the following environment variables in your `.env` file:

Code
    
    
    # Required
    OPENAI_API_KEY=sk-...
    
    # Optional
    OPENAI_API_BASE=<custom-base-url>
    OPENAI_ORGANIZATION=<your-org-id>

Example usage in your CrewAI project:

Code
    
    
    from crewai import LLM
    
    llm = LLM(
        model="openai/gpt-4", # call model by provider/model_name
        temperature=0.8,
        max_tokens=150,
        top_p=0.9,
        frequency_penalty=0.1,
        presence_penalty=0.1,
        stop=["END"],
        seed=42
    )

OpenAI is one of the leading providers of LLMs with a wide range of models and features.

Model| Context Window| Best For  
---|---|---  
GPT-4| 8,192 tokens| High-accuracy tasks, complex reasoning  
GPT-4 Turbo| 128,000 tokens| Long-form content, document analysis  
GPT-4o & GPT-4o-mini| 128,000 tokens| Cost-effective large context processing  
o3-mini| 200,000 tokens| Fast reasoning, complex reasoning  
o1-mini| 128,000 tokens| Fast reasoning, complex reasoning  
o1-preview| 128,000 tokens| Fast reasoning, complex reasoning  
o1| 200,000 tokens| Fast reasoning, complex reasoning  
  
Meta-Llama

Meta’s Llama API provides access to Meta’s family of large language models. The API is available through the [Meta Llama API](https://llama.developer.meta.com?utm_source=partner-crewai&utm_medium=website). Set the following environment variables in your `.env` file:

Code
    
    
    # Meta Llama API Key Configuration
    LLAMA_API_KEY=LLM|your_api_key_here

Example usage in your CrewAI project:

Code
    
    
    from crewai import LLM
    
    # Initialize Meta Llama LLM
    llm = LLM(
        model="meta_llama/Llama-4-Scout-17B-16E-Instruct-FP8",
        temperature=0.8,
        stop=["END"],
        seed=42
    )

All models listed here <https://llama.developer.meta.com/docs/models/> are supported.

Model ID| Input context length| Output context length| Input Modalities| Output Modalities  
---|---|---|---|---  
`meta_llama/Llama-4-Scout-17B-16E-Instruct-FP8`| 128k| 4028| Text, Image| Text  
`meta_llama/Llama-4-Maverick-17B-128E-Instruct-FP8`| 128k| 4028| Text, Image| Text  
`meta_llama/Llama-3.3-70B-Instruct`| 128k| 4028| Text| Text  
`meta_llama/Llama-3.3-8B-Instruct`| 128k| 4028| Text| Text  
  
Anthropic

Code
    
    
    # Required
    ANTHROPIC_API_KEY=sk-ant-...
    
    # Optional
    ANTHROPIC_API_BASE=<custom-base-url>

Example usage in your CrewAI project:

Code
    
    
    llm = LLM(
        model="anthropic/claude-3-sonnet-20240229-v1:0",
        temperature=0.7
    )

Google (Gemini API)

Set your API key in your `.env` file. If you need a key, or need to find an existing key, check [AI Studio](https://aistudio.google.com/apikey).

.env
    
    
    # https://ai.google.dev/gemini-api/docs/api-key
    GEMINI_API_KEY=<your-api-key>

Example usage in your CrewAI project:

Code
    
    
    from crewai import LLM
    
    llm = LLM(
        model="gemini/gemini-2.0-flash",
        temperature=0.7,
    )

### 

​

Gemini models

Google offers a range of powerful models optimized for different use cases.

Model| Context Window| Best For  
---|---|---  
gemini-2.5-flash-preview-04-17| 1M tokens| Adaptive thinking, cost efficiency  
gemini-2.5-pro-preview-05-06| 1M tokens| Enhanced thinking and reasoning, multimodal understanding, advanced coding, and more  
gemini-2.0-flash| 1M tokens| Next generation features, speed, thinking, and realtime streaming  
gemini-2.0-flash-lite| 1M tokens| Cost efficiency and low latency  
gemini-1.5-flash| 1M tokens| Balanced multimodal model, good for most tasks  
gemini-1.5-flash-8B| 1M tokens| Fastest, most cost-efficient, good for high-frequency tasks  
gemini-1.5-pro| 2M tokens| Best performing, wide variety of reasoning tasks including logical reasoning, coding, and creative collaboration  
  
The full list of models is available in the [Gemini model docs](https://ai.google.dev/gemini-api/docs/models).

### 

​

Gemma

The Gemini API also allows you to use your API key to access [Gemma models](https://ai.google.dev/gemma/docs) hosted on Google infrastructure.

Model| Context Window  
---|---  
gemma-3-1b-it| 32k tokens  
gemma-3-4b-it| 32k tokens  
gemma-3-12b-it| 32k tokens  
gemma-3-27b-it| 128k tokens  
  
Google (Vertex AI)

Get credentials from your Google Cloud Console and save it to a JSON file, then load it with the following code:

Code
    
    
    import json
    
    file_path = 'path/to/vertex_ai_service_account.json'
    
    # Load the JSON file
    with open(file_path, 'r') as file:
        vertex_credentials = json.load(file)
    
    # Convert the credentials to a JSON string
    vertex_credentials_json = json.dumps(vertex_credentials)

Example usage in your CrewAI project:

Code
    
    
    from crewai import LLM
    
    llm = LLM(
        model="gemini/gemini-1.5-pro-latest",
        temperature=0.7,
        vertex_credentials=vertex_credentials_json
    )

Google offers a range of powerful models optimized for different use cases:

Model| Context Window| Best For  
---|---|---  
gemini-2.5-flash-preview-04-17| 1M tokens| Adaptive thinking, cost efficiency  
gemini-2.5-pro-preview-05-06| 1M tokens| Enhanced thinking and reasoning, multimodal understanding, advanced coding, and more  
gemini-2.0-flash| 1M tokens| Next generation features, speed, thinking, and realtime streaming  
gemini-2.0-flash-lite| 1M tokens| Cost efficiency and low latency  
gemini-1.5-flash| 1M tokens| Balanced multimodal model, good for most tasks  
gemini-1.5-flash-8B| 1M tokens| Fastest, most cost-efficient, good for high-frequency tasks  
gemini-1.5-pro| 2M tokens| Best performing, wide variety of reasoning tasks including logical reasoning, coding, and creative collaboration  
  
Azure

Code
    
    
    # Required
    AZURE_API_KEY=<your-api-key>
    AZURE_API_BASE=<your-resource-url>
    AZURE_API_VERSION=<api-version>
    
    # Optional
    AZURE_AD_TOKEN=<your-azure-ad-token>
    AZURE_API_TYPE=<your-azure-api-type>

Example usage in your CrewAI project:

Code
    
    
    llm = LLM(
        model="azure/gpt-4",
        api_version="2023-05-15"
    )

AWS Bedrock

Code
    
    
    AWS_ACCESS_KEY_ID=<your-access-key>
    AWS_SECRET_ACCESS_KEY=<your-secret-key>
    AWS_DEFAULT_REGION=<your-region>

Example usage in your CrewAI project:

Code
    
    
    llm = LLM(
        model="bedrock/anthropic.claude-3-sonnet-20240229-v1:0"
    )

Before using Amazon Bedrock, make sure you have boto3 installed in your environment

[Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html) is a managed service that provides access to multiple foundation models from top AI companies through a unified API, enabling secure and responsible AI application development.

Model| Context Window| Best For  
---|---|---  
Amazon Nova Pro| Up to 300k tokens| High-performance, model balancing accuracy, speed, and cost-effectiveness across diverse tasks.  
Amazon Nova Micro| Up to 128k tokens| High-performance, cost-effective text-only model optimized for lowest latency responses.  
Amazon Nova Lite| Up to 300k tokens| High-performance, affordable multimodal processing for images, video, and text with real-time capabilities.  
Claude 3.7 Sonnet| Up to 128k tokens| High-performance, best for complex reasoning, coding & AI agents  
Claude 3.5 Sonnet v2| Up to 200k tokens| State-of-the-art model specialized in software engineering, agentic capabilities, and computer interaction at optimized cost.  
Claude 3.5 Sonnet| Up to 200k tokens| High-performance model delivering superior intelligence and reasoning across diverse tasks with optimal speed-cost balance.  
Claude 3.5 Haiku| Up to 200k tokens| Fast, compact multimodal model optimized for quick responses and seamless human-like interactions  
Claude 3 Sonnet| Up to 200k tokens| Multimodal model balancing intelligence and speed for high-volume deployments.  
Claude 3 Haiku| Up to 200k tokens| Compact, high-speed multimodal model optimized for quick responses and natural conversational interactions  
Claude 3 Opus| Up to 200k tokens| Most advanced multimodal model exceling at complex tasks with human-like reasoning and superior contextual understanding.  
Claude 2.1| Up to 200k tokens| Enhanced version with expanded context window, improved reliability, and reduced hallucinations for long-form and RAG applications  
Claude| Up to 100k tokens| Versatile model excelling in sophisticated dialogue, creative content, and precise instruction following.  
Claude Instant| Up to 100k tokens| Fast, cost-effective model for everyday tasks like dialogue, analysis, summarization, and document Q&A  
Llama 3.1 405B Instruct| Up to 128k tokens| Advanced LLM for synthetic data generation, distillation, and inference for chatbots, coding, and domain-specific tasks.  
Llama 3.1 70B Instruct| Up to 128k tokens| Powers complex conversations with superior contextual understanding, reasoning and text generation.  
Llama 3.1 8B Instruct| Up to 128k tokens| Advanced state-of-the-art model with language understanding, superior reasoning, and text generation.  
Llama 3 70B Instruct| Up to 8k tokens| Powers complex conversations with superior contextual understanding, reasoning and text generation.  
Llama 3 8B Instruct| Up to 8k tokens| Advanced state-of-the-art LLM with language understanding, superior reasoning, and text generation.  
Titan Text G1 - Lite| Up to 4k tokens| Lightweight, cost-effective model optimized for English tasks and fine-tuning with focus on summarization and content generation.  
Titan Text G1 - Express| Up to 8k tokens| Versatile model for general language tasks, chat, and RAG applications with support for English and 100+ languages.  
Cohere Command| Up to 4k tokens| Model specialized in following user commands and delivering practical enterprise solutions.  
Jurassic-2 Mid| Up to 8,191 tokens| Cost-effective model balancing quality and affordability for diverse language tasks like Q&A, summarization, and content generation.  
Jurassic-2 Ultra| Up to 8,191 tokens| Model for advanced text generation and comprehension, excelling in complex tasks like analysis and content creation.  
Jamba-Instruct| Up to 256k tokens| Model with extended context window optimized for cost-effective text generation, summarization, and Q&A.  
Mistral 7B Instruct| Up to 32k tokens| This LLM follows instructions, completes requests, and generates creative text.  
Mistral 8x7B Instruct| Up to 32k tokens| An MOE LLM that follows instructions, completes requests, and generates creative text.  
  
Amazon SageMaker

Code
    
    
    AWS_ACCESS_KEY_ID=<your-access-key>
    AWS_SECRET_ACCESS_KEY=<your-secret-key>
    AWS_DEFAULT_REGION=<your-region>

Example usage in your CrewAI project:

Code
    
    
    llm = LLM(
        model="sagemaker/<my-endpoint>"
    )

Mistral

Set the following environment variables in your `.env` file:

Code
    
    
    MISTRAL_API_KEY=<your-api-key>

Example usage in your CrewAI project:

Code
    
    
    llm = LLM(
        model="mistral/mistral-large-latest",
        temperature=0.7
    )

Nvidia NIM

Set the following environment variables in your `.env` file:

Code
    
    
    NVIDIA_API_KEY=<your-api-key>

Example usage in your CrewAI project:

Code
    
    
    llm = LLM(
        model="nvidia_nim/meta/llama3-70b-instruct",
        temperature=0.7
    )

Nvidia NIM provides a comprehensive suite of models for various use cases, from general-purpose tasks to specialized applications.

Model| Context Window| Best For  
---|---|---  
nvidia/mistral-nemo-minitron-8b-8k-instruct| 8,192 tokens| State-of-the-art small language model delivering superior accuracy for chatbot, virtual assistants, and content generation.  
nvidia/nemotron-4-mini-hindi-4b-instruct| 4,096 tokens| A bilingual Hindi-English SLM for on-device inference, tailored specifically for Hindi Language.  
nvidia/llama-3.1-nemotron-70b-instruct| 128k tokens| Customized for enhanced helpfulness in responses  
nvidia/llama3-chatqa-1.5-8b| 128k tokens| Advanced LLM to generate high-quality, context-aware responses for chatbots and search engines.  
nvidia/llama3-chatqa-1.5-70b| 128k tokens| Advanced LLM to generate high-quality, context-aware responses for chatbots and search engines.  
nvidia/vila| 128k tokens| Multi-modal vision-language model that understands text/img/video and creates informative responses  
nvidia/neva-22| 4,096 tokens| Multi-modal vision-language model that understands text/images and generates informative responses  
nvidia/nemotron-mini-4b-instruct| 8,192 tokens| General-purpose tasks  
nvidia/usdcode-llama3-70b-instruct| 128k tokens| State-of-the-art LLM that answers OpenUSD knowledge queries and generates USD-Python code.  
nvidia/nemotron-4-340b-instruct| 4,096 tokens| Creates diverse synthetic data that mimics the characteristics of real-world data.  
meta/codellama-70b| 100k tokens| LLM capable of generating code from natural language and vice versa.  
meta/llama2-70b| 4,096 tokens| Cutting-edge large language AI model capable of generating text and code in response to prompts.  
meta/llama3-8b-instruct| 8,192 tokens| Advanced state-of-the-art LLM with language understanding, superior reasoning, and text generation.  
meta/llama3-70b-instruct| 8,192 tokens| Powers complex conversations with superior contextual understanding, reasoning and text generation.  
meta/llama-3.1-8b-instruct| 128k tokens| Advanced state-of-the-art model with language understanding, superior reasoning, and text generation.  
meta/llama-3.1-70b-instruct| 128k tokens| Powers complex conversations with superior contextual understanding, reasoning and text generation.  
meta/llama-3.1-405b-instruct| 128k tokens| Advanced LLM for synthetic data generation, distillation, and inference for chatbots, coding, and domain-specific tasks.  
meta/llama-3.2-1b-instruct| 128k tokens| Advanced state-of-the-art small language model with language understanding, superior reasoning, and text generation.  
meta/llama-3.2-3b-instruct| 128k tokens| Advanced state-of-the-art small language model with language understanding, superior reasoning, and text generation.  
meta/llama-3.2-11b-vision-instruct| 128k tokens| Advanced state-of-the-art small language model with language understanding, superior reasoning, and text generation.  
meta/llama-3.2-90b-vision-instruct| 128k tokens| Advanced state-of-the-art small language model with language understanding, superior reasoning, and text generation.  
google/gemma-7b| 8,192 tokens| Cutting-edge text generation model text understanding, transformation, and code generation.  
google/gemma-2b| 8,192 tokens| Cutting-edge text generation model text understanding, transformation, and code generation.  
google/codegemma-7b| 8,192 tokens| Cutting-edge model built on Google’s Gemma-7B specialized for code generation and code completion.  
google/codegemma-1.1-7b| 8,192 tokens| Advanced programming model for code generation, completion, reasoning, and instruction following.  
google/recurrentgemma-2b| 8,192 tokens| Novel recurrent architecture based language model for faster inference when generating long sequences.  
google/gemma-2-9b-it| 8,192 tokens| Cutting-edge text generation model text understanding, transformation, and code generation.  
google/gemma-2-27b-it| 8,192 tokens| Cutting-edge text generation model text understanding, transformation, and code generation.  
google/gemma-2-2b-it| 8,192 tokens| Cutting-edge text generation model text understanding, transformation, and code generation.  
google/deplot| 512 tokens| One-shot visual language understanding model that translates images of plots into tables.  
google/paligemma| 8,192 tokens| Vision language model adept at comprehending text and visual inputs to produce informative responses.  
mistralai/mistral-7b-instruct-v0.2| 32k tokens| This LLM follows instructions, completes requests, and generates creative text.  
mistralai/mixtral-8x7b-instruct-v0.1| 8,192 tokens| An MOE LLM that follows instructions, completes requests, and generates creative text.  
mistralai/mistral-large| 4,096 tokens| Creates diverse synthetic data that mimics the characteristics of real-world data.  
mistralai/mixtral-8x22b-instruct-v0.1| 8,192 tokens| Creates diverse synthetic data that mimics the characteristics of real-world data.  
mistralai/mistral-7b-instruct-v0.3| 32k tokens| This LLM follows instructions, completes requests, and generates creative text.  
nv-mistralai/mistral-nemo-12b-instruct| 128k tokens| Most advanced language model for reasoning, code, multilingual tasks; runs on a single GPU.  
mistralai/mamba-codestral-7b-v0.1| 256k tokens| Model for writing and interacting with code across a wide range of programming languages and tasks.  
microsoft/phi-3-mini-128k-instruct| 128K tokens| Lightweight, state-of-the-art open LLM with strong math and logical reasoning skills.  
microsoft/phi-3-mini-4k-instruct| 4,096 tokens| Lightweight, state-of-the-art open LLM with strong math and logical reasoning skills.  
microsoft/phi-3-small-8k-instruct| 8,192 tokens| Lightweight, state-of-the-art open LLM with strong math and logical reasoning skills.  
microsoft/phi-3-small-128k-instruct| 128K tokens| Lightweight, state-of-the-art open LLM with strong math and logical reasoning skills.  
microsoft/phi-3-medium-4k-instruct| 4,096 tokens| Lightweight, state-of-the-art open LLM with strong math and logical reasoning skills.  
microsoft/phi-3-medium-128k-instruct| 128K tokens| Lightweight, state-of-the-art open LLM with strong math and logical reasoning skills.  
microsoft/phi-3.5-mini-instruct| 128K tokens| Lightweight multilingual LLM powering AI applications in latency bound, memory/compute constrained environments  
microsoft/phi-3.5-moe-instruct| 128K tokens| Advanced LLM based on Mixture of Experts architecture to deliver compute efficient content generation  
microsoft/kosmos-2| 1,024 tokens| Groundbreaking multimodal model designed to understand and reason about visual elements in images.  
microsoft/phi-3-vision-128k-instruct| 128k tokens| Cutting-edge open multimodal model exceling in high-quality reasoning from images.  
microsoft/phi-3.5-vision-instruct| 128k tokens| Cutting-edge open multimodal model exceling in high-quality reasoning from images.  
databricks/dbrx-instruct| 12k tokens| A general-purpose LLM with state-of-the-art performance in language understanding, coding, and RAG.  
snowflake/arctic| 1,024 tokens| Delivers high efficiency inference for enterprise applications focused on SQL generation and coding.  
aisingapore/sea-lion-7b-instruct| 4,096 tokens| LLM to represent and serve the linguistic and cultural diversity of Southeast Asia  
ibm/granite-8b-code-instruct| 4,096 tokens| Software programming LLM for code generation, completion, explanation, and multi-turn conversion.  
ibm/granite-34b-code-instruct| 8,192 tokens| Software programming LLM for code generation, completion, explanation, and multi-turn conversion.  
ibm/granite-3.0-8b-instruct| 4,096 tokens| Advanced Small Language Model supporting RAG, summarization, classification, code, and agentic AI  
ibm/granite-3.0-3b-a800m-instruct| 4,096 tokens| Highly efficient Mixture of Experts model for RAG, summarization, entity extraction, and classification  
mediatek/breeze-7b-instruct| 4,096 tokens| Creates diverse synthetic data that mimics the characteristics of real-world data.  
upstage/solar-10.7b-instruct| 4,096 tokens| Excels in NLP tasks, particularly in instruction-following, reasoning, and mathematics.  
writer/palmyra-med-70b-32k| 32k tokens| Leading LLM for accurate, contextually relevant responses in the medical domain.  
writer/palmyra-med-70b| 32k tokens| Leading LLM for accurate, contextually relevant responses in the medical domain.  
writer/palmyra-fin-70b-32k| 32k tokens| Specialized LLM for financial analysis, reporting, and data processing  
01-ai/yi-large| 32k tokens| Powerful model trained on English and Chinese for diverse tasks including chatbot and creative writing.  
deepseek-ai/deepseek-coder-6.7b-instruct| 2k tokens| Powerful coding model offering advanced capabilities in code generation, completion, and infilling  
rakuten/rakutenai-7b-instruct| 1,024 tokens| Advanced state-of-the-art LLM with language understanding, superior reasoning, and text generation.  
rakuten/rakutenai-7b-chat| 1,024 tokens| Advanced state-of-the-art LLM with language understanding, superior reasoning, and text generation.  
baichuan-inc/baichuan2-13b-chat| 4,096 tokens| Support Chinese and English chat, coding, math, instruction following, solving quizzes  
  
Local NVIDIA NIM Deployed using WSL2

NVIDIA NIM enables you to run powerful LLMs locally on your Windows machine using WSL2 (Windows Subsystem for Linux). This approach allows you to leverage your NVIDIA GPU for private, secure, and cost-effective AI inference without relying on cloud services. Perfect for development, testing, or production scenarios where data privacy or offline capabilities are required.

Here is a step-by-step guide to setting up a local NVIDIA NIM model:

  1. Follow installation instructions from [NVIDIA Website](https://docs.nvidia.com/nim/wsl2/latest/getting-started.html)

  2. Install the local model. For Llama 3.1-8b follow [instructions](https://build.nvidia.com/meta/llama-3_1-8b-instruct/deploy)

  3. Configure your crewai local models:




Code
    
    
    from crewai.llm import LLM
    
    local_nvidia_nim_llm = LLM(
        model="openai/meta/llama-3.1-8b-instruct", # it's an openai-api compatible model
        base_url="http://localhost:8000/v1",
        api_key="<your_api_key|any text if you have not configured it>", # api_key is required, but you can use any text
    )
    
    # Then you can use it in your crew:
    
    @CrewBase
    class MyCrew():
        # ...
    
        @agent
        def researcher(self) -> Agent:
            return Agent(
                config=self.agents_config['researcher'], # type: ignore[index]
                llm=local_nvidia_nim_llm
            )
    
        # ...

Groq

Set the following environment variables in your `.env` file:

Code
    
    
    GROQ_API_KEY=<your-api-key>

Example usage in your CrewAI project:

Code
    
    
    llm = LLM(
        model="groq/llama-3.2-90b-text-preview",
        temperature=0.7
    )

Model| Context Window| Best For  
---|---|---  
Llama 3.1 70B/8B| 131,072 tokens| High-performance, large context tasks  
Llama 3.2 Series| 8,192 tokens| General-purpose tasks  
Mixtral 8x7B| 32,768 tokens| Balanced performance and context  
  
IBM watsonx.ai

Set the following environment variables in your `.env` file:

Code
    
    
    # Required
    WATSONX_URL=<your-url>
    WATSONX_APIKEY=<your-apikey>
    WATSONX_PROJECT_ID=<your-project-id>
    
    # Optional
    WATSONX_TOKEN=<your-token>
    WATSONX_DEPLOYMENT_SPACE_ID=<your-space-id>

Example usage in your CrewAI project:

Code
    
    
    llm = LLM(
        model="watsonx/meta-llama/llama-3-1-70b-instruct",
        base_url="https://api.watsonx.ai/v1"
    )

Ollama (Local LLMs)

  1. Install Ollama: [ollama.ai](https://ollama.ai/)
  2. Run a model: `ollama run llama3`
  3. Configure:



Code
    
    
    llm = LLM(
        model="ollama/llama3:70b",
        base_url="http://localhost:11434"
    )

Fireworks AI

Set the following environment variables in your `.env` file:

Code
    
    
    FIREWORKS_API_KEY=<your-api-key>

Example usage in your CrewAI project:

Code
    
    
    llm = LLM(
        model="fireworks_ai/accounts/fireworks/models/llama-v3-70b-instruct",
        temperature=0.7
    )

Perplexity AI

Set the following environment variables in your `.env` file:

Code
    
    
    PERPLEXITY_API_KEY=<your-api-key>

Example usage in your CrewAI project:

Code
    
    
    llm = LLM(
        model="llama-3.1-sonar-large-128k-online",
        base_url="https://api.perplexity.ai/"
    )

Hugging Face

Set the following environment variables in your `.env` file:

Code
    
    
    HF_TOKEN=<your-api-key>

Example usage in your CrewAI project:

Code
    
    
    llm = LLM(
        model="huggingface/meta-llama/Meta-Llama-3.1-8B-Instruct"
    )

SambaNova

Set the following environment variables in your `.env` file:

Code
    
    
    SAMBANOVA_API_KEY=<your-api-key>

Example usage in your CrewAI project:

Code
    
    
    llm = LLM(
        model="sambanova/Meta-Llama-3.1-8B-Instruct",
        temperature=0.7
    )

Model| Context Window| Best For  
---|---|---  
Llama 3.1 70B/8B| Up to 131,072 tokens| High-performance, large context tasks  
Llama 3.1 405B| 8,192 tokens| High-performance and output quality  
Llama 3.2 Series| 8,192 tokens| General-purpose, multimodal tasks  
Llama 3.3 70B| Up to 131,072 tokens| High-performance and output quality  
Qwen2 familly| 8,192 tokens| High-performance and output quality  
  
Cerebras

Set the following environment variables in your `.env` file:

Code
    
    
    # Required
    CEREBRAS_API_KEY=<your-api-key>

Example usage in your CrewAI project:

Code
    
    
    llm = LLM(
        model="cerebras/llama3.1-70b",
        temperature=0.7,
        max_tokens=8192
    )

Cerebras features:

  * Fast inference speeds
  * Competitive pricing
  * Good balance of speed and quality
  * Support for long context windows



Open Router

Set the following environment variables in your `.env` file:

Code
    
    
    OPENROUTER_API_KEY=<your-api-key>

Example usage in your CrewAI project:

Code
    
    
    llm = LLM(
        model="openrouter/deepseek/deepseek-r1",
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY
    )

Open Router models:

  * openrouter/deepseek/deepseek-r1
  * openrouter/deepseek/deepseek-chat



## 

​

Streaming Responses

CrewAI supports streaming responses from LLMs, allowing your application to receive and process outputs in real-time as they’re generated.

  * Basic Setup
  * Event Handling



Enable streaming by setting the `stream` parameter to `True` when initializing your LLM:
    
    
    from crewai import LLM
    
    # Create an LLM with streaming enabled
    llm = LLM(
        model="openai/gpt-4o",
        stream=True  # Enable streaming
    )

When streaming is enabled, responses are delivered in chunks as they’re generated, creating a more responsive user experience.

Enable streaming by setting the `stream` parameter to `True` when initializing your LLM:
    
    
    from crewai import LLM
    
    # Create an LLM with streaming enabled
    llm = LLM(
        model="openai/gpt-4o",
        stream=True  # Enable streaming
    )

When streaming is enabled, responses are delivered in chunks as they’re generated, creating a more responsive user experience.

CrewAI emits events for each chunk received during streaming:
    
    
    from crewai.utilities.events import (
      LLMStreamChunkEvent
    )
    from crewai.utilities.events.base_event_listener import BaseEventListener
    
    class MyCustomListener(BaseEventListener):
        def setup_listeners(self, crewai_event_bus):
            @crewai_event_bus.on(LLMStreamChunkEvent)
            def on_llm_stream_chunk(self, event: LLMStreamChunkEvent):
              # Process each chunk as it arrives
              print(f"Received chunk: {event.chunk}")
    
    my_listener = MyCustomListener()

[Click here](https://docs.crewai.com/concepts/event-listener#event-listeners) for more details

## 

​

Structured LLM Calls

CrewAI supports structured responses from LLM calls by allowing you to define a `response_format` using a Pydantic model. This enables the framework to automatically parse and validate the output, making it easier to integrate the response into your application without manual post-processing.

For example, you can define a Pydantic model to represent the expected response structure and pass it as the `response_format` when instantiating the LLM. The model will then be used to convert the LLM output into a structured Python object.

Code
    
    
    from crewai import LLM
    
    class Dog(BaseModel):
        name: str
        age: int
        breed: str
    
    
    llm = LLM(model="gpt-4o", response_format=Dog)
    
    response = llm.call(
        "Analyze the following messages and return the name, age, and breed. "
        "Meet Kona! She is 3 years old and is a black german shepherd."
    )
    print(response)
    
    # Output:
    # Dog(name='Kona', age=3, breed='black german shepherd')

## 

​

Advanced Features and Optimization

Learn how to get the most out of your LLM configuration:

Context Window Management

CrewAI includes smart context management features:
    
    
    from crewai import LLM
    
    # CrewAI automatically handles:
    # 1. Token counting and tracking
    # 2. Content summarization when needed
    # 3. Task splitting for large contexts
    
    llm = LLM(
        model="gpt-4",
        max_tokens=4000,  # Limit response length
    )

Best practices for context management:

  1. Choose models with appropriate context windows
  2. Pre-process long inputs when possible
  3. Use chunking for large documents
  4. Monitor token usage to optimize costs



Performance Optimization

1

Token Usage Optimization

Choose the right context window for your task:

  * Small tasks (up to 4K tokens): Standard models
  * Medium tasks (between 4K-32K): Enhanced models
  * Large tasks (over 32K): Large context models


    
    
    # Configure model with appropriate settings
    llm = LLM(
        model="openai/gpt-4-turbo-preview",
        temperature=0.7,    # Adjust based on task
        max_tokens=4096,    # Set based on output needs
        timeout=300        # Longer timeout for complex tasks
    )

  * Lower temperature (0.1 to 0.3) for factual responses
  * Higher temperature (0.7 to 0.9) for creative tasks



2

Best Practices

  1. Monitor token usage
  2. Implement rate limiting
  3. Use caching when possible
  4. Set appropriate max_tokens limits



Remember to regularly monitor your token usage and adjust your configuration as needed to optimize costs and performance.

Drop Additional Parameters

CrewAI internally uses Litellm for LLM calls, which allows you to drop additional parameters that are not needed for your specific use case. This can help simplify your code and reduce the complexity of your LLM configuration. For example, if you don’t need to send the `stop` parameter, you can simply omit it from your LLM call:
    
    
    from crewai import LLM
    import os
    
    os.environ["OPENAI_API_KEY"] = "<api-key>"
    
    o3_llm = LLM(
        model="o3",
        drop_params=True,
        additional_drop_params=["stop"]
    )

## 

​

Common Issues and Solutions

  * Authentication
  * Model Names
  * Context Length



Most authentication issues can be resolved by checking API key format and environment variable names.
    
    
    # OpenAI
    OPENAI_API_KEY=sk-...
    
    # Anthropic
    ANTHROPIC_API_KEY=sk-ant-...

Most authentication issues can be resolved by checking API key format and environment variable names.
    
    
    # OpenAI
    OPENAI_API_KEY=sk-...
    
    # Anthropic
    ANTHROPIC_API_KEY=sk-ant-...

Always include the provider prefix in model names
    
    
    # Correct
    llm = LLM(model="openai/gpt-4")
    
    # Incorrect
    llm = LLM(model="gpt-4")

Use larger context models for extensive tasks
    
    
    # Large context model
    llm = LLM(model="openai/gpt-4o")  # 128K tokens

Was this page helpful?

YesNo

[Knowledge](/concepts/knowledge)[Processes](/concepts/processes)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Overview
  * What are LLMs?
  * Setting up your LLM
  * Provider Configuration Examples
  * Streaming Responses
  * Structured LLM Calls
  * Advanced Features and Optimization
  * Common Issues and Solutions



Assistant

Responses are generated using AI and may contain mistakes.


---

### Connect to any LLM {#connect-to-any-llm}

**Source:** [https://docs.crewai.com/learn/llm-connections](https://docs.crewai.com/learn/llm-connections)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Learn

Connect to any LLM

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Learn

# Connect to any LLM

Copy page

Comprehensive guide on integrating CrewAI with various Large Language Models (LLMs) using LiteLLM, including supported providers and configuration options.

## 

​

Connect CrewAI to LLMs

CrewAI uses LiteLLM to connect to a wide variety of Language Models (LLMs). This integration provides extensive versatility, allowing you to use models from numerous providers with a simple, unified interface.

By default, CrewAI uses the `gpt-4o-mini` model. This is determined by the `OPENAI_MODEL_NAME` environment variable, which defaults to “gpt-4o-mini” if not set. You can easily configure your agents to use a different model or provider as described in this guide.

## 

​

Supported Providers

LiteLLM supports a wide range of providers, including but not limited to:

  * OpenAI
  * Anthropic
  * Google (Vertex AI, Gemini)
  * Azure OpenAI
  * AWS (Bedrock, SageMaker)
  * Cohere
  * VoyageAI
  * Hugging Face
  * Ollama
  * Mistral AI
  * Replicate
  * Together AI
  * AI21
  * Cloudflare Workers AI
  * DeepInfra
  * Groq
  * SambaNova
  * [NVIDIA NIMs](https://docs.api.nvidia.com/nim/reference/models-1)
  * And many more!



For a complete and up-to-date list of supported providers, please refer to the [LiteLLM Providers documentation](https://docs.litellm.ai/docs/providers).

## 

​

Changing the LLM

To use a different LLM with your CrewAI agents, you have several options:

  * Using a String Identifier
  * Using the LLM Class



Pass the model name as a string when initializing the agent:

Code
    
    
    from crewai import Agent
    
    # Using OpenAI's GPT-4
    openai_agent = Agent(
        role='OpenAI Expert',
        goal='Provide insights using GPT-4',
        backstory="An AI assistant powered by OpenAI's latest model.",
        llm='gpt-4'
    )
    
    # Using Anthropic's Claude
    claude_agent = Agent(
        role='Anthropic Expert',
        goal='Analyze data using Claude',
        backstory="An AI assistant leveraging Anthropic's language model.",
        llm='claude-2'
    )

Pass the model name as a string when initializing the agent:

Code
    
    
    from crewai import Agent
    
    # Using OpenAI's GPT-4
    openai_agent = Agent(
        role='OpenAI Expert',
        goal='Provide insights using GPT-4',
        backstory="An AI assistant powered by OpenAI's latest model.",
        llm='gpt-4'
    )
    
    # Using Anthropic's Claude
    claude_agent = Agent(
        role='Anthropic Expert',
        goal='Analyze data using Claude',
        backstory="An AI assistant leveraging Anthropic's language model.",
        llm='claude-2'
    )

For more detailed configuration, use the LLM class:

Code
    
    
    from crewai import Agent, LLM
    
    llm = LLM(
        model="gpt-4",
        temperature=0.7,
        base_url="https://api.openai.com/v1",
        api_key="your-api-key-here"
    )
    
    agent = Agent(
        role='Customized LLM Expert',
        goal='Provide tailored responses',
        backstory="An AI assistant with custom LLM settings.",
        llm=llm
    )

## 

​

Configuration Options

When configuring an LLM for your agent, you have access to a wide range of parameters:

Parameter| Type| Description  
---|---|---  
**model**| `str`| The name of the model to use (e.g., “gpt-4”, “claude-2”)  
**temperature**| `float`| Controls randomness in output (0.0 to 1.0)  
**max_tokens**| `int`| Maximum number of tokens to generate  
**top_p**| `float`| Controls diversity of output (0.0 to 1.0)  
**frequency_penalty**| `float`| Penalizes new tokens based on their frequency in the text so far  
**presence_penalty**| `float`| Penalizes new tokens based on their presence in the text so far  
**stop**| `str`, `List[str]`| Sequence(s) to stop generation  
**base_url**| `str`| The base URL for the API endpoint  
**api_key**| `str`| Your API key for authentication  
  
For a complete list of parameters and their descriptions, refer to the LLM class documentation.

## 

​

Connecting to OpenAI-Compatible LLMs

You can connect to OpenAI-compatible LLMs using either environment variables or by setting specific attributes on the LLM class:

  * Using Environment Variables
  * Using LLM Class Attributes



Generic

Google
    
    
    import os
    
    os.environ["OPENAI_API_KEY"] = "your-api-key"
    os.environ["OPENAI_API_BASE"] = "https://api.your-provider.com/v1"
    os.environ["OPENAI_MODEL_NAME"] = "your-model-name"

Generic

Google
    
    
    import os
    
    os.environ["OPENAI_API_KEY"] = "your-api-key"
    os.environ["OPENAI_API_BASE"] = "https://api.your-provider.com/v1"
    os.environ["OPENAI_MODEL_NAME"] = "your-model-name"

Generic

Google
    
    
    llm = LLM(
        model="custom-model-name",
        api_key="your-api-key",
        base_url="https://api.your-provider.com/v1"
    )
    agent = Agent(llm=llm, ...)

## 

​

Using Local Models with Ollama

For local models like those provided by Ollama:

1

Download and install Ollama

[Click here to download and install Ollama](https://ollama.com/download)

2

Pull the desired model

For example, run `ollama pull llama3.2` to download the model.

3

Configure your agent

Code
    
    
    agent = Agent(
            role='Local AI Expert',
            goal='Process information using a local model',
            backstory="An AI assistant running on local hardware.",
            llm=LLM(model="ollama/llama3.2", base_url="http://localhost:11434")
        )

## 

​

Changing the Base API URL

You can change the base API URL for any LLM provider by setting the `base_url` parameter:

Code
    
    
    llm = LLM(
        model="custom-model-name",
        base_url="https://api.your-provider.com/v1",
        api_key="your-api-key"
    )
    agent = Agent(llm=llm, ...)

This is particularly useful when working with OpenAI-compatible APIs or when you need to specify a different endpoint for your chosen provider.

## 

​

Conclusion

By leveraging LiteLLM, CrewAI offers seamless integration with a vast array of LLMs. This flexibility allows you to choose the most suitable model for your specific needs, whether you prioritize performance, cost-efficiency, or local deployment. Remember to consult the [LiteLLM documentation](https://docs.litellm.ai/docs/) for the most up-to-date information on supported models and configuration options.

Was this page helpful?

YesNo

[Kickoff Crew for Each](/learn/kickoff-for-each)[Using Multimodal Agents](/learn/multimodal-agents)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Connect CrewAI to LLMs
  * Supported Providers
  * Changing the LLM
  * Configuration Options
  * Connecting to OpenAI-Compatible LLMs
  * Using Local Models with Ollama
  * Changing the Base API URL
  * Conclusion



Assistant

Responses are generated using AI and may contain mistakes.


---



## Flows {#flows}

### MLflow Integration {#mlflow-integration}

**Source:** [https://docs.crewai.com/observability/mlflow](https://docs.crewai.com/observability/mlflow)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Observability

MLflow Integration

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Observability

# MLflow Integration

Copy page

Quickly start monitoring your Agents with MLflow.

# 

​

MLflow Overview

[MLflow](https://mlflow.org/) is an open-source platform to assist machine learning practitioners and teams in handling the complexities of the machine learning process.

It provides a tracing feature that enhances LLM observability in your Generative AI applications by capturing detailed information about the execution of your application’s services. Tracing provides a way to record the inputs, outputs, and metadata associated with each intermediate step of a request, enabling you to easily pinpoint the source of bugs and unexpected behaviors.

### 

​

Features

  * **Tracing Dashboard** : Monitor activities of your crewAI agents with detailed dashboards that include inputs, outputs and metadata of spans.
  * **Automated Tracing** : A fully automated integration with crewAI, which can be enabled by running `mlflow.crewai.autolog()`.
  * **Manual Trace Instrumentation with minor efforts** : Customize trace instrumentation through MLflow’s high-level fluent APIs such as decorators, function wrappers and context managers.
  * **OpenTelemetry Compatibility** : MLflow Tracing supports exporting traces to an OpenTelemetry Collector, which can then be used to export traces to various backends such as Jaeger, Zipkin, and AWS X-Ray.
  * **Package and Deploy Agents** : Package and deploy your crewAI agents to an inference server with a variety of deployment targets.
  * **Securely Host LLMs** : Host multiple LLM from various providers in one unified endpoint through MFflow gateway.
  * **Evaluation** : Evaluate your crewAI agents with a wide range of metrics using a convenient API `mlflow.evaluate()`.



## 

​

Setup Instructions

1

Install MLflow package
    
    
    # The crewAI integration is available in mlflow>=2.19.0
    pip install mlflow

2

Start MFflow tracking server
    
    
    # This process is optional, but it is recommended to use MLflow tracking server for better visualization and broader features.
    mlflow server

3

Initialize MLflow in Your Application

Add the following two lines to your application code:
    
    
    import mlflow
    
    mlflow.crewai.autolog()
    
    # Optional: Set a tracking URI and an experiment name if you have a tracking server
    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("CrewAI")

Example Usage for tracing CrewAI Agents:
    
    
    from crewai import Agent, Crew, Task
    from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
    from crewai_tools import SerperDevTool, WebsiteSearchTool
    
    from textwrap import dedent
    
    content = "Users name is John. He is 30 years old and lives in San Francisco."
    string_source = StringKnowledgeSource(
        content=content, metadata={"preference": "personal"}
    )
    
    search_tool = WebsiteSearchTool()
    
    
    class TripAgents:
        def city_selection_agent(self):
            return Agent(
                role="City Selection Expert",
                goal="Select the best city based on weather, season, and prices",
                backstory="An expert in analyzing travel data to pick ideal destinations",
                tools=[
                    search_tool,
                ],
                verbose=True,
            )
    
        def local_expert(self):
            return Agent(
                role="Local Expert at this city",
                goal="Provide the BEST insights about the selected city",
                backstory="""A knowledgeable local guide with extensive information
            about the city, it's attractions and customs""",
                tools=[search_tool],
                verbose=True,
            )
    
    
    class TripTasks:
        def identify_task(self, agent, origin, cities, interests, range):
            return Task(
                description=dedent(
                    f"""
                    Analyze and select the best city for the trip based
                    on specific criteria such as weather patterns, seasonal
                    events, and travel costs. This task involves comparing
                    multiple cities, considering factors like current weather
                    conditions, upcoming cultural or seasonal events, and
                    overall travel expenses.
                    Your final answer must be a detailed
                    report on the chosen city, and everything you found out
                    about it, including the actual flight costs, weather
                    forecast and attractions.
    
                    Traveling from: {origin}
                    City Options: {cities}
                    Trip Date: {range}
                    Traveler Interests: {interests}
                """
                ),
                agent=agent,
                expected_output="Detailed report on the chosen city including flight costs, weather forecast, and attractions",
            )
    
        def gather_task(self, agent, origin, interests, range):
            return Task(
                description=dedent(
                    f"""
                    As a local expert on this city you must compile an
                    in-depth guide for someone traveling there and wanting
                    to have THE BEST trip ever!
                    Gather information about key attractions, local customs,
                    special events, and daily activity recommendations.
                    Find the best spots to go to, the kind of place only a
                    local would know.
                    This guide should provide a thorough overview of what
                    the city has to offer, including hidden gems, cultural
                    hotspots, must-visit landmarks, weather forecasts, and
                    high level costs.
                    The final answer must be a comprehensive city guide,
                    rich in cultural insights and practical tips,
                    tailored to enhance the travel experience.
    
                    Trip Date: {range}
                    Traveling from: {origin}
                    Traveler Interests: {interests}
                """
                ),
                agent=agent,
                expected_output="Comprehensive city guide including hidden gems, cultural hotspots, and practical travel tips",
            )
    
    
    class TripCrew:
        def __init__(self, origin, cities, date_range, interests):
            self.cities = cities
            self.origin = origin
            self.interests = interests
            self.date_range = date_range
    
        def run(self):
            agents = TripAgents()
            tasks = TripTasks()
    
            city_selector_agent = agents.city_selection_agent()
            local_expert_agent = agents.local_expert()
    
            identify_task = tasks.identify_task(
                city_selector_agent,
                self.origin,
                self.cities,
                self.interests,
                self.date_range,
            )
            gather_task = tasks.gather_task(
                local_expert_agent, self.origin, self.interests, self.date_range
            )
    
            crew = Crew(
                agents=[city_selector_agent, local_expert_agent],
                tasks=[identify_task, gather_task],
                verbose=True,
                memory=True,
                knowledge={
                    "sources": [string_source],
                    "metadata": {"preference": "personal"},
                },
            )
    
            result = crew.kickoff()
            return result
    
    
    trip_crew = TripCrew("California", "Tokyo", "Dec 12 - Dec 20", "sports")
    result = trip_crew.run()
    
    print(result)

Refer to [MLflow Tracing Documentation](https://mlflow.org/docs/latest/llms/tracing/index.html) for more configurations and use cases.

4

Visualize Activities of Agents

Now traces for your crewAI agents are captured by MLflow. Let’s visit MLflow tracking server to view the traces and get insights into your Agents.

Open `127.0.0.1:5000` on your browser to visit MLflow tracking server.

MLflow Tracing Dashboard

Was this page helpful?

YesNo

[Langtrace Integration](/observability/langtrace)[OpenLIT Integration](/observability/openlit)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * MLflow Overview
  * Features
  * Setup Instructions



Assistant

Responses are generated using AI and may contain mistakes.


---

### Flows {#flows}

**Source:** [https://docs.crewai.com/concepts/flows](https://docs.crewai.com/concepts/flows)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Core Concepts

Flows

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Core Concepts

# Flows

Copy page

Learn how to create and manage AI workflows using CrewAI Flows.

## 

​

Overview

CrewAI Flows is a powerful feature designed to streamline the creation and management of AI workflows. Flows allow developers to combine and coordinate coding tasks and Crews efficiently, providing a robust framework for building sophisticated AI automations.

Flows allow you to create structured, event-driven workflows. They provide a seamless way to connect multiple tasks, manage state, and control the flow of execution in your AI applications. With Flows, you can easily design and implement multi-step processes that leverage the full potential of CrewAI’s capabilities.

  1. **Simplified Workflow Creation** : Easily chain together multiple Crews and tasks to create complex AI workflows.

  2. **State Management** : Flows make it super easy to manage and share state between different tasks in your workflow.

  3. **Event-Driven Architecture** : Built on an event-driven model, allowing for dynamic and responsive workflows.

  4. **Flexible Control Flow** : Implement conditional logic, loops, and branching within your workflows.




## 

​

Getting Started

Let’s create a simple Flow where you will use OpenAI to generate a random city in one task and then use that city to generate a fun fact in another task.

Code
    
    
    from crewai.flow.flow import Flow, listen, start
    from dotenv import load_dotenv
    from litellm import completion
    
    
    class ExampleFlow(Flow):
        model = "gpt-4o-mini"
    
        @start()
        def generate_city(self):
            print("Starting flow")
            # Each flow state automatically gets a unique ID
            print(f"Flow State ID: {self.state['id']}")
    
            response = completion(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": "Return the name of a random city in the world.",
                    },
                ],
            )
    
            random_city = response["choices"][0]["message"]["content"]
            # Store the city in our state
            self.state["city"] = random_city
            print(f"Random City: {random_city}")
    
            return random_city
    
        @listen(generate_city)
        def generate_fun_fact(self, random_city):
            response = completion(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": f"Tell me a fun fact about {random_city}",
                    },
                ],
            )
    
            fun_fact = response["choices"][0]["message"]["content"]
            # Store the fun fact in our state
            self.state["fun_fact"] = fun_fact
            return fun_fact
    
    
    
    flow = ExampleFlow()
    flow.plot()
    result = flow.kickoff()
    
    print(f"Generated fun fact: {result}")

In the above example, we have created a simple Flow that generates a random city using OpenAI and then generates a fun fact about that city. The Flow consists of two tasks: `generate_city` and `generate_fun_fact`. The `generate_city` task is the starting point of the Flow, and the `generate_fun_fact` task listens for the output of the `generate_city` task.

Each Flow instance automatically receives a unique identifier (UUID) in its state, which helps track and manage flow executions. The state can also store additional data (like the generated city and fun fact) that persists throughout the flow’s execution.

When you run the Flow, it will:

  1. Generate a unique ID for the flow state
  2. Generate a random city and store it in the state
  3. Generate a fun fact about that city and store it in the state
  4. Print the results to the console



The state’s unique ID and stored data can be useful for tracking flow executions and maintaining context between tasks.

**Note:** Ensure you have set up your `.env` file to store your `OPENAI_API_KEY`. This key is necessary for authenticating requests to the OpenAI API.

### 

​

@start()

The `@start()` decorator is used to mark a method as the starting point of a Flow. When a Flow is started, all the methods decorated with `@start()` are executed in parallel. You can have multiple start methods in a Flow, and they will all be executed when the Flow is started.

### 

​

@listen()

The `@listen()` decorator is used to mark a method as a listener for the output of another task in the Flow. The method decorated with `@listen()` will be executed when the specified task emits an output. The method can access the output of the task it is listening to as an argument.

#### 

​

Usage

The `@listen()` decorator can be used in several ways:

  1. **Listening to a Method by Name** : You can pass the name of the method you want to listen to as a string. When that method completes, the listener method will be triggered.

Code
         
         @listen("generate_city")
         def generate_fun_fact(self, random_city):
             # Implementation

  2. **Listening to a Method Directly** : You can pass the method itself. When that method completes, the listener method will be triggered.

Code
         
         @listen(generate_city)
         def generate_fun_fact(self, random_city):
             # Implementation




### 

​

Flow Output

Accessing and handling the output of a Flow is essential for integrating your AI workflows into larger applications or systems. CrewAI Flows provide straightforward mechanisms to retrieve the final output, access intermediate results, and manage the overall state of your Flow.

#### 

​

Retrieving the Final Output

When you run a Flow, the final output is determined by the last method that completes. The `kickoff()` method returns the output of this final method.

Here’s how you can access the final output:

Code

Output
    
    
    from crewai.flow.flow import Flow, listen, start
    
    class OutputExampleFlow(Flow):
        @start()
        def first_method(self):
            return "Output from first_method"
    
        @listen(first_method)
        def second_method(self, first_output):
            return f"Second method received: {first_output}"
    
    
    flow = OutputExampleFlow()
    flow.plot("my_flow_plot")
    final_output = flow.kickoff()
    
    print("---- Final Output ----")
    print(final_output)

In this example, the `second_method` is the last method to complete, so its output will be the final output of the Flow. The `kickoff()` method will return the final output, which is then printed to the console. The `plot()` method will generate the HTML file, which will help you understand the flow.

#### 

​

Accessing and Updating State

In addition to retrieving the final output, you can also access and update the state within your Flow. The state can be used to store and share data between different methods in the Flow. After the Flow has run, you can access the state to retrieve any information that was added or updated during the execution.

Here’s an example of how to update and access the state:

Code

Output
    
    
    from crewai.flow.flow import Flow, listen, start
    from pydantic import BaseModel
    
    class ExampleState(BaseModel):
        counter: int = 0
        message: str = ""
    
    class StateExampleFlow(Flow[ExampleState]):
    
        @start()
        def first_method(self):
            self.state.message = "Hello from first_method"
            self.state.counter += 1
    
        @listen(first_method)
        def second_method(self):
            self.state.message += " - updated by second_method"
            self.state.counter += 1
            return self.state.message
    
    flow = StateExampleFlow()
    flow.plot("my_flow_plot")
    final_output = flow.kickoff()
    print(f"Final Output: {final_output}")
    print("Final State:")
    print(flow.state)

In this example, the state is updated by both `first_method` and `second_method`. After the Flow has run, you can access the final state to see the updates made by these methods.

By ensuring that the final method’s output is returned and providing access to the state, CrewAI Flows make it easy to integrate the results of your AI workflows into larger applications or systems, while also maintaining and accessing the state throughout the Flow’s execution.

## 

​

Flow State Management

Managing state effectively is crucial for building reliable and maintainable AI workflows. CrewAI Flows provides robust mechanisms for both unstructured and structured state management, allowing developers to choose the approach that best fits their application’s needs.

### 

​

Unstructured State Management

In unstructured state management, all state is stored in the `state` attribute of the `Flow` class. This approach offers flexibility, enabling developers to add or modify state attributes on the fly without defining a strict schema. Even with unstructured states, CrewAI Flows automatically generates and maintains a unique identifier (UUID) for each state instance.

Code
    
    
    from crewai.flow.flow import Flow, listen, start
    
    class UnstructuredExampleFlow(Flow):
    
        @start()
        def first_method(self):
            # The state automatically includes an 'id' field
            print(f"State ID: {self.state['id']}")
            self.state['counter'] = 0
            self.state['message'] = "Hello from structured flow"
    
        @listen(first_method)
        def second_method(self):
            self.state['counter'] += 1
            self.state['message'] += " - updated"
    
        @listen(second_method)
        def third_method(self):
            self.state['counter'] += 1
            self.state['message'] += " - updated again"
    
            print(f"State after third_method: {self.state}")
    
    
    flow = UnstructuredExampleFlow()
    flow.plot("my_flow_plot")
    flow.kickoff()

**Note:** The `id` field is automatically generated and preserved throughout the flow’s execution. You don’t need to manage or set it manually, and it will be maintained even when updating the state with new data.

**Key Points:**

  * **Flexibility:** You can dynamically add attributes to `self.state` without predefined constraints.
  * **Simplicity:** Ideal for straightforward workflows where state structure is minimal or varies significantly.



### 

​

Structured State Management

Structured state management leverages predefined schemas to ensure consistency and type safety across the workflow. By using models like Pydantic’s `BaseModel`, developers can define the exact shape of the state, enabling better validation and auto-completion in development environments.

Each state in CrewAI Flows automatically receives a unique identifier (UUID) to help track and manage state instances. This ID is automatically generated and managed by the Flow system.

Code
    
    
    from crewai.flow.flow import Flow, listen, start
    from pydantic import BaseModel
    
    
    class ExampleState(BaseModel):
        # Note: 'id' field is automatically added to all states
        counter: int = 0
        message: str = ""
    
    
    class StructuredExampleFlow(Flow[ExampleState]):
    
        @start()
        def first_method(self):
            # Access the auto-generated ID if needed
            print(f"State ID: {self.state.id}")
            self.state.message = "Hello from structured flow"
    
        @listen(first_method)
        def second_method(self):
            self.state.counter += 1
            self.state.message += " - updated"
    
        @listen(second_method)
        def third_method(self):
            self.state.counter += 1
            self.state.message += " - updated again"
    
            print(f"State after third_method: {self.state}")
    
    
    flow = StructuredExampleFlow()
    flow.kickoff()

**Key Points:**

  * **Defined Schema:** `ExampleState` clearly outlines the state structure, enhancing code readability and maintainability.
  * **Type Safety:** Leveraging Pydantic ensures that state attributes adhere to the specified types, reducing runtime errors.
  * **Auto-Completion:** IDEs can provide better auto-completion and error checking based on the defined state model.



### 

​

Choosing Between Unstructured and Structured State Management

  * **Use Unstructured State Management when:**

    * The workflow’s state is simple or highly dynamic.
    * Flexibility is prioritized over strict state definitions.
    * Rapid prototyping is required without the overhead of defining schemas.
  * **Use Structured State Management when:**

    * The workflow requires a well-defined and consistent state structure.
    * Type safety and validation are important for your application’s reliability.
    * You want to leverage IDE features like auto-completion and type checking for better developer experience.



By providing both unstructured and structured state management options, CrewAI Flows empowers developers to build AI workflows that are both flexible and robust, catering to a wide range of application requirements.

## 

​

Flow Persistence

The @persist decorator enables automatic state persistence in CrewAI Flows, allowing you to maintain flow state across restarts or different workflow executions. This decorator can be applied at either the class level or method level, providing flexibility in how you manage state persistence.

### 

​

Class-Level Persistence

When applied at the class level, the @persist decorator automatically persists all flow method states:
    
    
    @persist  # Using SQLiteFlowPersistence by default
    class MyFlow(Flow[MyState]):
        @start()
        def initialize_flow(self):
            # This method will automatically have its state persisted
            self.state.counter = 1
            print("Initialized flow. State ID:", self.state.id)
    
        @listen(initialize_flow)
        def next_step(self):
            # The state (including self.state.id) is automatically reloaded
            self.state.counter += 1
            print("Flow state is persisted. Counter:", self.state.counter)

### 

​

Method-Level Persistence

For more granular control, you can apply @persist to specific methods:
    
    
    class AnotherFlow(Flow[dict]):
        @persist  # Persists only this method's state
        @start()
        def begin(self):
            if "runs" not in self.state:
                self.state["runs"] = 0
            self.state["runs"] += 1
            print("Method-level persisted runs:", self.state["runs"])

### 

​

How It Works

  1. **Unique State Identification**

     * Each flow state automatically receives a unique UUID
     * The ID is preserved across state updates and method calls
     * Supports both structured (Pydantic BaseModel) and unstructured (dictionary) states
  2. **Default SQLite Backend**

     * SQLiteFlowPersistence is the default storage backend
     * States are automatically saved to a local SQLite database
     * Robust error handling ensures clear messages if database operations fail
  3. **Error Handling**

     * Comprehensive error messages for database operations
     * Automatic state validation during save and load
     * Clear feedback when persistence operations encounter issues



### 

​

Important Considerations

  * **State Types** : Both structured (Pydantic BaseModel) and unstructured (dictionary) states are supported
  * **Automatic ID** : The `id` field is automatically added if not present
  * **State Recovery** : Failed or restarted flows can automatically reload their previous state
  * **Custom Implementation** : You can provide your own FlowPersistence implementation for specialized storage needs



### 

​

Technical Advantages

  1. **Precise Control Through Low-Level Access**

     * Direct access to persistence operations for advanced use cases
     * Fine-grained control via method-level persistence decorators
     * Built-in state inspection and debugging capabilities
     * Full visibility into state changes and persistence operations
  2. **Enhanced Reliability**

     * Automatic state recovery after system failures or restarts
     * Transaction-based state updates for data integrity
     * Comprehensive error handling with clear error messages
     * Robust validation during state save and load operations
  3. **Extensible Architecture**

     * Customizable persistence backend through FlowPersistence interface
     * Support for specialized storage solutions beyond SQLite
     * Compatible with both structured (Pydantic) and unstructured (dict) states
     * Seamless integration with existing CrewAI flow patterns



The persistence system’s architecture emphasizes technical precision and customization options, allowing developers to maintain full control over state management while benefiting from built-in reliability features.

## 

​

Flow Control

### 

​

Conditional Logic: `or`

The `or_` function in Flows allows you to listen to multiple methods and trigger the listener method when any of the specified methods emit an output.

Code

Output
    
    
    from crewai.flow.flow import Flow, listen, or_, start
    
    class OrExampleFlow(Flow):
    
        @start()
        def start_method(self):
            return "Hello from the start method"
    
        @listen(start_method)
        def second_method(self):
            return "Hello from the second method"
    
        @listen(or_(start_method, second_method))
        def logger(self, result):
            print(f"Logger: {result}")
    
    
    
    flow = OrExampleFlow()
    flow.plot("my_flow_plot")
    flow.kickoff()

When you run this Flow, the `logger` method will be triggered by the output of either the `start_method` or the `second_method`. The `or_` function is used to listen to multiple methods and trigger the listener method when any of the specified methods emit an output.

### 

​

Conditional Logic: `and`

The `and_` function in Flows allows you to listen to multiple methods and trigger the listener method only when all the specified methods emit an output.

Code

Output
    
    
    from crewai.flow.flow import Flow, and_, listen, start
    
    class AndExampleFlow(Flow):
    
        @start()
        def start_method(self):
            self.state["greeting"] = "Hello from the start method"
    
        @listen(start_method)
        def second_method(self):
            self.state["joke"] = "What do computers eat? Microchips."
    
        @listen(and_(start_method, second_method))
        def logger(self):
            print("---- Logger ----")
            print(self.state)
    
    flow = AndExampleFlow()
    flow.plot()
    flow.kickoff()

When you run this Flow, the `logger` method will be triggered only when both the `start_method` and the `second_method` emit an output. The `and_` function is used to listen to multiple methods and trigger the listener method only when all the specified methods emit an output.

### 

​

Router

The `@router()` decorator in Flows allows you to define conditional routing logic based on the output of a method. You can specify different routes based on the output of the method, allowing you to control the flow of execution dynamically.

Code

Output
    
    
    import random
    from crewai.flow.flow import Flow, listen, router, start
    from pydantic import BaseModel
    
    class ExampleState(BaseModel):
        success_flag: bool = False
    
    class RouterFlow(Flow[ExampleState]):
    
        @start()
        def start_method(self):
            print("Starting the structured flow")
            random_boolean = random.choice([True, False])
            self.state.success_flag = random_boolean
    
        @router(start_method)
        def second_method(self):
            if self.state.success_flag:
                return "success"
            else:
                return "failed"
    
        @listen("success")
        def third_method(self):
            print("Third method running")
    
        @listen("failed")
        def fourth_method(self):
            print("Fourth method running")
    
    
    flow = RouterFlow()
    flow.plot("my_flow_plot")
    flow.kickoff()

In the above example, the `start_method` generates a random boolean value and sets it in the state. The `second_method` uses the `@router()` decorator to define conditional routing logic based on the value of the boolean. If the boolean is `True`, the method returns `"success"`, and if it is `False`, the method returns `"failed"`. The `third_method` and `fourth_method` listen to the output of the `second_method` and execute based on the returned value.

When you run this Flow, the output will change based on the random boolean value generated by the `start_method`.

## 

​

Adding Agents to Flows

Agents can be seamlessly integrated into your flows, providing a lightweight alternative to full Crews when you need simpler, focused task execution. Here’s an example of how to use an Agent within a flow to perform market research:
    
    
    import asyncio
    from typing import Any, Dict, List
    
    from crewai_tools import SerperDevTool
    from pydantic import BaseModel, Field
    
    from crewai.agent import Agent
    from crewai.flow.flow import Flow, listen, start
    
    
    # Define a structured output format
    class MarketAnalysis(BaseModel):
        key_trends: List[str] = Field(description="List of identified market trends")
        market_size: str = Field(description="Estimated market size")
        competitors: List[str] = Field(description="Major competitors in the space")
    
    
    # Define flow state
    class MarketResearchState(BaseModel):
        product: str = ""
        analysis: MarketAnalysis | None = None
    
    
    # Create a flow class
    class MarketResearchFlow(Flow[MarketResearchState]):
        @start()
        def initialize_research(self) -> Dict[str, Any]:
            print(f"Starting market research for {self.state.product}")
            return {"product": self.state.product}
    
        @listen(initialize_research)
        async def analyze_market(self) -> Dict[str, Any]:
            # Create an Agent for market research
            analyst = Agent(
                role="Market Research Analyst",
                goal=f"Analyze the market for {self.state.product}",
                backstory="You are an experienced market analyst with expertise in "
                "identifying market trends and opportunities.",
                tools=[SerperDevTool()],
                verbose=True,
            )
    
            # Define the research query
            query = f"""
            Research the market for {self.state.product}. Include:
            1. Key market trends
            2. Market size
            3. Major competitors
    
            Format your response according to the specified structure.
            """
    
            # Execute the analysis with structured output format
            result = await analyst.kickoff_async(query, response_format=MarketAnalysis)
            if result.pydantic:
                print("result", result.pydantic)
            else:
                print("result", result)
    
            # Return the analysis to update the state
            return {"analysis": result.pydantic}
    
        @listen(analyze_market)
        def present_results(self, analysis) -> None:
            print("\nMarket Analysis Results")
            print("=====================")
    
            if isinstance(analysis, dict):
                # If we got a dict with 'analysis' key, extract the actual analysis object
                market_analysis = analysis.get("analysis")
            else:
                market_analysis = analysis
    
            if market_analysis and isinstance(market_analysis, MarketAnalysis):
                print("\nKey Market Trends:")
                for trend in market_analysis.key_trends:
                    print(f"- {trend}")
    
                print(f"\nMarket Size: {market_analysis.market_size}")
    
                print("\nMajor Competitors:")
                for competitor in market_analysis.competitors:
                    print(f"- {competitor}")
            else:
                print("No structured analysis data available.")
                print("Raw analysis:", analysis)
    
    
    # Usage example
    async def run_flow():
        flow = MarketResearchFlow()
        flow.plot("MarketResearchFlowPlot")
        result = await flow.kickoff_async(inputs={"product": "AI-powered chatbots"})
        return result
    
    
    # Run the flow
    if __name__ == "__main__":
        asyncio.run(run_flow())

This example demonstrates several key features of using Agents in flows:

  1. **Structured Output** : Using Pydantic models to define the expected output format (`MarketAnalysis`) ensures type safety and structured data throughout the flow.

  2. **State Management** : The flow state (`MarketResearchState`) maintains context between steps and stores both inputs and outputs.

  3. **Tool Integration** : Agents can use tools (like `WebsiteSearchTool`) to enhance their capabilities.




## 

​

Adding Crews to Flows

Creating a flow with multiple crews in CrewAI is straightforward.

You can generate a new CrewAI project that includes all the scaffolding needed to create a flow with multiple crews by running the following command:
    
    
    crewai create flow name_of_flow

This command will generate a new CrewAI project with the necessary folder structure. The generated project includes a prebuilt crew called `poem_crew` that is already working. You can use this crew as a template by copying, pasting, and editing it to create other crews.

### 

​

Folder Structure

After running the `crewai create flow name_of_flow` command, you will see a folder structure similar to the following:

Directory/File| Description  
---|---  
`name_of_flow/`| Root directory for the flow.  
├── `crews/`| Contains directories for specific crews.  
│ └── `poem_crew/`| Directory for the “poem_crew” with its configurations and scripts.  
│ ├── `config/`| Configuration files directory for the “poem_crew”.  
│ │ ├── `agents.yaml`| YAML file defining the agents for “poem_crew”.  
│ │ └── `tasks.yaml`| YAML file defining the tasks for “poem_crew”.  
│ ├── `poem_crew.py`| Script for “poem_crew” functionality.  
├── `tools/`| Directory for additional tools used in the flow.  
│ └── `custom_tool.py`| Custom tool implementation.  
├── `main.py`| Main script for running the flow.  
├── `README.md`| Project description and instructions.  
├── `pyproject.toml`| Configuration file for project dependencies and settings.  
└── `.gitignore`| Specifies files and directories to ignore in version control.  
  
### 

​

Building Your Crews

In the `crews` folder, you can define multiple crews. Each crew will have its own folder containing configuration files and the crew definition file. For example, the `poem_crew` folder contains:

  * `config/agents.yaml`: Defines the agents for the crew.
  * `config/tasks.yaml`: Defines the tasks for the crew.
  * `poem_crew.py`: Contains the crew definition, including agents, tasks, and the crew itself.



You can copy, paste, and edit the `poem_crew` to create other crews.

### 

​

Connecting Crews in `main.py`

The `main.py` file is where you create your flow and connect the crews together. You can define your flow by using the `Flow` class and the decorators `@start` and `@listen` to specify the flow of execution.

Here’s an example of how you can connect the `poem_crew` in the `main.py` file:

Code
    
    
    #!/usr/bin/env python
    from random import randint
    
    from pydantic import BaseModel
    from crewai.flow.flow import Flow, listen, start
    from .crews.poem_crew.poem_crew import PoemCrew
    
    class PoemState(BaseModel):
        sentence_count: int = 1
        poem: str = ""
    
    class PoemFlow(Flow[PoemState]):
    
        @start()
        def generate_sentence_count(self):
            print("Generating sentence count")
            self.state.sentence_count = randint(1, 5)
    
        @listen(generate_sentence_count)
        def generate_poem(self):
            print("Generating poem")
            result = PoemCrew().crew().kickoff(inputs={"sentence_count": self.state.sentence_count})
    
            print("Poem generated", result.raw)
            self.state.poem = result.raw
    
        @listen(generate_poem)
        def save_poem(self):
            print("Saving poem")
            with open("poem.txt", "w") as f:
                f.write(self.state.poem)
    
    def kickoff():
        poem_flow = PoemFlow()
        poem_flow.kickoff()
    
    
    def plot():
        poem_flow = PoemFlow()
        poem_flow.plot("PoemFlowPlot")
    
    if __name__ == "__main__":
        kickoff()
        plot()

In this example, the `PoemFlow` class defines a flow that generates a sentence count, uses the `PoemCrew` to generate a poem, and then saves the poem to a file. The flow is kicked off by calling the `kickoff()` method. The PoemFlowPlot will be generated by `plot()` method.

### 

​

Running the Flow

(Optional) Before running the flow, you can install the dependencies by running:
    
    
    crewai install

Once all of the dependencies are installed, you need to activate the virtual environment by running:
    
    
    source .venv/bin/activate

After activating the virtual environment, you can run the flow by executing one of the following commands:
    
    
    crewai flow kickoff

or
    
    
    uv run kickoff

The flow will execute, and you should see the output in the console.

## 

​

Plot Flows

Visualizing your AI workflows can provide valuable insights into the structure and execution paths of your flows. CrewAI offers a powerful visualization tool that allows you to generate interactive plots of your flows, making it easier to understand and optimize your AI workflows.

### 

​

What are Plots?

Plots in CrewAI are graphical representations of your AI workflows. They display the various tasks, their connections, and the flow of data between them. This visualization helps in understanding the sequence of operations, identifying bottlenecks, and ensuring that the workflow logic aligns with your expectations.

### 

​

How to Generate a Plot

CrewAI provides two convenient methods to generate plots of your flows:

#### 

​

Option 1: Using the `plot()` Method

If you are working directly with a flow instance, you can generate a plot by calling the `plot()` method on your flow object. This method will create an HTML file containing the interactive plot of your flow.

Code
    
    
    # Assuming you have a flow instance
    flow.plot("my_flow_plot")

This will generate a file named `my_flow_plot.html` in your current directory. You can open this file in a web browser to view the interactive plot.

#### 

​

Option 2: Using the Command Line

If you are working within a structured CrewAI project, you can generate a plot using the command line. This is particularly useful for larger projects where you want to visualize the entire flow setup.
    
    
    crewai flow plot

This command will generate an HTML file with the plot of your flow, similar to the `plot()` method. The file will be saved in your project directory, and you can open it in a web browser to explore the flow.

### 

​

Understanding the Plot

The generated plot will display nodes representing the tasks in your flow, with directed edges indicating the flow of execution. The plot is interactive, allowing you to zoom in and out, and hover over nodes to see additional details.

By visualizing your flows, you can gain a clearer understanding of the workflow’s structure, making it easier to debug, optimize, and communicate your AI processes to others.

### 

​

Conclusion

Plotting your flows is a powerful feature of CrewAI that enhances your ability to design and manage complex AI workflows. Whether you choose to use the `plot()` method or the command line, generating plots will provide you with a visual representation of your workflows, aiding in both development and presentation.

## 

​

Next Steps

If you’re interested in exploring additional examples of flows, we have a variety of recommendations in our examples repository. Here are four specific flow examples, each showcasing unique use cases to help you match your current problem type to a specific example:

  1. **Email Auto Responder Flow** : This example demonstrates an infinite loop where a background job continually runs to automate email responses. It’s a great use case for tasks that need to be performed repeatedly without manual intervention. [View Example](https://github.com/crewAIInc/crewAI-examples/tree/main/email_auto_responder_flow)

  2. **Lead Score Flow** : This flow showcases adding human-in-the-loop feedback and handling different conditional branches using the router. It’s an excellent example of how to incorporate dynamic decision-making and human oversight into your workflows. [View Example](https://github.com/crewAIInc/crewAI-examples/tree/main/lead-score-flow)

  3. **Write a Book Flow** : This example excels at chaining multiple crews together, where the output of one crew is used by another. Specifically, one crew outlines an entire book, and another crew generates chapters based on the outline. Eventually, everything is connected to produce a complete book. This flow is perfect for complex, multi-step processes that require coordination between different tasks. [View Example](https://github.com/crewAIInc/crewAI-examples/tree/main/write_a_book_with_flows)

  4. **Meeting Assistant Flow** : This flow demonstrates how to broadcast one event to trigger multiple follow-up actions. For instance, after a meeting is completed, the flow can update a Trello board, send a Slack message, and save the results. It’s a great example of handling multiple outcomes from a single event, making it ideal for comprehensive task management and notification systems. [View Example](https://github.com/crewAIInc/crewAI-examples/tree/main/meeting_assistant_flow)




By exploring these examples, you can gain insights into how to leverage CrewAI Flows for various use cases, from automating repetitive tasks to managing complex, multi-step processes with dynamic decision-making and human feedback.

Also, check out our YouTube video on how to use flows in CrewAI below!

## 

​

Running Flows

There are two ways to run a flow:

### 

​

Using the Flow API

You can run a flow programmatically by creating an instance of your flow class and calling the `kickoff()` method:
    
    
    flow = ExampleFlow()
    result = flow.kickoff()

### 

​

Using the CLI

Starting from version 0.103.0, you can run flows using the `crewai run` command:
    
    
    crewai run

This command automatically detects if your project is a flow (based on the `type = "flow"` setting in your pyproject.toml) and runs it accordingly. This is the recommended way to run flows from the command line.

For backward compatibility, you can also use:
    
    
    crewai flow kickoff

However, the `crewai run` command is now the preferred method as it works for both crews and flows.

Was this page helpful?

YesNo

[Crews](/concepts/crews)[Knowledge](/concepts/knowledge)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Overview
  * Getting Started
  * @start()
  * @listen()
  * Usage
  * Flow Output
  * Retrieving the Final Output
  * Accessing and Updating State
  * Flow State Management
  * Unstructured State Management
  * Structured State Management
  * Choosing Between Unstructured and Structured State Management
  * Flow Persistence
  * Class-Level Persistence
  * Method-Level Persistence
  * How It Works
  * Important Considerations
  * Technical Advantages
  * Flow Control
  * Conditional Logic: or
  * Conditional Logic: and
  * Router
  * Adding Agents to Flows
  * Adding Crews to Flows
  * Folder Structure
  * Building Your Crews
  * Connecting Crews in main.py
  * Running the Flow
  * Plot Flows
  * What are Plots?
  * How to Generate a Plot
  * Option 1: Using the plot() Method
  * Option 2: Using the Command Line
  * Understanding the Plot
  * Conclusion
  * Next Steps
  * Running Flows
  * Using the Flow API
  * Using the CLI



Assistant

Responses are generated using AI and may contain mistakes.


---

### Build Your First Flow {#build-your-first-flow}

**Source:** [https://docs.crewai.com/guides/flows/first-flow](https://docs.crewai.com/guides/flows/first-flow)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Flows

Build Your First Flow

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

    * [Build Your First Flow](/guides/flows/first-flow)
    * [Mastering Flow State Management](/guides/flows/mastering-flow-state)
  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Flows

# Build Your First Flow

Copy page

Learn how to create structured, event-driven workflows with precise control over execution.

## 

​

Taking Control of AI Workflows with Flows

CrewAI Flows represent the next level in AI orchestration - combining the collaborative power of AI agent crews with the precision and flexibility of procedural programming. While crews excel at agent collaboration, flows give you fine-grained control over exactly how and when different components of your AI system interact.

In this guide, we’ll walk through creating a powerful CrewAI Flow that generates a comprehensive learning guide on any topic. This tutorial will demonstrate how Flows provide structured, event-driven control over your AI workflows by combining regular code, direct LLM calls, and crew-based processing.

### 

​

What Makes Flows Powerful

Flows enable you to:

  1. **Combine different AI interaction patterns** \- Use crews for complex collaborative tasks, direct LLM calls for simpler operations, and regular code for procedural logic
  2. **Build event-driven systems** \- Define how components respond to specific events and data changes
  3. **Maintain state across components** \- Share and transform data between different parts of your application
  4. **Integrate with external systems** \- Seamlessly connect your AI workflow with databases, APIs, and user interfaces
  5. **Create complex execution paths** \- Design conditional branches, parallel processing, and dynamic workflows



### 

​

What You’ll Build and Learn

By the end of this guide, you’ll have:

  1. **Created a sophisticated content generation system** that combines user input, AI planning, and multi-agent content creation
  2. **Orchestrated the flow of information** between different components of your system
  3. **Implemented event-driven architecture** where each step responds to the completion of previous steps
  4. **Built a foundation for more complex AI applications** that you can expand and customize



This guide creator flow demonstrates fundamental patterns that can be applied to create much more advanced applications, such as:

  * Interactive AI assistants that combine multiple specialized subsystems
  * Complex data processing pipelines with AI-enhanced transformations
  * Autonomous agents that integrate with external services and APIs
  * Multi-stage decision-making systems with human-in-the-loop processes



Let’s dive in and build your first flow!

## 

​

Prerequisites

Before starting, make sure you have:

  1. Installed CrewAI following the [installation guide](/installation)
  2. Set up your LLM API key in your environment, following the [LLM setup guide](/concepts/llms#setting-up-your-llm)
  3. Basic understanding of Python



## 

​

Step 1: Create a New CrewAI Flow Project

First, let’s create a new CrewAI Flow project using the CLI. This command sets up a scaffolded project with all the necessary directories and template files for your flow.
    
    
    crewai create flow guide_creator_flow
    cd guide_creator_flow

This will generate a project with the basic structure needed for your flow.

CrewAI Framework Overview

## 

​

Step 2: Understanding the Project Structure

The generated project has the following structure. Take a moment to familiarize yourself with it, as understanding this structure will help you create more complex flows in the future.
    
    
    guide_creator_flow/
    ├── .gitignore
    ├── pyproject.toml
    ├── README.md
    ├── .env
    ├── main.py
    ├── crews/
    │   └── poem_crew/
    │       ├── config/
    │       │   ├── agents.yaml
    │       │   └── tasks.yaml
    │       └── poem_crew.py
    └── tools/
        └── custom_tool.py

This structure provides a clear separation between different components of your flow:

  * The main flow logic in the `main.py` file
  * Specialized crews in the `crews` directory
  * Custom tools in the `tools` directory



We’ll modify this structure to create our guide creator flow, which will orchestrate the process of generating comprehensive learning guides.

## 

​

Step 3: Add a Content Writer Crew

Our flow will need a specialized crew to handle the content creation process. Let’s use the CrewAI CLI to add a content writer crew:
    
    
    crewai flow add-crew content-crew

This command automatically creates the necessary directories and template files for your crew. The content writer crew will be responsible for writing and reviewing sections of our guide, working within the overall flow orchestrated by our main application.

## 

​

Step 4: Configure the Content Writer Crew

Now, let’s modify the generated files for the content writer crew. We’ll set up two specialized agents - a writer and a reviewer - that will collaborate to create high-quality content for our guide.

  1. First, update the agents configuration file to define our content creation team:

Remember to set `llm` to the provider you are using.



    
    
    # src/guide_creator_flow/crews/content_crew/config/agents.yaml
    content_writer:
      role: >
        Educational Content Writer
      goal: >
        Create engaging, informative content that thoroughly explains the assigned topic
        and provides valuable insights to the reader
      backstory: >
        You are a talented educational writer with expertise in creating clear, engaging
        content. You have a gift for explaining complex concepts in accessible language
        and organizing information in a way that helps readers build their understanding.
      llm: provider/model-id  # e.g. openai/gpt-4o, google/gemini-2.0-flash, anthropic/claude...
    
    content_reviewer:
      role: >
        Educational Content Reviewer and Editor
      goal: >
        Ensure content is accurate, comprehensive, well-structured, and maintains
        consistency with previously written sections
      backstory: >
        You are a meticulous editor with years of experience reviewing educational
        content. You have an eye for detail, clarity, and coherence. You excel at
        improving content while maintaining the original author's voice and ensuring
        consistent quality across multiple sections.
      llm: provider/model-id  # e.g. openai/gpt-4o, google/gemini-2.0-flash, anthropic/claude...

These agent definitions establish the specialized roles and perspectives that will shape how our AI agents approach content creation. Notice how each agent has a distinct purpose and expertise.

  2. Next, update the tasks configuration file to define the specific writing and reviewing tasks:


    
    
    # src/guide_creator_flow/crews/content_crew/config/tasks.yaml
    write_section_task:
      description: >
        Write a comprehensive section on the topic: "{section_title}"
    
        Section description: {section_description}
        Target audience: {audience_level} level learners
    
        Your content should:
        1. Begin with a brief introduction to the section topic
        2. Explain all key concepts clearly with examples
        3. Include practical applications or exercises where appropriate
        4. End with a summary of key points
        5. Be approximately 500-800 words in length
    
        Format your content in Markdown with appropriate headings, lists, and emphasis.
    
        Previously written sections:
        {previous_sections}
    
        Make sure your content maintains consistency with previously written sections
        and builds upon concepts that have already been explained.
      expected_output: >
        A well-structured, comprehensive section in Markdown format that thoroughly
        explains the topic and is appropriate for the target audience.
      agent: content_writer
    
    review_section_task:
      description: >
        Review and improve the following section on "{section_title}":
    
        {draft_content}
    
        Target audience: {audience_level} level learners
    
        Previously written sections:
        {previous_sections}
    
        Your review should:
        1. Fix any grammatical or spelling errors
        2. Improve clarity and readability
        3. Ensure content is comprehensive and accurate
        4. Verify consistency with previously written sections
        5. Enhance the structure and flow
        6. Add any missing key information
    
        Provide the improved version of the section in Markdown format.
      expected_output: >
        An improved, polished version of the section that maintains the original
        structure but enhances clarity, accuracy, and consistency.
      agent: content_reviewer
      context:
        - write_section_task

These task definitions provide detailed instructions to our agents, ensuring they produce content that meets our quality standards. Note how the `context` parameter in the review task creates a workflow where the reviewer has access to the writer’s output.

  3. Now, update the crew implementation file to define how our agents and tasks work together:


    
    
    # src/guide_creator_flow/crews/content_crew/content_crew.py
    from crewai import Agent, Crew, Process, Task
    from crewai.project import CrewBase, agent, crew, task
    from crewai.agents.agent_builder.base_agent import BaseAgent
    from typing import List
    
    @CrewBase
    class ContentCrew():
        """Content writing crew"""
    
        agents: List[BaseAgent]
        tasks: List[Task]
    
        @agent
        def content_writer(self) -> Agent:
            return Agent(
                config=self.agents_config['content_writer'], # type: ignore[index]
                verbose=True
            )
    
        @agent
        def content_reviewer(self) -> Agent:
            return Agent(
                config=self.agents_config['content_reviewer'], # type: ignore[index]
                verbose=True
            )
    
        @task
        def write_section_task(self) -> Task:
            return Task(
                config=self.tasks_config['write_section_task'] # type: ignore[index]
            )
    
        @task
        def review_section_task(self) -> Task:
            return Task(
                config=self.tasks_config['review_section_task'], # type: ignore[index]
                context=[self.write_section_task()]
            )
    
        @crew
        def crew(self) -> Crew:
            """Creates the content writing crew"""
            return Crew(
                agents=self.agents,
                tasks=self.tasks,
                process=Process.sequential,
                verbose=True,
            )

This crew definition establishes the relationship between our agents and tasks, setting up a sequential process where the content writer creates a draft and then the reviewer improves it. While this crew can function independently, in our flow it will be orchestrated as part of a larger system.

## 

​

Step 5: Create the Flow

Now comes the exciting part - creating the flow that will orchestrate the entire guide creation process. This is where we’ll combine regular Python code, direct LLM calls, and our content creation crew into a cohesive system.

Our flow will:

  1. Get user input for a topic and audience level
  2. Make a direct LLM call to create a structured guide outline
  3. Process each section sequentially using the content writer crew
  4. Combine everything into a final comprehensive document



Let’s create our flow in the `main.py` file:
    
    
    #!/usr/bin/env python
    import json
    import os
    from typing import List, Dict
    from pydantic import BaseModel, Field
    from crewai import LLM
    from crewai.flow.flow import Flow, listen, start
    from guide_creator_flow.crews.content_crew.content_crew import ContentCrew
    
    # Define our models for structured data
    class Section(BaseModel):
        title: str = Field(description="Title of the section")
        description: str = Field(description="Brief description of what the section should cover")
    
    class GuideOutline(BaseModel):
        title: str = Field(description="Title of the guide")
        introduction: str = Field(description="Introduction to the topic")
        target_audience: str = Field(description="Description of the target audience")
        sections: List[Section] = Field(description="List of sections in the guide")
        conclusion: str = Field(description="Conclusion or summary of the guide")
    
    # Define our flow state
    class GuideCreatorState(BaseModel):
        topic: str = ""
        audience_level: str = ""
        guide_outline: GuideOutline = None
        sections_content: Dict[str, str] = {}
    
    class GuideCreatorFlow(Flow[GuideCreatorState]):
        """Flow for creating a comprehensive guide on any topic"""
    
        @start()
        def get_user_input(self):
            """Get input from the user about the guide topic and audience"""
            print("\n=== Create Your Comprehensive Guide ===\n")
    
            # Get user input
            self.state.topic = input("What topic would you like to create a guide for? ")
    
            # Get audience level with validation
            while True:
                audience = input("Who is your target audience? (beginner/intermediate/advanced) ").lower()
                if audience in ["beginner", "intermediate", "advanced"]:
                    self.state.audience_level = audience
                    break
                print("Please enter 'beginner', 'intermediate', or 'advanced'")
    
            print(f"\nCreating a guide on {self.state.topic} for {self.state.audience_level} audience...\n")
            return self.state
    
        @listen(get_user_input)
        def create_guide_outline(self, state):
            """Create a structured outline for the guide using a direct LLM call"""
            print("Creating guide outline...")
    
            # Initialize the LLM
            llm = LLM(model="openai/gpt-4o-mini", response_format=GuideOutline)
    
            # Create the messages for the outline
            messages = [
                {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                {"role": "user", "content": f"""
                Create a detailed outline for a comprehensive guide on "{state.topic}" for {state.audience_level} level learners.
    
                The outline should include:
                1. A compelling title for the guide
                2. An introduction to the topic
                3. 4-6 main sections that cover the most important aspects of the topic
                4. A conclusion or summary
    
                For each section, provide a clear title and a brief description of what it should cover.
                """}
            ]
    
            # Make the LLM call with JSON response format
            response = llm.call(messages=messages)
    
            # Parse the JSON response
            outline_dict = json.loads(response)
            self.state.guide_outline = GuideOutline(**outline_dict)
    
            # Ensure output directory exists before saving
            os.makedirs("output", exist_ok=True)
    
            # Save the outline to a file
            with open("output/guide_outline.json", "w") as f:
                json.dump(outline_dict, f, indent=2)
    
            print(f"Guide outline created with {len(self.state.guide_outline.sections)} sections")
            return self.state.guide_outline
    
        @listen(create_guide_outline)
        def write_and_compile_guide(self, outline):
            """Write all sections and compile the guide"""
            print("Writing guide sections and compiling...")
            completed_sections = []
    
            # Process sections one by one to maintain context flow
            for section in outline.sections:
                print(f"Processing section: {section.title}")
    
                # Build context from previous sections
                previous_sections_text = ""
                if completed_sections:
                    previous_sections_text = "# Previously Written Sections\n\n"
                    for title in completed_sections:
                        previous_sections_text += f"## {title}\n\n"
                        previous_sections_text += self.state.sections_content.get(title, "") + "\n\n"
                else:
                    previous_sections_text = "No previous sections written yet."
    
                # Run the content crew for this section
                result = ContentCrew().crew().kickoff(inputs={
                    "section_title": section.title,
                    "section_description": section.description,
                    "audience_level": self.state.audience_level,
                    "previous_sections": previous_sections_text,
                    "draft_content": ""
                })
    
                # Store the content
                self.state.sections_content[section.title] = result.raw
                completed_sections.append(section.title)
                print(f"Section completed: {section.title}")
    
            # Compile the final guide
            guide_content = f"# {outline.title}\n\n"
            guide_content += f"## Introduction\n\n{outline.introduction}\n\n"
    
            # Add each section in order
            for section in outline.sections:
                section_content = self.state.sections_content.get(section.title, "")
                guide_content += f"\n\n{section_content}\n\n"
    
            # Add conclusion
            guide_content += f"## Conclusion\n\n{outline.conclusion}\n\n"
    
            # Save the guide
            with open("output/complete_guide.md", "w") as f:
                f.write(guide_content)
    
            print("\nComplete guide compiled and saved to output/complete_guide.md")
            return "Guide creation completed successfully"
    
    def kickoff():
        """Run the guide creator flow"""
        GuideCreatorFlow().kickoff()
        print("\n=== Flow Complete ===")
        print("Your comprehensive guide is ready in the output directory.")
        print("Open output/complete_guide.md to view it.")
    
    def plot():
        """Generate a visualization of the flow"""
        flow = GuideCreatorFlow()
        flow.plot("guide_creator_flow")
        print("Flow visualization saved to guide_creator_flow.html")
    
    if __name__ == "__main__":
        kickoff()

Let’s analyze what’s happening in this flow:

  1. We define Pydantic models for structured data, ensuring type safety and clear data representation
  2. We create a state class to maintain data across different steps of the flow
  3. We implement three main flow steps:
     * Getting user input with the `@start()` decorator
     * Creating a guide outline with a direct LLM call
     * Processing sections with our content crew
  4. We use the `@listen()` decorator to establish event-driven relationships between steps



This is the power of flows - combining different types of processing (user interaction, direct LLM calls, crew-based tasks) into a coherent, event-driven system.

## 

​

Step 6: Set Up Your Environment Variables

Create a `.env` file in your project root with your API keys. See the [LLM setup guide](/concepts/llms#setting-up-your-llm) for details on configuring a provider.

.env
    
    
    OPENAI_API_KEY=your_openai_api_key
    # or
    GEMINI_API_KEY=your_gemini_api_key
    # or
    ANTHROPIC_API_KEY=your_anthropic_api_key

## 

​

Step 7: Install Dependencies

Install the required dependencies:
    
    
    crewai install

## 

​

Step 8: Run Your Flow

Now it’s time to see your flow in action! Run it using the CrewAI CLI:
    
    
    crewai flow kickoff

When you run this command, you’ll see your flow spring to life:

  1. It will prompt you for a topic and audience level
  2. It will create a structured outline for your guide
  3. It will process each section, with the content writer and reviewer collaborating on each
  4. Finally, it will compile everything into a comprehensive guide



This demonstrates the power of flows to orchestrate complex processes involving multiple components, both AI and non-AI.

## 

​

Step 9: Visualize Your Flow

One of the powerful features of flows is the ability to visualize their structure:
    
    
    crewai flow plot

This will create an HTML file that shows the structure of your flow, including the relationships between different steps and the data that flows between them. This visualization can be invaluable for understanding and debugging complex flows.

## 

​

Step 10: Review the Output

Once the flow completes, you’ll find two files in the `output` directory:

  1. `guide_outline.json`: Contains the structured outline of the guide
  2. `complete_guide.md`: The comprehensive guide with all sections



Take a moment to review these files and appreciate what you’ve built - a system that combines user input, direct AI interactions, and collaborative agent work to produce a complex, high-quality output.

## 

​

The Art of the Possible: Beyond Your First Flow

What you’ve learned in this guide provides a foundation for creating much more sophisticated AI systems. Here are some ways you could extend this basic flow:

### 

​

Enhancing User Interaction

You could create more interactive flows with:

  * Web interfaces for input and output
  * Real-time progress updates
  * Interactive feedback and refinement loops
  * Multi-stage user interactions



### 

​

Adding More Processing Steps

You could expand your flow with additional steps for:

  * Research before outline creation
  * Image generation for illustrations
  * Code snippet generation for technical guides
  * Final quality assurance and fact-checking



### 

​

Creating More Complex Flows

You could implement more sophisticated flow patterns:

  * Conditional branching based on user preferences or content type
  * Parallel processing of independent sections
  * Iterative refinement loops with feedback
  * Integration with external APIs and services



### 

​

Applying to Different Domains

The same patterns can be applied to create flows for:

  * **Interactive storytelling** : Create personalized stories based on user input
  * **Business intelligence** : Process data, generate insights, and create reports
  * **Product development** : Facilitate ideation, design, and planning
  * **Educational systems** : Create personalized learning experiences



## 

​

Key Features Demonstrated

This guide creator flow demonstrates several powerful features of CrewAI:

  1. **User interaction** : The flow collects input directly from the user
  2. **Direct LLM calls** : Uses the LLM class for efficient, single-purpose AI interactions
  3. **Structured data with Pydantic** : Uses Pydantic models to ensure type safety
  4. **Sequential processing with context** : Writes sections in order, providing previous sections for context
  5. **Multi-agent crews** : Leverages specialized agents (writer and reviewer) for content creation
  6. **State management** : Maintains state across different steps of the process
  7. **Event-driven architecture** : Uses the `@listen` decorator to respond to events



## 

​

Understanding the Flow Structure

Let’s break down the key components of flows to help you understand how to build your own:

### 

​

1\. Direct LLM Calls

Flows allow you to make direct calls to language models when you need simple, structured responses:
    
    
    llm = LLM(
        model="model-id-here",  # gpt-4o, gemini-2.0-flash, anthropic/claude...
        response_format=GuideOutline
    )
    response = llm.call(messages=messages)

This is more efficient than using a crew when you need a specific, structured output.

### 

​

2\. Event-Driven Architecture

Flows use decorators to establish relationships between components:
    
    
    @start()
    def get_user_input(self):
        # First step in the flow
        # ...
    
    @listen(get_user_input)
    def create_guide_outline(self, state):
        # This runs when get_user_input completes
        # ...

This creates a clear, declarative structure for your application.

### 

​

3\. State Management

Flows maintain state across steps, making it easy to share data:
    
    
    class GuideCreatorState(BaseModel):
        topic: str = ""
        audience_level: str = ""
        guide_outline: GuideOutline = None
        sections_content: Dict[str, str] = {}

This provides a type-safe way to track and transform data throughout your flow.

### 

​

4\. Crew Integration

Flows can seamlessly integrate with crews for complex collaborative tasks:
    
    
    result = ContentCrew().crew().kickoff(inputs={
        "section_title": section.title,
        # ...
    })

This allows you to use the right tool for each part of your application - direct LLM calls for simple tasks and crews for complex collaboration.

## 

​

Next Steps

Now that you’ve built your first flow, you can:

  1. Experiment with more complex flow structures and patterns
  2. Try using `@router()` to create conditional branches in your flows
  3. Explore the `and_` and `or_` functions for more complex parallel execution
  4. Connect your flow to external APIs, databases, or user interfaces
  5. Combine multiple specialized crews in a single flow



Congratulations! You’ve successfully built your first CrewAI Flow that combines regular code, direct LLM calls, and crew-based processing to create a comprehensive guide. These foundational skills enable you to create increasingly sophisticated AI applications that can tackle complex, multi-stage problems through a combination of procedural control and collaborative intelligence.

Was this page helpful?

YesNo

[Build Your First Crew](/guides/crews/first-crew)[Mastering Flow State Management](/guides/flows/mastering-flow-state)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Taking Control of AI Workflows with Flows
  * What Makes Flows Powerful
  * What You’ll Build and Learn
  * Prerequisites
  * Step 1: Create a New CrewAI Flow Project
  * Step 2: Understanding the Project Structure
  * Step 3: Add a Content Writer Crew
  * Step 4: Configure the Content Writer Crew
  * Step 5: Create the Flow
  * Step 6: Set Up Your Environment Variables
  * Step 7: Install Dependencies
  * Step 8: Run Your Flow
  * Step 9: Visualize Your Flow
  * Step 10: Review the Output
  * The Art of the Possible: Beyond Your First Flow
  * Enhancing User Interaction
  * Adding More Processing Steps
  * Creating More Complex Flows
  * Applying to Different Domains
  * Key Features Demonstrated
  * Understanding the Flow Structure
  * 1\. Direct LLM Calls
  * 2\. Event-Driven Architecture
  * 3\. State Management
  * 4\. Crew Integration
  * Next Steps



Assistant

Responses are generated using AI and may contain mistakes.


---

### Mastering Flow State Management {#mastering-flow-state-management}

**Source:** [https://docs.crewai.com/guides/flows/mastering-flow-state](https://docs.crewai.com/guides/flows/mastering-flow-state)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Flows

Mastering Flow State Management

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

    * [Build Your First Flow](/guides/flows/first-flow)
    * [Mastering Flow State Management](/guides/flows/mastering-flow-state)
  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Flows

# Mastering Flow State Management

Copy page

A comprehensive guide to managing, persisting, and leveraging state in CrewAI Flows for building robust AI applications.

## 

​

Understanding the Power of State in Flows

State management is the backbone of any sophisticated AI workflow. In CrewAI Flows, the state system allows you to maintain context, share data between steps, and build complex application logic. Mastering state management is essential for creating reliable, maintainable, and powerful AI applications.

This guide will walk you through everything you need to know about managing state in CrewAI Flows, from basic concepts to advanced techniques, with practical code examples along the way.

### 

​

Why State Management Matters

Effective state management enables you to:

  1. **Maintain context across execution steps** \- Pass information seamlessly between different stages of your workflow
  2. **Build complex conditional logic** \- Make decisions based on accumulated data
  3. **Create persistent applications** \- Save and restore workflow progress
  4. **Handle errors gracefully** \- Implement recovery patterns for more robust applications
  5. **Scale your applications** \- Support complex workflows with proper data organization
  6. **Enable conversational applications** \- Store and access conversation history for context-aware AI interactions



Let’s explore how to leverage these capabilities effectively.

## 

​

State Management Fundamentals

### 

​

The Flow State Lifecycle

In CrewAI Flows, the state follows a predictable lifecycle:

  1. **Initialization** \- When a flow is created, its state is initialized (either as an empty dictionary or a Pydantic model instance)
  2. **Modification** \- Flow methods access and modify the state as they execute
  3. **Transmission** \- State is passed automatically between flow methods
  4. **Persistence** (optional) - State can be saved to storage and later retrieved
  5. **Completion** \- The final state reflects the cumulative changes from all executed methods



Understanding this lifecycle is crucial for designing effective flows.

### 

​

Two Approaches to State Management

CrewAI offers two ways to manage state in your flows:

  1. **Unstructured State** \- Using dictionary-like objects for flexibility
  2. **Structured State** \- Using Pydantic models for type safety and validation



Let’s examine each approach in detail.

## 

​

Unstructured State Management

Unstructured state uses a dictionary-like approach, offering flexibility and simplicity for straightforward applications.

### 

​

How It Works

With unstructured state:

  * You access state via `self.state` which behaves like a dictionary
  * You can freely add, modify, or remove keys at any point
  * All state is automatically available to all flow methods



### 

​

Basic Example

Here’s a simple example of unstructured state management:
    
    
    from crewai.flow.flow import Flow, listen, start
    
    class UnstructuredStateFlow(Flow):
        @start()
        def initialize_data(self):
            print("Initializing flow data")
            # Add key-value pairs to state
            self.state["user_name"] = "Alex"
            self.state["preferences"] = {
                "theme": "dark",
                "language": "English"
            }
            self.state["items"] = []
    
            # The flow state automatically gets a unique ID
            print(f"Flow ID: {self.state['id']}")
    
            return "Initialized"
    
        @listen(initialize_data)
        def process_data(self, previous_result):
            print(f"Previous step returned: {previous_result}")
    
            # Access and modify state
            user = self.state["user_name"]
            print(f"Processing data for {user}")
    
            # Add items to a list in state
            self.state["items"].append("item1")
            self.state["items"].append("item2")
    
            # Add a new key-value pair
            self.state["processed"] = True
    
            return "Processed"
    
        @listen(process_data)
        def generate_summary(self, previous_result):
            # Access multiple state values
            user = self.state["user_name"]
            theme = self.state["preferences"]["theme"]
            items = self.state["items"]
            processed = self.state.get("processed", False)
    
            summary = f"User {user} has {len(items)} items with {theme} theme. "
            summary += "Data is processed." if processed else "Data is not processed."
    
            return summary
    
    # Run the flow
    flow = UnstructuredStateFlow()
    result = flow.kickoff()
    print(f"Final result: {result}")
    print(f"Final state: {flow.state}")

### 

​

When to Use Unstructured State

Unstructured state is ideal for:

  * Quick prototyping and simple flows
  * Dynamically evolving state needs
  * Cases where the structure may not be known in advance
  * Flows with simple state requirements



While flexible, unstructured state lacks type checking and schema validation, which can lead to errors in complex applications.

## 

​

Structured State Management

Structured state uses Pydantic models to define a schema for your flow’s state, providing type safety, validation, and better developer experience.

### 

​

How It Works

With structured state:

  * You define a Pydantic model that represents your state structure
  * You pass this model type to your Flow class as a type parameter
  * You access state via `self.state`, which behaves like a Pydantic model instance
  * All fields are validated according to their defined types
  * You get IDE autocompletion and type checking support



### 

​

Basic Example

Here’s how to implement structured state management:
    
    
    from crewai.flow.flow import Flow, listen, start
    from pydantic import BaseModel, Field
    from typing import List, Dict, Optional
    
    # Define your state model
    class UserPreferences(BaseModel):
        theme: str = "light"
        language: str = "English"
    
    class AppState(BaseModel):
        user_name: str = ""
        preferences: UserPreferences = UserPreferences()
        items: List[str] = []
        processed: bool = False
        completion_percentage: float = 0.0
    
    # Create a flow with typed state
    class StructuredStateFlow(Flow[AppState]):
        @start()
        def initialize_data(self):
            print("Initializing flow data")
            # Set state values (type-checked)
            self.state.user_name = "Taylor"
            self.state.preferences.theme = "dark"
    
            # The ID field is automatically available
            print(f"Flow ID: {self.state.id}")
    
            return "Initialized"
    
        @listen(initialize_data)
        def process_data(self, previous_result):
            print(f"Processing data for {self.state.user_name}")
    
            # Modify state (with type checking)
            self.state.items.append("item1")
            self.state.items.append("item2")
            self.state.processed = True
            self.state.completion_percentage = 50.0
    
            return "Processed"
    
        @listen(process_data)
        def generate_summary(self, previous_result):
            # Access state (with autocompletion)
            summary = f"User {self.state.user_name} has {len(self.state.items)} items "
            summary += f"with {self.state.preferences.theme} theme. "
            summary += "Data is processed." if self.state.processed else "Data is not processed."
            summary += f" Completion: {self.state.completion_percentage}%"
    
            return summary
    
    # Run the flow
    flow = StructuredStateFlow()
    result = flow.kickoff()
    print(f"Final result: {result}")
    print(f"Final state: {flow.state}")

### 

​

Benefits of Structured State

Using structured state provides several advantages:

  1. **Type Safety** \- Catch type errors at development time
  2. **Self-Documentation** \- The state model clearly documents what data is available
  3. **Validation** \- Automatic validation of data types and constraints
  4. **IDE Support** \- Get autocomplete and inline documentation
  5. **Default Values** \- Easily define fallbacks for missing data



### 

​

When to Use Structured State

Structured state is recommended for:

  * Complex flows with well-defined data schemas
  * Team projects where multiple developers work on the same code
  * Applications where data validation is important
  * Flows that need to enforce specific data types and constraints



## 

​

The Automatic State ID

Both unstructured and structured states automatically receive a unique identifier (UUID) to help track and manage state instances.

### 

​

How It Works

  * For unstructured state, the ID is accessible as `self.state["id"]`
  * For structured state, the ID is accessible as `self.state.id`
  * This ID is generated automatically when the flow is created
  * The ID remains the same throughout the flow’s lifecycle
  * The ID can be used for tracking, logging, and retrieving persisted states



This UUID is particularly valuable when implementing persistence or tracking multiple flow executions.

## 

​

Dynamic State Updates

Regardless of whether you’re using structured or unstructured state, you can update state dynamically throughout your flow’s execution.

### 

​

Passing Data Between Steps

Flow methods can return values that are then passed as arguments to listening methods:
    
    
    from crewai.flow.flow import Flow, listen, start
    
    class DataPassingFlow(Flow):
        @start()
        def generate_data(self):
            # This return value will be passed to listening methods
            return "Generated data"
    
        @listen(generate_data)
        def process_data(self, data_from_previous_step):
            print(f"Received: {data_from_previous_step}")
            # You can modify the data and pass it along
            processed_data = f"{data_from_previous_step} - processed"
            # Also update state
            self.state["last_processed"] = processed_data
            return processed_data
    
        @listen(process_data)
        def finalize_data(self, processed_data):
            print(f"Received processed data: {processed_data}")
            # Access both the passed data and state
            last_processed = self.state.get("last_processed", "")
            return f"Final: {processed_data} (from state: {last_processed})"

This pattern allows you to combine direct data passing with state updates for maximum flexibility.

## 

​

Persisting Flow State

One of CrewAI’s most powerful features is the ability to persist flow state across executions. This enables workflows that can be paused, resumed, and even recovered after failures.

### 

​

The @persist Decorator

The `@persist` decorator automates state persistence, saving your flow’s state at key points in execution.

#### 

​

Class-Level Persistence

When applied at the class level, `@persist` saves state after every method execution:
    
    
    from crewai.flow.flow import Flow, listen, persist, start
    from pydantic import BaseModel
    
    class CounterState(BaseModel):
        value: int = 0
    
    @persist  # Apply to the entire flow class
    class PersistentCounterFlow(Flow[CounterState]):
        @start()
        def increment(self):
            self.state.value += 1
            print(f"Incremented to {self.state.value}")
            return self.state.value
    
        @listen(increment)
        def double(self, value):
            self.state.value = value * 2
            print(f"Doubled to {self.state.value}")
            return self.state.value
    
    # First run
    flow1 = PersistentCounterFlow()
    result1 = flow1.kickoff()
    print(f"First run result: {result1}")
    
    # Second run - state is automatically loaded
    flow2 = PersistentCounterFlow()
    result2 = flow2.kickoff()
    print(f"Second run result: {result2}")  # Will be higher due to persisted state

#### 

​

Method-Level Persistence

For more granular control, you can apply `@persist` to specific methods:
    
    
    from crewai.flow.flow import Flow, listen, persist, start
    
    class SelectivePersistFlow(Flow):
        @start()
        def first_step(self):
            self.state["count"] = 1
            return "First step"
    
        @persist  # Only persist after this method
        @listen(first_step)
        def important_step(self, prev_result):
            self.state["count"] += 1
            self.state["important_data"] = "This will be persisted"
            return "Important step completed"
    
        @listen(important_step)
        def final_step(self, prev_result):
            self.state["count"] += 1
            return f"Complete with count {self.state['count']}"

## 

​

Advanced State Patterns

### 

​

State-Based Conditional Logic

You can use state to implement complex conditional logic in your flows:
    
    
    from crewai.flow.flow import Flow, listen, router, start
    from pydantic import BaseModel
    
    class PaymentState(BaseModel):
        amount: float = 0.0
        is_approved: bool = False
        retry_count: int = 0
    
    class PaymentFlow(Flow[PaymentState]):
        @start()
        def process_payment(self):
            # Simulate payment processing
            self.state.amount = 100.0
            self.state.is_approved = self.state.amount < 1000
            return "Payment processed"
    
        @router(process_payment)
        def check_approval(self, previous_result):
            if self.state.is_approved:
                return "approved"
            elif self.state.retry_count < 3:
                return "retry"
            else:
                return "rejected"
    
        @listen("approved")
        def handle_approval(self):
            return f"Payment of ${self.state.amount} approved!"
    
        @listen("retry")
        def handle_retry(self):
            self.state.retry_count += 1
            print(f"Retrying payment (attempt {self.state.retry_count})...")
            # Could implement retry logic here
            return "Retry initiated"
    
        @listen("rejected")
        def handle_rejection(self):
            return f"Payment of ${self.state.amount} rejected after {self.state.retry_count} retries."

### 

​

Handling Complex State Transformations

For complex state transformations, you can create dedicated methods:
    
    
    from crewai.flow.flow import Flow, listen, start
    from pydantic import BaseModel
    from typing import List, Dict
    
    class UserData(BaseModel):
        name: str
        active: bool = True
        login_count: int = 0
    
    class ComplexState(BaseModel):
        users: Dict[str, UserData] = {}
        active_user_count: int = 0
    
    class TransformationFlow(Flow[ComplexState]):
        @start()
        def initialize(self):
            # Add some users
            self.add_user("alice", "Alice")
            self.add_user("bob", "Bob")
            self.add_user("charlie", "Charlie")
            return "Initialized"
    
        @listen(initialize)
        def process_users(self, _):
            # Increment login counts
            for user_id in self.state.users:
                self.increment_login(user_id)
    
            # Deactivate one user
            self.deactivate_user("bob")
    
            # Update active count
            self.update_active_count()
    
            return f"Processed {len(self.state.users)} users"
    
        # Helper methods for state transformations
        def add_user(self, user_id: str, name: str):
            self.state.users[user_id] = UserData(name=name)
            self.update_active_count()
    
        def increment_login(self, user_id: str):
            if user_id in self.state.users:
                self.state.users[user_id].login_count += 1
    
        def deactivate_user(self, user_id: str):
            if user_id in self.state.users:
                self.state.users[user_id].active = False
                self.update_active_count()
    
        def update_active_count(self):
            self.state.active_user_count = sum(
                1 for user in self.state.users.values() if user.active
            )

This pattern of creating helper methods keeps your flow methods clean while enabling complex state manipulations.

## 

​

State Management with Crews

One of the most powerful patterns in CrewAI is combining flow state management with crew execution.

### 

​

Passing State to Crews

You can use flow state to parameterize crews:
    
    
    from crewai.flow.flow import Flow, listen, start
    from crewai import Agent, Crew, Process, Task
    from pydantic import BaseModel
    
    class ResearchState(BaseModel):
        topic: str = ""
        depth: str = "medium"
        results: str = ""
    
    class ResearchFlow(Flow[ResearchState]):
        @start()
        def get_parameters(self):
            # In a real app, this might come from user input
            self.state.topic = "Artificial Intelligence Ethics"
            self.state.depth = "deep"
            return "Parameters set"
    
        @listen(get_parameters)
        def execute_research(self, _):
            # Create agents
            researcher = Agent(
                role="Research Specialist",
                goal=f"Research {self.state.topic} in {self.state.depth} detail",
                backstory="You are an expert researcher with a talent for finding accurate information."
            )
    
            writer = Agent(
                role="Content Writer",
                goal="Transform research into clear, engaging content",
                backstory="You excel at communicating complex ideas clearly and concisely."
            )
    
            # Create tasks
            research_task = Task(
                description=f"Research {self.state.topic} with {self.state.depth} analysis",
                expected_output="Comprehensive research notes in markdown format",
                agent=researcher
            )
    
            writing_task = Task(
                description=f"Create a summary on {self.state.topic} based on the research",
                expected_output="Well-written article in markdown format",
                agent=writer,
                context=[research_task]
            )
    
            # Create and run crew
            research_crew = Crew(
                agents=[researcher, writer],
                tasks=[research_task, writing_task],
                process=Process.sequential,
                verbose=True
            )
    
            # Run crew and store result in state
            result = research_crew.kickoff()
            self.state.results = result.raw
    
            return "Research completed"
    
        @listen(execute_research)
        def summarize_results(self, _):
            # Access the stored results
            result_length = len(self.state.results)
            return f"Research on {self.state.topic} completed with {result_length} characters of results."

### 

​

Handling Crew Outputs in State

When a crew completes, you can process its output and store it in your flow state:
    
    
    @listen(execute_crew)
    def process_crew_results(self, _):
        # Parse the raw results (assuming JSON output)
        import json
        try:
            results_dict = json.loads(self.state.raw_results)
            self.state.processed_results = {
                "title": results_dict.get("title", ""),
                "main_points": results_dict.get("main_points", []),
                "conclusion": results_dict.get("conclusion", "")
            }
            return "Results processed successfully"
        except json.JSONDecodeError:
            self.state.error = "Failed to parse crew results as JSON"
            return "Error processing results"

## 

​

Best Practices for State Management

### 

​

1\. Keep State Focused

Design your state to contain only what’s necessary:
    
    
    # Too broad
    class BloatedState(BaseModel):
        user_data: Dict = {}
        system_settings: Dict = {}
        temporary_calculations: List = []
        debug_info: Dict = {}
        # ...many more fields
    
    # Better: Focused state
    class FocusedState(BaseModel):
        user_id: str
        preferences: Dict[str, str]
        completion_status: Dict[str, bool]

### 

​

2\. Use Structured State for Complex Flows

As your flows grow in complexity, structured state becomes increasingly valuable:
    
    
    # Simple flow can use unstructured state
    class SimpleGreetingFlow(Flow):
        @start()
        def greet(self):
            self.state["name"] = "World"
            return f"Hello, {self.state['name']}!"
    
    # Complex flow benefits from structured state
    class UserRegistrationState(BaseModel):
        username: str
        email: str
        verification_status: bool = False
        registration_date: datetime = Field(default_factory=datetime.now)
        last_login: Optional[datetime] = None
    
    class RegistrationFlow(Flow[UserRegistrationState]):
        # Methods with strongly-typed state access

### 

​

3\. Document State Transitions

For complex flows, document how state changes throughout the execution:
    
    
    @start()
    def initialize_order(self):
        """
        Initialize order state with empty values.
    
        State before: {}
        State after: {order_id: str, items: [], status: 'new'}
        """
        self.state.order_id = str(uuid.uuid4())
        self.state.items = []
        self.state.status = "new"
        return "Order initialized"

### 

​

4\. Handle State Errors Gracefully

Implement error handling for state access:
    
    
    @listen(previous_step)
    def process_data(self, _):
        try:
            # Try to access a value that might not exist
            user_preference = self.state.preferences.get("theme", "default")
        except (AttributeError, KeyError):
            # Handle the error gracefully
            self.state.errors = self.state.get("errors", [])
            self.state.errors.append("Failed to access preferences")
            user_preference = "default"
    
        return f"Used preference: {user_preference}"

### 

​

5\. Use State for Progress Tracking

Leverage state to track progress in long-running flows:
    
    
    class ProgressTrackingFlow(Flow):
        @start()
        def initialize(self):
            self.state["total_steps"] = 3
            self.state["current_step"] = 0
            self.state["progress"] = 0.0
            self.update_progress()
            return "Initialized"
    
        def update_progress(self):
            """Helper method to calculate and update progress"""
            if self.state.get("total_steps", 0) > 0:
                self.state["progress"] = (self.state.get("current_step", 0) /
                                        self.state["total_steps"]) * 100
                print(f"Progress: {self.state['progress']:.1f}%")
    
        @listen(initialize)
        def step_one(self, _):
            # Do work...
            self.state["current_step"] = 1
            self.update_progress()
            return "Step 1 complete"
    
        # Additional steps...

### 

​

6\. Use Immutable Operations When Possible

Especially with structured state, prefer immutable operations for clarity:
    
    
    # Instead of modifying lists in place:
    self.state.items.append(new_item)  # Mutable operation
    
    # Consider creating new state:
    from pydantic import BaseModel
    from typing import List
    
    class ItemState(BaseModel):
        items: List[str] = []
    
    class ImmutableFlow(Flow[ItemState]):
        @start()
        def add_item(self):
            # Create new list with the added item
            self.state.items = [*self.state.items, "new item"]
            return "Item added"

## 

​

Debugging Flow State

### 

​

Logging State Changes

When developing, add logging to track state changes:
    
    
    import logging
    logging.basicConfig(level=logging.INFO)
    
    class LoggingFlow(Flow):
        def log_state(self, step_name):
            logging.info(f"State after {step_name}: {self.state}")
    
        @start()
        def initialize(self):
            self.state["counter"] = 0
            self.log_state("initialize")
            return "Initialized"
    
        @listen(initialize)
        def increment(self, _):
            self.state["counter"] += 1
            self.log_state("increment")
            return f"Incremented to {self.state['counter']}"

### 

​

State Visualization

You can add methods to visualize your state for debugging:
    
    
    def visualize_state(self):
        """Create a simple visualization of the current state"""
        import json
        from rich.console import Console
        from rich.panel import Panel
    
        console = Console()
    
        if hasattr(self.state, "model_dump"):
            # Pydantic v2
            state_dict = self.state.model_dump()
        elif hasattr(self.state, "dict"):
            # Pydantic v1
            state_dict = self.state.dict()
        else:
            # Unstructured state
            state_dict = dict(self.state)
    
        # Remove id for cleaner output
        if "id" in state_dict:
            state_dict.pop("id")
    
        state_json = json.dumps(state_dict, indent=2, default=str)
        console.print(Panel(state_json, title="Current Flow State"))

## 

​

Conclusion

Mastering state management in CrewAI Flows gives you the power to build sophisticated, robust AI applications that maintain context, make complex decisions, and deliver consistent results.

Whether you choose unstructured or structured state, implementing proper state management practices will help you create flows that are maintainable, extensible, and effective at solving real-world problems.

As you develop more complex flows, remember that good state management is about finding the right balance between flexibility and structure, making your code both powerful and easy to understand.

You’ve now mastered the concepts and practices of state management in CrewAI Flows! With this knowledge, you can create robust AI workflows that effectively maintain context, share data between steps, and build sophisticated application logic.

## 

​

Next Steps

  * Experiment with both structured and unstructured state in your flows
  * Try implementing state persistence for long-running workflows
  * Explore [building your first crew](/guides/crews/first-crew) to see how crews and flows can work together
  * Check out the [Flow reference documentation](/concepts/flows) for more advanced features



Was this page helpful?

YesNo

[Build Your First Flow](/guides/flows/first-flow)[Customizing Prompts](/guides/advanced/customizing-prompts)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Understanding the Power of State in Flows
  * Why State Management Matters
  * State Management Fundamentals
  * The Flow State Lifecycle
  * Two Approaches to State Management
  * Unstructured State Management
  * How It Works
  * Basic Example
  * When to Use Unstructured State
  * Structured State Management
  * How It Works
  * Basic Example
  * Benefits of Structured State
  * When to Use Structured State
  * The Automatic State ID
  * How It Works
  * Dynamic State Updates
  * Passing Data Between Steps
  * Persisting Flow State
  * The @persist Decorator
  * Class-Level Persistence
  * Method-Level Persistence
  * Advanced State Patterns
  * State-Based Conditional Logic
  * Handling Complex State Transformations
  * State Management with Crews
  * Passing State to Crews
  * Handling Crew Outputs in State
  * Best Practices for State Management
  * 1\. Keep State Focused
  * 2\. Use Structured State for Complex Flows
  * 3\. Document State Transitions
  * 4\. Handle State Errors Gracefully
  * 5\. Use State for Progress Tracking
  * 6\. Use Immutable Operations When Possible
  * Debugging Flow State
  * Logging State Changes
  * State Visualization
  * Conclusion
  * Next Steps



Assistant

Responses are generated using AI and may contain mistakes.


---



## Guides {#guides}

### Customizing Prompts {#customizing-prompts}

**Source:** [https://docs.crewai.com/guides/advanced/customizing-prompts](https://docs.crewai.com/guides/advanced/customizing-prompts)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Advanced

Customizing Prompts

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced

    * [Customizing Prompts](/guides/advanced/customizing-prompts)
    * [Fingerprinting](/guides/advanced/fingerprinting)



##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Advanced

# Customizing Prompts

Copy page

Dive deeper into low-level prompt customization for CrewAI, enabling super custom and complex use cases for different models and languages.

## 

​

Why Customize Prompts?

Although CrewAI’s default prompts work well for many scenarios, low-level customization opens the door to significantly more flexible and powerful agent behavior. Here’s why you might want to take advantage of this deeper control:

  1. **Optimize for specific LLMs** – Different models (such as GPT-4, Claude, or Llama) thrive with prompt formats tailored to their unique architectures.
  2. **Change the language** – Build agents that operate exclusively in languages beyond English, handling nuances with precision.
  3. **Specialize for complex domains** – Adapt prompts for highly specialized industries like healthcare, finance, or legal.
  4. **Adjust tone and style** – Make agents more formal, casual, creative, or analytical.
  5. **Support super custom use cases** – Utilize advanced prompt structures and formatting to meet intricate, project-specific requirements.



This guide explores how to tap into CrewAI’s prompts at a lower level, giving you fine-grained control over how agents think and interact.

## 

​

Understanding CrewAI’s Prompt System

Under the hood, CrewAI employs a modular prompt system that you can customize extensively:

  * **Agent templates** – Govern each agent’s approach to their assigned role.
  * **Prompt slices** – Control specialized behaviors such as tasks, tool usage, and output structure.
  * **Error handling** – Direct how agents respond to failures, exceptions, or timeouts.
  * **Tool-specific prompts** – Define detailed instructions for how tools are invoked or utilized.



Check out the [original prompt templates in CrewAI’s repository](https://github.com/crewAIInc/crewAI/blob/main/src/crewai/translations/en.json) to see how these elements are organized. From there, you can override or adapt them as needed to unlock advanced behaviors.

## 

​

Understanding Default System Instructions

**Production Transparency Issue** : CrewAI automatically injects default instructions into your prompts that you might not be aware of. This section explains what’s happening under the hood and how to gain full control.

When you define an agent with `role`, `goal`, and `backstory`, CrewAI automatically adds additional system instructions that control formatting and behavior. Understanding these default injections is crucial for production systems where you need full prompt transparency.

### 

​

What CrewAI Automatically Injects

Based on your agent configuration, CrewAI adds different default instructions:

#### 

​

For Agents Without Tools
    
    
    "I MUST use these formats, my job depends on it!"

#### 

​

For Agents With Tools
    
    
    "IMPORTANT: Use the following format in your response:
    
    Thought: you should always think about what to do
    Action: the action to take, only one name of [tool_names]
    Action Input: the input to the action, just a simple JSON object...

#### 

​

For Structured Outputs (JSON/Pydantic)
    
    
    "Ensure your final answer contains only the content in the following format: {output_format}
    Ensure the final output does not include any code block markers like ```json or ```python."

### 

​

Viewing the Complete System Prompt

To see exactly what prompt is being sent to your LLM, you can inspect the generated prompt:
    
    
    from crewai import Agent, Crew, Task
    from crewai.utilities.prompts import Prompts
    
    # Create your agent
    agent = Agent(
        role="Data Analyst",
        goal="Analyze data and provide insights",
        backstory="You are an expert data analyst with 10 years of experience.",
        verbose=True
    )
    
    # Create a sample task
    task = Task(
        description="Analyze the sales data and identify trends",
        expected_output="A detailed analysis with key insights and trends",
        agent=agent
    )
    
    # Create the prompt generator
    prompt_generator = Prompts(
        agent=agent,
        has_tools=len(agent.tools) > 0,
        use_system_prompt=agent.use_system_prompt
    )
    
    # Generate and inspect the actual prompt
    generated_prompt = prompt_generator.task_execution()
    
    # Print the complete system prompt that will be sent to the LLM
    if "system" in generated_prompt:
        print("=== SYSTEM PROMPT ===")
        print(generated_prompt["system"])
        print("\n=== USER PROMPT ===")
        print(generated_prompt["user"])
    else:
        print("=== COMPLETE PROMPT ===")
        print(generated_prompt["prompt"])
    
    # You can also see how the task description gets formatted
    print("\n=== TASK CONTEXT ===")
    print(f"Task Description: {task.description}")
    print(f"Expected Output: {task.expected_output}")

### 

​

Overriding Default Instructions

You have several options to gain full control over the prompts:

#### 

​

Option 1: Custom Templates (Recommended)
    
    
    from crewai import Agent
    
    # Define your own system template without default instructions
    custom_system_template = """You are {role}. {backstory}
    Your goal is: {goal}
    
    Respond naturally and conversationally. Focus on providing helpful, accurate information."""
    
    custom_prompt_template = """Task: {input}
    
    Please complete this task thoughtfully."""
    
    agent = Agent(
        role="Research Assistant", 
        goal="Help users find accurate information",
        backstory="You are a helpful research assistant.",
        system_template=custom_system_template,
        prompt_template=custom_prompt_template,
        use_system_prompt=True  # Use separate system/user messages
    )

#### 

​

Option 2: Custom Prompt File

Create a `custom_prompts.json` file to override specific prompt slices:
    
    
    {
      "slices": {
        "no_tools": "\nProvide your best answer in a natural, conversational way.",
        "tools": "\nYou have access to these tools: {tools}\n\nUse them when helpful, but respond naturally.",
        "formatted_task_instructions": "Format your response as: {output_format}"
      }
    }

Then use it in your crew:
    
    
    crew = Crew(
        agents=[agent],
        tasks=[task],
        prompt_file="custom_prompts.json",
        verbose=True
    )

#### 

​

Option 3: Disable System Prompts for o1 Models
    
    
    agent = Agent(
        role="Analyst",
        goal="Analyze data", 
        backstory="Expert analyst",
        use_system_prompt=False  # Disables system prompt separation
    )

### 

​

Debugging with Observability Tools

For production transparency, integrate with observability platforms to monitor all prompts and LLM interactions. This allows you to see exactly what prompts (including default instructions) are being sent to your LLMs.

See our [Observability documentation](/how-to/observability) for detailed integration guides with various platforms including Langfuse, MLflow, Weights & Biases, and custom logging solutions.

### 

​

Best Practices for Production

  1. **Always inspect generated prompts** before deploying to production
  2. **Use custom templates** when you need full control over prompt content
  3. **Integrate observability tools** for ongoing prompt monitoring (see [Observability docs](/how-to/observability))
  4. **Test with different LLMs** as default instructions may work differently across models
  5. **Document your prompt customizations** for team transparency



The default instructions exist to ensure consistent agent behavior, but they can interfere with domain-specific requirements. Use the customization options above to maintain full control over your agent’s behavior in production systems.

## 

​

Best Practices for Managing Prompt Files

When engaging in low-level prompt customization, follow these guidelines to keep things organized and maintainable:

  1. **Keep files separate** – Store your customized prompts in dedicated JSON files outside your main codebase.
  2. **Version control** – Track changes within your repository, ensuring clear documentation of prompt adjustments over time.
  3. **Organize by model or language** – Use naming schemes like `prompts_llama.json` or `prompts_es.json` to quickly identify specialized configurations.
  4. **Document changes** – Provide comments or maintain a README detailing the purpose and scope of your customizations.
  5. **Minimize alterations** – Only override the specific slices you genuinely need to adjust, keeping default functionality intact for everything else.



## 

​

The Simplest Way to Customize Prompts

One straightforward approach is to create a JSON file for the prompts you want to override and then point your Crew at that file:

  1. Craft a JSON file with your updated prompt slices.
  2. Reference that file via the `prompt_file` parameter in your Crew.



CrewAI then merges your customizations with the defaults, so you don’t have to redefine every prompt. Here’s how:

### 

​

Example: Basic Prompt Customization

Create a `custom_prompts.json` file with the prompts you want to modify. Ensure you list all top-level prompts it should contain, not just your changes:
    
    
    {
      "slices": {
        "format": "When responding, follow this structure:\n\nTHOUGHTS: Your step-by-step thinking\nACTION: Any tool you're using\nRESULT: Your final answer or conclusion"
      }
    }

Then integrate it like so:
    
    
    from crewai import Agent, Crew, Task, Process
    
    # Create agents and tasks as normal
    researcher = Agent(
        role="Research Specialist",
        goal="Find information on quantum computing",
        backstory="You are a quantum physics expert",
        verbose=True
    )
    
    research_task = Task(
        description="Research quantum computing applications",
        expected_output="A summary of practical applications",
        agent=researcher
    )
    
    # Create a crew with your custom prompt file
    crew = Crew(
        agents=[researcher],
        tasks=[research_task],
        prompt_file="path/to/custom_prompts.json",
        verbose=True
    )
    
    # Run the crew
    result = crew.kickoff()

With these few edits, you gain low-level control over how your agents communicate and solve tasks.

## 

​

Optimizing for Specific Models

Different models thrive on differently structured prompts. Making deeper adjustments can significantly boost performance by aligning your prompts with a model’s nuances.

### 

​

Example: Llama 3.3 Prompting Template

For instance, when dealing with Meta’s Llama 3.3, deeper-level customization may reflect the recommended structure described at: <https://www.llama.com/docs/model-cards-and-prompt-formats/llama3_1/#prompt-template>

Here’s an example to highlight how you might fine-tune an Agent to leverage Llama 3.3 in code:
    
    
    from crewai import Agent, Crew, Task, Process
    from crewai_tools import DirectoryReadTool, FileReadTool
    
    # Define templates for system, user (prompt), and assistant (response) messages
    system_template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>{{ .System }}<|eot_id|>"""
    prompt_template = """<|start_header_id|>user<|end_header_id|>{{ .Prompt }}<|eot_id|>"""
    response_template = """<|start_header_id|>assistant<|end_header_id|>{{ .Response }}<|eot_id|>"""
    
    # Create an Agent using Llama-specific layouts
    principal_engineer = Agent(
        role="Principal Engineer",
        goal="Oversee AI architecture and make high-level decisions",
        backstory="You are the lead engineer responsible for critical AI systems",
        verbose=True,
        llm="groq/llama-3.3-70b-versatile",  # Using the Llama 3 model
        system_template=system_template,
        prompt_template=prompt_template,
        response_template=response_template,
        tools=[DirectoryReadTool(), FileReadTool()]
    )
    
    # Define a sample task
    engineering_task = Task(
        description="Review AI implementation files for potential improvements",
        expected_output="A summary of key findings and recommendations",
        agent=principal_engineer
    )
    
    # Create a Crew for the task
    llama_crew = Crew(
        agents=[principal_engineer],
        tasks=[engineering_task],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute the crew
    result = llama_crew.kickoff()
    print(result.raw)

Through this deeper configuration, you can exercise comprehensive, low-level control over your Llama-based workflows without needing a separate JSON file.

## 

​

Conclusion

Low-level prompt customization in CrewAI opens the door to super custom, complex use cases. By establishing well-organized prompt files (or direct inline templates), you can accommodate various models, languages, and specialized domains. This level of flexibility ensures you can craft precisely the AI behavior you need, all while knowing CrewAI still provides reliable defaults when you don’t override them.

You now have the foundation for advanced prompt customizations in CrewAI. Whether you’re adapting for model-specific structures or domain-specific constraints, this low-level approach lets you shape agent interactions in highly specialized ways.

Was this page helpful?

YesNo

[Mastering Flow State Management](/guides/flows/mastering-flow-state)[Fingerprinting](/guides/advanced/fingerprinting)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Why Customize Prompts?
  * Understanding CrewAI’s Prompt System
  * Understanding Default System Instructions
  * What CrewAI Automatically Injects
  * For Agents Without Tools
  * For Agents With Tools
  * For Structured Outputs (JSON/Pydantic)
  * Viewing the Complete System Prompt
  * Overriding Default Instructions
  * Option 1: Custom Templates (Recommended)
  * Option 2: Custom Prompt File
  * Option 3: Disable System Prompts for o1 Models
  * Debugging with Observability Tools
  * Best Practices for Production
  * Best Practices for Managing Prompt Files
  * The Simplest Way to Customize Prompts
  * Example: Basic Prompt Customization
  * Optimizing for Specific Models
  * Example: Llama 3.3 Prompting Template
  * Conclusion



Assistant

Responses are generated using AI and may contain mistakes.


---

### Fingerprinting {#fingerprinting}

**Source:** [https://docs.crewai.com/guides/advanced/fingerprinting](https://docs.crewai.com/guides/advanced/fingerprinting)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Advanced

Fingerprinting

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced

    * [Customizing Prompts](/guides/advanced/customizing-prompts)
    * [Fingerprinting](/guides/advanced/fingerprinting)



##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Advanced

# Fingerprinting

Copy page

Learn how to use CrewAI’s fingerprinting system to uniquely identify and track components throughout their lifecycle.

## 

​

Overview

Fingerprints in CrewAI provide a way to uniquely identify and track components throughout their lifecycle. Each `Agent`, `Crew`, and `Task` automatically receives a unique fingerprint when created, which cannot be manually overridden.

These fingerprints can be used for:

  * Auditing and tracking component usage
  * Ensuring component identity integrity
  * Attaching metadata to components
  * Creating a traceable chain of operations



## 

​

How Fingerprints Work

A fingerprint is an instance of the `Fingerprint` class from the `crewai.security` module. Each fingerprint contains:

  * A UUID string: A unique identifier for the component that is automatically generated and cannot be manually set
  * A creation timestamp: When the fingerprint was generated, automatically set and cannot be manually modified
  * Metadata: A dictionary of additional information that can be customized



Fingerprints are automatically generated and assigned when a component is created. Each component exposes its fingerprint through a read-only property.

## 

​

Basic Usage

### 

​

Accessing Fingerprints
    
    
    from crewai import Agent, Crew, Task
    
    # Create components - fingerprints are automatically generated
    agent = Agent(
        role="Data Scientist",
        goal="Analyze data",
        backstory="Expert in data analysis"
    )
    
    crew = Crew(
        agents=[agent],
        tasks=[]
    )
    
    task = Task(
        description="Analyze customer data",
        expected_output="Insights from data analysis",
        agent=agent
    )
    
    # Access the fingerprints
    agent_fingerprint = agent.fingerprint
    crew_fingerprint = crew.fingerprint
    task_fingerprint = task.fingerprint
    
    # Print the UUID strings
    print(f"Agent fingerprint: {agent_fingerprint.uuid_str}")
    print(f"Crew fingerprint: {crew_fingerprint.uuid_str}")
    print(f"Task fingerprint: {task_fingerprint.uuid_str}")

### 

​

Working with Fingerprint Metadata

You can add metadata to fingerprints for additional context:
    
    
    # Add metadata to the agent's fingerprint
    agent.security_config.fingerprint.metadata = {
        "version": "1.0",
        "department": "Data Science",
        "project": "Customer Analysis"
    }
    
    # Access the metadata
    print(f"Agent metadata: {agent.fingerprint.metadata}")

## 

​

Fingerprint Persistence

Fingerprints are designed to persist and remain unchanged throughout a component’s lifecycle. If you modify a component, the fingerprint remains the same:
    
    
    original_fingerprint = agent.fingerprint.uuid_str
    
    # Modify the agent
    agent.goal = "New goal for analysis"
    
    # The fingerprint remains unchanged
    assert agent.fingerprint.uuid_str == original_fingerprint

## 

​

Deterministic Fingerprints

While you cannot directly set the UUID and creation timestamp, you can create deterministic fingerprints using the `generate` method with a seed:
    
    
    from crewai.security import Fingerprint
    
    # Create a deterministic fingerprint using a seed string
    deterministic_fingerprint = Fingerprint.generate(seed="my-agent-id")
    
    # The same seed always produces the same fingerprint
    same_fingerprint = Fingerprint.generate(seed="my-agent-id")
    assert deterministic_fingerprint.uuid_str == same_fingerprint.uuid_str
    
    # You can also set metadata
    custom_fingerprint = Fingerprint.generate(
        seed="my-agent-id",
        metadata={"version": "1.0"}
    )

## 

​

Advanced Usage

### 

​

Fingerprint Structure

Each fingerprint has the following structure:
    
    
    from crewai.security import Fingerprint
    
    fingerprint = agent.fingerprint
    
    # UUID string - the unique identifier (auto-generated)
    uuid_str = fingerprint.uuid_str  # e.g., "123e4567-e89b-12d3-a456-426614174000"
    
    # Creation timestamp (auto-generated)
    created_at = fingerprint.created_at  # A datetime object
    
    # Metadata - for additional information (can be customized)
    metadata = fingerprint.metadata  # A dictionary, defaults to {}

Was this page helpful?

YesNo

[Customizing Prompts](/guides/advanced/customizing-prompts)[Agents](/concepts/agents)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Overview
  * How Fingerprints Work
  * Basic Usage
  * Accessing Fingerprints
  * Working with Fingerprint Metadata
  * Fingerprint Persistence
  * Deterministic Fingerprints
  * Advanced Usage
  * Fingerprint Structure



Assistant

Responses are generated using AI and may contain mistakes.


---



## Examples {#examples}

### CrewAI Examples {#crewai-examples}

**Source:** [https://docs.crewai.com/examples/example](https://docs.crewai.com/examples/example)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Examples

CrewAI Examples

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Examples

  * [CrewAI Examples](/examples/example)



Examples

# CrewAI Examples

Copy page

A collection of examples that show how to use CrewAI framework to automate workflows.

## [Marketing StrategyAutomate marketing strategy creation with CrewAI.](https://github.com/crewAIInc/crewAI-examples/tree/main/marketing_strategy)## [Surprise TripCreate a surprise trip itinerary with CrewAI.](https://github.com/crewAIInc/crewAI-examples/tree/main/surprise_trip)## [Match Profile to PositionsMatch a profile to jobpositions with CrewAI.](https://github.com/crewAIInc/crewAI-examples/tree/main/match_profile_to_positions)## [Create Job PostingCreate a job posting with CrewAI.](https://github.com/crewAIInc/crewAI-examples/tree/main/job-posting)## [Game GeneratorCreate a game with CrewAI.](https://github.com/crewAIInc/crewAI-examples/tree/main/game-builder-crew)## [Find Job CandidatesFind job candidates with CrewAI.](https://github.com/crewAIInc/crewAI-examples/tree/main/recruitment)

Was this page helpful?

YesNo

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

Assistant

Responses are generated using AI and may contain mistakes.


---



## How-to Guides {#how-to-guides}

### Introduction {#introduction}

**Source:** [https://docs.crewai.com/how-to/observability](https://docs.crewai.com/how-to/observability)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Get Started

Introduction

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Get Started

# Introduction

Copy page

Build AI agent teams that work together to tackle complex tasks

# 

​

What is CrewAI?

**CrewAI is a lean, lightning-fast Python framework built entirely from scratch—completely independent of LangChain or other agent frameworks.**

CrewAI empowers developers with both high-level simplicity and precise low-level control, ideal for creating autonomous AI agents tailored to any scenario:

  * **[CrewAI Crews](/guides/crews/first-crew)** : Optimize for autonomy and collaborative intelligence, enabling you to create AI teams where each agent has specific roles, tools, and goals.
  * **[CrewAI Flows](/guides/flows/first-flow)** : Enable granular, event-driven control, single LLM calls for precise task orchestration and supports Crews natively.



With over 100,000 developers certified through our community courses, CrewAI is rapidly becoming the standard for enterprise-ready AI automation.

## 

​

How Crews Work

Just like a company has departments (Sales, Engineering, Marketing) working together under leadership to achieve business goals, CrewAI helps you create an organization of AI agents with specialized roles collaborating to accomplish complex tasks.

CrewAI Framework Overview

Component| Description| Key Features  
---|---|---  
**Crew**|  The top-level organization| • Manages AI agent teams  
• Oversees workflows  
• Ensures collaboration  
• Delivers outcomes  
**AI Agents**|  Specialized team members| • Have specific roles (researcher, writer)  
• Use designated tools  
• Can delegate tasks  
• Make autonomous decisions  
**Process**|  Workflow management system| • Defines collaboration patterns  
• Controls task assignments  
• Manages interactions  
• Ensures efficient execution  
**Tasks**|  Individual assignments| • Have clear objectives  
• Use specific tools  
• Feed into larger process  
• Produce actionable results  
  
### 

​

How It All Works Together

  1. The **Crew** organizes the overall operation
  2. **AI Agents** work on their specialized tasks
  3. The **Process** ensures smooth collaboration
  4. **Tasks** get completed to achieve the goal



## 

​

Key Features

## Role-Based Agents

Create specialized agents with defined roles, expertise, and goals - from researchers to analysts to writers

## Flexible Tools

Equip agents with custom tools and APIs to interact with external services and data sources

## Intelligent Collaboration

Agents work together, sharing insights and coordinating tasks to achieve complex objectives

## Task Management

Define sequential or parallel workflows, with agents automatically handling task dependencies

## 

​

How Flows Work

While Crews excel at autonomous collaboration, Flows provide structured automations, offering granular control over workflow execution. Flows ensure tasks are executed reliably, securely, and efficiently, handling conditional logic, loops, and dynamic state management with precision. Flows integrate seamlessly with Crews, enabling you to balance high autonomy with exacting control.

CrewAI Framework Overview

Component| Description| Key Features  
---|---|---  
**Flow**|  Structured workflow orchestration| • Manages execution paths  
• Handles state transitions  
• Controls task sequencing  
• Ensures reliable execution  
**Events**|  Triggers for workflow actions| • Initiate specific processes  
• Enable dynamic responses  
• Support conditional branching  
• Allow for real-time adaptation  
**States**|  Workflow execution contexts| • Maintain execution data  
• Enable persistence  
• Support resumability  
• Ensure execution integrity  
**Crew Support**|  Enhances workflow automation| • Injects pockets of agency when needed  
• Complements structured workflows  
• Balances automation with intelligence  
• Enables adaptive decision-making  
  
### 

​

Key Capabilities

## Event-Driven Orchestration

Define precise execution paths responding dynamically to events

## Fine-Grained Control

Manage workflow states and conditional execution securely and efficiently

## Native Crew Integration

Effortlessly combine with Crews for enhanced autonomy and intelligence

## Deterministic Execution

Ensure predictable outcomes with explicit control flow and error handling

## 

​

When to Use Crews vs. Flows

Understanding when to use [Crews](/guides/crews/first-crew) versus [Flows](/guides/flows/first-flow) is key to maximizing the potential of CrewAI in your applications.

Use Case| Recommended Approach| Why?  
---|---|---  
**Open-ended research**| [Crews](/guides/crews/first-crew)| When tasks require creative thinking, exploration, and adaptation  
**Content generation**| [Crews](/guides/crews/first-crew)| For collaborative creation of articles, reports, or marketing materials  
**Decision workflows**| [Flows](/guides/flows/first-flow)| When you need predictable, auditable decision paths with precise control  
**API orchestration**| [Flows](/guides/flows/first-flow)| For reliable integration with multiple external services in a specific sequence  
**Hybrid applications**|  Combined approach| Use [Flows](/guides/flows/first-flow) to orchestrate overall process with [Crews](/guides/crews/first-crew) handling complex subtasks  
  
### 

​

Decision Framework

  * **Choose[Crews](/guides/crews/first-crew) when:** You need autonomous problem-solving, creative collaboration, or exploratory tasks
  * **Choose[Flows](/guides/flows/first-flow) when:** You require deterministic outcomes, auditability, or precise control over execution
  * **Combine both when:** Your application needs both structured processes and pockets of autonomous intelligence



## 

​

Why Choose CrewAI?

  * 🧠 **Autonomous Operation** : Agents make intelligent decisions based on their roles and available tools
  * 📝 **Natural Interaction** : Agents communicate and collaborate like human team members
  * 🛠️ **Extensible Design** : Easy to add new tools, roles, and capabilities
  * 🚀 **Production Ready** : Built for reliability and scalability in real-world applications
  * 🔒 **Security-Focused** : Designed with enterprise security requirements in mind
  * 💰 **Cost-Efficient** : Optimized to minimize token usage and API calls



## 

​

Ready to Start Building?

## [Build Your First CrewStep-by-step tutorial to create a collaborative AI team that works together to solve complex problems.](/guides/crews/first-crew)## [Build Your First FlowLearn how to create structured, event-driven workflows with precise control over execution.](/guides/flows/first-flow)

## [Install CrewAIGet started with CrewAI in your development environment.](/installation)## [Quick StartFollow our quickstart guide to create your first CrewAI agent and get hands-on experience.](/quickstart)## [Join the CommunityConnect with other developers, get help, and share your CrewAI experiences.](https://community.crewai.com)

Was this page helpful?

YesNo

[Installation](/installation)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * What is CrewAI?
  * How Crews Work
  * How It All Works Together
  * Key Features
  * How Flows Work
  * Key Capabilities
  * When to Use Crews vs. Flows
  * Decision Framework
  * Why Choose CrewAI?
  * Ready to Start Building?



Assistant

Responses are generated using AI and may contain mistakes.


---



## Other {#other}

### Opik Integration {#opik-integration}

**Source:** [https://docs.crewai.com/observability/opik](https://docs.crewai.com/observability/opik)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Observability

Opik Integration

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Observability

# Opik Integration

Copy page

Learn how to use Comet Opik to debug, evaluate, and monitor your CrewAI applications with comprehensive tracing, automated evaluations, and production-ready dashboards.

# 

​

Opik Overview

With [Comet Opik](https://www.comet.com/docs/opik/), debug, evaluate, and monitor your LLM applications, RAG systems, and agentic workflows with comprehensive tracing, automated evaluations, and production-ready dashboards.

Opik Agent Dashboard

Opik provides comprehensive support for every stage of your CrewAI application development:

  * **Log Traces and Spans** : Automatically track LLM calls and application logic to debug and analyze development and production systems. Manually or programmatically annotate, view, and compare responses across projects.
  * **Evaluate Your LLM Application’s Performance** : Evaluate against a custom test set and run built-in evaluation metrics or define your own metrics in the SDK or UI.
  * **Test Within Your CI/CD Pipeline** : Establish reliable performance baselines with Opik’s LLM unit tests, built on PyTest. Run online evaluations for continuous monitoring in production.
  * **Monitor & Analyze Production Data**: Understand your models’ performance on unseen data in production and generate datasets for new dev iterations.



## 

​

Setup

Comet provides a hosted version of the Opik platform, or you can run the platform locally.

To use the hosted version, simply [create a free Comet account](https://www.comet.com/signup?utm_medium=github&utm_source=crewai_docs) and grab you API Key.

To run the Opik platform locally, see our [installation guide](https://www.comet.com/docs/opik/self-host/overview/) for more information.

For this guide we will use CrewAI’s quickstart example.

1

Install required packages
    
    
    pip install crewai crewai-tools opik --upgrade

2

Configure Opik
    
    
    import opik
    opik.configure(use_local=False)

3

Prepare environment

First, we set up our API keys for our LLM-provider as environment variables:
    
    
    import os
    import getpass
    
    if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

4

Using CrewAI

The first step is to create our project. We will use an example from CrewAI’s documentation:
    
    
    from crewai import Agent, Crew, Task, Process
    
    
    class YourCrewName:
        def agent_one(self) -> Agent:
            return Agent(
                role="Data Analyst",
                goal="Analyze data trends in the market",
                backstory="An experienced data analyst with a background in economics",
                verbose=True,
            )
    
        def agent_two(self) -> Agent:
            return Agent(
                role="Market Researcher",
                goal="Gather information on market dynamics",
                backstory="A diligent researcher with a keen eye for detail",
                verbose=True,
            )
    
        def task_one(self) -> Task:
            return Task(
                name="Collect Data Task",
                description="Collect recent market data and identify trends.",
                expected_output="A report summarizing key trends in the market.",
                agent=self.agent_one(),
            )
    
        def task_two(self) -> Task:
            return Task(
                name="Market Research Task",
                description="Research factors affecting market dynamics.",
                expected_output="An analysis of factors influencing the market.",
                agent=self.agent_two(),
            )
    
        def crew(self) -> Crew:
            return Crew(
                agents=[self.agent_one(), self.agent_two()],
                tasks=[self.task_one(), self.task_two()],
                process=Process.sequential,
                verbose=True,
            )

Now we can import Opik’s tracker and run our crew:
    
    
    from opik.integrations.crewai import track_crewai
    
    track_crewai(project_name="crewai-integration-demo")
    
    my_crew = YourCrewName().crew()
    result = my_crew.kickoff()
    
    print(result)

After running your CrewAI application, visit the Opik app to view:

  * LLM traces, spans, and their metadata
  * Agent interactions and task execution flow
  * Performance metrics like latency and token usage
  * Evaluation metrics (built-in or custom)



## 

​

Resources

  * [🦉 Opik Documentation](https://www.comet.com/docs/opik/)
  * [👉 Opik + CrewAI Colab](https://colab.research.google.com/github/comet-ml/opik/blob/main/apps/opik-documentation/documentation/docs/cookbook/crewai.ipynb)
  * [🐦 X](https://x.com/cometml)
  * [💬 Slack](https://slack.comet.com/)



Was this page helpful?

YesNo

[OpenLIT Integration](/observability/openlit)[Patronus AI Evaluation](/observability/patronus-evaluation)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Opik Overview
  * Setup
  * Resources



Assistant

Responses are generated using AI and may contain mistakes.


---

### Patronus AI Evaluation {#patronus-ai-evaluation}

**Source:** [https://docs.crewai.com/observability/patronus-evaluation](https://docs.crewai.com/observability/patronus-evaluation)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Observability

Patronus AI Evaluation

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Observability

# Patronus AI Evaluation

Copy page

Monitor and evaluate CrewAI agent performance using Patronus AI’s comprehensive evaluation platform for LLM outputs and agent behaviors.

# 

​

Patronus AI Evaluation

## 

​

Overview

[Patronus AI](https://patronus.ai) provides comprehensive evaluation and monitoring capabilities for CrewAI agents, enabling you to assess model outputs, agent behaviors, and overall system performance. This integration allows you to implement continuous evaluation workflows that help maintain quality and reliability in production environments.

## 

​

Key Features

  * **Automated Evaluation** : Real-time assessment of agent outputs and behaviors
  * **Custom Criteria** : Define specific evaluation criteria tailored to your use cases
  * **Performance Monitoring** : Track agent performance metrics over time
  * **Quality Assurance** : Ensure consistent output quality across different scenarios
  * **Safety & Compliance**: Monitor for potential issues and policy violations



## 

​

Evaluation Tools

Patronus provides three main evaluation tools for different use cases:

  1. **PatronusEvalTool** : Allows agents to select the most appropriate evaluator and criteria for the evaluation task.
  2. **PatronusPredefinedCriteriaEvalTool** : Uses predefined evaluator and criteria specified by the user.
  3. **PatronusLocalEvaluatorTool** : Uses custom function evaluators defined by the user.



## 

​

Installation

To use these tools, you need to install the Patronus package:
    
    
    uv add patronus

You’ll also need to set up your Patronus API key as an environment variable:
    
    
    export PATRONUS_API_KEY="your_patronus_api_key"

## 

​

Steps to Get Started

To effectively use the Patronus evaluation tools, follow these steps:

  1. **Install Patronus** : Install the Patronus package using the command above.
  2. **Set Up API Key** : Set your Patronus API key as an environment variable.
  3. **Choose the Right Tool** : Select the appropriate Patronus evaluation tool based on your needs.
  4. **Configure the Tool** : Configure the tool with the necessary parameters.



## 

​

Examples

### 

​

Using PatronusEvalTool

The following example demonstrates how to use the `PatronusEvalTool`, which allows agents to select the most appropriate evaluator and criteria:

Code
    
    
    from crewai import Agent, Task, Crew
    from crewai_tools import PatronusEvalTool
    
    # Initialize the tool
    patronus_eval_tool = PatronusEvalTool()
    
    # Define an agent that uses the tool
    coding_agent = Agent(
        role="Coding Agent",
        goal="Generate high quality code and verify that the output is code",
        backstory="An experienced coder who can generate high quality python code.",
        tools=[patronus_eval_tool],
        verbose=True,
    )
    
    # Example task to generate and evaluate code
    generate_code_task = Task(
        description="Create a simple program to generate the first N numbers in the Fibonacci sequence. Select the most appropriate evaluator and criteria for evaluating your output.",
        expected_output="Program that generates the first N numbers in the Fibonacci sequence.",
        agent=coding_agent,
    )
    
    # Create and run the crew
    crew = Crew(agents=[coding_agent], tasks=[generate_code_task])
    result = crew.kickoff()

### 

​

Using PatronusPredefinedCriteriaEvalTool

The following example demonstrates how to use the `PatronusPredefinedCriteriaEvalTool`, which uses predefined evaluator and criteria:

Code
    
    
    from crewai import Agent, Task, Crew
    from crewai_tools import PatronusPredefinedCriteriaEvalTool
    
    # Initialize the tool with predefined criteria
    patronus_eval_tool = PatronusPredefinedCriteriaEvalTool(
        evaluators=[{"evaluator": "judge", "criteria": "contains-code"}]
    )
    
    # Define an agent that uses the tool
    coding_agent = Agent(
        role="Coding Agent",
        goal="Generate high quality code",
        backstory="An experienced coder who can generate high quality python code.",
        tools=[patronus_eval_tool],
        verbose=True,
    )
    
    # Example task to generate code
    generate_code_task = Task(
        description="Create a simple program to generate the first N numbers in the Fibonacci sequence.",
        expected_output="Program that generates the first N numbers in the Fibonacci sequence.",
        agent=coding_agent,
    )
    
    # Create and run the crew
    crew = Crew(agents=[coding_agent], tasks=[generate_code_task])
    result = crew.kickoff()

### 

​

Using PatronusLocalEvaluatorTool

The following example demonstrates how to use the `PatronusLocalEvaluatorTool`, which uses custom function evaluators:

Code
    
    
    from crewai import Agent, Task, Crew
    from crewai_tools import PatronusLocalEvaluatorTool
    from patronus import Client, EvaluationResult
    import random
    
    # Initialize the Patronus client
    client = Client()
    
    # Register a custom evaluator
    @client.register_local_evaluator("random_evaluator")
    def random_evaluator(**kwargs):
        score = random.random()
        return EvaluationResult(
            score_raw=score,
            pass_=score >= 0.5,
            explanation="example explanation",
        )
    
    # Initialize the tool with the custom evaluator
    patronus_eval_tool = PatronusLocalEvaluatorTool(
        patronus_client=client,
        evaluator="random_evaluator",
        evaluated_model_gold_answer="example label",
    )
    
    # Define an agent that uses the tool
    coding_agent = Agent(
        role="Coding Agent",
        goal="Generate high quality code",
        backstory="An experienced coder who can generate high quality python code.",
        tools=[patronus_eval_tool],
        verbose=True,
    )
    
    # Example task to generate code
    generate_code_task = Task(
        description="Create a simple program to generate the first N numbers in the Fibonacci sequence.",
        expected_output="Program that generates the first N numbers in the Fibonacci sequence.",
        agent=coding_agent,
    )
    
    # Create and run the crew
    crew = Crew(agents=[coding_agent], tasks=[generate_code_task])
    result = crew.kickoff()

## 

​

Parameters

### 

​

PatronusEvalTool

The `PatronusEvalTool` does not require any parameters during initialization. It automatically fetches available evaluators and criteria from the Patronus API.

### 

​

PatronusPredefinedCriteriaEvalTool

The `PatronusPredefinedCriteriaEvalTool` accepts the following parameters during initialization:

  * **evaluators** : Required. A list of dictionaries containing the evaluator and criteria to use. For example: `[{"evaluator": "judge", "criteria": "contains-code"}]`.



### 

​

PatronusLocalEvaluatorTool

The `PatronusLocalEvaluatorTool` accepts the following parameters during initialization:

  * **patronus_client** : Required. The Patronus client instance.
  * **evaluator** : Optional. The name of the registered local evaluator to use. Default is an empty string.
  * **evaluated_model_gold_answer** : Optional. The gold answer to use for evaluation. Default is an empty string.



## 

​

Usage

When using the Patronus evaluation tools, you provide the model input, output, and context, and the tool returns the evaluation results from the Patronus API.

For the `PatronusEvalTool` and `PatronusPredefinedCriteriaEvalTool`, the following parameters are required when calling the tool:

  * **evaluated_model_input** : The agent’s task description in simple text.
  * **evaluated_model_output** : The agent’s output of the task.
  * **evaluated_model_retrieved_context** : The agent’s context.



For the `PatronusLocalEvaluatorTool`, the same parameters are required, but the evaluator and gold answer are specified during initialization.

## 

​

Conclusion

The Patronus evaluation tools provide a powerful way to evaluate and score model inputs and outputs using the Patronus AI platform. By enabling agents to evaluate their own outputs or the outputs of other agents, these tools can help improve the quality and reliability of CrewAI workflows.

Was this page helpful?

YesNo

[Opik Integration](/observability/opik)[Portkey Integration](/observability/portkey)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Patronus AI Evaluation
  * Overview
  * Key Features
  * Evaluation Tools
  * Installation
  * Steps to Get Started
  * Examples
  * Using PatronusEvalTool
  * Using PatronusPredefinedCriteriaEvalTool
  * Using PatronusLocalEvaluatorTool
  * Parameters
  * PatronusEvalTool
  * PatronusPredefinedCriteriaEvalTool
  * PatronusLocalEvaluatorTool
  * Usage
  * Conclusion



Assistant

Responses are generated using AI and may contain mistakes.


---

### Telemetry {#telemetry}

**Source:** [https://docs.crewai.com/telemetry](https://docs.crewai.com/telemetry)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Telemetry

Telemetry

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Telemetry

# Telemetry

Copy page

Understanding the telemetry data collected by CrewAI and how it contributes to the enhancement of the library.

## 

​

Telemetry

By default, we collect no data that would be considered personal information under GDPR and other privacy regulations. We do collect Tool’s names and Agent’s roles, so be advised not to include any personal information in the tool’s names or the Agent’s roles. Because no personal information is collected, it’s not necessary to worry about data residency. When `share_crew` is enabled, additional data is collected which may contain personal information if included by the user. Users should exercise caution when enabling this feature to ensure compliance with privacy regulations.

CrewAI utilizes anonymous telemetry to gather usage statistics with the primary goal of enhancing the library. Our focus is on improving and developing the features, integrations, and tools most utilized by our users.

It’s pivotal to understand that by default, **NO personal data is collected** concerning prompts, task descriptions, agents’ backstories or goals, usage of tools, API calls, responses, any data processed by the agents, or secrets and environment variables. When the `share_crew` feature is enabled, detailed data including task descriptions, agents’ backstories or goals, and other specific attributes are collected to provide deeper insights. This expanded data collection may include personal information if users have incorporated it into their crews or tasks. Users should carefully consider the content of their crews and tasks before enabling `share_crew`. Users can disable telemetry by setting the environment variable `CREWAI_DISABLE_TELEMETRY` to `true` or by setting `OTEL_SDK_DISABLED` to `true` (note that the latter disables all OpenTelemetry instrumentation globally).

### 

​

Examples:
    
    
    # Disable CrewAI telemetry only
    os.environ['CREWAI_DISABLE_TELEMETRY'] = 'true'
    
    # Disable all OpenTelemetry (including CrewAI)
    os.environ['OTEL_SDK_DISABLED'] = 'true'

### 

​

Data Explanation:

Defaulted| Data| Reason and Specifics  
---|---|---  
Yes| CrewAI and Python Version| Tracks software versions. Example: CrewAI v1.2.3, Python 3.8.10. No personal data.  
Yes| Crew Metadata| Includes: randomly generated key and ID, process type (e.g., ‘sequential’, ‘parallel’), boolean flag for memory usage (true/false), count of tasks, count of agents. All non-personal.  
Yes| Agent Data| Includes: randomly generated key and ID, role name (should not include personal info), boolean settings (verbose, delegation enabled, code execution allowed), max iterations, max RPM, max retry limit, LLM info (see LLM Attributes), list of tool names (should not include personal info). No personal data.  
Yes| Task Metadata| Includes: randomly generated key and ID, boolean execution settings (async_execution, human_input), associated agent’s role and key, list of tool names. All non-personal.  
Yes| Tool Usage Statistics| Includes: tool name (should not include personal info), number of usage attempts (integer), LLM attributes used. No personal data.  
Yes| Test Execution Data| Includes: crew’s randomly generated key and ID, number of iterations, model name used, quality score (float), execution time (in seconds). All non-personal.  
Yes| Task Lifecycle Data| Includes: creation and execution start/end times, crew and task identifiers. Stored as spans with timestamps. No personal data.  
Yes| LLM Attributes| Includes: name, model_name, model, top_k, temperature, and class name of the LLM. All technical, non-personal data.  
Yes| Crew Deployment attempt using crewAI CLI| Includes: The fact a deploy is being made and crew id, and if it’s trying to pull logs, no other data.  
No| Agent’s Expanded Data| Includes: goal description, backstory text, i18n prompt file identifier. Users should ensure no personal info is included in text fields.  
No| Detailed Task Information| Includes: task description, expected output description, context references. Users should ensure no personal info is included in these fields.  
No| Environment Information| Includes: platform, release, system, version, and CPU count. Example: ‘Windows 10’, ‘x86_64’. No personal data.  
No| Crew and Task Inputs and Outputs| Includes: input parameters and output results as non-identifiable data. Users should ensure no personal info is included.  
No| Comprehensive Crew Execution Data| Includes: detailed logs of crew operations, all agents and tasks data, final output. All non-personal and technical in nature.  
  
“No” in the “Defaulted” column indicates that this data is only collected when `share_crew` is set to `true`.

### 

​

Opt-In Further Telemetry Sharing

Users can choose to share their complete telemetry data by enabling the `share_crew` attribute to `True` in their crew configurations. Enabling `share_crew` results in the collection of detailed crew and task execution data, including `goal`, `backstory`, `context`, and `output` of tasks. This enables a deeper insight into usage patterns.

If you enable `share_crew`, the collected data may include personal information if it has been incorporated into crew configurations, task descriptions, or outputs. Users should carefully review their data and ensure compliance with GDPR and other applicable privacy regulations before enabling this feature.

Was this page helpful?

YesNo

[Using Annotations in crew.py](/learn/using-annotations)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Telemetry
  * Examples:
  * Data Explanation:
  * Opt-In Further Telemetry Sharing



Assistant

Responses are generated using AI and may contain mistakes.


---

### Arize Phoenix {#arize-phoenix}

**Source:** [https://docs.crewai.com/observability/arize-phoenix](https://docs.crewai.com/observability/arize-phoenix)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Observability

Arize Phoenix

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Observability

# Arize Phoenix

Copy page

Arize Phoenix integration for CrewAI with OpenTelemetry and OpenInference

# 

​

Arize Phoenix Integration

This guide demonstrates how to integrate **Arize Phoenix** with **CrewAI** using OpenTelemetry via the [OpenInference](https://github.com/openinference/openinference) SDK. By the end of this guide, you will be able to trace your CrewAI agents and easily debug your agents.

> **What is Arize Phoenix?** [Arize Phoenix](https://phoenix.arize.com) is an LLM observability platform that provides tracing and evaluation for AI applications.

[](https://www.youtube.com/watch?v=Yc5q3l6F7Ww)

## 

​

Get Started

We’ll walk through a simple example of using CrewAI and integrating it with Arize Phoenix via OpenTelemetry using OpenInference.

You can also access this guide on [Google Colab](https://colab.research.google.com/github/Arize-ai/phoenix/blob/main/tutorials/tracing/crewai_tracing_tutorial.ipynb).

### 

​

Step 1: Install Dependencies
    
    
    pip install openinference-instrumentation-crewai crewai crewai-tools arize-phoenix-otel

### 

​

Step 2: Set Up Environment Variables

Setup Phoenix Cloud API keys and configure OpenTelemetry to send traces to Phoenix. Phoenix Cloud is a hosted version of Arize Phoenix, but it is not required to use this integration.

You can get your free Serper API key [here](https://serper.dev/).
    
    
    import os
    from getpass import getpass
    
    # Get your Phoenix Cloud credentials
    PHOENIX_API_KEY = getpass("🔑 Enter your Phoenix Cloud API Key: ")
    
    # Get API keys for services
    OPENAI_API_KEY = getpass("🔑 Enter your OpenAI API key: ")
    SERPER_API_KEY = getpass("🔑 Enter your Serper API key: ")
    
    # Set environment variables
    os.environ["PHOENIX_CLIENT_HEADERS"] = f"api_key={PHOENIX_API_KEY}"
    os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "https://app.phoenix.arize.com" # Phoenix Cloud, change this to your own endpoint if you are using a self-hosted instance
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    os.environ["SERPER_API_KEY"] = SERPER_API_KEY

### 

​

Step 3: Initialize OpenTelemetry with Phoenix

Initialize the OpenInference OpenTelemetry instrumentation SDK to start capturing traces and send them to Phoenix.
    
    
    from phoenix.otel import register
    
    tracer_provider = register(
        project_name="crewai-tracing-demo",
        auto_instrument=True,
    )

### 

​

Step 4: Create a CrewAI Application

We’ll create a CrewAI application where two agents collaborate to research and write a blog post about AI advancements.
    
    
    from crewai import Agent, Crew, Process, Task
    from crewai_tools import SerperDevTool
    from openinference.instrumentation.crewai import CrewAIInstrumentor
    from phoenix.otel import register
    
    # setup monitoring for your crew
    tracer_provider = register(
        endpoint="http://localhost:6006/v1/traces")
    CrewAIInstrumentor().instrument(skip_dep_check=True, tracer_provider=tracer_provider)
    search_tool = SerperDevTool()
    
    # Define your agents with roles and goals
    researcher = Agent(
        role="Senior Research Analyst",
        goal="Uncover cutting-edge developments in AI and data science",
        backstory="""You work at a leading tech think tank.
        Your expertise lies in identifying emerging trends.
        You have a knack for dissecting complex data and presenting actionable insights.""",
        verbose=True,
        allow_delegation=False,
        # You can pass an optional llm attribute specifying what model you wanna use.
        # llm=ChatOpenAI(model_name="gpt-3.5", temperature=0.7),
        tools=[search_tool],
    )
    writer = Agent(
        role="Tech Content Strategist",
        goal="Craft compelling content on tech advancements",
        backstory="""You are a renowned Content Strategist, known for your insightful and engaging articles.
        You transform complex concepts into compelling narratives.""",
        verbose=True,
        allow_delegation=True,
    )
    
    # Create tasks for your agents
    task1 = Task(
        description="""Conduct a comprehensive analysis of the latest advancements in AI in 2024.
        Identify key trends, breakthrough technologies, and potential industry impacts.""",
        expected_output="Full analysis report in bullet points",
        agent=researcher,
    )
    
    task2 = Task(
        description="""Using the insights provided, develop an engaging blog
        post that highlights the most significant AI advancements.
        Your post should be informative yet accessible, catering to a tech-savvy audience.
        Make it sound cool, avoid complex words so it doesn't sound like AI.""",
        expected_output="Full blog post of at least 4 paragraphs",
        agent=writer,
    )
    
    # Instantiate your crew with a sequential process
    crew = Crew(
        agents=[researcher, writer], tasks=[task1, task2], verbose=1, process=Process.sequential
    )
    
    # Get your crew to work!
    result = crew.kickoff()
    
    print("######################")
    print(result)

### 

​

Step 5: View Traces in Phoenix

After running the agent, you can view the traces generated by your CrewAI application in Phoenix. You should see detailed steps of the agent interactions and LLM calls, which can help you debug and optimize your AI agents.

Log into your Phoenix Cloud account and navigate to the project you specified in the `project_name` parameter. You’ll see a timeline view of your trace with all the agent interactions, tool usages, and LLM calls.

### 

​

Version Compatibility Information

  * Python 3.8+
  * CrewAI >= 0.86.0
  * Arize Phoenix >= 7.0.1
  * OpenTelemetry SDK >= 1.31.0



### 

​

References

  * [Phoenix Documentation](https://docs.arize.com/phoenix/) \- Overview of the Phoenix platform.
  * [CrewAI Documentation](https://docs.crewai.com/) \- Overview of the CrewAI framework.
  * [OpenTelemetry Docs](https://opentelemetry.io/docs/) \- OpenTelemetry guide
  * [OpenInference GitHub](https://github.com/openinference/openinference) \- Source code for OpenInference SDK.



Was this page helpful?

YesNo

[AgentOps Integration](/observability/agentops)[Langfuse Integration](/observability/langfuse)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Arize Phoenix Integration
  * Get Started
  * Step 1: Install Dependencies
  * Step 2: Set Up Environment Variables
  * Step 3: Initialize OpenTelemetry with Phoenix
  * Step 4: Create a CrewAI Application
  * Step 5: View Traces in Phoenix
  * Version Compatibility Information
  * References



Assistant

Responses are generated using AI and may contain mistakes.


---

### Langtrace Integration {#langtrace-integration}

**Source:** [https://docs.crewai.com/observability/langtrace](https://docs.crewai.com/observability/langtrace)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Observability

Langtrace Integration

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Observability

# Langtrace Integration

Copy page

How to monitor cost, latency, and performance of CrewAI Agents using Langtrace, an external observability tool.

# 

​

Langtrace Overview

Langtrace is an open-source, external tool that helps you set up observability and evaluations for Large Language Models (LLMs), LLM frameworks, and Vector Databases. While not built directly into CrewAI, Langtrace can be used alongside CrewAI to gain deep visibility into the cost, latency, and performance of your CrewAI Agents. This integration allows you to log hyperparameters, monitor performance regressions, and establish a process for continuous improvement of your Agents.

## 

​

Setup Instructions

1

Sign up for Langtrace

Sign up by visiting <https://langtrace.ai/signup>.

2

Create a project

Set the project type to `CrewAI` and generate an API key.

3

Install Langtrace in your CrewAI project

Use the following command:
    
    
    pip install langtrace-python-sdk

4

Import Langtrace

Import and initialize Langtrace at the beginning of your script, before any CrewAI imports:
    
    
    from langtrace_python_sdk import langtrace
    langtrace.init(api_key='<LANGTRACE_API_KEY>')
    
    # Now import CrewAI modules
    from crewai import Agent, Task, Crew

### 

​

Features and Their Application to CrewAI

  1. **LLM Token and Cost Tracking**

     * Monitor the token usage and associated costs for each CrewAI agent interaction.
  2. **Trace Graph for Execution Steps**

     * Visualize the execution flow of your CrewAI tasks, including latency and logs.
     * Useful for identifying bottlenecks in your agent workflows.
  3. **Dataset Curation with Manual Annotation**

     * Create datasets from your CrewAI task outputs for future training or evaluation.
  4. **Prompt Versioning and Management**

     * Keep track of different versions of prompts used in your CrewAI agents.
     * Useful for A/B testing and optimizing agent performance.
  5. **Prompt Playground with Model Comparisons**

     * Test and compare different prompts and models for your CrewAI agents before deployment.
  6. **Testing and Evaluations**

     * Set up automated tests for your CrewAI agents and tasks.



Was this page helpful?

YesNo

[Langfuse Integration](/observability/langfuse)[MLflow Integration](/observability/mlflow)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Langtrace Overview
  * Setup Instructions
  * Features and Their Application to CrewAI



Assistant

Responses are generated using AI and may contain mistakes.


---

### SSE Transport {#sse-transport}

**Source:** [https://docs.crewai.com/mcp/sse](https://docs.crewai.com/mcp/sse)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

MCP Integration

SSE Transport

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



MCP Integration

# SSE Transport

Copy page

Learn how to connect CrewAI to remote MCP servers using Server-Sent Events (SSE) for real-time communication.

## 

​

Overview

Server-Sent Events (SSE) provide a standard way for a web server to send updates to a client over a single, long-lived HTTP connection. In the context of MCP, SSE is used for remote servers to stream data (like tool responses) to your CrewAI application in real-time.

## 

​

Key Concepts

  * **Remote Servers** : SSE is suitable for MCP servers hosted remotely.
  * **Unidirectional Stream** : Typically, SSE is a one-way communication channel from server to client.
  * **`MCPServerAdapter` Configuration**: For SSE, you’ll provide the server’s URL and specify the transport type.



## 

​

Connecting via SSE

You can connect to an SSE-based MCP server using two main approaches for managing the connection lifecycle:

### 

​

1\. Fully Managed Connection (Recommended)

Using a Python context manager (`with` statement) is the recommended approach. It automatically handles establishing and closing the connection to the SSE MCP server.
    
    
    from crewai import Agent, Task, Crew, Process
    from crewai_tools import MCPServerAdapter
    
    server_params = {
        "url": "http://localhost:8000/sse", # Replace with your actual SSE server URL
        "transport": "sse" 
    }
    
    # Using MCPServerAdapter with a context manager
    try:
        with MCPServerAdapter(server_params) as tools:
            print(f"Available tools from SSE MCP server: {[tool.name for tool in tools]}")
    
            # Example: Using a tool from the SSE MCP server
            sse_agent = Agent(
                role="Remote Service User",
                goal="Utilize a tool provided by a remote SSE MCP server.",
                backstory="An AI agent that connects to external services via SSE.",
                tools=tools,
                reasoning=True,
                verbose=True,
            )
    
            sse_task = Task(
                description="Fetch real-time stock updates for 'AAPL' using an SSE tool.",
                expected_output="The latest stock price for AAPL.",
                agent=sse_agent,
                markdown=True
            )
    
            sse_crew = Crew(
                agents=[sse_agent],
                tasks=[sse_task],
                verbose=True,
                process=Process.sequential
            )
            
            if tools: # Only kickoff if tools were loaded
                result = sse_crew.kickoff() # Add inputs={'stock_symbol': 'AAPL'} if tool requires it
                print("\nCrew Task Result (SSE - Managed):\n", result)
            else:
                print("Skipping crew kickoff as tools were not loaded (check server connection).")
    
    except Exception as e:
        print(f"Error connecting to or using SSE MCP server (Managed): {e}")
        print("Ensure the SSE MCP server is running and accessible at the specified URL.")

Replace `"http://localhost:8000/sse"` with the actual URL of your SSE MCP server.

### 

​

2\. Manual Connection Lifecycle

If you need finer-grained control, you can manage the `MCPServerAdapter` connection lifecycle manually.

You **MUST** call `mcp_server_adapter.stop()` to ensure the connection is closed and resources are released. Using a `try...finally` block is highly recommended.
    
    
    from crewai import Agent, Task, Crew, Process
    from crewai_tools import MCPServerAdapter
    
    server_params = {
        "url": "http://localhost:8000/sse", # Replace with your actual SSE server URL
        "transport": "sse"
    }
    
    mcp_server_adapter = None 
    try:
        mcp_server_adapter = MCPServerAdapter(server_params)
        mcp_server_adapter.start()
        tools = mcp_server_adapter.tools
        print(f"Available tools (manual SSE): {[tool.name for tool in tools]}")
    
        manual_sse_agent = Agent(
            role="Remote Data Analyst",
            goal="Analyze data fetched from a remote SSE MCP server using manual connection management.",
            backstory="An AI skilled in handling SSE connections explicitly.",
            tools=tools,
            verbose=True
        )
        
        analysis_task = Task(
            description="Fetch and analyze the latest user activity trends from the SSE server.",
            expected_output="A summary report of user activity trends.",
            agent=manual_sse_agent
        )
        
        analysis_crew = Crew(
            agents=[manual_sse_agent],
            tasks=[analysis_task],
            verbose=True,
            process=Process.sequential
        )
        
        result = analysis_crew.kickoff()
        print("\nCrew Task Result (SSE - Manual):\n", result)
    
    except Exception as e:
        print(f"An error occurred during manual SSE MCP integration: {e}")
        print("Ensure the SSE MCP server is running and accessible.")
    finally:
        if mcp_server_adapter and mcp_server_adapter.is_connected:
            print("Stopping SSE MCP server connection (manual)...")
            mcp_server_adapter.stop()  # **Crucial: Ensure stop is called**
        elif mcp_server_adapter:
            print("SSE MCP server adapter was not connected. No stop needed or start failed.")

## 

​

Security Considerations for SSE

**DNS Rebinding Attacks** : SSE transports can be vulnerable to DNS rebinding attacks if the MCP server is not properly secured. This could allow malicious websites to interact with local or intranet-based MCP servers.

To mitigate this risk:

  * MCP server implementations should **validate`Origin` headers** on incoming SSE connections.
  * When running local SSE MCP servers for development, **bind only to`localhost` (`127.0.0.1`)** rather than all network interfaces (`0.0.0.0`).
  * Implement **proper authentication** for all SSE connections if they expose sensitive tools or data.



For a comprehensive overview of security best practices, please refer to our [Security Considerations](./security.mdx) page and the official [MCP Transport Security documentation](https://modelcontextprotocol.io/docs/concepts/transports#security-considerations).

Was this page helpful?

YesNo

[Stdio Transport](/mcp/stdio)[Streamable HTTP Transport](/mcp/streamable-http)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Overview
  * Key Concepts
  * Connecting via SSE
  * 1\. Fully Managed Connection (Recommended)
  * 2\. Manual Connection Lifecycle
  * Security Considerations for SSE



Assistant

Responses are generated using AI and may contain mistakes.


---

### MCP Security Considerations {#mcp-security-considerations}

**Source:** [https://docs.crewai.com/mcp/security](https://docs.crewai.com/mcp/security)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

MCP Integration

MCP Security Considerations

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



MCP Integration

# MCP Security Considerations

Copy page

Learn about important security best practices when integrating MCP servers with your CrewAI agents.

## 

​

Overview

The most critical aspect of MCP security is **trust**. You should **only** connect your CrewAI agents to MCP servers that you fully trust.

When integrating external services like MCP (Model Context Protocol) servers into your CrewAI agents, security is paramount. MCP servers can execute code, access data, or interact with other systems based on the tools they expose. It’s crucial to understand the implications and follow best practices to protect your applications and data.

### 

​

Risks

  * Execute arbitrary code on the machine where the agent is running (especially with `Stdio` transport if the server can control the command executed).
  * Expose sensitive data from your agent or its environment.
  * Manipulate your agent’s behavior in unintended ways, including making unauthorized API calls on your behalf.
  * Hijack your agent’s reasoning process through sophisticated prompt injection techniques (see below).



### 

​

1\. Trusting MCP Servers

**Only connect to MCP servers that you trust.**

Before configuring `MCPServerAdapter` to connect to an MCP server, ensure you know:

  * **Who operates the server?** Is it a known, reputable service, or an internal server under your control?
  * **What tools does it expose?** Understand the capabilities of the tools. Could they be misused if an attacker gained control or if the server itself is malicious?
  * **What data does it access or process?** Be aware of any sensitive information that might be sent to or handled by the MCP server.



Avoid connecting to unknown or unverified MCP servers, especially if your agents handle sensitive tasks or data.

### 

​

2\. Secure Prompt Injection via Tool Metadata: The “Model Control Protocol” Risk

A significant and subtle risk is the potential for prompt injection through tool metadata. Here’s how it works:

  1. When your CrewAI agent connects to an MCP server, it typically requests a list of available tools.
  2. The MCP server responds with metadata for each tool, including its name, description, and parameter descriptions.
  3. Your agent’s underlying Language Model (LLM) uses this metadata to understand how and when to use the tools. This metadata is often incorporated into the LLM’s system prompt or context.
  4. A malicious MCP server can craft its tool metadata (names, descriptions) to include hidden or overt instructions. These instructions can act as a prompt injection, effectively telling your LLM to behave in a certain way, reveal sensitive information, or perform malicious actions.



**Crucially, this attack can occur simply by connecting to a malicious server and listing its tools, even if your agent never explicitly decides to _use_ any of those tools.** The mere exposure to the malicious metadata can be enough to compromise the agent’s behavior.

**Mitigation:**

  * **Extreme Caution with Untrusted Servers:** Reiterate: _Do not connect to MCP servers you do not fully trust._ The risk of metadata injection makes this paramount.



### 

​

Stdio Transport Security

Stdio (Standard Input/Output) transport is typically used for local MCP servers running on the same machine as your CrewAI application.

  * **Process Isolation** : While generally safer as it doesn’t involve network exposure by default, ensure the script or command run by `StdioServerParameters` is from a trusted source and has appropriate file system permissions. A malicious Stdio server script could still harm your local system.
  * **Input Sanitization** : If your Stdio server script takes complex inputs derived from agent interactions, ensure the script itself sanitizes these inputs to prevent command injection or other vulnerabilities within the script’s logic.
  * **Resource Limits** : Be mindful that a local Stdio server process consumes local resources (CPU, memory). Ensure it’s well-behaved and won’t exhaust system resources.



### 

​

Confused Deputy Attacks

The [Confused Deputy Problem](https://en.wikipedia.org/wiki/Confused_deputy_problem) is a classic security vulnerability that can manifest in MCP integrations, especially when an MCP server acts as a proxy to other third-party services (e.g., Google Calendar, GitHub) that use OAuth 2.0 for authorization.

**Scenario:**

  1. An MCP server (let’s call it `MCP-Proxy`) allows your agent to interact with `ThirdPartyAPI`.
  2. `MCP-Proxy` uses its own single, static `client_id` when talking to `ThirdPartyAPI`’s authorization server.
  3. You, as the user, legitimately authorize `MCP-Proxy` to access `ThirdPartyAPI` on your behalf. During this, `ThirdPartyAPI`’s auth server might set a cookie in your browser indicating your consent for `MCP-Proxy`’s `client_id`.
  4. An attacker crafts a malicious link. This link initiates an OAuth flow with `MCP-Proxy`, but is designed to trick `ThirdPartyAPI`’s auth server.
  5. If you click this link, and `ThirdPartyAPI`’s auth server sees your existing consent cookie for `MCP-Proxy`’s `client_id`, it might _skip_ asking for your consent again.
  6. `MCP-Proxy` might then be tricked into forwarding an authorization code (for `ThirdPartyAPI`) to the attacker, or an MCP authorization code that the attacker can use to impersonate you to `MCP-Proxy`.



**Mitigation (Primarily for MCP Server Developers):**

  * MCP proxy servers using static client IDs for downstream services **must** obtain explicit user consent for _each client application or agent_ connecting to them _before_ initiating an OAuth flow with the third-party service. This means `MCP-Proxy` itself should show a consent screen.



**CrewAI User Implication:**

  * Be cautious if an MCP server redirects you for multiple OAuth authentications, especially if it seems unexpected or if the permissions requested are overly broad.
  * Prefer MCP servers that clearly delineate their own identity versus the third-party services they might proxy.



### 

​

Remote Transport Security (SSE & Streamable HTTP)

When connecting to remote MCP servers via Server-Sent Events (SSE) or Streamable HTTP, standard web security practices are essential.

### 

​

SSE Security Considerations

### 

​

a. DNS Rebinding Attacks (Especially for SSE)

DNS rebinding allows an attacker-controlled website to bypass the same-origin policy and make requests to servers on the user’s local network (e.g., `localhost`) or intranet. This is particularly risky if you run an MCP server locally (e.g., for development) and an agent in a browser-like environment (though less common for typical CrewAI backend setups) or if the MCP server is on an internal network.

**Mitigation Strategies for MCP Server Implementers:**

  * **Validate`Origin` and `Host` Headers**: MCP servers (especially SSE ones) should validate the `Origin` and/or `Host` HTTP headers to ensure requests are coming from expected domains/clients.
  * **Bind to`localhost` (127.0.0.1)**: When running MCP servers locally for development, bind them to `127.0.0.1` instead of `0.0.0.0`. This prevents them from being accessible from other machines on the network.
  * **Authentication** : Require authentication for all connections to your MCP server if it’s not intended for public anonymous access.



### 

​

b. Use HTTPS

  * **Encrypt Data in Transit** : Always use HTTPS (HTTP Secure) for the URLs of remote MCP servers. This encrypts the communication between your CrewAI application and the MCP server, protecting against eavesdropping and man-in-the-middle attacks. `MCPServerAdapter` will respect the scheme (`http` or `https`) provided in the URL.



### 

​

c. Token Passthrough (Anti-Pattern)

This is primarily a concern for MCP server developers but understanding it helps in choosing secure servers.

“Token passthrough” is when an MCP server accepts an access token from your CrewAI agent (which might be a token for a _different_ service, say `ServiceA`) and simply passes it through to another downstream API (`ServiceB`) without proper validation. Specifically, `ServiceB` (or the MCP server itself) should only accept tokens that were explicitly issued _for them_ (i.e., the ‘audience’ claim in the token matches the server/service).

**Risks:**

  * Bypasses security controls (like rate limiting or fine-grained permissions) on the MCP server or the downstream API.
  * Breaks audit trails and accountability.
  * Allows misuse of stolen tokens.



**Mitigation (For MCP Server Developers):**

  * MCP servers **MUST NOT** accept tokens that were not explicitly issued for them. They must validate the token’s audience claim.



**CrewAI User Implication:**

  * While not directly controllable by the user, this highlights the importance of connecting to well-designed MCP servers that adhere to security best practices.



#### 

​

Authentication and Authorization

  * **Verify Identity** : If the MCP server provides sensitive tools or access to private data, it MUST implement strong authentication mechanisms to verify the identity of the client (your CrewAI application). This could involve API keys, OAuth tokens, or other standard methods.
  * **Principle of Least Privilege** : Ensure the credentials used by `MCPServerAdapter` (if any) have only the necessary permissions to access the required tools.



### 

​

d. Input Validation and Sanitization

  * **Input Validation is Critical** : MCP servers **must** rigorously validate all inputs received from agents _before_ processing them or passing them to tools. This is a primary defense against many common vulnerabilities:
    * **Command Injection:** If a tool constructs shell commands, SQL queries, or other interpreted language statements based on input, the server must meticulously sanitize this input to prevent malicious commands from being injected and executed.
    * **Path Traversal:** If a tool accesses files based on input parameters, the server must validate and sanitize these paths to prevent access to unauthorized files or directories (e.g., by blocking `../` sequences).
    * **Data Type & Range Checks:** Servers must ensure that input data conforms to the expected data types (e.g., string, number, boolean) and falls within acceptable ranges or adheres to defined formats (e.g., regex for URLs).
    * **JSON Schema Validation:** All tool parameters should be strictly validated against their defined JSON schema. This helps catch malformed requests early.
  * **Client-Side Awareness** : While server-side validation is paramount, as a CrewAI user, be mindful of the data your agents are constructed to send to MCP tools, especially if interacting with less-trusted or new MCP servers.



### 

​

e. Rate Limiting and Resource Management

  * **Prevent Abuse** : MCP servers should implement rate limiting to prevent abuse, whether intentional (Denial of Service attacks) or unintentional (e.g., a misconfigured agent making too many requests).
  * **Client-Side Retries** : Implement sensible retry logic in your CrewAI tasks if transient network issues or server rate limits are expected, but avoid aggressive retries that could exacerbate server load.



## 

​

4\. Secure MCP Server Implementation Advice (For Developers)

If you are developing an MCP server that CrewAI agents might connect to, consider these best practices in addition to the points above:

  * **Follow Secure Coding Practices** : Adhere to standard secure coding principles for your chosen language and framework (e.g., OWASP Top 10).
  * **Principle of Least Privilege** : Ensure the process running the MCP server (especially for `Stdio`) has only the minimum necessary permissions. Tools themselves should also operate with the least privilege required to perform their function.
  * **Dependency Management** : Keep all server-side dependencies, including operating system packages, language runtimes, and third-party libraries, up-to-date to patch known vulnerabilities. Use tools to scan for vulnerable dependencies.
  * **Secure Defaults** : Design your server and its tools to be secure by default. For example, features that could be risky should be off by default or require explicit opt-in with clear warnings.
  * **Access Control for Tools** : Implement robust mechanisms to control which authenticated and authorized agents or users can access specific tools, especially those that are powerful, sensitive, or incur costs.
  * **Secure Error Handling** : Servers should not expose detailed internal error messages, stack traces, or debugging information to the client, as these can reveal internal workings or potential vulnerabilities. Log errors comprehensively on the server-side for diagnostics.
  * **Comprehensive Logging and Monitoring** : Implement detailed logging of security-relevant events (e.g., authentication attempts, tool invocations, errors, authorization changes). Monitor these logs for suspicious activity or abuse patterns.
  * **Adherence to MCP Authorization Spec** : If implementing authentication and authorization, strictly follow the [MCP Authorization specification](https://modelcontextprotocol.io/specification/draft/basic/authorization) and relevant [OAuth 2.0 security best practices](https://datatracker.ietf.org/doc/html/rfc9700).
  * **Regular Security Audits** : If your MCP server handles sensitive data, performs critical operations, or is publicly exposed, consider periodic security audits by qualified professionals.



## 

​

5\. Further Reading

For more detailed information on MCP security, refer to the official documentation:

  * **[MCP Transport Security](https://modelcontextprotocol.io/docs/concepts/transports#security-considerations)**



By understanding these security considerations and implementing best practices, you can safely leverage the power of MCP servers in your CrewAI projects. These are by no means exhaustive, but they cover the most common and critical security concerns. The threats will continue to evolve, so it’s important to stay informed and adapt your security measures accordingly.

Was this page helpful?

YesNo

[Connecting to Multiple MCP Servers](/mcp/multiple-servers)[Tools Overview](/tools/overview)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Overview
  * Risks
  * 1\. Trusting MCP Servers
  * 2\. Secure Prompt Injection via Tool Metadata: The “Model Control Protocol” Risk
  * Stdio Transport Security
  * Confused Deputy Attacks
  * Remote Transport Security (SSE & Streamable HTTP)
  * SSE Security Considerations
  * a. DNS Rebinding Attacks (Especially for SSE)
  * b. Use HTTPS
  * c. Token Passthrough (Anti-Pattern)
  * Authentication and Authorization
  * d. Input Validation and Sanitization
  * e. Rate Limiting and Resource Management
  * 4\. Secure MCP Server Implementation Advice (For Developers)
  * 5\. Further Reading



Assistant

Responses are generated using AI and may contain mistakes.


---

### Image Generation with DALL-E {#image-generation-with-dall-e}

**Source:** [https://docs.crewai.com/learn/dalle-image-generation](https://docs.crewai.com/learn/dalle-image-generation)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Learn

Image Generation with DALL-E

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Learn

# Image Generation with DALL-E

Copy page

Learn how to use DALL-E for AI-powered image generation in your CrewAI projects

CrewAI supports integration with OpenAI’s DALL-E, allowing your AI agents to generate images as part of their tasks. This guide will walk you through how to set up and use the DALL-E tool in your CrewAI projects.

## 

​

Prerequisites

  * crewAI installed (latest version)
  * OpenAI API key with access to DALL-E



## 

​

Setting Up the DALL-E Tool

1

Import the DALL-E tool
    
    
    from crewai_tools import DallETool

2

Add the DALL-E tool to your agent configuration
    
    
    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            tools=[SerperDevTool(), DallETool()],  # Add DallETool to the list of tools
            allow_delegation=False,
            verbose=True
        )

## 

​

Using the DALL-E Tool

Once you’ve added the DALL-E tool to your agent, it can generate images based on text prompts. The tool will return a URL to the generated image, which can be used in the agent’s output or passed to other agents for further processing.

### 

​

Example Agent Configuration
    
    
    role: >
        LinkedIn Profile Senior Data Researcher
    goal: >
        Uncover detailed LinkedIn profiles based on provided name {name} and domain {domain}
        Generate a Dall-e image based on domain {domain}
    backstory: >
        You're a seasoned researcher with a knack for uncovering the most relevant LinkedIn profiles.
        Known for your ability to navigate LinkedIn efficiently, you excel at gathering and presenting
        professional information clearly and concisely.

### 

​

Expected Output

The agent with the DALL-E tool will be able to generate the image and provide a URL in its response. You can then download the image.

## 

​

Best Practices

  1. **Be specific in your image generation prompts** to get the best results.
  2. **Consider generation time** \- Image generation can take some time, so factor this into your task planning.
  3. **Follow usage policies** \- Always comply with OpenAI’s usage policies when generating images.



## 

​

Troubleshooting

  1. **Check API access** \- Ensure your OpenAI API key has access to DALL-E.
  2. **Version compatibility** \- Check that you’re using the latest version of crewAI and crewai-tools.
  3. **Tool configuration** \- Verify that the DALL-E tool is correctly added to the agent’s tool list.



Was this page helpful?

YesNo

[Customize Agents](/learn/customizing-agents)[Force Tool Output as Result](/learn/force-tool-output-as-result)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Prerequisites
  * Setting Up the DALL-E Tool
  * Using the DALL-E Tool
  * Example Agent Configuration
  * Expected Output
  * Best Practices
  * Troubleshooting



Assistant

Responses are generated using AI and may contain mistakes.


---

### Overview {#overview}

**Source:** [https://docs.crewai.com/observability/overview](https://docs.crewai.com/observability/overview)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Observability

Overview

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Observability

# Overview

Copy page

Monitor, evaluate, and optimize your CrewAI agents with comprehensive observability tools

## 

​

Observability for CrewAI

Observability is crucial for understanding how your CrewAI agents perform, identifying bottlenecks, and ensuring reliable operation in production environments. This section covers various tools and platforms that provide monitoring, evaluation, and optimization capabilities for your agent workflows.

## 

​

Why Observability Matters

  * **Performance Monitoring** : Track agent execution times, token usage, and resource consumption
  * **Quality Assurance** : Evaluate output quality and consistency across different scenarios
  * **Debugging** : Identify and resolve issues in agent behavior and task execution
  * **Cost Management** : Monitor LLM API usage and associated costs
  * **Continuous Improvement** : Gather insights to optimize agent performance over time



## 

​

Available Observability Tools

### 

​

Monitoring & Tracing Platforms

## [AgentOpsSession replays, metrics, and monitoring for agent development and production.](/observability/agentops)## [OpenLITOpenTelemetry-native monitoring with cost tracking and performance analytics.](/observability/openlit)## [MLflowMachine learning lifecycle management with tracing and evaluation capabilities.](/observability/mlflow)## [LangfuseLLM engineering platform with detailed tracing and analytics.](/observability/langfuse)## [LangtraceOpen-source observability for LLMs and agent frameworks.](/observability/langtrace)## [Arize PhoenixAI observability platform for monitoring and troubleshooting.](/observability/arize-phoenix)## [PortkeyAI gateway with comprehensive monitoring and reliability features.](/observability/portkey)## [OpikDebug, evaluate, and monitor LLM applications with comprehensive tracing.](/observability/opik)## [WeaveWeights & Biases platform for tracking and evaluating AI applications.](/observability/weave)

### 

​

Evaluation & Quality Assurance

## [Patronus AIComprehensive evaluation platform for LLM outputs and agent behaviors.](/observability/patronus-evaluation)

## 

​

Key Observability Metrics

### 

​

Performance Metrics

  * **Execution Time** : How long agents take to complete tasks
  * **Token Usage** : Input/output tokens consumed by LLM calls
  * **API Latency** : Response times from external services
  * **Success Rate** : Percentage of successfully completed tasks



### 

​

Quality Metrics

  * **Output Accuracy** : Correctness of agent responses
  * **Consistency** : Reliability across similar inputs
  * **Relevance** : How well outputs match expected results
  * **Safety** : Compliance with content policies and guidelines



### 

​

Cost Metrics

  * **API Costs** : Expenses from LLM provider usage
  * **Resource Utilization** : Compute and memory consumption
  * **Cost per Task** : Economic efficiency of agent operations
  * **Budget Tracking** : Monitoring against spending limits



## 

​

Getting Started

  1. **Choose Your Tools** : Select observability platforms that match your needs
  2. **Instrument Your Code** : Add monitoring to your CrewAI applications
  3. **Set Up Dashboards** : Configure visualizations for key metrics
  4. **Define Alerts** : Create notifications for important events
  5. **Establish Baselines** : Measure initial performance for comparison
  6. **Iterate and Improve** : Use insights to optimize your agents



## 

​

Best Practices

### 

​

Development Phase

  * Use detailed tracing to understand agent behavior
  * Implement evaluation metrics early in development
  * Monitor resource usage during testing
  * Set up automated quality checks



### 

​

Production Phase

  * Implement comprehensive monitoring and alerting
  * Track performance trends over time
  * Monitor for anomalies and degradation
  * Maintain cost visibility and control



### 

​

Continuous Improvement

  * Regular performance reviews and optimization
  * A/B testing of different agent configurations
  * Feedback loops for quality improvement
  * Documentation of lessons learned



Choose the observability tools that best fit your use case, infrastructure, and monitoring requirements to ensure your CrewAI agents perform reliably and efficiently.

Was this page helpful?

YesNo

[MultiOn Tool](/tools/automation/multiontool)[AgentOps Integration](/observability/agentops)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Observability for CrewAI
  * Why Observability Matters
  * Available Observability Tools
  * Monitoring & Tracing Platforms
  * Evaluation & Quality Assurance
  * Key Observability Metrics
  * Performance Metrics
  * Quality Metrics
  * Cost Metrics
  * Getting Started
  * Best Practices
  * Development Phase
  * Production Phase
  * Continuous Improvement



Assistant

Responses are generated using AI and may contain mistakes.


---

### Hierarchical Process {#hierarchical-process}

**Source:** [https://docs.crewai.com/learn/hierarchical-process](https://docs.crewai.com/learn/hierarchical-process)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Learn

Hierarchical Process

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Learn

# Hierarchical Process

Copy page

A comprehensive guide to understanding and applying the hierarchical process within your CrewAI projects, updated to reflect the latest coding practices and functionalities.

## 

​

Introduction

The hierarchical process in CrewAI introduces a structured approach to task management, simulating traditional organizational hierarchies for efficient task delegation and execution. This systematic workflow enhances project outcomes by ensuring tasks are handled with optimal efficiency and accuracy.

The hierarchical process is designed to leverage advanced models like GPT-4, optimizing token usage while handling complex tasks with greater efficiency.

## 

​

Hierarchical Process Overview

By default, tasks in CrewAI are managed through a sequential process. However, adopting a hierarchical approach allows for a clear hierarchy in task management, where a ‘manager’ agent coordinates the workflow, delegates tasks, and validates outcomes for streamlined and effective execution. This manager agent can now be either automatically created by CrewAI or explicitly set by the user.

### 

​

Key Features

  * **Task Delegation** : A manager agent allocates tasks among crew members based on their roles and capabilities.
  * **Result Validation** : The manager evaluates outcomes to ensure they meet the required standards.
  * **Efficient Workflow** : Emulates corporate structures, providing an organized approach to task management.
  * **System Prompt Handling** : Optionally specify whether the system should use predefined prompts.
  * **Stop Words Control** : Optionally specify whether stop words should be used, supporting various models including the o1 models.
  * **Context Window Respect** : Prioritize important context by enabling respect of the context window, which is now the default behavior.
  * **Delegation Control** : Delegation is now disabled by default to give users explicit control.
  * **Max Requests Per Minute** : Configurable option to set the maximum number of requests per minute.
  * **Max Iterations** : Limit the maximum number of iterations for obtaining a final answer.



## 

​

Implementing the Hierarchical Process

To utilize the hierarchical process, it’s essential to explicitly set the process attribute to `Process.hierarchical`, as the default behavior is `Process.sequential`. Define a crew with a designated manager and establish a clear chain of command.

Assign tools at the agent level to facilitate task delegation and execution by the designated agents under the manager’s guidance. Tools can also be specified at the task level for precise control over tool availability during task execution.

Configuring the `manager_llm` parameter is crucial for the hierarchical process. The system requires a manager LLM to be set up for proper function, ensuring tailored decision-making.

Code
    
    
    from crewai import Crew, Process, Agent
    
    # Agents are defined with attributes for backstory, cache, and verbose mode
    researcher = Agent(
        role='Researcher',
        goal='Conduct in-depth analysis',
        backstory='Experienced data analyst with a knack for uncovering hidden trends.',
    )
    writer = Agent(
        role='Writer',
        goal='Create engaging content',
        backstory='Creative writer passionate about storytelling in technical domains.',
    )
    
    # Establishing the crew with a hierarchical process and additional configurations
    project_crew = Crew(
        tasks=[...],  # Tasks to be delegated and executed under the manager's supervision
        agents=[researcher, writer],
        manager_llm="gpt-4o",  # Specify which LLM the manager should use
        process=Process.hierarchical,  
        planning=True, 
    )

### 

​

Using a Custom Manager Agent

Alternatively, you can create a custom manager agent with specific attributes tailored to your project’s management needs. This gives you more control over the manager’s behavior and capabilities.
    
    
    # Define a custom manager agent
    manager = Agent(
        role="Project Manager",
        goal="Efficiently manage the crew and ensure high-quality task completion",
        backstory="You're an experienced project manager, skilled in overseeing complex projects and guiding teams to success.",
        allow_delegation=True,
    )
    
    # Use the custom manager in your crew
    project_crew = Crew(
        tasks=[...],
        agents=[researcher, writer],
        manager_agent=manager,  # Use your custom manager agent
        process=Process.hierarchical,
        planning=True,
    )

For more details on creating and customizing a manager agent, check out the [Custom Manager Agent documentation](https://docs.crewai.com/how-to/custom-manager-agent#custom-manager-agent).

### 

​

Workflow in Action

  1. **Task Assignment** : The manager assigns tasks strategically, considering each agent’s capabilities and available tools.
  2. **Execution and Review** : Agents complete their tasks with the option for asynchronous execution and callback functions for streamlined workflows.
  3. **Sequential Task Progression** : Despite being a hierarchical process, tasks follow a logical order for smooth progression, facilitated by the manager’s oversight.



## 

​

Conclusion

Adopting the hierarchical process in CrewAI, with the correct configurations and understanding of the system’s capabilities, facilitates an organized and efficient approach to project management. Utilize the advanced features and customizations to tailor the workflow to your specific needs, ensuring optimal task execution and project success.

Was this page helpful?

YesNo

[Force Tool Output as Result](/learn/force-tool-output-as-result)[Human Input on Execution](/learn/human-input-on-execution)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Introduction
  * Hierarchical Process Overview
  * Key Features
  * Implementing the Hierarchical Process
  * Using a Custom Manager Agent
  * Workflow in Action
  * Conclusion



Assistant

Responses are generated using AI and may contain mistakes.


---

### Streamable HTTP Transport {#streamable-http-transport}

**Source:** [https://docs.crewai.com/mcp/streamable-http](https://docs.crewai.com/mcp/streamable-http)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

MCP Integration

Streamable HTTP Transport

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



MCP Integration

# Streamable HTTP Transport

Copy page

Learn how to connect CrewAI to remote MCP servers using the flexible Streamable HTTP transport.

## 

​

Overview

Streamable HTTP transport provides a flexible way to connect to remote MCP servers. It’s often built upon HTTP and can support various communication patterns, including request-response and streaming, sometimes utilizing Server-Sent Events (SSE) for server-to-client streams within a broader HTTP interaction.

## 

​

Key Concepts

  * **Remote Servers** : Designed for MCP servers hosted remotely.
  * **Flexibility** : Can support more complex interaction patterns than plain SSE, potentially including bi-directional communication if the server implements it.
  * **`MCPServerAdapter` Configuration**: You’ll need to provide the server’s base URL for MCP communication and specify `"streamable-http"` as the transport type.



## 

​

Connecting via Streamable HTTP

You have two primary methods for managing the connection lifecycle with a Streamable HTTP MCP server:

### 

​

1\. Fully Managed Connection (Recommended)

The recommended approach is to use a Python context manager (`with` statement), which handles the connection’s setup and teardown automatically.
    
    
    from crewai import Agent, Task, Crew, Process
    from crewai_tools import MCPServerAdapter
    
    server_params = {
        "url": "http://localhost:8001/mcp", # Replace with your actual Streamable HTTP server URL
        "transport": "streamable-http"
    }
    
    try:
        with MCPServerAdapter(server_params) as tools:
            print(f"Available tools from Streamable HTTP MCP server: {[tool.name for tool in tools]}")
    
            http_agent = Agent(
                role="HTTP Service Integrator",
                goal="Utilize tools from a remote MCP server via Streamable HTTP.",
                backstory="An AI agent adept at interacting with complex web services.",
                tools=tools,
                verbose=True,
            )
    
            http_task = Task(
                description="Perform a complex data query using a tool from the Streamable HTTP server.",
                expected_output="The result of the complex data query.",
                agent=http_agent,
            )
    
            http_crew = Crew(
                agents=[http_agent],
                tasks=[http_task],
                verbose=True,
                process=Process.sequential
            )
            
            result = http_crew.kickoff() 
            print("\nCrew Task Result (Streamable HTTP - Managed):\n", result)
    
    except Exception as e:
        print(f"Error connecting to or using Streamable HTTP MCP server (Managed): {e}")
        print("Ensure the Streamable HTTP MCP server is running and accessible at the specified URL.")

**Note:** Replace `"http://localhost:8001/mcp"` with the actual URL of your Streamable HTTP MCP server.

### 

​

2\. Manual Connection Lifecycle

For scenarios requiring more explicit control, you can manage the `MCPServerAdapter` connection manually.

It is **critical** to call `mcp_server_adapter.stop()` when you are done to close the connection and free up resources. A `try...finally` block is the safest way to ensure this.
    
    
    from crewai import Agent, Task, Crew, Process
    from crewai_tools import MCPServerAdapter
    
    server_params = {
        "url": "http://localhost:8001/mcp", # Replace with your actual Streamable HTTP server URL
        "transport": "streamable-http"
    }
    
    mcp_server_adapter = None 
    try:
        mcp_server_adapter = MCPServerAdapter(server_params)
        mcp_server_adapter.start()
        tools = mcp_server_adapter.tools
        print(f"Available tools (manual Streamable HTTP): {[tool.name for tool in tools]}")
    
        manual_http_agent = Agent(
            role="Advanced Web Service User",
            goal="Interact with an MCP server using manually managed Streamable HTTP connections.",
            backstory="An AI specialist in fine-tuning HTTP-based service integrations.",
            tools=tools,
            verbose=True
        )
        
        data_processing_task = Task(
            description="Submit data for processing and retrieve results via Streamable HTTP.",
            expected_output="Processed data or confirmation.",
            agent=manual_http_agent
        )
        
        data_crew = Crew(
            agents=[manual_http_agent],
            tasks=[data_processing_task],
            verbose=True,
            process=Process.sequential
        )
        
        result = data_crew.kickoff()
        print("\nCrew Task Result (Streamable HTTP - Manual):\n", result)
    
    except Exception as e:
        print(f"An error occurred during manual Streamable HTTP MCP integration: {e}")
        print("Ensure the Streamable HTTP MCP server is running and accessible.")
    finally:
        if mcp_server_adapter and mcp_server_adapter.is_connected:
            print("Stopping Streamable HTTP MCP server connection (manual)...")
            mcp_server_adapter.stop()  # **Crucial: Ensure stop is called**
        elif mcp_server_adapter:
            print("Streamable HTTP MCP server adapter was not connected. No stop needed or start failed.")

## 

​

Security Considerations

When using Streamable HTTP transport, general web security best practices are paramount:

  * **Use HTTPS** : Always prefer HTTPS (HTTP Secure) for your MCP server URLs to encrypt data in transit.
  * **Authentication** : Implement robust authentication mechanisms if your MCP server exposes sensitive tools or data.
  * **Input Validation** : Ensure your MCP server validates all incoming requests and parameters.



For a comprehensive guide on securing your MCP integrations, please refer to our [Security Considerations](./security.mdx) page and the official [MCP Transport Security documentation](https://modelcontextprotocol.io/docs/concepts/transports#security-considerations).

Was this page helpful?

YesNo

[SSE Transport](/mcp/sse)[Connecting to Multiple MCP Servers](/mcp/multiple-servers)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Overview
  * Key Concepts
  * Connecting via Streamable HTTP
  * 1\. Fully Managed Connection (Recommended)
  * 2\. Manual Connection Lifecycle
  * Security Considerations



Assistant

Responses are generated using AI and may contain mistakes.


---

### Kickoff Crew for Each {#kickoff-crew-for-each}

**Source:** [https://docs.crewai.com/learn/kickoff-for-each](https://docs.crewai.com/learn/kickoff-for-each)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Learn

Kickoff Crew for Each

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Learn

# Kickoff Crew for Each

Copy page

Kickoff Crew for Each Item in a List

## 

​

Introduction

CrewAI provides the ability to kickoff a crew for each item in a list, allowing you to execute the crew for each item in the list. This feature is particularly useful when you need to perform the same set of tasks for multiple items.

## 

​

Kicking Off a Crew for Each Item

To kickoff a crew for each item in a list, use the `kickoff_for_each()` method. This method executes the crew for each item in the list, allowing you to process multiple items efficiently.

Here’s an example of how to kickoff a crew for each item in a list:

Code
    
    
    from crewai import Crew, Agent, Task
    
    # Create an agent with code execution enabled
    coding_agent = Agent(
        role="Python Data Analyst",
        goal="Analyze data and provide insights using Python",
        backstory="You are an experienced data analyst with strong Python skills.",
        allow_code_execution=True
    )
    
    # Create a task that requires code execution
    data_analysis_task = Task(
        description="Analyze the given dataset and calculate the average age of participants. Ages: {ages}",
        agent=coding_agent,
        expected_output="The average age calculated from the dataset"
    )
    
    # Create a crew and add the task
    analysis_crew = Crew(
        agents=[coding_agent],
        tasks=[data_analysis_task],
        verbose=True,
        memory=False
    )
    
    datasets = [
      { "ages": [25, 30, 35, 40, 45] },
      { "ages": [20, 25, 30, 35, 40] },
      { "ages": [30, 35, 40, 45, 50] }
    ]
    
    # Execute the crew
    result = analysis_crew.kickoff_for_each(inputs=datasets)

Was this page helpful?

YesNo

[Kickoff Crew Asynchronously](/learn/kickoff-async)[Connect to any LLM](/learn/llm-connections)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Introduction
  * Kicking Off a Crew for Each Item



Assistant

Responses are generated using AI and may contain mistakes.


---

### Weave Integration {#weave-integration}

**Source:** [https://docs.crewai.com/observability/weave](https://docs.crewai.com/observability/weave)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Observability

Weave Integration

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Observability

# Weave Integration

Copy page

Learn how to use Weights & Biases (W&B) Weave to track, experiment with, evaluate, and improve your CrewAI applications.

# 

​

Weave Overview

[Weights & Biases (W&B) Weave](https://weave-docs.wandb.ai/) is a framework for tracking, experimenting with, evaluating, deploying, and improving LLM-based applications.

Weave provides comprehensive support for every stage of your CrewAI application development:

  * **Tracing & Monitoring**: Automatically track LLM calls and application logic to debug and analyze production systems
  * **Systematic Iteration** : Refine and iterate on prompts, datasets, and models
  * **Evaluation** : Use custom or pre-built scorers to systematically assess and enhance agent performance
  * **Guardrails** : Protect your agents with pre- and post-safeguards for content moderation and prompt safety



Weave automatically captures traces for your CrewAI applications, enabling you to monitor and analyze your agents’ performance, interactions, and execution flow. This helps you build better evaluation datasets and optimize your agent workflows.

## 

​

Setup Instructions

1

Install required packages
    
    
    pip install crewai weave

2

Set up W&B Account

Sign up for a [Weights & Biases account](https://wandb.ai) if you haven’t already. You’ll need this to view your traces and metrics.

3

Initialize Weave in Your Application

Add the following code to your application:
    
    
    import weave
    
    # Initialize Weave with your project name
    weave.init(project_name="crewai_demo")

After initialization, Weave will provide a URL where you can view your traces and metrics.

4

Create your Crews/Flows
    
    
    from crewai import Agent, Task, Crew, LLM, Process
    
    # Create an LLM with a temperature of 0 to ensure deterministic outputs
    llm = LLM(model="gpt-4o", temperature=0)
    
    # Create agents
    researcher = Agent(
        role='Research Analyst',
        goal='Find and analyze the best investment opportunities',
        backstory='Expert in financial analysis and market research',
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
    
    writer = Agent(
        role='Report Writer',
        goal='Write clear and concise investment reports',
        backstory='Experienced in creating detailed financial reports',
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
    
    # Create tasks
    research_task = Task(
        description='Deep research on the {topic}',
        expected_output='Comprehensive market data including key players, market size, and growth trends.',
        agent=researcher
    )
    
    writing_task = Task(
        description='Write a detailed report based on the research',
        expected_output='The report should be easy to read and understand. Use bullet points where applicable.',
        agent=writer
    )
    
    # Create a crew
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        verbose=True,
        process=Process.sequential,
    )
    
    # Run the crew
    result = crew.kickoff(inputs={"topic": "AI in material science"})
    print(result)

5

View Traces in Weave

After running your CrewAI application, visit the Weave URL provided during initialization to view:

  * LLM calls and their metadata
  * Agent interactions and task execution flow
  * Performance metrics like latency and token usage
  * Any errors or issues that occurred during execution



Weave Tracing Dashboard

## 

​

Features

  * Weave automatically captures all CrewAI operations: agent interactions and task executions; LLM calls with metadata and token usage; tool usage and results.
  * The integration supports all CrewAI execution methods: `kickoff()`, `kickoff_for_each()`, `kickoff_async()`, and `kickoff_for_each_async()`.
  * Automatic tracing of all [crewAI-tools](https://github.com/crewAIInc/crewAI-tools).
  * Flow feature support with decorator patching (`@start`, `@listen`, `@router`, `@or_`, `@and_`).
  * Track custom guardrails passed to CrewAI `Task` with `@weave.op()`.



For detailed information on what’s supported, visit the [Weave CrewAI documentation](https://weave-docs.wandb.ai/guides/integrations/crewai/#getting-started-with-flow).

## 

​

Resources

  * [📘 Weave Documentation](https://weave-docs.wandb.ai)
  * [📊 Example Weave x CrewAI dashboard](https://wandb.ai/ayut/crewai_demo/weave/traces?cols=%7B%22wb_run_id%22%3Afalse%2C%22attributes.weave.client_version%22%3Afalse%2C%22attributes.weave.os_name%22%3Afalse%2C%22attributes.weave.os_release%22%3Afalse%2C%22attributes.weave.os_version%22%3Afalse%2C%22attributes.weave.source%22%3Afalse%2C%22attributes.weave.sys_version%22%3Afalse%7D&peekPath=%2Fayut%2Fcrewai_demo%2Fcalls%2F0195c838-38cb-71a2-8a15-651ecddf9d89)
  * [🐦 X](https://x.com/weave_wb)



Was this page helpful?

YesNo

[Portkey Integration](/observability/portkey)[Overview](/learn/overview)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Weave Overview
  * Setup Instructions
  * Features
  * Resources



Assistant

Responses are generated using AI and may contain mistakes.


---

### OpenLIT Integration {#openlit-integration}

**Source:** [https://docs.crewai.com/observability/openlit](https://docs.crewai.com/observability/openlit)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Observability

OpenLIT Integration

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Observability

# OpenLIT Integration

Copy page

Quickly start monitoring your Agents in just a single line of code with OpenTelemetry.

# 

​

OpenLIT Overview

[OpenLIT](https://github.com/openlit/openlit?src=crewai-docs) is an open-source tool that makes it simple to monitor the performance of AI agents, LLMs, VectorDBs, and GPUs with just **one** line of code.

It provides OpenTelemetry-native tracing and metrics to track important parameters like cost, latency, interactions and task sequences. This setup enables you to track hyperparameters and monitor for performance issues, helping you find ways to enhance and fine-tune your agents over time.

OpenLIT Dashboard

### 

​

Features

  * **Analytics Dashboard** : Monitor your Agents health and performance with detailed dashboards that track metrics, costs, and user interactions.
  * **OpenTelemetry-native Observability SDK** : Vendor-neutral SDKs to send traces and metrics to your existing observability tools like Grafana, DataDog and more.
  * **Cost Tracking for Custom and Fine-Tuned Models** : Tailor cost estimations for specific models using custom pricing files for precise budgeting.
  * **Exceptions Monitoring Dashboard** : Quickly spot and resolve issues by tracking common exceptions and errors with a monitoring dashboard.
  * **Compliance and Security** : Detect potential threats such as profanity and PII leaks.
  * **Prompt Injection Detection** : Identify potential code injection and secret leaks.
  * **API Keys and Secrets Management** : Securely handle your LLM API keys and secrets centrally, avoiding insecure practices.
  * **Prompt Management** : Manage and version Agent prompts using PromptHub for consistent and easy access across Agents.
  * **Model Playground** Test and compare different models for your CrewAI agents before deployment.



## 

​

Setup Instructions

1

Deploy OpenLIT

1

Git Clone OpenLIT Repository
    
    
    git clone git@github.com:openlit/openlit.git

2

Start Docker Compose

From the root directory of the [OpenLIT Repo](https://github.com/openlit/openlit), Run the below command:
    
    
    docker compose up -d

2

Install OpenLIT SDK
    
    
    pip install openlit

3

Initialize OpenLIT in Your Application

Add the following two lines to your application code:

  * Setup using function arguments
  * Setup using Environment Variables


    
    
    import openlit
    openlit.init(otlp_endpoint="http://127.0.0.1:4318")

Example Usage for monitoring a CrewAI Agent:
    
    
    from crewai import Agent, Task, Crew, Process
    import openlit
    
    openlit.init(disable_metrics=True)
    # Define your agents
    researcher = Agent(
        role="Researcher",
        goal="Conduct thorough research and analysis on AI and AI agents",
        backstory="You're an expert researcher, specialized in technology, software engineering, AI, and startups. You work as a freelancer and are currently researching for a new client.",
        allow_delegation=False,
        llm='command-r'
    )
    
    
    # Define your task
    task = Task(
        description="Generate a list of 5 interesting ideas for an article, then write one captivating paragraph for each idea that showcases the potential of a full article on this topic. Return the list of ideas with their paragraphs and your notes.",
        expected_output="5 bullet points, each with a paragraph and accompanying notes.",
    )
    
    # Define the manager agent
    manager = Agent(
        role="Project Manager",
        goal="Efficiently manage the crew and ensure high-quality task completion",
        backstory="You're an experienced project manager, skilled in overseeing complex projects and guiding teams to success. Your role is to coordinate the efforts of the crew members, ensuring that each task is completed on time and to the highest standard.",
        allow_delegation=True,
        llm='command-r'
    )
    
    # Instantiate your crew with a custom manager
    crew = Crew(
        agents=[researcher],
        tasks=[task],
        manager_agent=manager,
        process=Process.hierarchical,
    )
    
    # Start the crew's work
    result = crew.kickoff()
    
    print(result)
    
    
    import openlit
    openlit.init(otlp_endpoint="http://127.0.0.1:4318")

Example Usage for monitoring a CrewAI Agent:
    
    
    from crewai import Agent, Task, Crew, Process
    import openlit
    
    openlit.init(disable_metrics=True)
    # Define your agents
    researcher = Agent(
        role="Researcher",
        goal="Conduct thorough research and analysis on AI and AI agents",
        backstory="You're an expert researcher, specialized in technology, software engineering, AI, and startups. You work as a freelancer and are currently researching for a new client.",
        allow_delegation=False,
        llm='command-r'
    )
    
    
    # Define your task
    task = Task(
        description="Generate a list of 5 interesting ideas for an article, then write one captivating paragraph for each idea that showcases the potential of a full article on this topic. Return the list of ideas with their paragraphs and your notes.",
        expected_output="5 bullet points, each with a paragraph and accompanying notes.",
    )
    
    # Define the manager agent
    manager = Agent(
        role="Project Manager",
        goal="Efficiently manage the crew and ensure high-quality task completion",
        backstory="You're an experienced project manager, skilled in overseeing complex projects and guiding teams to success. Your role is to coordinate the efforts of the crew members, ensuring that each task is completed on time and to the highest standard.",
        allow_delegation=True,
        llm='command-r'
    )
    
    # Instantiate your crew with a custom manager
    crew = Crew(
        agents=[researcher],
        tasks=[task],
        manager_agent=manager,
        process=Process.hierarchical,
    )
    
    # Start the crew's work
    result = crew.kickoff()
    
    print(result)

Add the following two lines to your application code:
    
    
    import openlit
    
    openlit.init()

Run the following command to configure the OTEL export endpoint:
    
    
    export OTEL_EXPORTER_OTLP_ENDPOINT = "http://127.0.0.1:4318"

Example Usage for monitoring a CrewAI Async Agent:
    
    
    import asyncio
    from crewai import Crew, Agent, Task
    import openlit
    
    openlit.init(otlp_endpoint="http://127.0.0.1:4318")
    
    # Create an agent with code execution enabled
    coding_agent = Agent(
      role="Python Data Analyst",
      goal="Analyze data and provide insights using Python",
      backstory="You are an experienced data analyst with strong Python skills.",
      allow_code_execution=True,
      llm="command-r"
    )
    
    # Create a task that requires code execution
    data_analysis_task = Task(
      description="Analyze the given dataset and calculate the average age of participants. Ages: {ages}",
      agent=coding_agent,
      expected_output="5 bullet points, each with a paragraph and accompanying notes.",
    )
    
    # Create a crew and add the task
    analysis_crew = Crew(
      agents=[coding_agent],
      tasks=[data_analysis_task]
    )
    
    # Async function to kickoff the crew asynchronously
    async def async_crew_execution():
        result = await analysis_crew.kickoff_async(inputs={"ages": [25, 30, 35, 40, 45]})
        print("Crew Result:", result)
    
    # Run the async function
    asyncio.run(async_crew_execution())

Refer to OpenLIT [Python SDK repository](https://github.com/openlit/openlit/tree/main/sdk/python) for more advanced configurations and use cases.

4

Visualize and Analyze

With the Agent Observability data now being collected and sent to OpenLIT, the next step is to visualize and analyze this data to get insights into your Agent’s performance, behavior, and identify areas of improvement.

Just head over to OpenLIT at `127.0.0.1:3000` on your browser to start exploring. You can login using the default credentials

  * **Email** : `user@openlit.io`
  * **Password** : `openlituser`



OpenLIT Dashboard

Was this page helpful?

YesNo

[MLflow Integration](/observability/mlflow)[Opik Integration](/observability/opik)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * OpenLIT Overview
  * Features
  * Setup Instructions



Assistant

Responses are generated using AI and may contain mistakes.


---

### Stdio Transport {#stdio-transport}

**Source:** [https://docs.crewai.com/mcp/stdio](https://docs.crewai.com/mcp/stdio)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

MCP Integration

Stdio Transport

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



MCP Integration

# Stdio Transport

Copy page

Learn how to connect CrewAI to local MCP servers using the Stdio (Standard Input/Output) transport mechanism.

## 

​

Overview

The Stdio (Standard Input/Output) transport is designed for connecting `MCPServerAdapter` to local MCP servers that communicate over their standard input and output streams. This is typically used when the MCP server is a script or executable running on the same machine as your CrewAI application.

## 

​

Key Concepts

  * **Local Execution** : Stdio transport manages a locally running process for the MCP server.
  * **`StdioServerParameters`** : This class from the `mcp` library is used to configure the command, arguments, and environment variables for launching the Stdio server.



## 

​

Connecting via Stdio

You can connect to an Stdio-based MCP server using two main approaches for managing the connection lifecycle:

### 

​

1\. Fully Managed Connection (Recommended)

Using a Python context manager (`with` statement) is the recommended approach. It automatically handles starting the MCP server process and stopping it when the context is exited.
    
    
    from crewai import Agent, Task, Crew, Process
    from crewai_tools import MCPServerAdapter
    from mcp import StdioServerParameters
    import os
    
    # Create a StdioServerParameters object
    server_params=StdioServerParameters(
        command="python3", 
        args=["servers/your_stdio_server.py"],
        env={"UV_PYTHON": "3.12", **os.environ},
    )
    
    with MCPServerAdapter(server_params) as tools:
        print(f"Available tools from Stdio MCP server: {[tool.name for tool in tools]}")
    
        # Example: Using the tools from the Stdio MCP server in a CrewAI Agent
        research_agent = Agent(
            role="Local Data Processor",
            goal="Process data using a local Stdio-based tool.",
            backstory="An AI that leverages local scripts via MCP for specialized tasks.",
            tools=tools,
            reasoning=True,
            verbose=True,
        )
        
        processing_task = Task(
            description="Process the input data file 'data.txt' and summarize its contents.",
            expected_output="A summary of the processed data.",
            agent=research_agent,
            markdown=True
        )
        
        data_crew = Crew(
            agents=[research_agent],
            tasks=[processing_task],
            verbose=True,
            process=Process.sequential 
        )
       
        result = data_crew.kickoff()
        print("\nCrew Task Result (Stdio - Managed):\n", result)

### 

​

2\. Manual Connection Lifecycle

If you need finer-grained control over when the Stdio MCP server process is started and stopped, you can manage the `MCPServerAdapter` lifecycle manually.

You **MUST** call `mcp_server_adapter.stop()` to ensure the server process is terminated and resources are released. Using a `try...finally` block is highly recommended.
    
    
    from crewai import Agent, Task, Crew, Process
    from crewai_tools import MCPServerAdapter
    from mcp import StdioServerParameters
    import os
    
    # Create a StdioServerParameters object
    stdio_params=StdioServerParameters(
        command="python3", 
        args=["servers/your_stdio_server.py"],
        env={"UV_PYTHON": "3.12", **os.environ},
    )
    
    mcp_server_adapter = MCPServerAdapter(server_params=stdio_params)
    try:
        mcp_server_adapter.start()  # Manually start the connection and server process
        tools = mcp_server_adapter.tools
        print(f"Available tools (manual Stdio): {[tool.name for tool in tools]}")
    
        # Example: Using the tools with your Agent, Task, Crew setup
        manual_agent = Agent(
            role="Local Task Executor",
            goal="Execute a specific local task using a manually managed Stdio tool.",
            backstory="An AI proficient in controlling local processes via MCP.",
            tools=tools,
            verbose=True
        )
        
        manual_task = Task(
            description="Execute the 'perform_analysis' command via the Stdio tool.",
            expected_output="Results of the analysis.",
            agent=manual_agent
        )
        
        manual_crew = Crew(
            agents=[manual_agent],
            tasks=[manual_task],
            verbose=True,
            process=Process.sequential
        )
            
           
        result = manual_crew.kickoff() # Actual inputs depend on your tool
        print("\nCrew Task Result (Stdio - Manual):\n", result)
                
    except Exception as e:
        print(f"An error occurred during manual Stdio MCP integration: {e}")
    finally:
        if mcp_server_adapter and mcp_server_adapter.is_connected: # Check if connected before stopping
            print("Stopping Stdio MCP server connection (manual)...")
            mcp_server_adapter.stop()  # **Crucial: Ensure stop is called**
        elif mcp_server_adapter: # If adapter exists but not connected (e.g. start failed)
            print("Stdio MCP server adapter was not connected. No stop needed or start failed.")

Remember to replace placeholder paths and commands with your actual Stdio server details. The `env` parameter in `StdioServerParameters` can be used to set environment variables for the server process, which can be useful for configuring its behavior or providing necessary paths (like `PYTHONPATH`).

Was this page helpful?

YesNo

[MCP Servers as Tools in CrewAI](/mcp/overview)[SSE Transport](/mcp/sse)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Overview
  * Key Concepts
  * Connecting via Stdio
  * 1\. Fully Managed Connection (Recommended)
  * 2\. Manual Connection Lifecycle



Assistant

Responses are generated using AI and may contain mistakes.


---

### Langfuse Integration {#langfuse-integration}

**Source:** [https://docs.crewai.com/observability/langfuse](https://docs.crewai.com/observability/langfuse)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Observability

Langfuse Integration

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Observability

# Langfuse Integration

Copy page

Learn how to integrate Langfuse with CrewAI via OpenTelemetry using OpenLit

# 

​

Integrate Langfuse with CrewAI

This notebook demonstrates how to integrate **Langfuse** with **CrewAI** using OpenTelemetry via the **OpenLit** SDK. By the end of this notebook, you will be able to trace your CrewAI applications with Langfuse for improved observability and debugging.

> **What is Langfuse?** [Langfuse](https://langfuse.com) is an open-source LLM engineering platform. It provides tracing and monitoring capabilities for LLM applications, helping developers debug, analyze, and optimize their AI systems. Langfuse integrates with various tools and frameworks via native integrations, OpenTelemetry, and APIs/SDKs.

[](https://langfuse.com/watch-demo)

## 

​

Get Started

We’ll walk through a simple example of using CrewAI and integrating it with Langfuse via OpenTelemetry using OpenLit.

### 

​

Step 1: Install Dependencies
    
    
    %pip install langfuse openlit crewai crewai_tools

### 

​

Step 2: Set Up Environment Variables

Set your Langfuse API keys and configure OpenTelemetry export settings to send traces to Langfuse. Please refer to the [Langfuse OpenTelemetry Docs](https://langfuse.com/docs/opentelemetry/get-started) for more information on the Langfuse OpenTelemetry endpoint `/api/public/otel` and authentication.
    
    
    import os
    import base64
    
    LANGFUSE_PUBLIC_KEY="pk-lf-..."
    LANGFUSE_SECRET_KEY="sk-lf-..."
    LANGFUSE_AUTH=base64.b64encode(f"{LANGFUSE_PUBLIC_KEY}:{LANGFUSE_SECRET_KEY}".encode()).decode()
    
    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "https://cloud.langfuse.com/api/public/otel" # EU data region
    # os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "https://us.cloud.langfuse.com/api/public/otel" # US data region
    os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"
    
    # your openai key
    os.environ["OPENAI_API_KEY"] = "sk-..."

### 

​

Step 3: Initialize OpenLit

Initialize the OpenLit OpenTelemetry instrumentation SDK to start capturing OpenTelemetry traces.
    
    
    import openlit
    
    openlit.init()

### 

​

Step 4: Create a Simple CrewAI Application

We’ll create a simple CrewAI application where multiple agents collaborate to answer a user’s question.
    
    
    from crewai import Agent, Task, Crew
    
    from crewai_tools import (
        WebsiteSearchTool
    )
    
    web_rag_tool = WebsiteSearchTool()
    
    writer = Agent(
            role="Writer",
            goal="You make math engaging and understandable for young children through poetry",
            backstory="You're an expert in writing haikus but you know nothing of math.",
            tools=[web_rag_tool],  
        )
    
    task = Task(description=("What is {multiplication}?"),
                expected_output=("Compose a haiku that includes the answer."),
                agent=writer)
    
    crew = Crew(
      agents=[writer],
      tasks=[task],
      share_crew=False
    )

### 

​

Step 5: See Traces in Langfuse

After running the agent, you can view the traces generated by your CrewAI application in [Langfuse](https://cloud.langfuse.com). You should see detailed steps of the LLM interactions, which can help you debug and optimize your AI agent.

_[Public example trace in Langfuse](https://cloud.langfuse.com/project/cloramnkj0002jz088vzn1ja4/traces/e2cf380ffc8d47d28da98f136140642b?timestamp=2025-02-05T15%3A12%3A02.717Z&observation=3b32338ee6a5d9af)_

## 

​

References

  * [Langfuse OpenTelemetry Docs](https://langfuse.com/docs/opentelemetry/get-started)



Was this page helpful?

YesNo

[Arize Phoenix](/observability/arize-phoenix)[Langtrace Integration](/observability/langtrace)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Integrate Langfuse with CrewAI
  * Get Started
  * Step 1: Install Dependencies
  * Step 2: Set Up Environment Variables
  * Step 3: Initialize OpenLit
  * Step 4: Create a Simple CrewAI Application
  * Step 5: See Traces in Langfuse
  * References



Assistant

Responses are generated using AI and may contain mistakes.


---

### Using Annotations in crew.py {#using-annotations-in-crew.py}

**Source:** [https://docs.crewai.com/learn/using-annotations](https://docs.crewai.com/learn/using-annotations)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Learn

Using Annotations in crew.py

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Learn

# Using Annotations in crew.py

Copy page

Learn how to use annotations to properly structure agents, tasks, and components in CrewAI

This guide explains how to use annotations to properly reference **agents** , **tasks** , and other components in the `crew.py` file.

## 

​

Introduction

Annotations in the CrewAI framework are used to decorate classes and methods, providing metadata and functionality to various components of your crew. These annotations help in organizing and structuring your code, making it more readable and maintainable.

## 

​

Available Annotations

The CrewAI framework provides the following annotations:

  * `@CrewBase`: Used to decorate the main crew class.
  * `@agent`: Decorates methods that define and return Agent objects.
  * `@task`: Decorates methods that define and return Task objects.
  * `@crew`: Decorates the method that creates and returns the Crew object.
  * `@llm`: Decorates methods that initialize and return Language Model objects.
  * `@tool`: Decorates methods that initialize and return Tool objects.
  * `@callback`: Used for defining callback methods.
  * `@output_json`: Used for methods that output JSON data.
  * `@output_pydantic`: Used for methods that output Pydantic models.
  * `@cache_handler`: Used for defining cache handling methods.



## 

​

Usage Examples

Let’s go through examples of how to use these annotations:

### 

​

1\. Crew Base Class
    
    
    @CrewBase
    class LinkedinProfileCrew():
        """LinkedinProfile crew"""
        agents_config = 'config/agents.yaml'
        tasks_config = 'config/tasks.yaml'

The `@CrewBase` annotation is used to decorate the main crew class. This class typically contains configurations and methods for creating agents, tasks, and the crew itself.

### 

​

2\. Tool Definition
    
    
    @tool
    def myLinkedInProfileTool(self):
        return LinkedInProfileTool()

The `@tool` annotation is used to decorate methods that return tool objects. These tools can be used by agents to perform specific tasks.

### 

​

3\. LLM Definition
    
    
    @llm
    def groq_llm(self):
        api_key = os.getenv('api_key')
        return ChatGroq(api_key=api_key, temperature=0, model_name="mixtral-8x7b-32768")

The `@llm` annotation is used to decorate methods that initialize and return Language Model objects. These LLMs are used by agents for natural language processing tasks.

### 

​

4\. Agent Definition
    
    
    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher']
        )

The `@agent` annotation is used to decorate methods that define and return Agent objects.

### 

​

5\. Task Definition
    
    
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_linkedin_task'],
            agent=self.researcher()
        )

The `@task` annotation is used to decorate methods that define and return Task objects. These methods specify the task configuration and the agent responsible for the task.

### 

​

6\. Crew Creation
    
    
    @crew
    def crew(self) -> Crew:
        """Creates the LinkedinProfile crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

The `@crew` annotation is used to decorate the method that creates and returns the `Crew` object. This method assembles all the components (agents and tasks) into a functional crew.

## 

​

YAML Configuration

The agent configurations are typically stored in a YAML file. Here’s an example of how the `agents.yaml` file might look for the researcher agent:
    
    
    researcher:
        role: >
            LinkedIn Profile Senior Data Researcher
        goal: >
            Uncover detailed LinkedIn profiles based on provided name {name} and domain {domain}
            Generate a Dall-E image based on domain {domain}
        backstory: >
            You're a seasoned researcher with a knack for uncovering the most relevant LinkedIn profiles.
            Known for your ability to navigate LinkedIn efficiently, you excel at gathering and presenting
            professional information clearly and concisely.
        allow_delegation: False
        verbose: True
        llm: groq_llm
        tools:
            - myLinkedInProfileTool
            - mySerperDevTool
            - myDallETool

This YAML configuration corresponds to the researcher agent defined in the `LinkedinProfileCrew` class. The configuration specifies the agent’s role, goal, backstory, and other properties such as the LLM and tools it uses.

Note how the `llm` and `tools` in the YAML file correspond to the methods decorated with `@llm` and `@tool` in the Python class.

## 

​

Best Practices

  * **Consistent Naming** : Use clear and consistent naming conventions for your methods. For example, agent methods could be named after their roles (e.g., researcher, reporting_analyst).
  * **Environment Variables** : Use environment variables for sensitive information like API keys.
  * **Flexibility** : Design your crew to be flexible by allowing easy addition or removal of agents and tasks.
  * **YAML-Code Correspondence** : Ensure that the names and structures in your YAML files correspond correctly to the decorated methods in your Python code.



By following these guidelines and properly using annotations, you can create well-structured and maintainable crews using the CrewAI framework.

Was this page helpful?

YesNo

[Sequential Processes](/learn/sequential-process)[Telemetry](/telemetry)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Introduction
  * Available Annotations
  * Usage Examples
  * 1\. Crew Base Class
  * 2\. Tool Definition
  * 3\. LLM Definition
  * 4\. Agent Definition
  * 5\. Task Definition
  * 6\. Crew Creation
  * YAML Configuration
  * Best Practices



Assistant

Responses are generated using AI and may contain mistakes.


---

### Overview {#overview}

**Source:** [https://docs.crewai.com/learn/overview](https://docs.crewai.com/learn/overview)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Learn

Overview

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Learn

# Overview

Copy page

Learn how to build, customize, and optimize your CrewAI applications with comprehensive guides and tutorials

## 

​

Learn CrewAI

This section provides comprehensive guides and tutorials to help you master CrewAI, from basic concepts to advanced techniques. Whether you’re just getting started or looking to optimize your existing implementations, these resources will guide you through every aspect of building powerful AI agent workflows.

## 

​

Getting Started Guides

### 

​

Core Concepts

## [Sequential ProcessLearn how to execute tasks in a sequential order for structured workflows.](/learn/sequential-process)## [Hierarchical ProcessImplement hierarchical task execution with manager agents overseeing workflows.](/learn/hierarchical-process)## [Conditional TasksCreate dynamic workflows with conditional task execution based on outcomes.](/learn/conditional-tasks)## [Async KickoffExecute crews asynchronously for improved performance and concurrency.](/learn/kickoff-async)

### 

​

Agent Development

## [Customizing AgentsLearn how to customize agent behavior, roles, and capabilities.](/learn/customizing-agents)## [Coding AgentsBuild agents that can write, execute, and debug code automatically.](/learn/coding-agents)## [Multimodal AgentsCreate agents that can process text, images, and other media types.](/learn/multimodal-agents)## [Custom Manager AgentImplement custom manager agents for complex hierarchical workflows.](/learn/custom-manager-agent)

## 

​

Advanced Features

### 

​

Workflow Control

## [Human in the LoopIntegrate human oversight and intervention into agent workflows.](/learn/human-in-the-loop)## [Human Input on ExecutionAllow human input during task execution for dynamic decision making.](/learn/human-input-on-execution)## [Replay TasksReplay and resume tasks from previous crew executions.](/learn/replay-tasks-from-latest-crew-kickoff)## [Kickoff for EachExecute crews multiple times with different inputs efficiently.](/learn/kickoff-for-each)

### 

​

Customization & Integration

## [Custom LLMIntegrate custom language models and providers with CrewAI.](/learn/custom-llm)## [LLM ConnectionsConfigure and manage connections to various LLM providers.](/learn/llm-connections)## [Create Custom ToolsBuild custom tools to extend agent capabilities.](/learn/create-custom-tools)## [Using AnnotationsUse Python annotations for cleaner, more maintainable code.](/learn/using-annotations)

## 

​

Specialized Applications

### 

​

Content & Media

## [DALL-E Image GenerationGenerate images using DALL-E integration with your agents.](/learn/dalle-image-generation)## [Bring Your Own AgentIntegrate existing agents and models into CrewAI workflows.](/learn/bring-your-own-agent)

### 

​

Tool Management

## [Force Tool Output as ResultConfigure tools to return their output directly as task results.](/learn/force-tool-output-as-result)

## 

​

Learning Path Recommendations

### 

​

For Beginners

  1. Start with **Sequential Process** to understand basic workflow execution
  2. Learn **Customizing Agents** to create effective agent configurations
  3. Explore **Create Custom Tools** to extend functionality
  4. Try **Human in the Loop** for interactive workflows



### 

​

For Intermediate Users

  1. Master **Hierarchical Process** for complex multi-agent systems
  2. Implement **Conditional Tasks** for dynamic workflows
  3. Use **Async Kickoff** for performance optimization
  4. Integrate **Custom LLM** for specialized models



### 

​

For Advanced Users

  1. Build **Multimodal Agents** for complex media processing
  2. Create **Custom Manager Agents** for sophisticated orchestration
  3. Implement **Bring Your Own Agent** for hybrid systems
  4. Use **Replay Tasks** for robust error recovery



## 

​

Best Practices

### 

​

Development

  * **Start Simple** : Begin with basic sequential workflows before adding complexity
  * **Test Incrementally** : Test each component before integrating into larger systems
  * **Use Annotations** : Leverage Python annotations for cleaner, more maintainable code
  * **Custom Tools** : Build reusable tools that can be shared across different agents



### 

​

Production

  * **Error Handling** : Implement robust error handling and recovery mechanisms
  * **Performance** : Use async execution and optimize LLM calls for better performance
  * **Monitoring** : Integrate observability tools to track agent performance
  * **Human Oversight** : Include human checkpoints for critical decisions



### 

​

Optimization

  * **Resource Management** : Monitor and optimize token usage and API costs
  * **Workflow Design** : Design workflows that minimize unnecessary LLM calls
  * **Tool Efficiency** : Create efficient tools that provide maximum value with minimal overhead
  * **Iterative Improvement** : Use feedback and metrics to continuously improve agent performance



## 

​

Getting Help

  * **Documentation** : Each guide includes detailed examples and explanations
  * **Community** : Join the [CrewAI Forum](https://community.crewai.com) for discussions and support
  * **Examples** : Check the Examples section for complete working implementations
  * **Support** : Contact [support@crewai.com](mailto:support@crewai.com) for technical assistance



Start with the guides that match your current needs and gradually explore more advanced topics as you become comfortable with the fundamentals.

Was this page helpful?

YesNo

[Weave Integration](/observability/weave)[Conditional Tasks](/learn/conditional-tasks)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Learn CrewAI
  * Getting Started Guides
  * Core Concepts
  * Agent Development
  * Advanced Features
  * Workflow Control
  * Customization & Integration
  * Specialized Applications
  * Content & Media
  * Tool Management
  * Learning Path Recommendations
  * For Beginners
  * For Intermediate Users
  * For Advanced Users
  * Best Practices
  * Development
  * Production
  * Optimization
  * Getting Help



Assistant

Responses are generated using AI and may contain mistakes.


---

### Connecting to Multiple MCP Servers {#connecting-to-multiple-mcp-servers}

**Source:** [https://docs.crewai.com/mcp/multiple-servers](https://docs.crewai.com/mcp/multiple-servers)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

MCP Integration

Connecting to Multiple MCP Servers

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



MCP Integration

# Connecting to Multiple MCP Servers

Copy page

Learn how to use MCPServerAdapter in CrewAI to connect to multiple MCP servers simultaneously and aggregate their tools.

## 

​

Overview

`MCPServerAdapter` in `crewai-tools` allows you to connect to multiple MCP servers concurrently. This is useful when your agents need to access tools distributed across different services or environments. The adapter aggregates tools from all specified servers, making them available to your CrewAI agents.

## 

​

Configuration

To connect to multiple servers, you provide a list of server parameter dictionaries to `MCPServerAdapter`. Each dictionary in the list should define the parameters for one MCP server.

Supported transport types for each server in the list include `stdio`, `sse`, and `streamable-http`.
    
    
    from crewai import Agent, Task, Crew, Process
    from crewai_tools import MCPServerAdapter
    from mcp import StdioServerParameters # Needed for Stdio example
    
    # Define parameters for multiple MCP servers
    server_params_list = [
        # Streamable HTTP Server
        {
            "url": "http://localhost:8001/mcp", 
            "transport": "streamable-http"
        },
        # SSE Server
        {
            "url": "http://localhost:8000/sse",
            "transport": "sse"
        },
        # StdIO Server
        StdioServerParameters(
            command="python3",
            args=["servers/your_stdio_server.py"],
            env={"UV_PYTHON": "3.12", **os.environ},
        )
    ]
    
    try:
        with MCPServerAdapter(server_params_list) as aggregated_tools:
            print(f"Available aggregated tools: {[tool.name for tool in aggregated_tools]}")
    
            multi_server_agent = Agent(
                role="Versatile Assistant",
                goal="Utilize tools from local Stdio, remote SSE, and remote HTTP MCP servers.",
                backstory="An AI agent capable of leveraging a diverse set of tools from multiple sources.",
                tools=aggregated_tools, # All tools are available here
                verbose=True,
            )
    
            ... # Your other agent, tasks, and crew code here
    
    except Exception as e:
        print(f"Error connecting to or using multiple MCP servers (Managed): {e}")
        print("Ensure all MCP servers are running and accessible with correct configurations.")

## 

​

Connection Management

When using the context manager (`with` statement), `MCPServerAdapter` handles the lifecycle (start and stop) of all connections to the configured MCP servers. This simplifies resource management and ensures that all connections are properly closed when the context is exited.

Was this page helpful?

YesNo

[Streamable HTTP Transport](/mcp/streamable-http)[MCP Security Considerations](/mcp/security)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Overview
  * Configuration
  * Connection Management



Assistant

Responses are generated using AI and may contain mistakes.


---

### Changelog {#changelog}

**Source:** [https://docs.crewai.com/changelog](https://docs.crewai.com/changelog)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Releases

Changelog

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Releases

  * [Changelog](/changelog)



Releases

# Changelog

Copy page

View the latest updates and changes to CrewAI

​

2024-05-22

Latest

v0.121.0

## 

​

Release Highlights

[View on GitHub](https://github.com/crewAIInc/crewAI/releases/tag/0.121.0)

**Core Improvements & Fixes**

  * Fixed encoding error when creating tools
  * Fixed failing llama test
  * Updated logging configuration for consistency
  * Enhanced telemetry initialization and event handling



**New Features & Enhancements**

  * Added **markdown attribute** to the Task class
  * Added **reasoning attribute** to the Agent class
  * Added **inject_date flag** to Agent for automatic date injection
  * Implemented **HallucinationGuardrail** (no-op with test coverage)



**Documentation & Guides**

  * Added documentation for **StagehandTool** and improved MDX structure
  * Added documentation for **MCP integration** and updated enterprise docs
  * Documented knowledge events and updated reasoning docs
  * Added stop parameter documentation
  * Fixed import references in doc examples (before_kickoff, after_kickoff)
  * General docs updates and restructuring for clarity



​

2024-05-15

v0.120.1

## 

​

Release Highlights

[View on GitHub](https://github.com/crewAIInc/crewAI/releases/tag/0.120.1)

**Core Improvements & Fixes**

  * Fixed **interpolation with hyphens**



​

2024-05-14

v0.120.0

## 

​

Release Highlights

[View on GitHub](https://github.com/crewAIInc/crewAI/releases/tag/0.120.0)

**Core Improvements & Fixes**

  * Enabled **full Ruff rule set** by default for stricter linting
  * Addressed race condition in FilteredStream using context managers
  * Fixed agent knowledge reset issue
  * Refactored agent fetching logic into utility module



**New Features & Enhancements**

  * Added support for **loading an Agent directly from a repository**
  * Enabled setting an empty context for Task
  * Enhanced Agent repository feedback and fixed Tool auto-import behavior
  * Introduced direct initialization of knowledge (bypassing knowledge_sources)



**Documentation & Guides**

  * Updated security.md for current security practices
  * Cleaned up Google setup section for clarity
  * Added link to AI Studio when entering Gemini key
  * Updated Arize Phoenix observability guide
  * Refreshed flow documentation



​

2024-05-08

v0.119.0

## 

​

Release Highlights

[View on GitHub](https://github.com/crewAIInc/crewAI/releases/tag/0.119.0)

**Core Improvements & Fixes**

  * Improved test reliability by enhancing pytest handling for flaky tests
  * Fixed memory reset crash when embedding dimensions mismatch
  * Enabled parent flow identification for Crew and LiteAgent
  * Prevented telemetry-related crashes when unavailable
  * Upgraded **LiteLLM version** for better compatibility
  * Fixed llama converter tests by removing skip_external_api



**New Features & Enhancements**

  * Introduced **knowledge retrieval prompt re-writing** in Agent for improved tracking and debugging
  * Made LLM setup and quickstart guides model-agnostic



**Documentation & Guides**

  * Added advanced configuration docs for the RAG tool
  * Updated Windows troubleshooting guide
  * Refined documentation examples for better clarity
  * Fixed typos across docs and config files



​

2024-04-28

v0.118.0

## 

​

Release Highlights

[View on GitHub](https://github.com/crewAIInc/crewAI/releases/tag/0.118.0)

**Core Improvements & Fixes**

  * Fixed issues with missing prompt or system templates
  * Removed global logging configuration to avoid unintended overrides
  * Renamed **TaskGuardrail to LLMGuardrail** for improved clarity
  * Downgraded litellm to version 1.167.1 for compatibility
  * Added missing init.py files to ensure proper module initialization



**New Features & Enhancements**

  * Added support for **no-code Guardrail creation** to simplify AI behavior controls



**Documentation & Guides**

  * Removed CrewStructuredTool from public documentation to reflect internal usage
  * Updated enterprise documentation and YouTube embed for improved onboarding experience



​

2024-04-20

v0.117.0

## 

​

Release Highlights

[View on GitHub](https://github.com/crewAIInc/crewAI/releases/tag/0.117.0)

**New Features & Enhancements**

  * Added `result_as_answer` parameter support in `@tool` decorator.
  * Introduced support for new language models: GPT-4.1, Gemini-2.0, and Gemini-2.5 Pro.
  * Enhanced knowledge management capabilities.
  * Added Huggingface provider option in CLI.
  * Improved compatibility and CI support for Python 3.10+.



**Core Improvements & Fixes**

  * Fixed issues with incorrect template parameters and missing inputs.
  * Improved asynchronous flow handling with coroutine condition checks.
  * Enhanced memory management with isolated configuration and correct memory object copying.
  * Fixed initialization of lite agents with correct references.
  * Addressed Python type hint issues and removed redundant imports.
  * Updated event placement for improved tool usage tracking.
  * Raised explicit exceptions when flows fail.
  * Removed unused code and redundant comments from various modules.
  * Updated GitHub App token action to v2.



**Documentation & Guides**

  * Enhanced documentation structure, including enterprise deployment instructions.
  * Automatically create output folders for documentation generation.
  * Fixed broken link in WeaviateVectorSearchTool documentation.
  * Fixed guardrail documentation usage and import paths for JSON search tools.
  * Updated documentation for CodeInterpreterTool.
  * Improved SEO, contextual navigation, and error handling for documentation pages.



​

2024-04-25

v0.117.1

## 

​

Release Highlights

[View on GitHub](https://github.com/crewAIInc/crewAI/releases/tag/0.117.1)

**Core Improvements & Fixes**

  * Upgraded **crewai-tools** to latest version
  * Upgraded **liteLLM** to latest version
  * Fixed **Mem0 OSS**



​

2024-04-07

v0.114.0

## 

​

Release Highlights

[View on GitHub](https://github.com/crewAIInc/crewAI/releases/tag/0.114.0)

**New Features & Enhancements**

  * Agents as an atomic unit. (`Agent(...).kickoff()`)
  * Support for [Custom LLM implementations](https://docs.crewai.com/guides/advanced/custom-llm).
  * Integrated External Memory and [Opik observability](https://docs.crewai.com/how-to/opik-observability).
  * Enhanced YAML extraction.
  * Multimodal agent validation.
  * Added Secure fingerprints for agents and crews.



**Core Improvements & Fixes**

  * Improved serialization, agent copying, and Python compatibility.
  * Added wildcard support to `emit()`
  * Added support for additional router calls and context window adjustments.
  * Fixed typing issues, validation, and import statements.
  * Improved method performance.
  * Enhanced agent task handling, event emissions, and memory management.
  * Fixed CLI issues, conditional tasks, cloning behavior, and tool outputs.



**Documentation & Guides**

  * Improved documentation structure, theme, and organization.
  * Added guides for Local NVIDIA NIM with WSL2, W&B Weave, and Arize Phoenix.
  * Updated tool configuration examples, prompts, and observability docs.
  * Guide on using singular agents within Flows.



​

2024-03-17

v0.108.0

## 

​

Release Highlights

[View on GitHub](https://github.com/crewAIInc/crewAI/releases/tag/0.108.0)

**New Features & Enhancements**

  * Converted tabs to spaces in `crew.py` template
  * Enhanced LLM Streaming Response Handling and Event System
  * Included `model_name`
  * Enhanced Event Listener with rich visualization and improved logging
  * Added fingerprints



**Bug Fixes**

  * Fixed Mistral issues
  * Fixed a bug in documentation
  * Fixed type check error in fingerprint property



**Documentation Updates**

  * Improved tool documentation
  * Updated installation guide for the `uv` tool package
  * Added instructions for upgrading crewAI with the `uv` tool
  * Added documentation for `ApifyActorsTool`



​

2024-03-10

v0.105.0

## 

​

Release Highlights

[View on GitHub](https://github.com/crewAIInc/crewAI/releases/tag/0.105.0)

**Core Improvements & Fixes**

  * Fixed issues with missing template variables and user memory configuration
  * Improved async flow support and addressed agent response formatting
  * Enhanced memory reset functionality and fixed CLI memory commands
  * Fixed type issues, tool calling properties, and telemetry decoupling



**New Features & Enhancements**

  * Added Flow state export and improved state utilities
  * Enhanced agent knowledge setup with optional crew embedder
  * Introduced event emitter for better observability and LLM call tracking
  * Added support for Python 3.10 and ChatOllama from langchain_ollama
  * Integrated context window size support for the o3-mini model
  * Added support for multiple router calls



**Documentation & Guides**

  * Improved documentation layout and hierarchical structure
  * Added QdrantVectorSearchTool guide and clarified event listener usage
  * Fixed typos in prompts and updated Amazon Bedrock model listings



​

2024-02-12

v0.102.0

## 

​

Release Highlights

[View on GitHub](https://github.com/crewAIInc/crewAI/releases/tag/0.102.0)

**Core Improvements & Fixes**

  * Enhanced LLM Support: Improved structured LLM output, parameter handling, and formatting for Anthropic models
  * Crew & Agent Stability: Fixed issues with cloning agents/crews using knowledge sources, multiple task outputs in conditional tasks, and ignored Crew task callbacks
  * Memory & Storage Fixes: Fixed short-term memory handling with Bedrock, ensured correct embedder initialization, and added a reset memories function in the crew class
  * Training & Execution Reliability: Fixed broken training and interpolation issues with dict and list input types



**New Features & Enhancements**

  * Advanced Knowledge Management: Improved naming conventions and enhanced embedding configuration with custom embedder support
  * Expanded Logging & Observability: Added JSON format support for logging and integrated MLflow tracing documentation
  * Data Handling Improvements: Updated excel_knowledge_source.py to process multi-tab files
  * General Performance & Codebase Clean-Up: Streamlined enterprise code alignment and resolved linting issues
  * Adding new tool: `QdrantVectorSearchTool`



**Documentation & Guides**

  * Updated AI & Memory Docs: Improved Bedrock, Google AI, and long-term memory documentation
  * Task & Workflow Clarity: Added “Human Input” row to Task Attributes, Langfuse guide, and FileWriterTool documentation
  * Fixed Various Typos & Formatting Issues



​

2024-01-28

v0.100.0

## 

​

Release Highlights

[View on GitHub](https://github.com/crewAIInc/crewAI/releases/tag/0.100.0)

**Features**

  * Add Composio docs
  * Add SageMaker as a LLM provider



**Fixes**

  * Overall LLM connection issues
  * Using safe accessors on training
  * Add version check to crew_chat.py



**Documentation**

  * New docs for crewai chat
  * Improve formatting and clarity in CLI and Composio Tool docs



​

2024-01-20

v0.98.0

## 

​

Release Highlights

[View on GitHub](https://github.com/crewAIInc/crewAI/releases/tag/0.98.0)

**Features**

  * Conversation crew v1
  * Add unique ID to flow states
  * Add @persist decorator with FlowPersistence interface



**Integrations**

  * Add SambaNova integration
  * Add NVIDIA NIM provider in cli
  * Introducing VoyageAI



**Fixes**

  * Fix API Key Behavior and Entity Handling in Mem0 Integration
  * Fixed core invoke loop logic and relevant tests
  * Make tool inputs actual objects and not strings
  * Add important missing parts to creating tools
  * Drop litellm version to prevent windows issue
  * Before kickoff if inputs are none
  * Fixed typos, nested pydantic model issue, and docling issues



​

2024-01-04

v0.95.0

## 

​

Release Highlights

[View on GitHub](https://github.com/crewAIInc/crewAI/releases/tag/0.95.0)

**New Features**

  * Adding Multimodal Abilities to Crew
  * Programatic Guardrails
  * HITL multiple rounds
  * Gemini 2.0 Support
  * CrewAI Flows Improvements
  * Add Workflow Permissions
  * Add support for langfuse with litellm
  * Portkey Integration with CrewAI
  * Add interpolate_only method and improve error handling
  * Docling Support
  * Weviate Support



**Fixes**

  * output_file not respecting system path
  * disk I/O error when resetting short-term memory
  * CrewJSONEncoder now accepts enums
  * Python max version
  * Interpolation for output_file in Task
  * Handle coworker role name case/whitespace properly
  * Add tiktoken as explicit dependency and document Rust requirement
  * Include agent knowledge in planning process
  * Change storage initialization to None for KnowledgeStorage
  * Fix optional storage checks
  * include event emitter in flows
  * Docstring, Error Handling, and Type Hints Improvements
  * Suppressed userWarnings from litellm pydantic issues



​

2024-12-05

v0.86.0

## 

​

Release Highlights

[View on GitHub](https://github.com/crewAIInc/crewAI/releases/tag/0.86.0)

**Changes**

  * Remove all references to pipeline and pipeline router
  * Add Nvidia NIM as provider in Custom LLM
  * Add knowledge demo + improve knowledge docs
  * Add HITL multiple rounds of followup
  * New docs about yaml crew with decorators
  * Simplify template crew



​

2024-12-04

v0.85.0

## 

​

Release Highlights

[View on GitHub](https://github.com/crewAIInc/crewAI/releases/tag/0.85.0)

**Features**

  * Added knowledge to agent level
  * Feat/remove langchain
  * Improve typed task outputs
  * Log in to Tool Repository on crewai login



**Fixes**

  * Fixes issues with result as answer not properly exiting LLM loop
  * Fix missing key name when running with ollama provider
  * Fix spelling issue found



**Documentation**

  * Update readme for running mypy
  * Add knowledge to mint.json
  * Update Github actions
  * Update Agents docs to include two approaches for creating an agent
  * Improvements to LLM Configuration and Usage



​

2024-11-25

v0.83.0

**New Features**

  * New before_kickoff and after_kickoff crew callbacks
  * Support to pre-seed agents with Knowledge
  * Add support for retrieving user preferences and memories using Mem0



**Fixes**

  * Fix Async Execution
  * Upgrade chroma and adjust embedder function generator
  * Update CLI Watson supported models + docs
  * Reduce level for Bandit
  * Fixing all tests



**Documentation**

  * Update Docs



​

2024-11-13

v0.80.0

**Fixes**

  * Fixing Tokens callback replacement bug
  * Fixing Step callback issue
  * Add cached prompt tokens info on usage metrics
  * Fix crew_train_success test



Was this page helpful?

YesNo

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

FiltersClear

Latest

Assistant

Responses are generated using AI and may contain mistakes.


---

### MCP Servers as Tools in CrewAI {#mcp-servers-as-tools-in-crewai}

**Source:** [https://docs.crewai.com/mcp/overview](https://docs.crewai.com/mcp/overview)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

MCP Integration

MCP Servers as Tools in CrewAI

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



MCP Integration

# MCP Servers as Tools in CrewAI

Copy page

Learn how to integrate MCP servers as tools in your CrewAI agents using the `crewai-tools` library.

## 

​

Overview

The [Model Context Protocol](https://modelcontextprotocol.io/introduction) (MCP) provides a standardized way for AI agents to provide context to LLMs by communicating with external services, known as MCP Servers. The `crewai-tools` library extends CrewAI’s capabilities by allowing you to seamlessly integrate tools from these MCP servers into your agents. This gives your crews access to a vast ecosystem of functionalities.

We currently support the following transport mechanisms:

  * **Stdio** : for local servers (communication via standard input/output between processes on the same machine)
  * **Server-Sent Events (SSE)** : for remote servers (unidirectional, real-time data streaming from server to client over HTTP)
  * **Streamable HTTP** : for remote servers (flexible, potentially bi-directional communication over HTTP, often utilizing SSE for server-to-client streams)



## 

​

Video Tutorial

Watch this video tutorial for a comprehensive guide on MCP integration with CrewAI:

## 

​

Installation

Before you start using MCP with `crewai-tools`, you need to install the `mcp` extra `crewai-tools` dependency with the following command:
    
    
    uv pip install 'crewai-tools[mcp]'

## 

​

Key Concepts & Getting Started

The `MCPServerAdapter` class from `crewai-tools` is the primary way to connect to an MCP server and make its tools available to your CrewAI agents. It supports different transport mechanisms and simplifies connection management.

Using a Python context manager (`with` statement) is the **recommended approach** for `MCPServerAdapter`. It automatically handles starting and stopping the connection to the MCP server.
    
    
    from crewai import Agent
    from crewai_tools import MCPServerAdapter
    from mcp import StdioServerParameters # For Stdio Server
    
    # Example server_params (choose one based on your server type):
    # 1. Stdio Server:
    server_params=StdioServerParameters(
        command="python3", 
        args=["servers/your_server.py"],
        env={"UV_PYTHON": "3.12", **os.environ},
    )
    
    # 2. SSE Server:
    server_params = {
        "url": "http://localhost:8000/sse", 
        "transport": "sse"
    }
    
    # 3. Streamable HTTP Server:
    server_params = {
        "url": "http://localhost:8001/mcp", 
        "transport": "streamable-http"
    }
    
    # Example usage (uncomment and adapt once server_params is set):
    with MCPServerAdapter(server_params) as mcp_tools:
        print(f"Available tools: {[tool.name for tool in mcp_tools]}")
        
        my_agent = Agent(
            role="MCP Tool User",
            goal="Utilize tools from an MCP server.",
            backstory="I can connect to MCP servers and use their tools.",
            tools=mcp_tools, # Pass the loaded tools to your agent
            reasoning=True,
            verbose=True
        )
        # ... rest of your crew setup ...

This general pattern shows how to integrate tools. For specific examples tailored to each transport, refer to the detailed guides below.

## 

​

Explore MCP Integrations

## [Stdio TransportConnect to local MCP servers via standard input/output. Ideal for scripts and local executables.](/mcp/stdio)## [SSE TransportIntegrate with remote MCP servers using Server-Sent Events for real-time data streaming.](/mcp/sse)## [Streamable HTTP TransportUtilize flexible Streamable HTTP for robust communication with remote MCP servers.](/mcp/streamable-http)## [Connecting to Multiple ServersAggregate tools from several MCP servers simultaneously using a single adapter.](/mcp/multiple-servers)## [Security ConsiderationsReview important security best practices for MCP integration to keep your agents safe.](/mcp/security)

Checkout this repository for full demos and examples of MCP integration with CrewAI! 👇

## [GitHub RepositoryCrewAI MCP Demo](https://github.com/tonykipkemboi/crewai-mcp-demo)

## 

​

Staying Safe with MCP

Always ensure that you trust an MCP Server before using it.

#### 

​

Security Warning: DNS Rebinding Attacks

SSE transports can be vulnerable to DNS rebinding attacks if not properly secured. To prevent this:

  1. **Always validate Origin headers** on incoming SSE connections to ensure they come from expected sources
  2. **Avoid binding servers to all network interfaces** (0.0.0.0) when running locally - bind only to localhost (127.0.0.1) instead
  3. **Implement proper authentication** for all SSE connections



Without these protections, attackers could use DNS rebinding to interact with local MCP servers from remote websites.

For more details, see the [Anthropic’s MCP Transport Security docs](https://modelcontextprotocol.io/docs/concepts/transports#security-considerations).

### 

​

Limitations

  * **Supported Primitives** : Currently, `MCPServerAdapter` primarily supports adapting MCP `tools`. Other MCP primitives like `prompts` or `resources` are not directly integrated as CrewAI components through this adapter at this time.
  * **Output Handling** : The adapter typically processes the primary text output from an MCP tool (e.g., `.content[0].text`). Complex or multi-modal outputs might require custom handling if not fitting this pattern.



Was this page helpful?

YesNo

[Event Listeners](/concepts/event-listener)[Stdio Transport](/mcp/stdio)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Overview
  * Video Tutorial
  * Installation
  * Key Concepts & Getting Started
  * Explore MCP Integrations
  * Staying Safe with MCP
  * Security Warning: DNS Rebinding Attacks
  * Limitations



Assistant

Responses are generated using AI and may contain mistakes.


---

### Human Input on Execution {#human-input-on-execution}

**Source:** [https://docs.crewai.com/learn/human-input-on-execution](https://docs.crewai.com/learn/human-input-on-execution)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Learn

Human Input on Execution

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Learn

# Human Input on Execution

Copy page

Integrating CrewAI with human input during execution in complex decision-making processes and leveraging the full capabilities of the agent’s attributes and tools.

## 

​

Human input in agent execution

Human input is critical in several agent execution scenarios, allowing agents to request additional information or clarification when necessary. This feature is especially useful in complex decision-making processes or when agents require more details to complete a task effectively.

## 

​

Using human input with CrewAI

To integrate human input into agent execution, set the `human_input` flag in the task definition. When enabled, the agent prompts the user for input before delivering its final answer. This input can provide extra context, clarify ambiguities, or validate the agent’s output.

### 

​

Example:
    
    
    pip install crewai

Code
    
    
    import os
    from crewai import Agent, Task, Crew
    from crewai_tools import SerperDevTool
    
    os.environ["SERPER_API_KEY"] = "Your Key"  # serper.dev API key
    os.environ["OPENAI_API_KEY"] = "Your Key"
    
    # Loading Tools
    search_tool = SerperDevTool()
    
    # Define your agents with roles, goals, tools, and additional attributes
    researcher = Agent(
        role='Senior Research Analyst',
        goal='Uncover cutting-edge developments in AI and data science',
        backstory=(
            "You are a Senior Research Analyst at a leading tech think tank. "
            "Your expertise lies in identifying emerging trends and technologies in AI and data science. "
            "You have a knack for dissecting complex data and presenting actionable insights."
        ),
        verbose=True,
        allow_delegation=False,
        tools=[search_tool]
    )
    writer = Agent(
        role='Tech Content Strategist',
        goal='Craft compelling content on tech advancements',
        backstory=(
            "You are a renowned Tech Content Strategist, known for your insightful and engaging articles on technology and innovation. "
            "With a deep understanding of the tech industry, you transform complex concepts into compelling narratives."
        ),
        verbose=True,
        allow_delegation=True,
        tools=[search_tool],
        cache=False,  # Disable cache for this agent
    )
    
    # Create tasks for your agents
    task1 = Task(
        description=(
            "Conduct a comprehensive analysis of the latest advancements in AI in 2025. "
            "Identify key trends, breakthrough technologies, and potential industry impacts. "
            "Compile your findings in a detailed report. "
            "Make sure to check with a human if the draft is good before finalizing your answer."
        ),
        expected_output='A comprehensive full report on the latest AI advancements in 2025, leave nothing out',
        agent=researcher,
        human_input=True
    )
    
    task2 = Task(
        description=(
            "Using the insights from the researcher\'s report, develop an engaging blog post that highlights the most significant AI advancements. "
            "Your post should be informative yet accessible, catering to a tech-savvy audience. "
            "Aim for a narrative that captures the essence of these breakthroughs and their implications for the future."
        ),
        expected_output='A compelling 3 paragraphs blog post formatted as markdown about the latest AI advancements in 2025',
        agent=writer,
        human_input=True
    )
    
    # Instantiate your crew with a sequential process
    crew = Crew(
        agents=[researcher, writer],
        tasks=[task1, task2],
        verbose=True,
        memory=True,
        planning=True  # Enable planning feature for the crew
    )
    
    # Get your crew to work!
    result = crew.kickoff()
    
    print("######################")
    print(result)

Was this page helpful?

YesNo

[Hierarchical Process](/learn/hierarchical-process)[Kickoff Crew Asynchronously](/learn/kickoff-async)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Human input in agent execution
  * Using human input with CrewAI
  * Example:



Assistant

Responses are generated using AI and may contain mistakes.


---

### Kickoff Crew Asynchronously {#kickoff-crew-asynchronously}

**Source:** [https://docs.crewai.com/learn/kickoff-async](https://docs.crewai.com/learn/kickoff-async)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Learn

Kickoff Crew Asynchronously

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Learn

# Kickoff Crew Asynchronously

Copy page

Kickoff a Crew Asynchronously

## 

​

Introduction

CrewAI provides the ability to kickoff a crew asynchronously, allowing you to start the crew execution in a non-blocking manner. This feature is particularly useful when you want to run multiple crews concurrently or when you need to perform other tasks while the crew is executing.

## 

​

Asynchronous Crew Execution

To kickoff a crew asynchronously, use the `kickoff_async()` method. This method initiates the crew execution in a separate thread, allowing the main thread to continue executing other tasks.

### 

​

Method Signature

Code
    
    
    def kickoff_async(self, inputs: dict) -> CrewOutput:

### 

​

Parameters

  * `inputs` (dict): A dictionary containing the input data required for the tasks.



### 

​

Returns

  * `CrewOutput`: An object representing the result of the crew execution.



## 

​

Potential Use Cases

  * **Parallel Content Generation** : Kickoff multiple independent crews asynchronously, each responsible for generating content on different topics. For example, one crew might research and draft an article on AI trends, while another crew generates social media posts about a new product launch. Each crew operates independently, allowing content production to scale efficiently.

  * **Concurrent Market Research Tasks** : Launch multiple crews asynchronously to conduct market research in parallel. One crew might analyze industry trends, while another examines competitor strategies, and yet another evaluates consumer sentiment. Each crew independently completes its task, enabling faster and more comprehensive insights.

  * **Independent Travel Planning Modules** : Execute separate crews to independently plan different aspects of a trip. One crew might handle flight options, another handles accommodation, and a third plans activities. Each crew works asynchronously, allowing various components of the trip to be planned simultaneously and independently for faster results.




## 

​

Example: Single Asynchronous Crew Execution

Here’s an example of how to kickoff a crew asynchronously using asyncio and awaiting the result:

Code
    
    
    import asyncio
    from crewai import Crew, Agent, Task
    
    # Create an agent with code execution enabled
    coding_agent = Agent(
        role="Python Data Analyst",
        goal="Analyze data and provide insights using Python",
        backstory="You are an experienced data analyst with strong Python skills.",
        allow_code_execution=True
    )
    
    # Create a task that requires code execution
    data_analysis_task = Task(
        description="Analyze the given dataset and calculate the average age of participants. Ages: {ages}",
        agent=coding_agent,
        expected_output="The average age of the participants."
    )
    
    # Create a crew and add the task
    analysis_crew = Crew(
        agents=[coding_agent],
        tasks=[data_analysis_task]
    )
    
    # Async function to kickoff the crew asynchronously
    async def async_crew_execution():
        result = await analysis_crew.kickoff_async(inputs={"ages": [25, 30, 35, 40, 45]})
        print("Crew Result:", result)
    
    # Run the async function
    asyncio.run(async_crew_execution())

## 

​

Example: Multiple Asynchronous Crew Executions

In this example, we’ll show how to kickoff multiple crews asynchronously and wait for all of them to complete using `asyncio.gather()`:

Code
    
    
    import asyncio
    from crewai import Crew, Agent, Task
    
    # Create an agent with code execution enabled
    coding_agent = Agent(
        role="Python Data Analyst",
        goal="Analyze data and provide insights using Python",
        backstory="You are an experienced data analyst with strong Python skills.",
        allow_code_execution=True
    )
    
    # Create tasks that require code execution
    task_1 = Task(
        description="Analyze the first dataset and calculate the average age of participants. Ages: {ages}",
        agent=coding_agent,
        expected_output="The average age of the participants."
    )
    
    task_2 = Task(
        description="Analyze the second dataset and calculate the average age of participants. Ages: {ages}",
        agent=coding_agent,
        expected_output="The average age of the participants."
    )
    
    # Create two crews and add tasks
    crew_1 = Crew(agents=[coding_agent], tasks=[task_1])
    crew_2 = Crew(agents=[coding_agent], tasks=[task_2])
    
    # Async function to kickoff multiple crews asynchronously and wait for all to finish
    async def async_multiple_crews():
        result_1 = crew_1.kickoff_async(inputs={"ages": [25, 30, 35, 40, 45]})
        result_2 = crew_2.kickoff_async(inputs={"ages": [20, 22, 24, 28, 30]})
    
        # Wait for both crews to finish
        results = await asyncio.gather(result_1, result_2)
    
        for i, result in enumerate(results, 1):
            print(f"Crew {i} Result:", result)
    
    # Run the async function
    asyncio.run(async_multiple_crews())

Was this page helpful?

YesNo

[Human Input on Execution](/learn/human-input-on-execution)[Kickoff Crew for Each](/learn/kickoff-for-each)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Introduction
  * Asynchronous Crew Execution
  * Method Signature
  * Parameters
  * Returns
  * Potential Use Cases
  * Example: Single Asynchronous Crew Execution
  * Example: Multiple Asynchronous Crew Executions



Assistant

Responses are generated using AI and may contain mistakes.


---

### Sequential Processes {#sequential-processes}

**Source:** [https://docs.crewai.com/learn/sequential-process](https://docs.crewai.com/learn/sequential-process)

[CrewAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crew_only_logo.png)](/)

Search CrewAI docs

Ask AI

  * [Start Cloud Trial](https://app.crewai.com)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)
  * [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI)



Search...

Navigation

Learn

Sequential Processes

[Documentation](/introduction)[Enterprise](/enterprise/introduction)[API Reference](/api-reference/introduction)[Examples](/examples/example)[Releases](/changelog)

* [Website](https://crewai.com)
* [Forum](https://community.crewai.com)
* [Crew GPT](https://chatgpt.com/g/g-qqTuUWsBY-crewai-assistant)
* [Get Help](mailto:support@crewai.com)

##### Get Started

  * [Introduction](/introduction)
  * [Installation](/installation)
  * [Quickstart](/quickstart)



##### Guides

  * Strategy

  * Agents

  * Crews

  * Flows

  * Advanced




##### Core Concepts

  * [Agents](/concepts/agents)
  * [Tasks](/concepts/tasks)
  * [Crews](/concepts/crews)
  * [Flows](/concepts/flows)
  * [Knowledge](/concepts/knowledge)
  * [LLMs](/concepts/llms)
  * [Processes](/concepts/processes)
  * [Collaboration](/concepts/collaboration)
  * [Training](/concepts/training)
  * [Memory](/concepts/memory)
  * [Reasoning](/concepts/reasoning)
  * [Planning](/concepts/planning)
  * [Testing](/concepts/testing)
  * [CLI](/concepts/cli)
  * [Tools](/concepts/tools)
  * [Event Listeners](/concepts/event-listener)



##### MCP Integration

  * [MCP Servers as Tools in CrewAI](/mcp/overview)
  * [Stdio Transport](/mcp/stdio)
  * [SSE Transport](/mcp/sse)
  * [Streamable HTTP Transport](/mcp/streamable-http)
  * [Connecting to Multiple MCP Servers](/mcp/multiple-servers)
  * [MCP Security Considerations](/mcp/security)



##### Tools

  * [Tools Overview](/tools/overview)
  * File & Document

  * Web Scraping & Browsing

  * Search & Research

  * Database & Data

  * AI & Machine Learning

  * Cloud & Storage

  * Automation & Integration




##### Observability

  * [Overview](/observability/overview)
  * [AgentOps Integration](/observability/agentops)
  * [Arize Phoenix](/observability/arize-phoenix)
  * [Langfuse Integration](/observability/langfuse)
  * [Langtrace Integration](/observability/langtrace)
  * [MLflow Integration](/observability/mlflow)
  * [OpenLIT Integration](/observability/openlit)
  * [Opik Integration](/observability/opik)
  * [Patronus AI Evaluation](/observability/patronus-evaluation)
  * [Portkey Integration](/observability/portkey)
  * [Weave Integration](/observability/weave)



##### Learn

  * [Overview](/learn/overview)
  * [Conditional Tasks](/learn/conditional-tasks)
  * [Coding Agents](/learn/coding-agents)
  * [Create Custom Tools](/learn/create-custom-tools)
  * [Custom LLM Implementation](/learn/custom-llm)
  * [Custom Manager Agent](/learn/custom-manager-agent)
  * [Customize Agents](/learn/customizing-agents)
  * [Image Generation with DALL-E](/learn/dalle-image-generation)
  * [Force Tool Output as Result](/learn/force-tool-output-as-result)
  * [Hierarchical Process](/learn/hierarchical-process)
  * [Human Input on Execution](/learn/human-input-on-execution)
  * [Kickoff Crew Asynchronously](/learn/kickoff-async)
  * [Kickoff Crew for Each](/learn/kickoff-for-each)
  * [Connect to any LLM](/learn/llm-connections)
  * [Using Multimodal Agents](/learn/multimodal-agents)
  * [Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)
  * [Sequential Processes](/learn/sequential-process)
  * [Using Annotations in crew.py](/learn/using-annotations)



##### Telemetry

  * [Telemetry](/telemetry)



Learn

# Sequential Processes

Copy page

A comprehensive guide to utilizing the sequential processes for task execution in CrewAI projects.

## 

​

Introduction

CrewAI offers a flexible framework for executing tasks in a structured manner, supporting both sequential and hierarchical processes. This guide outlines how to effectively implement these processes to ensure efficient task execution and project completion.

## 

​

Sequential Process Overview

The sequential process ensures tasks are executed one after the other, following a linear progression. This approach is ideal for projects requiring tasks to be completed in a specific order.

### 

​

Key Features

  * **Linear Task Flow** : Ensures orderly progression by handling tasks in a predetermined sequence.
  * **Simplicity** : Best suited for projects with clear, step-by-step tasks.
  * **Easy Monitoring** : Facilitates easy tracking of task completion and project progress.



## 

​

Implementing the Sequential Process

To use the sequential process, assemble your crew and define tasks in the order they need to be executed.

Code
    
    
    from crewai import Crew, Process, Agent, Task, TaskOutput, CrewOutput
    
    # Define your agents
    researcher = Agent(
      role='Researcher',
      goal='Conduct foundational research',
      backstory='An experienced researcher with a passion for uncovering insights'
    )
    analyst = Agent(
      role='Data Analyst',
      goal='Analyze research findings',
      backstory='A meticulous analyst with a knack for uncovering patterns'
    )
    writer = Agent(
      role='Writer',
      goal='Draft the final report',
      backstory='A skilled writer with a talent for crafting compelling narratives'
    )
    
    # Define your tasks
    research_task = Task(
      description='Gather relevant data...', 
      agent=researcher, 
      expected_output='Raw Data'
    )
    analysis_task = Task(
      description='Analyze the data...', 
      agent=analyst, 
      expected_output='Data Insights'
    )
    writing_task = Task(
      description='Compose the report...', 
      agent=writer, 
      expected_output='Final Report'
    )
    
    # Form the crew with a sequential process
    report_crew = Crew(
      agents=[researcher, analyst, writer],
      tasks=[research_task, analysis_task, writing_task],
      process=Process.sequential
    )
    
    # Execute the crew
    result = report_crew.kickoff()
    
    # Accessing the type-safe output
    task_output: TaskOutput = result.tasks[0].output
    crew_output: CrewOutput = result.output

### 

​

Note:

Each task in a sequential process **must** have an agent assigned. Ensure that every `Task` includes an `agent` parameter.

### 

​

Workflow in Action

  1. **Initial Task** : In a sequential process, the first agent completes their task and signals completion.
  2. **Subsequent Tasks** : Agents pick up their tasks based on the process type, with outcomes of preceding tasks or directives guiding their execution.
  3. **Completion** : The process concludes once the final task is executed, leading to project completion.



## 

​

Advanced Features

### 

​

Task Delegation

In sequential processes, if an agent has `allow_delegation` set to `True`, they can delegate tasks to other agents in the crew. This feature is automatically set up when there are multiple agents in the crew.

### 

​

Asynchronous Execution

Tasks can be executed asynchronously, allowing for parallel processing when appropriate. To create an asynchronous task, set `async_execution=True` when defining the task.

### 

​

Memory and Caching

CrewAI supports both memory and caching features:

  * **Memory** : Enable by setting `memory=True` when creating the Crew. This allows agents to retain information across tasks.
  * **Caching** : By default, caching is enabled. Set `cache=False` to disable it.



### 

​

Callbacks

You can set callbacks at both the task and step level:

  * `task_callback`: Executed after each task completion.
  * `step_callback`: Executed after each step in an agent’s execution.



### 

​

Usage Metrics

CrewAI tracks token usage across all tasks and agents. You can access these metrics after execution.

## 

​

Best Practices for Sequential Processes

  1. **Order Matters** : Arrange tasks in a logical sequence where each task builds upon the previous one.
  2. **Clear Task Descriptions** : Provide detailed descriptions for each task to guide the agents effectively.
  3. **Appropriate Agent Selection** : Match agents’ skills and roles to the requirements of each task.
  4. **Use Context** : Leverage the context from previous tasks to inform subsequent ones.



This updated documentation ensures that details accurately reflect the latest changes in the codebase and clearly describes how to leverage new features and configurations. The content is kept simple and direct to ensure easy understanding.

Was this page helpful?

YesNo

[Replay Tasks from Latest Crew Kickoff](/learn/replay-tasks-from-latest-crew-kickoff)[Using Annotations in crew.py](/learn/using-annotations)

[website](https://crewai.com)[x](https://x.com/crewAIInc)[github](https://github.com/crewAIInc/crewAI)[linkedin](https://www.linkedin.com/company/crewai-inc)[youtube](https://youtube.com/@crewAIInc)[reddit](https://www.reddit.com/r/crewAIInc/)

[Powered by Mintlify](https://mintlify.com/preview-request?utm_campaign=poweredBy&utm_medium=referral&utm_source=docs.crewai.com)

On this page

  * Introduction
  * Sequential Process Overview
  * Key Features
  * Implementing the Sequential Process
  * Note:
  * Workflow in Action
  * Advanced Features
  * Task Delegation
  * Asynchronous Execution
  * Memory and Caching
  * Callbacks
  * Usage Metrics
  * Best Practices for Sequential Processes



Assistant

Responses are generated using AI and may contain mistakes.


---

