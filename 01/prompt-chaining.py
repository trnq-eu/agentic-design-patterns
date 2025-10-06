from google import genai
from dotenv import load_dotenv
import os

'''
Implementation of the prompt chaining technique using Gemini SDK
'''

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')


client = genai.Client(api_key = GEMINI_API_KEY)

prompt_extract = "Extract the technical specifications from the following text:\n\n{text_input}"
prompt_transform = "Transform the following specifications into a JSON object with 'cpu', 'memory', and 'storage' as keys:\n\n{specifications}"
input_text = "The new laptop model features a 3.5 GHz octa-core processor, 16GB of RAM, and a 1TB NVMe SSD."

print("--- Step 1: Extracting Specifications ---")
formatted_prompt_1 = prompt_extract.format(text_input=input_text)

response_step_1 = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=formatted_prompt_1,
)

specifications_output = response_step_1.text.strip()
print(f"Extracted Specifications:\n{specifications_output}")
print("-" * 30)

print("--- Step 2: Transforming to JSON ---")


formatted_prompt_2 = prompt_transform.format(specifications = specifications_output)

response_step_2 = client.models.generate_content(
    model="gemini-2.5-flash",
    contents = formatted_prompt_2
)

json_output = response_step_2
print(f"Final JSON Output:\n{json_output.text}")
