from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

feedback_list = []

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':

        name = request.form.get('name')
        feedback_text = request.form.get('feedback')

        feedback_list.append({'name': name, 'feedback': feedback_text})
        
        return redirect(url_for('feedback'))

    return render_template('feedback.html', feedbacks=feedback_list)

if __name__ == '__main__':
    app.run(debug=True)
