from src import create_app

app = create_app()

if __name__ == '__main__':
    # debug=True hace que si cambias código, el servidor se reinicie solo
    app.run(debug=True, port=5000)