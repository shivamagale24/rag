from llm import LLMService


llm = LLMService()

response = llm.generate_response(
    "What is ISO 27001? Answer in one sentence."
)

print("\nLLM Response:\n")
print(response)