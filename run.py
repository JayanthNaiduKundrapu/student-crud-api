from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=False) # auto reload the server when code changes are detected