from ollama import chat
from ollama import ChatResponse

response: ChatResponse = chat(
    model='llama3.2:3b',
    messages=[
        {
            'role': 'user',
            'content': 'Hello! Do you know about wikipedia?',
        },
    ],
)

# Print out the model's conversational response
print(response['message']['content'])