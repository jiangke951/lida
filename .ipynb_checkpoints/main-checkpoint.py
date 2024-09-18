# from openai import OpenAI
#
# client = OpenAI(
#     base_url="https://api.cpdd666.cn/v1",
#     api_key=""
# )
#
# completion = client.chat.completions.create(
#   model="gpt-3.5-turbo",
#   messages=[
#     {"role": "system", "content": "You are a helpful assistant."},
#     {"role": "user", "content": "Hello!"}
#   ]
# )
#
# lida = Manager(text_gen = llm("openai", api_key='')) # !! api key
# textgen_config = TextGenerationConfig(n=1, temperature=0.5, model="gpt-3.5-turbo-0301", use_cache=True)
#
# summary = lida.summarize("https://raw.githubusercontent.com/uwdata/draco/master/data/cars.csv", summary_method="default", textgen_config=textgen_config)
# goals = lida.goals(summary, n=2, textgen_config=textgen_config)
#
# for goal in goals:
#     display(goal)

from lida import Manager, TextGenerationConfig , llm
lida = Manager(text_gen = llm("openai", api_key='')) # !! api key
textgen_config = TextGenerationConfig(n=1, temperature=0.5, model="gpt-3.5-turbo", use_cache=True)

summary = lida.summarize("https://raw.githubusercontent.com/uwdata/draco/master/data/cars.csv", summary_method="default", textgen_config=textgen_config)
goals = lida.goals(summary, n=2, textgen_config=textgen_config)

for goal in goals:
    display(goal)