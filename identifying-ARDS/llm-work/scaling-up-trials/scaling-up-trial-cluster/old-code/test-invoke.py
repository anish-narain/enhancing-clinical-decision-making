from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

def test_model_invocation():
    model_name = "llama3"
    base_url = "http://localhost:11434"  # Specify the base URL here
    llm = Ollama(model=model_name, base_url=base_url, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))
    prompt_template = PromptTemplate(
        template=(
            "Context: You are a clinician receiving chunks of clinical text for patients in an ICU. Please do the reviewing as quickly as possible.\n"
            "Task: Determine if the patient had pneumonia.\n"
            "Instructions: Answer with 'Yes' or 'No'. If there is not enough information, answer 'No'.\n"
            "Discharge Text:\n{discharge_text}\n\n"
            "Query: Does the chunk of text suggest that the patient has pneumonia? Answer strictly in 'Yes' or 'No'."
        ),
        input_variables=["discharge_text"]
    )

    discharge_text = "Patient has a history of coughing and fever. Chest X-ray shows some infiltrates."
    prompt = prompt_template.format(discharge_text=discharge_text)
    response = llm.invoke(prompt)
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")

test_model_invocation()
