import pprint
from langchain.utilities import SearxSearchWrapper

search = SearxSearchWrapper(searx_host="https://searx.billbert.co/")

#search.run("What is the capital of France")

#results = search.run("large language model ", engines=['wiki'])

results = search.results("Large Language Model prompt", num_results=5, categories='science', time_range='year')
pprint.pp(results)