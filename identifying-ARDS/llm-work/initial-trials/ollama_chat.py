from ollama import Client

client = Client(host='http://localhost:11434')
response = client.chat(model='llama2', messages=[
  {
    'role': 'user',
    'content': 'Why is the sky blue?',
  },
])

print(response)

