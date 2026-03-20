import random

def get_choice(question, options):
    print(f"  {question}")
    for key, value in options.items():
        print(f"    {key}. {value}")
    while True:
        answer = input("  Alegerea ta: ").strip()
        if answer in options:
            return answer
        print("  ⚠️  Alege un număr valid.")

def add_players():
    players = []
    print("\n" + "="*50)
    print("       ⚽  GENERATOR ECHIPE SINTETIC  ⚽")
    print("           Format: 5v5 (4 + 1 portar)")
    print("="*50)
    print(f"\nAdaugă 10 jucători.\n")

    for i in range(1, 11):
        print(f"--- Jucătorul {i} ---")
        name = input("Nume: ").strip()

        role_choice = get_choice("Care e stilul tău de joc?", {
            "1": "Portar",
            "2": "Fundaș",
            "3": "Mijlocaș",
            "4": "Atacant",
            "5": "Flexibil (joc oriunde)",
        })

        level_choice = get_choice("Cât de bun ești?", {
            "1": "Slab (abia mă țin pe picioare)",
            "2": "Mediu (mă descurc)",
            "3": "Bun (sunt golgheter la sintetic)",
            "4": "Fenomen (toți vor să fie în echipa mea)",
        })

        role_map = {
            "1": "portar", "2": "fundas", "3": "mijlocas",
            "4": "atacant", "5": "flexibil",
        }
        position_map = {
            "1": "Portar", "2": "Fundaș", "3": "Mijlocaș",
            "4": "Atacant", "5": "Flexibil",
        }

        players.append({
            "name": name,
            "role": role_map[role_choice],
            "position": position_map[role_choice],
            "level": int(level_choice),
        })
        print()

    return players

def make_teams(players):
    goalkeepers = [p for p in players if p["role"] == "portar"]
    field       = [p for p in players if p["role"] != "portar"]

    random.shuffle(goalkeepers)

    # Asigurăm 2 portari
    while len(goalkeepers) < 2:
        # Luăm cel mai slab jucător de câmp ca portar
        field_sorted = sorted(field, key=lambda x: x["level"])
        if field_sorted:
            p = field_sorted[0]
            field.remove(p)
            p["role"] = "portar"
            p["position"] = "Portar (convertit)"
            goalkeepers.append(p)
        else:
            break

    # Portari extra devin jucători de câmp
    extra_gk = goalkeepers[2:]
    goalkeepers = goalkeepers[:2]
    for p in extra_gk:
        p["role"] = "flexibil"
        p["position"] = "Flexibil"
        field.append(p)

    # Sortăm portarii — cel mai bun la echipa mai slabă (se decide după câmpari)
    goalkeepers = sorted(goalkeepers, key=lambda x: x["level"], reverse=True)

    # Sortăm jucătorii de câmp după nivel descrescător
    field = sorted(field, key=lambda x: x["level"], reverse=True)

    # Distribuim alternând: 1->echipa1, 2->echipa2, 3->echipa2, 4->echipa1 (snake draft)
    team1_field = []
    team2_field = []
    for idx, p in enumerate(field):
        # Snake draft pentru echilibru maxim
        cycle = idx // 2
        pos_in_cycle = idx % 2
        if cycle % 2 == 0:
            if pos_in_cycle == 0:
                team1_field.append(p)
            else:
                team2_field.append(p)
        else:
            if pos_in_cycle == 0:
                team2_field.append(p)
            else:
                team1_field.append(p)

    # Portarul mai bun merge la echipa mai slabă
    rating1 = sum(p["level"] for p in team1_field) / len(team1_field) if team1_field else 0
    rating2 = sum(p["level"] for p in team2_field) / len(team2_field) if team2_field else 0

    if rating1 >= rating2:
        gk1, gk2 = goalkeepers[1], goalkeepers[0]  # echipa mai slabă primește GK mai bun
    else:
        gk1, gk2 = goalkeepers[0], goalkeepers[1]

    team1 = [gk1] + team1_field[:4]
    team2 = [gk2] + team2_field[:4]

    return team1, team2

def team_rating(team):
    if not team:
        return 0
    return round(sum(p["level"] for p in team) / len(team), 1)

def level_label(level):
    return {1: "Slab", 2: "Mediu", 3: "Bun", 4: "Fenomen"}.get(level, "?")

def print_team(team, team_name):
    print(f"\n  🟦 {team_name}  (Rating mediu: {team_rating(team)}/4)")
    print("  " + "-"*45)
    for p in team:
        role_icon = {
            "portar": "🧤", "fundas": "🛡️ ", "mijlocas": "🔄",
            "atacant": "⚡", "flexibil": "🔀",
        }.get(p["role"], "👟")
        level_str = f"[{level_label(p['level'])}]"
        print(f"  {role_icon} {p['name']:<16} {p['position']:<20} {level_str}")

def print_results(team1, team2):
    print("\n" + "="*50)
    print("           ⚽  ECHIPELE DE AZI  ⚽")
    print("="*50)
    print_team(team1, "ECHIPA 1")
    print_team(team2, "ECHIPA 2")
    diff = abs(team_rating(team1) - team_rating(team2))
    if diff <= 0.5:
        balance = "⚖️  Echipe echilibrate!"
    elif diff <= 1:
        balance = f"🟡 Diferență mică: {diff:.1f} puncte"
    else:
        balance = f"⚠️  Diferență mare: {diff:.1f} puncte — regenerează!"
    print(f"\n  {balance}")
    print("\n" + "="*50)
    print("  Spor la joacă! 🏃 Nu vă mai certați! 😄")
    print("="*50 + "\n")

def main():
    while True:
        players = add_players()
        team1, team2 = make_teams(players)
        print_results(team1, team2)

        while True:
            again = input("Regenerezi echipele cu aceiași jucători? (da/nu): ").strip().lower()
            if again in ["da", "d"]:
                print("\n🔀 Regenerăm echipele...\n")
                team1, team2 = make_teams(players)
                print_results(team1, team2)
            else:
                break

        new_game = input("Joc nou cu alți jucători? (da/nu): ").strip().lower()
        if new_game not in ["da", "d"]:
            print("\nPa! ⚽\n")
            break

if __name__ == "__main__":
    main()
