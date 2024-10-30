from flask import Flask, render_template
import random

app = Flask(__name__)

quotes = [
    "Where there is a will, there is a way .",
    "Early to bed, early to rise, makes a man healthy, wealthy and wise.",
    "Keep your face always toward the sunshine—and shadows will fall behind you.",
    "It does not matter how slowly you go as long as you do not stop.",
    "The only way to achieve the impossible is to believe it is possible."
]

@app.route('/quote')
def quote():
    random_quote = random.choice(quotes)
    return render_template('quote.html', quote=random_quote)

if __name__ == '__main__':
    app.run(debug=True)
