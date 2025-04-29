---
layout: default
title: "Chat Memory"
parent: "Design Pattern"
nav_order: 5
---

# Chat Memory

Multi-turn conversations require memory management to maintain context while avoiding overwhelming the LLM.

### 1. Naive Approach: Full History

Sending the full chat history may overwhelm LLMs.

```python
class ChatNode(Node):
    def prep(self, shared):
        if "history" not in shared:
            shared["history"] = []
        user_input = input("You: ")
        return shared["history"], user_input

    def exec(self, inputs):
        history, user_input = inputs
        messages = [{"role": "system", "content": "You are a helpful assistant"}]
        for h in history:
            messages.append(h)
        messages.append({"role": "user", "content": user_input})
        response = call_llm(messages)
        return response

    def post(self, shared, prep_res, exec_res):
        shared["history"].append({"role": "user", "content": prep_res[1]})
        shared["history"].append({"role": "assistant", "content": exec_res})
        return "continue"

chat = ChatNode()
chat - "continue" >> chat
flow = Flow(start=chat)
```

### 2. Improved Memory Management

We can:
1. Limit the chat history to the most recent 4.
2. Use [vector search](./tool.md) to retrieve relevant exchanges beyond the last 4.

```python
################################
# Node A: Retrieve user input & relevant messages
################################
class ChatRetrieve(Node):
    def prep(self, s):
        s.setdefault("history", [])
        s.setdefault("memory_index", None)
        user_input = input("You: ")
        return user_input

    def exec(self, user_input):
        emb = get_embedding(user_input)
        relevant = []
        if len(shared["history"]) > 8 and shared["memory_index"]:
            idx, _ = search_index(shared["memory_index"], emb, top_k=2)
            relevant = [shared["history"][i[0]] for i in idx]
        return (user_input, relevant)

    def post(self, s, p, r):
        user_input, relevant = r
        s["user_input"] = user_input
        s["relevant"] = relevant
        return "continue"

################################
# Node B: Call LLM, update history + index
################################
class ChatReply(Node):
    def prep(self, s):
        user_input = s["user_input"]
        recent = s["history"][-8:]
        relevant = s.get("relevant", [])
        return user_input, recent, relevant

    def exec(self, inputs):
        user_input, recent, relevant = inputs
        msgs = [{"role":"system","content":"You are a helpful assistant."}]
        if relevant:
            msgs.append({"role":"system","content":f"Relevant: {relevant}"})
        msgs.extend(recent)
        msgs.append({"role":"user","content":user_input})
        ans = call_llm(msgs)
        return ans

    def post(self, s, pre, ans):
        user_input, _, _ = pre
        s["history"].append({"role":"user","content":user_input})
        s["history"].append({"role":"assistant","content":ans})
        
        # Manage memory index
        if len(s["history"]) == 8:
            embs = []
            for i in range(0, 8, 2):
                text = s["history"][i]["content"] + " " + s["history"][i+1]["content"]
                embs.append(get_embedding(text))
            s["memory_index"] = create_index(embs)
        elif len(s["history"]) > 8:
            text = s["history"][-2]["content"] + " " + s["history"][-1]["content"]
            new_emb = np.array([get_embedding(text)]).astype('float32')
            s["memory_index"].add(new_emb)

        print(f"Assistant: {ans}")
        return "continue"

################################
# Flow wiring
################################
retrieve = ChatRetrieve()
reply = ChatReply()
retrieve - "continue" >> reply
reply - "continue" >> retrieve

flow = Flow(start=retrieve)
shared = {}
flow.run(shared)
```