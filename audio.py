from flask import Flask, render_template

app = Flask(__name__, static_url_path='/static')


@app.route('/')
def audiobook():
    return render_template('audio.html')

if __name__ == '__main__':
    app.run(debug=True)
