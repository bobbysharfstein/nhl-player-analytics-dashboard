import requests
import pandas as pd

SEASON = "20242025"
GAME_TYPE = 2

teams = [
    "ANA", "BOS", "BUF", "CAR", "CBJ", "CGY", "CHI", "COL",
    "DAL", "DET", "EDM", "FLA", "LAK", "MIN", "MTL", "NJD",
    "NSH", "NYI", "NYR", "OTT", "PHI", "PIT", "SEA", "SJS",
    "STL", "TBL", "TOR", "UTA", "VAN", "VGK", "WPG", "WSH"
]

stats_url = "https://api.nhle.com/stats/rest/en/skater/summary"

params = {
    "isAggregate": "true",
    "isGame": "false",
    "sort": '[{"property":"points","direction":"DESC"}]',
    "start": 0,
    "limit": -1,
    "cayenneExp": f"seasonId={SEASON} and gameTypeId={GAME_TYPE}"
}

response = requests.get(stats_url, params=params)
response.raise_for_status()

stats_data = response.json()["data"]
df = pd.DataFrame(stats_data)

team_lookup = {}

for team in teams:
    roster_url = f"https://api-web.nhle.com/v1/roster/{team}/{SEASON}"

    try:
        roster_response = requests.get(roster_url)
        roster_response.raise_for_status()
        roster_data = roster_response.json()

        for group in ["forwards", "defensemen", "goalies"]:
            for player in roster_data.get(group, []):
                player_id = player.get("id")
                if player_id:
                    team_lookup[player_id] = team

    except Exception as e:
        print(f"Could not load roster for {team}: {e}")

clean_df = pd.DataFrame()

clean_df["PlayerId"] = df["playerId"]
clean_df["Player"] = df["skaterFullName"]
clean_df["Team"] = df["playerId"].map(team_lookup).fillna("Unknown")
clean_df["Position"] = df["positionCode"]
clean_df["Games"] = df["gamesPlayed"]
clean_df["Goals"] = df["goals"]
clean_df["Assists"] = df["assists"]
clean_df["Points"] = df["points"]
clean_df["Shots"] = df["shots"]
clean_df["PlusMinus"] = df["plusMinus"]
clean_df["PIM"] = df["penaltyMinutes"]
clean_df["TOI Per Game"] = df["timeOnIcePerGame"]

clean_df["Points Per Game"] = clean_df["Points"] / clean_df["Games"]
clean_df["Goals Per Game"] = clean_df["Goals"] / clean_df["Games"]
clean_df["Assists Per Game"] = clean_df["Assists"] / clean_df["Games"]
clean_df["Shots Per Game"] = clean_df["Shots"] / clean_df["Games"]
clean_df["Shot Percentage"] = (clean_df["Goals"] / clean_df["Shots"]) * 100

clean_df = clean_df[
    [
        "PlayerId",
        "Player",
        "Team",
        "Position",
        "Games",
        "Goals",
        "Assists",
        "Points",
        "Shots",
        "Shots Per Game",
        "Shot Percentage",
        "Points Per Game",
        "Goals Per Game",
        "Assists Per Game",
        "PlusMinus",
        "PIM",
        "TOI Per Game"
    ]
]

clean_df.to_csv("players_2024_2025.csv", index=False)

print("Saved players_2024_2025.csv successfully")
print(clean_df["Team"].value_counts().head(40))