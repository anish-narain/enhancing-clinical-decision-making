import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("Henrychur/MMed-Llama-3-8B")
model = AutoModelForCausalLM.from_pretrained("Henrychur/MMed-Llama-3-8B", torch_dtype=torch.float16)

def generate_text(model, tokenizer, user_query, max_length=200, temperature=0.8, num_return_sequences=1):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # Tokenize the prompt
    input_ids = tokenizer.encode(user_query, return_tensors="pt").to(device)  # Move input_ids to the same device as the model
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
  
    return generated_text

# Example usage
user_query = "I'm a 35-year-old male experiencing symptoms like fatigue, increased sensitivity to cold, and dry, itchy skin. Could these be indicative of hypothyroidism?"
generated_text = generate_text(model, tokenizer, user_query)
print(generated_text)