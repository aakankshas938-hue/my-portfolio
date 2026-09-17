# app.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests 

app = Flask(__name__)
CORS(app)

# PostgreSQL Database Connection (Using DATABASE_URL)
DATABASE_URL = os.environ.get("DATABASE_URL", "dbname=portfolio_db user=postgres password=root host=localhost")
db = psycopg2.connect(DATABASE_URL)
cursor = db.cursor(cursor_factory=RealDictCursor)

# Auto-create Tables if they don't exist
def init_db():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            tech VARCHAR(255),
            image_url VARCHAR(500),
            description TEXT,
            github_link VARCHAR(500)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS certificates (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            issuer VARCHAR(255),
            image_url VARCHAR(500)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS techstack (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            logo_url VARCHAR(500)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            id SERIAL PRIMARY KEY,
            ip_address VARCHAR(255),
            city VARCHAR(255),
            country VARCHAR(255),
            browser VARCHAR(255),
            visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()

init_db() # Run table creation

# ================= VISITOR TRACKING APIs =================
@app.route('/api/track-view', methods=['GET'])
def track_view():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip == '127.0.0.1' or ip == '::1':
        city = 'Local'
        country = 'Network'
        browser = request.user_agent.string
    else:
        try:
            res = requests.get(f'https://ipapi.co/{ip}/json/').json()
            city = res.get('city', 'Unknown')
            country = res.get('country_name', 'Unknown')
        except:
            city = 'Unknown'
            country = 'Unknown'
        browser = request.user_agent.string

    cursor.execute("INSERT INTO visitors (ip_address, city, country, browser) VALUES (%s, %s, %s, %s)", 
                   (ip, city, country, browser))
    db.commit()
    return jsonify({"message": "View tracked!"})

@app.route('/api/visitors', methods=['GET'])
def get_visitors():
    cursor.execute("SELECT * FROM visitors ORDER BY visited_at DESC LIMIT 10")
    return jsonify(cursor.fetchall())

# ================= PROJECTS APIs =================
@app.route('/api/projects', methods=['GET'])
def get_projects():
    cursor.execute("SELECT * FROM projects")
    result = cursor.fetchall()
    return jsonify(result)

@app.route('/api/projects', methods=['POST'])
def add_project():
    data = request.json
    cursor.execute("INSERT INTO projects (title, tech, image_url, description, github_link) VALUES (%s, %s, %s, %s, %s) RETURNING id", 
                   (data['title'], data['tech'], data['image_url'], data['description'], data['github_link']))
    db.commit()
    return jsonify({"message": "Project added successfully!"}), 201

@app.route('/api/projects/<int:id>', methods=['DELETE'])
def delete_project(id):
    cursor.execute("DELETE FROM projects WHERE id = %s", (id,))
    db.commit()
    return jsonify({"message": "Project deleted successfully!"})

# ================= CERTIFICATES APIs =================
@app.route('/api/certificates', methods=['GET'])
def get_certificates():
    cursor.execute("SELECT * FROM certificates")
    return jsonify(cursor.fetchall())

@app.route('/api/certificates', methods=['POST'])
def add_certificate():
    data = request.json
    cursor.execute("INSERT INTO certificates (title, issuer, image_url) VALUES (%s, %s, %s) RETURNING id", 
                   (data['title'], data['issuer'], data['image_url']))
    db.commit()
    return jsonify({"message": "Certificate added"}), 201

@app.route('/api/certificates/<int:id>', methods=['DELETE'])
def delete_certificate(id):
    cursor.execute("DELETE FROM certificates WHERE id = %s", (id,))
    db.commit()
    return jsonify({"message": "Certificate deleted"})

# ================= TECH STACK APIs =================
@app.route('/api/techstack', methods=['GET'])
def get_techstack():
    cursor.execute("SELECT * FROM techstack")
    return jsonify(cursor.fetchall())

@app.route('/api/techstack', methods=['POST'])
def add_techstack():
    data = request.json
    cursor.execute("INSERT INTO techstack (name, logo_url) VALUES (%s, %s) RETURNING id", 
                   (data['name'], data['logo_url']))
    db.commit()
    return jsonify({"message": "Tech stack added"}), 201

@app.route('/api/techstack/<int:id>', methods=['DELETE'])
def delete_techstack(id):
    cursor.execute("DELETE FROM techstack WHERE id = %s", (id,))
    db.commit()
    return jsonify({"message": "Tech stack deleted"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
