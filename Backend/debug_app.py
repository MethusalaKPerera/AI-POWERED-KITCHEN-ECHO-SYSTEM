from app import app

if __name__ == '__main__':
    print("Starting debug server on 5001...")
    app.run(debug=True, port=5001)
