from flask import Flask, render_template, request, session, redirect, url_for
import random
import os

app = Flask(__name__)
app.secret_key = "sintetic-secret-key"

role_map = {
    "goalkeeper": "Goalkeeper",
    "defender": "Defender",
    "midfielder": "Midfielder",
    "attacker": "Attacker",
    "flexible": "Flexible",
}

level_label_map = {1: "Weak", 2: "Average", 3: "Good", 4: "Phenomenon"}
level_icon_map  = {1: "😅", 2: "🙂", 3: "😎", 4: "🔥"}
role_icon_map   = {
    "goalkeeper": "🧤",
    "defender": "🛡️",
    "midfielder": "🧠",
    "attacker": "🎯",
    "flexible": "🔝",
}

def make_teams(players):
    players = [p.copy() for p in players]
    goalkeepers = [p for p in players if p["role"] == "goalkeeper"]
    field       = [p for p in players if p["role"] != "goalkeeper"]

    random.shuffle(goalkeepers)

    while len(goalkeepers) < 2:
        field_sorted = sorted(field, key=lambda x: x["level"])
        if field_sorted:
            p = field_sorted[0]
            field.remove(p)
            p["role"] = "goalkeeper"
            p["position"] = "Goalkeeper (converted)"
            goalkeepers.append(p)
        else:
            break

    extra_gk = goalkeepers[2:]
    goalkeepers = goalkeepers[:2]
    for p in extra_gk:
        p["role"] = "flexible"
        p["position"] = "Flexible"
        field.append(p)

    goalkeepers = sorted(goalkeepers, key=lambda x: x["level"], reverse=True)
    field = sorted(field, key=lambda x: x["level"], reverse=True)

    team1_field, team2_field = [], []
    for idx, p in enumerate(field):
        cycle = idx // 2
        pos_in_cycle = idx % 2
        if cycle % 2 == 0:
            (team1_field if pos_in_cycle == 0 else team2_field).append(p)
        else:
            (team2_field if pos_in_cycle == 0 else team1_field).append(p)

    rating1 = sum(p["level"] for p in team1_field) / len(team1_field) if team1_field else 0
    rating2 = sum(p["level"] for p in team2_field) / len(team2_field) if team2_field else 0

    gk1, gk2 = (goalkeepers[1], goalkeepers[0]) if rating1 >= rating2 else (goalkeepers[0], goalkeepers[1])

    team1 = [gk1] + team1_field[:4]
    team2 = [gk2] + team2_field[:4]
    return team1, team2

def team_rating(team):
    if not team:
        return 0
    return round(sum(p["level"] for p in team) / len(team), 1)

@app.route("/", methods=["GET"])
def index():
    if "players" not in session:
        session["players"] = []
    return render_template("index.html",
        players=session["players"],
        role_icon_map=role_icon_map,
        level_label_map=level_label_map,
        level_icon_map=level_icon_map,
    )

@app.route("/add", methods=["POST"])
def add_player():
    if "players" not in session:
        session["players"] = []

    players = session["players"]

    if len(players) >= 10:
        return redirect(url_for("index"))

    name = request.form.get("name", "").strip()
    role = request.form.get("role", "flexible")
    level = int(request.form.get("level", 2))

    if name:
        players.append({
            "name": name,
            "role": role,
            "position": role_map.get(role, "Flexible"),
            "level": level,
        })
        session["players"] = players
        session.modified = True

    return redirect(url_for("index"))

@app.route("/delete/<int:idx>")
def delete_player(idx):
    players = session.get("players", [])
    if 0 <= idx < len(players):
        players.pop(idx)
        session["players"] = players
        session.modified = True
    return redirect(url_for("index"))

@app.route("/clear")
def clear_players():
    session["players"] = []
    session.modified = True
    return redirect(url_for("index"))

@app.route("/generate")
def generate():
    players = session.get("players", [])
    if len(players) != 10:
        return redirect(url_for("index"))

    team1, team2 = make_teams(players)
    r1 = team_rating(team1)
    r2 = team_rating(team2)
    diff = abs(r1 - r2)

    if diff <= 0.5:
        balance = ("success", "⚖️ Balanced teams! Good luck! 🏃")
    elif diff <= 1:
        balance = ("warning", f"🟡 Small difference: {diff:.1f} points — good enough!")
    else:
        balance = ("danger", f"⚠️ Big difference: {diff:.1f} points — regenerate!")

    return render_template("results.html",
        team1=team1, team2=team2,
        rating1=r1, rating2=r2,
        balance=balance,
        role_icon_map=role_icon_map,
        level_label_map=level_label_map,
        level_icon_map=level_icon_map,
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
