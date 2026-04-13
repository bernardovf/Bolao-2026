import requests


API_KEY = "e0ee125088694e0799a6ed7d23ccfc1c"

url = "https://api.football-data.org/v4/competitions/2021/matches"
headers = {"X-Auth-Token": API_KEY}
response = requests.get(url, headers=headers)
matches = response.json()["matches"]
for match in matches:
    match_id = match["id"]
    home = match["homeTeam"]["name"]
    away = match["awayTeam"]["name"]
    status = match["status"]
    date = match["utcDate"]

    if status != "FINISHED":
        print(match_id)
        print(status)
        print(match["score"])
        print("")
        print(home, away)
        print(date)
    """if status == "FINISHED":
        home_score = match["score"]["fullTime"]["home"]
        away_score = match["score"]["fullTime"]["away"]
        print(match_id, f"{home} {home_score} x {away_score} {away} ({date})")
    else:
        print(match_id, f"{home} vs {away} - {status} ({date})")"""
