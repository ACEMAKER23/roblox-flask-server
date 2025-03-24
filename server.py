from flask import Flask, request, jsonify
import psycopg2
# requests is imported but unused—kept for potential future use
import requests

app = Flask(__name__)

# Replace with your Supabase PostgreSQL connection string
DB_CONN = "postgresql://postgres:gtteXEC64xj2-4Z@db.fakggmzbhyoqcrllogdh.supabase.co:5432/postgres"

def get_db_connection():
    return psycopg2.connect(DB_CONN)

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS players (
        userId TEXT PRIMARY KEY,
        points INTEGER DEFAULT 0,
        todayPlayTime INTEGER DEFAULT 0,
        cycleIndex INTEGER DEFAULT 1,
        timeLastCheck INTEGER DEFAULT 0,
        timeLastReset INTEGER DEFAULT 0
    )''')
    conn.commit()
    conn.close()

@app.route('/get_player/<userId>', methods=['GET'])
def get_player(userId):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT points, todayPlayTime, cycleIndex, timeLastReset FROM players WHERE userId = %s", (userId,))
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
        INSERT INTO players (userId, points, todayPlayTime, cycleIndex, timeLastCheck, timeLastReset)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (userId) DO UPDATE
        SET points = %s, todayPlayTime = %s, cycleIndex = %s, timeLastCheck = %s, timeLastReset = %s
    """, (userId, points, todayPlayTime, cycleIndex, timeLastCheck, timeLastReset,
          points, todayPlayTime, cycleIndex, timeLastCheck, timeLastReset))
    conn.commit()
    conn.close()
    return jsonify({"points": points, "cycleIndex": cycleIndex, "todayPlayTime": todayPlayTime})

@app.route('/get_timeLastCheck/<userId>', methods=['GET'])
def get_timeLastCheck(userId):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT timeLastCheck FROM players WHERE userId = %s", (userId,))
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
    init_db()  # Create the table on startup
    app.run(host='0.0.0.0', port=5000)
