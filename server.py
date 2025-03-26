from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)
DB_CONN = os.getenv("DATABASE_URL")
if not DB_CONN:
    raise ValueError("DATABASE_URL not set in environment variables")

def get_db_connection():
    return psycopg2.connect(DB_CONN)

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS players (
        userid TEXT PRIMARY KEY,
        politicalpower INTEGER DEFAULT 0,
        militaryexperience INTEGER DEFAULT 0,
        policeauthority INTEGER DEFAULT 0,
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
    c.execute("SELECT politicalpower, militaryexperience, policeauthority, todayplaytime, cycleindex, timelastreset FROM players WHERE userid = %s", (userId,))
    result = c.fetchone()
    conn.close()
    if result:
        return jsonify({"politicalPower": result[0], "militaryExperience": result[1], "policeAuthority": result[2],
                        "todayPlayTime": result[3], "cycleIndex": result[4], "timeLastReset": result[5]})
    return jsonify({"politicalPower": 0, "militaryExperience": 0, "policeAuthority": 0,
                    "todayPlayTime": 0, "cycleIndex": 1, "timeLastReset": 0})

@app.route('/update_player/<userId>/<int:politicalPower>/<int:militaryExperience>/<int:policeAuthority>/<int:todayPlayTime>/<int:cycleIndex>/<int:timeLastCheck>/<int:timeLastReset>', methods=['POST'])
def update_player(userId, politicalPower, militaryExperience, policeAuthority, todayPlayTime, cycleIndex, timeLastCheck, timeLastReset):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO players (userid, politicalpower, militaryexperience, policeauthority, todayplaytime, cycleindex, timelastcheck, timelastreset)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (userid) DO UPDATE
        SET politicalpower = %s, militaryexperience = %s, policeauthority = %s, todayplaytime = %s, cycleindex = %s, timelastcheck = %s, timelastreset = %s
    """, (userId, politicalPower, militaryExperience, policeAuthority, todayPlayTime, cycleIndex, timeLastCheck, timeLastReset,
          politicalPower, militaryExperience, policeAuthority, todayPlayTime, cycleIndex, timeLastCheck, timeLastReset))
    conn.commit()
    conn.close()
    return jsonify({"politicalPower": politicalPower, "militaryExperience": militaryExperience, "policeAuthority": policeAuthority,
                    "todayPlayTime": todayPlayTime, "cycleIndex": cycleIndex})

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
    players = [{"userId": row[0], "politicalPower": row[1], "militaryExperience": row[2], "policeAuthority": row[3],
                "todayPlayTime": row[4], "cycleIndex": row[5], "timeLastCheck": row[6], "timeLastReset": row[7]} 
               for row in rows]
    return jsonify(players)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
