from flask import Flask, render_template

app = Flask(__name__)

users = [
    {'name': 'Ishita', 'age': 21, 'city': 'Chandigarh'},
    {'name': 'Anjali', 'age': 22, 'city': 'Varanasi'},
    {'name': 'Riddhi', 'age': 20, 'city': 'Delhi'},
]

@app.route('/users')
def users_table():
    return render_template('users.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)
