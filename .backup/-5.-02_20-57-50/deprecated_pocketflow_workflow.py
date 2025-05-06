# PocketFlow Workflow Definition

workflow = {
    'name': 'LLM Question Answering',
    'steps': [
        {
            'name': 'Input Question',
            'action': 'input',
            'description': 'Receive a question from the user.'
        },
        {
            'name': 'Process with LLM',
            'action': 'execute_script',
            'script': 'llm_interaction.py',
            'description': 'Use the LLM to process the question and get an answer.'
        },
        {
            'name': 'Output Answer',
            'action': 'output',
            'description': 'Return the answer to the user.'
        }
    ]
}