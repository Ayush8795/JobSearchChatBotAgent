
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GPT4V_KEY")
endpoint = os.getenv("GPT4V_ENDPOINT")

version = os.getenv('API_VERSION')


client = AzureOpenAI(azure_endpoint = endpoint, api_key = api_key, api_version = version)


def callGPT(messages, max_tokens = 4096):
    output = client.chat.completions.create(
        model = "gpt4onew",
        messages = messages,
        max_tokens = max_tokens
        
      )
    response = output.choices[0].message.content
    return response


async def stream_azure_openai(messages,max_tokens=4096):
    # Send a streaming request to Azure OpenAI
    stream = await client.chat.completions.create(
        model ="gpt4onew", # replace with your deployed model name
        messages = messages,
        stream = True,
        max_tokens = max_tokens
    )

    # Process the streaming response
    async for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            resp= chunk.choices[0].delta.content
            # print(chunk.choices[0].delta.content, end='', flush=True)
            yield resp


async def stream_caller(messages,max_tokens=4096):
    response= ""
    flag=0
    try:
      async for content in stream_azure_openai(messages,max_tokens):
        response+= content
    except:
       flag=1
       return response,flag

    return response,flag


def callGemini(prompt, max_tokens = 65535):
  client = genai.Client(
      vertexai=True,
      project="ai-agent-458906",
      location="us-central1",
  )

  msg1_text1 = types.Part.from_text(text = prompt)

  model = "gemini-2.5-flash-preview-05-20"
  contents = [
    types.Content(
      role="user",
      parts=[
        msg1_text1
      ]
    )
    ]

  generate_content_config = types.GenerateContentConfig(
    temperature = 1,
    top_p = 1,
    seed = 0,
    max_output_tokens = max_tokens,
    safety_settings = [types.SafetySetting(
      category="HARM_CATEGORY_HATE_SPEECH",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_DANGEROUS_CONTENT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_HARASSMENT",
      threshold="OFF"
    )],
  )

  response_text = ""

  for chunk in client.models.generate_content_stream(
    model = model,
    contents = contents,
    config = generate_content_config,
    ):
    response_text += chunk.text

  return response_text


# print(callGemini("what are the recent developments in technology?"))