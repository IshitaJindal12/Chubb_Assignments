from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'user' and password == 'password':
            return render_template('welcome.html', username=username)
        else:
            error = "Invalid username or password. Please try again."
            return render_template('login.html', error=error)
    
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
