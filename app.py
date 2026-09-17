# app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import requests 

app = Flask(__name__)
CORS(app)

# MySQL Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root", 
    database="portfolio_db"
)
cursor = db.cursor(dictionary=True)


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
    cursor.execute("SELECT * FROM visitors ORDER BY visited_at DESC LIMIT 10") # लास्ट १० व्हिजिटर्स
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
    cursor.execute("INSERT INTO projects (title, tech, image_url, description, github_link) VALUES (%s, %s, %s, %s, %s)", 
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
    cursor.execute("INSERT INTO certificates (title, issuer, image_url) VALUES (%s, %s, %s)", 
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
    cursor.execute("INSERT INTO techstack (name, logo_url) VALUES (%s, %s)", 
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