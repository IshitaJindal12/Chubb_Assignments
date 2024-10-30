from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/converter', methods=['GET', 'POST'])
def temperature_converter():
    fahrenheit = None
    if request.method == 'POST':
        
        celsius = request.form.get('celsius')
        if celsius:

            fahrenheit = (float(celsius) * 9/5) + 32

    return render_template('converter.html', fahrenheit=fahrenheit)

if __name__ == '__main__':
    app.run(debug=True)
