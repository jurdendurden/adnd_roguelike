from backend.app import app

if __name__ == '__main__':
    print("Starting AD&D 1e Dungeon Crawler...")
    print("Open http://localhost:5000 in your web browser")
    app.run(debug=True, host='0.0.0.0', port=5000) 