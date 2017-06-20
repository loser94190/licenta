from app import app

app.secret_key = 'secret_key'
app.run(debug=False, host='127.0.0.1', port=5000)
