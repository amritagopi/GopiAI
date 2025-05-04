---
layout: default
title: "RAG"
parent: "Design Pattern"
nav_order: 4
---

# RAG (Retrieval Augmented Generation)

For certain LLM tasks like answering questions, providing context is essential.
Most common way to retrive text-based context is through embedding:
1. Given texts, you first [chunk](../utility_function/chunking.md) them.
2. Next, you [embed](../utility_function/embedding.md) each chunk.
3. Then you store the chunks in [vector databases](../utility_function/vector.md).
4. Finally, given a query, you embed the query and find the closest chunk in the vector databases.

### Example: Question Answering

```python
class PrepareEmbeddings(Node):
    def prep(self, shared):
        return shared["texts"]

    def exec(self, texts):
        # Embed each text chunk
        embs = [get_embedding(t) for t in texts]
        return embs

    def post(self, shared, prep_res, exec_res):
        shared["search_index"] = create_index(exec_res)
        # no action string means "default"

class AnswerQuestion(Node):
    def prep(self, shared):
        question = input("Enter question: ")
        return question

    def exec(self, question):
        q_emb = get_embedding(question)
        idx, _ = search_index(shared["search_index"], q_emb, top_k=1)
        best_id = idx[0][0]
        relevant_text = shared["texts"][best_id]
        prompt = f"Question: {question}\nContext: {relevant_text}\nAnswer:"
        return call_llm(prompt)

    def post(self, shared, p, answer):
        print("Answer:", answer)

############################################
# Wire up the flow
prep = PrepareEmbeddings()
qa = AnswerQuestion()
prep >> qa

flow = Flow(start=prep)

# Example usage
shared = {"texts": ["I love apples", "Cats are great", "The sky is blue"]}
flow.run(shared)
```