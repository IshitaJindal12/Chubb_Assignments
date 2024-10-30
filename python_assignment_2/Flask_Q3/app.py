from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask!"

@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    result = None
    if request.method == 'POST':
        try:
            num1 = float(request.form['num1'])
            num2 = float(request.form['num2'])
            result = num1 + num2
        except (ValueError, KeyError):
            result = "Invalid input. Please enter numbers."
    return render_template('calculator.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
