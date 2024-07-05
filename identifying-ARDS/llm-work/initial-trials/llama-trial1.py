from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch

# Load tokenizer and model
model_id = "ruslanmv/llama3-8B-medical"

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16
)

tokenizer = AutoTokenizer.from_pretrained(model_id)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

model = AutoModelForCausalLM.from_pretrained(model_id, config=quantization_config)

def create_prompt(user_query):
  B_INST, E_INST = "<s>[INST]", "[/INST]"
  B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
  DEFAULT_SYSTEM_PROMPT = """\
  You are an AI Medical Chatbot Assistant, provide comprehensive and informative responses to your inquiries.
  If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information."""
  SYSTEM_PROMPT = B_SYS + DEFAULT_SYSTEM_PROMPT + E_SYS
  instruction = f"User asks: {user_query}\n"
  prompt = B_INST + SYSTEM_PROMPT + instruction + E_INST
  return prompt.strip()

def generate_text(model, tokenizer, prompt,
                  max_length=200,
                  temperature=0.8,
                  num_return_sequences=1):
    prompt = create_prompt(user_query)
    # Tokenize the prompt
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)  # Move input_ids to the same device as the model
    # Generate text
    output = model.generate(
        input_ids=input_ids,
        max_length=max_length,
        temperature=temperature,
        num_return_sequences=num_return_sequences,
        pad_token_id=tokenizer.eos_token_id,  # Set pad token to end of sequence token
        do_sample=True
    )    
    # Decode the generated output
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
  
   # Split the generated text based on the prompt and take the portion after it
    generated_text = generated_text.split(prompt)[-1].strip()

    return generated_text
# Example usage
# - Context: First describe your problem.
# - Question: Then make the question.
user_query = "I'm a 35-year-old male experiencing symptoms like fatigue, increased sensitivity to cold, and dry, itchy skin. Could these be indicative of hypothyroidism?"
generated_text = generate_text(model, tokenizer, user_query)    
print(generated_text)
