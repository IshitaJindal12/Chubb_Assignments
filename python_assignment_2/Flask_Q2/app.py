from flask import Flask, render_template

app = Flask(__name__)

@app.route('/bio')
def bio():
   
    bio_info = {
        "name": "Ishita Jindal",
        "age": 21,
        "College":"Vellore Institute of Technology, Vellore",
        "cgpa":8.93,
        "hobbies": ["Reading", "Skating", "Music"]
    }
    return render_template('bio.html', bio=bio_info)

if __name__ == '__main__':
    app.run(debug=True)
