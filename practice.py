import requests

root_url = 'https://www.dictionaryapi.com/api/v3/references/collegiate/json'
word = 'potato'
api_key = 'ed5728e8-d4ee-4cd7-a14b-b148bb491735'
final_url = f'{root_url}/{word}?key={api_key}'

requests.get(url)

definitions = res.json()

for definition in definitions:
    print(definitions)