from flask import Flask, request, jsonify
import psycopg2
# requests is imported but unused—kept for potential future use
import requests
import psycopg2
import os

app = Flask(__name__)
DB_CONN = os.getenv("DATABASE_URL")  # Render provides this—no .env needed

def get_db_connection():
    return psycopg2.connect(DB_CONN)

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS players (
        userid TEXT PRIMARY KEY,
        points INTEGER DEFAULT 0,
        todayplaytime INTEGER DEFAULT 0,
        cycleindex INTEGER DEFAULT 1,
        timelastcheck INTEGER DEFAULT 0,
        timelastreset INTEGER DEFAULT 0
    )''')
    conn.commit()
    conn.close()

@app.route('/get_player/<userId>', methods=['GET'])
def get_player(userId):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT points, todayplaytime, cycleindex, timelastreset FROM players WHERE userid = %s", (userId,))
    result = c.fetchone()
    conn.close()
    if result:
        return jsonify({"points": result[0], "todayPlayTime": result[1], "cycleIndex": result[2], 
                        "timeLastReset": result[3]})
    return jsonify({"points": 0, "todayPlayTime": 0, "cycleIndex": 1, "timeLastReset": 0})

@app.route('/update_player/<userId>/<int:points>/<int:todayPlayTime>/<int:cycleIndex>/<int:timeLastCheck>/<int:timeLastReset>', methods=['POST'])
def update_player(userId, points, todayPlayTime, cycleIndex, timeLastCheck, timeLastReset):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO players (userid, points, todayplaytime, cycleindex, timelastcheck, timelastreset)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (userid) DO UPDATE
        SET points = %s, todayplaytime = %s, cycleindex = %s, timelastcheck = %s, timelastreset = %s
    """, (userId, points, todayPlayTime, cycleIndex, timeLastCheck, timeLastReset,
          points, todayPlayTime, cycleIndex, timeLastCheck, timeLastReset))
    conn.commit()
    conn.close()
    return jsonify({"points": points, "cycleIndex": cycleIndex, "todayPlayTime": todayPlayTime})

@app.route('/get_timeLastCheck/<userId>', methods=['GET'])
def get_timeLastCheck(userId):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT timelastcheck FROM players WHERE userid = %s", (userId,))
    result = c.fetchone()
    conn.close()
    if result:
        return jsonify({"timeLastCheck": result[0]})
    return jsonify({"timeLastCheck": 0})

@app.route('/all_players', methods=['GET'])
def all_players():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM players")
    rows = c.fetchall()
    conn.close()
    players = [{"userId": row[0], "points": row[1], "todayPlayTime": row[2], 
                "cycleIndex": row[3], "timeLastCheck": row[4], "timeLastReset": row[5]} 
               for row in rows]
    return jsonify(players)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
