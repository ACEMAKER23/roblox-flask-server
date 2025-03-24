from flask import Flask, request, jsonify
import requests
import sqlite3

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect('player_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS players (userId TEXT PRIMARY KEY, points INTEGER, todayPlayTime INTEGER, cycleIndex INTEGER, timeLastCheck INTEGER, timeLastReset INTEGER)''')
    conn.commit()
    conn.close()


@app.route('/get_player/<userId>', methods=['GET'])
def get_player(userId):
    conn = sqlite3.connect('player_data.db')
    c = conn.cursor()
    c.execute("SELECT points, todayPlayTime, cycleIndex, timeLastReset FROM players WHERE userId = ?", (userId,))
    result = c.fetchone()
    conn.close()
    if result:
        return jsonify({"points": result[0], "todayPlayTime": result[1], "cycleIndex": result[2], 
                        "timeLastReset": result[3]})
    return jsonify({"points": 0, "todayPlayTime": 0, "cycleIndex": 1, "timeLastReset": 0})

@app.route('/update_player/<userId>/<int:points>/<int:todayPlayTime>/<int:cycleIndex>/<int:timeLastCheck>/<int:timeLastReset>', methods=['POST'])
def update_player(userId, points, todayPlayTime, cycleIndex, timeLastCheck, timeLastReset):
    conn = sqlite3.connect('player_data.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO players (userId, points, todayPlayTime, cycleIndex, timeLastCheck, timeLastReset) VALUES (?, ?, ?, ?, ?, ?)", (userId, points, todayPlayTime, cycleIndex, timeLastCheck, timeLastReset))
    conn.commit()
    conn.close()
    return jsonify({"points": points, "cycleIndex": cycleIndex, "todayPlayTime":todayPlayTime})


@app.route('/get_timeLastCheck/<userId>', methods=['GET'])
def get_timeLastCheck(userId):
    conn = sqlite3.connect('player_data.db')
    c = conn.cursor()
    c.execute("SELECT timeLastCheck FROM players WHERE userId = ?", (userId,))
    result = c.fetchone()
    conn.close()
    if result:
        return jsonify({"timeLastCheck": result[0]})
    return jsonify({"timeLastCheck": 0})

@app.route('/edit_db', methods=['POST'])
def edit_db():
    data = request.get_json()  # {"userId": "4081447945", "points": 5, "playtime": 7200.0, ...}
    userId = data['userId']
    points = data.get('points', 0)
    todayPlayTime = data.get('todayPlayTime', 0.0)
    cycleIndex = data.get('cycleIndex', 0.0)
    timeLastCheck = data.get('timeLastCheck', 1)
    timeLastReset = data.get('timeLastReset', 0.0)
    conn = sqlite3.connect('player_data.db')
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO players 
        (userId, points, todayPlayTime, cycleIndex, timeLastCheck, timeLastReset) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, (userId, points, todayPlayTime, cycleIndex, timeLastCheck, timeLastReset))
    conn.commit()
    conn.close()
    print(f"Edited userId: {userId} with playtime: {playtime}")
    return jsonify({"status": "success"})
    
@app.route('/resetAllPlayer', methods=['POST'])    
def resetAllPlayer(userId, points, todayPlayTime, cycleIndex, timeLastCheck, timeLastReset):
    conn = sqlite3.connect('player_data.db')
    c = conn.cursor()
    c.execute("TRUNCATE TABLE")
    conn.commit()
    conn.close()
    return jsonify({"points": points, "cycleIndex": cycleIndex, "todayPlayTime":todayPlayTime})
    
@app.route('/all_players', methods=['GET'])
def all_players():
    conn = sqlite3.connect('player_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM players")
    rows = c.fetchall()
    conn.close()
    players = [{"userId": row[0], "points": row[1], "todayPlayTime": row[2], 
                "cycleIndex": row[3], "timeLastCheck": row[4], "timeLastReset": row[5]} 
               for row in rows]
    return jsonify(players)

if __name__ == '__main__':
    init_db()  # Create the database and table on startup
    app.run(host='0.0.0.0', port=5000)
