from flask import jsonify,Flask, render_template, request, abort
from flask_cors import CORS
from lion import Anvisa, Pesquisa

app = Flask(__name__)

CORS(app, origins=['*'])

@app.route('/med', methods=['POST'])
def get_data():
    prod = request.json
    produto = prod.get('produto')

    if Anvisa(produto) != 'A consulta não retornou nenhum resultado.':
        return Anvisa(produto)
    else:
        return Pesquisa(produto)

if __name__ == '__main__':
    app.run(debug=True)