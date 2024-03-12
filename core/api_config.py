import os
# set your OPENAI_API_BASE, OPENAI_API_KEY here!
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://cfcus02.opapi.win/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-XVBaWFFC3af98090Dc32T3BLbkFJ0Ba9481790144B1eaA6B")


from openai import OpenAI

client = OpenAI(
  api_key = OPENAI_API_KEY,  # this is also the default, it can be omitted
  base_url = OPENAI_API_BASE,
)
# openai.api_type = "openai"
# openai.api_base = OPENAI_API_BASE
# # set your own api_version
# # openai.api_version = "2023-07-01-preview"
# openai.api_key = OPENAI_API_KEY

MODEL_NAME = 'gpt-3.5-turbo' # 128k 版本
# MODEL_NAME = 'CodeLlama-7b-hf'
# MODEL_NAME = 'gpt-4-32k' # 0613版本
# MODEL_NAME = 'gpt-4' # 0613版本
# MODEL_NAME = 'gpt-35-turbo-16k' # 0613版本