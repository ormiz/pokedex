from flask import Flask, request, jsonify
from flask_cors import CORS
import db

app = Flask(__name__)
CORS(app)

@app.route('/icon/<name>')
def get_icon_url(name:str):
    return f"https://img.pokemondb.net/sprites/silver/normal/{name}.png"

def enrich(pokemon):
    pokemon['icon_url'] = get_icon_url(pokemon['name'].lower())
    pokemon['captured'] = False if captured_pokemons.get(pokemon['name']) is None else True
    return pokemon

def pokemon_match(pokemon, search_term):
    for key in pokemon:
        if search_term in str(pokemon[key]):
            return True
    return False


def filter(data, args):
    if args.get('filterType') is not None:
        data = [x for x in data if x['type_one'] == args.get('filterType')]
    if args.get('globalSearch') is not None:
        data = [x for x in data if pokemon_match(x, args.get('globalSearch')) == True]
    return data

def limit(data, args):
    if args.get('start') is None:
        start = 0
    else:
        start = int(args.get('start'))
    if args.get('size'):
        size = int(args.get('size'))
    else: 
        size = len(data) - start
    return data[start:(start + size)]

def sort(data, args):
    if args.get('sort') == 'asc':
        data.sort(key=lambda x: x['number'])
    elif args.get('sort') == 'desc':
        data.sort(key=lambda x: x['number'], reverse=True)
    return data

@app.route('/')
def get_pokemons():
    args = request.args
    data = db.get()
    totalCount = len(data)
    data = filter(data, args)
    filteredCount = len(data)
    data = sort(data, args)
    data = limit(data, args)
    data = list(map(enrich, data))
    return jsonify(
        {'pokemons': data, 'totalCount': filteredCount if filteredCount < totalCount else totalCount }
    )

captured_pokemons = {}

@app.route('/capture', methods=['PATCH'])
def capture_pokemon():
    pokemon_name = request.json.get('pokemonName')
    captured_pokemons[pokemon_name] = True
    return ('', 204)
    


if __name__=='__main__':
    app.run(port=8080)