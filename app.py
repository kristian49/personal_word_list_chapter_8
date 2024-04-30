from flask import Flask, request, render_template, redirect, url_for, jsonify
from pymongo import MongoClient
import requests
from datetime import datetime
from bson import ObjectId

app = Flask(__name__)

# client = MongoClient('mongodb+srv://fransiscuskristian:belajarweb@cluster0.6vz5zah.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
password = 'belajarweb'
cxn_str = f'mongodb+srv://fransiscuskristian:{password}@cluster0.6vz5zah.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
client = MongoClient(cxn_str)
db = client.dbchapter8

@app.route('/')
def main():
    # This route should fetch all of the words from the database and pass them on to the HTML template
    words_result = db.words.find({}, {'_id': False})
    words = []
    for word in words_result:
        definition = word['definitions'][0]['shortdef']
        definition = definition if type(definition) is str else definition[0]
        words.append({
            'word': word['word'],
            'definition': definition
        })
    msg = request.args.get('msg')
    return render_template("index.html", words = words, msg = msg)

@app.route('/error')
def error():
    word = request.args.get('word')
    suggestions = request.args.get('suggestions')
    if suggestions:
        suggestions = suggestions.split(',')
    return render_template(
        'error.html',
        word = word,
        suggestions = suggestions
    )

@app.route('/detail/<keyword>')
def detail(keyword):
    # This handler should find the requested word through the dictionary API and pass the data for that word onto the template
    api_key = 'ed5728e8-d4ee-4cd7-a14b-b148bb491735'
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{keyword}?key={api_key}'
    response = requests.get(url)
    definitions = response.json()

    if not definitions:
        return redirect(url_for(
            'error',
            word = keyword
        ))
    
    if type(definitions[0]) is str:
        return redirect(url_for(
            'error',
            word = keyword,
            suggestions = ','.join(definitions)
        ))
    
    status = request.args.get('status_give', 'new')
    return render_template(
        'detail.html',
        word = keyword,
        definitions = definitions,
        status = status
    )

@app.route('/api/save_word', methods = ['POST'])
def save_word():
    # This handler should save the word in the database
    json_data = request.get_json()
    word = json_data.get('word_give')
    definitions = json_data.get('definitions_give')

    doc = {
        'word' : word,
        'definitions' : definitions,
        'date' : datetime.now().strftime('%Y-%m-%d')
    }

    db.words.insert_one(doc)

    return jsonify({
        'result': 'success',
        'msg': f'The word, {word}, was saved!!!'
    })

@app.route('/api/delete_word', methods = ['POST'])
def delete_word():
    # This handler should delete the word from the database
    word = request.form.get('word_give')
    db.words.delete_one({'word': word})
    db.examples.delete_many({'word': word})
    return jsonify({
        'result': 'success',
        'msg': f'The word, {word} was deleted'
    })

@app.route('/api/get_exs', methods = ['GET'])
def get_exs():
    word = request.args.get('word')
    example_data = db.examples.find({'word': word})
    examples = []
    for example in example_data:
        examples.append({
            'example': example.get('example'),
            'id': str(example.get('_id'))
        })
    return jsonify({
        'result': 'success',
        'examples': examples
    })

@app.route('/api/save_ex', methods = ['POST'])
def save_ex():
    word = request.form.get('word')
    example = request.form.get('example')
    doc = {
        'word': word,
        'example': example
    }
    db.examples.insert_one(doc)
    return jsonify({
        'result': 'success',
        'msg': f'Your example, {example}, for the word, {word}, was saved!'
    })

@app.route('/api/delete_ex', methods = ['POST'])
def delete_ex():
    id = request.form.get('id')
    word = request.form.get('word')
    db.examples.delete_one({'_id': ObjectId(id)})
    return jsonify({
        'result': 'success',
        'msg': f'Your example for the word, {word}, was deleted!'
    })

@app.route('/practice')
def practice():
    return render_template('practice.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port = 5000, debug = True)