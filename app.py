import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="NHL Player Analytics Dashboard",
    page_icon="🏒",
    layout="wide"
)

# -----------------------------
# CUSTOM STYLING
# -----------------------------

st.markdown("""
<style>
.stApp {
    background-color: #f8fafc;
    color: #111827;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

h1, h2, h3 {
    color: #0f172a;
}

[data-testid="stMetric"] {
    background-color: white;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
}

[data-testid="stMetricLabel"] {
    color: #475569;
}

[data-testid="stMetricValue"] {
    color: #0f172a;
    font-size: 28px;
}

section[data-testid="stSidebar"] {
    background-color: #eef2f7;
}

.stDataFrame {
    background-color: white;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOAD DATA
# -----------------------------

df = pd.read_csv("players_2024_2025.csv")

# -----------------------------
# CLEAN POSITION LABELS
# -----------------------------

df["Position"] = df["Position"].replace({
    "L": "LW",
    "R": "RW"
})

# -----------------------------
# SCOUTING REPORT FUNCTION
# -----------------------------

def generate_scouting_report(player_data):
    name = player_data["Player"]
    position = player_data["Position"]
    team = player_data["Team"]
    ppg = player_data["Points Per Game"]
    gpg = player_data["Goals Per Game"]
    apg = player_data["Assists Per Game"]
    spg = player_data["Shots Per Game"]
    shot_pct = player_data["Shot Percentage"]
    games = player_data["Games"]

    if ppg >= 1.0:
        production = "elite offensive producer"
    elif ppg >= 0.7:
        production = "strong top-six offensive contributor"
    elif ppg >= 0.4:
        production = "reliable depth scoring option"
    else:
        production = "limited offensive producer"

    if gpg >= 0.45:
        scoring_style = "high-end goal scorer"
    elif gpg >= 0.25:
        scoring_style = "solid finishing threat"
    else:
        scoring_style = "more of a secondary scoring option"

    if apg >= gpg:
        play_style = "leans more toward playmaking and puck distribution"
    else:
        play_style = "leans more toward shooting and goal scoring"

    if spg >= 3:
        shot_profile = "generates a high volume of shots"
    elif spg >= 2:
        shot_profile = "creates a moderate amount of shot volume"
    else:
        shot_profile = "does not rely heavily on shot volume"

    if shot_pct >= 15:
        efficiency = "shows strong shooting efficiency"
    elif shot_pct >= 10:
        efficiency = "has a reasonable shooting efficiency"
    else:
        efficiency = "may need more efficiency as a finisher"

    report = f"""
**Scouting Report:**  
{name} is a {position} for {team} who profiles as a **{production}** based on his current production rate across {int(games)} games. 
He is best described as a **{scoring_style}** and {play_style}. 
From a shot profile standpoint, he {shot_profile}, while his shooting percentage suggests he {efficiency}. 

Overall, {name} appears to be a player whose offensive value is driven by a combination of production, shot generation, and scoring efficiency.
"""

    return report

# -----------------------------
# HEADER
# -----------------------------

st.title("🏒 NHL Player Analytics Dashboard")

st.caption(
    "2024–2025 NHL Regular Season | Python, Pandas, Streamlit, Plotly"
)

st.info(
    "This dashboard analyzes 2024–2025 NHL player performance using Python, Pandas, Streamlit, and interactive data visualization. Users can filter players, compare performance, and generate simple scouting reports."
)

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------

st.sidebar.header("Filters")

search_player = st.sidebar.text_input("Search Player")

available_teams = sorted([
    team for team in df["Team"].dropna().unique()
    if team != "Unknown"
])

team_filter = st.sidebar.multiselect(
    "Team",
    available_teams
)

position_filter = st.sidebar.multiselect(
    "Position",
    sorted(df["Position"].dropna().unique())
)

min_games = st.sidebar.slider(
    "Minimum Games Played",
    0,
    int(df["Games"].max()),
    20
)

metric_choice = st.sidebar.selectbox(
    "Rank Players By",
    [
        "Points",
        "Goals",
        "Assists",
        "Points Per Game",
        "Goals Per Game",
        "Assists Per Game",
        "Shot Percentage",
        "Shots Per Game"
    ]
)

# -----------------------------
# FILTER DATA
# -----------------------------

filtered_df = df.copy()

if search_player:
    filtered_df = filtered_df[
        filtered_df["Player"].str.contains(
            search_player,
            case=False,
            na=False
        )
    ]

if team_filter:
    filtered_df = filtered_df[
        filtered_df["Team"].isin(team_filter)
    ]

if position_filter:
    filtered_df = filtered_df[
        filtered_df["Position"].isin(position_filter)
    ]

filtered_df = filtered_df[
    filtered_df["Games"] >= min_games
]

# -----------------------------
# KPI METRICS
# -----------------------------

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Players Shown", len(filtered_df))

col2.metric(
    "Total Goals",
    int(filtered_df["Goals"].sum()) if len(filtered_df) > 0 else 0
)

col3.metric(
    "Average PPG",
    round(filtered_df["Points Per Game"].mean(), 2)
    if len(filtered_df) > 0 else 0
)

col4.metric(
    "Average Shot %",
    f"{round(filtered_df['Shot Percentage'].mean(), 1)}%"
    if len(filtered_df) > 0 else "0%"
)

# -----------------------------
# TOP PLAYERS + PLAYER SPOTLIGHT
# -----------------------------

st.markdown("---")

left_col, right_col = st.columns([2, 1])

with left_col:

    st.subheader(f"Top 10 Players by {metric_choice}")

    if len(filtered_df) > 0:

        top_players = filtered_df.sort_values(
            metric_choice,
            ascending=False
        ).head(10)

        fig = px.bar(
            top_players.sort_values(metric_choice),
            x=metric_choice,
            y="Player",
            orientation="h",
            title=f"Top 10 NHL Players by {metric_choice}",
            hover_data=[
                "Team",
                "Position",
                "Games",
                "Goals",
                "Assists",
                "Points"
            ],
            template="plotly_white"
        )

        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(color="#111827")
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("No players match your filters.")

with right_col:

    st.subheader("Player Spotlight")

    if len(filtered_df) > 0:

        selected_player = st.selectbox(
            "Choose a Player",
            filtered_df.sort_values(
                "Points",
                ascending=False
            )["Player"]
        )

        player_data = filtered_df[
            filtered_df["Player"] == selected_player
        ].iloc[0]

        st.write(f"### {player_data['Player']}")
        st.write(f"**Team:** {player_data['Team']}")
        st.write(f"**Position:** {player_data['Position']}")
        st.write(f"**Games:** {int(player_data['Games'])}")
        st.write(f"**Goals:** {int(player_data['Goals'])}")
        st.write(f"**Assists:** {int(player_data['Assists'])}")
        st.write(f"**Points:** {int(player_data['Points'])}")
        st.write(f"**Points Per Game:** {round(player_data['Points Per Game'], 2)}")
        st.write(f"**Shots Per Game:** {round(player_data['Shots Per Game'], 2)}")
        st.write(f"**Shot Percentage:** {round(player_data['Shot Percentage'], 1)}%")

        if player_data["Points Per Game"] >= 1:
            st.success("Elite offensive producer")
        elif player_data["Points Per Game"] >= 0.7:
            st.info("Strong offensive contributor")
        elif player_data["Points Per Game"] >= 0.4:
            st.warning("Depth scoring contributor")
        else:
            st.error("Limited offensive production")

        st.markdown("### Generated Scouting Report")
        st.markdown(generate_scouting_report(player_data))

    else:
        st.warning("No players match your filters.")

# -----------------------------
# PLAYER COMPARISON
# -----------------------------

st.markdown("---")

st.subheader("Player Comparison")

if len(filtered_df) >= 2:

    player_options = sorted(filtered_df["Player"].unique())

    comp_col1, comp_col2 = st.columns(2)

    with comp_col1:
        player_1 = st.selectbox("Choose First Player", player_options)

    with comp_col2:
        player_2 = st.selectbox(
            "Choose Second Player",
            player_options,
            index=1
        )

    comparison_df = filtered_df[
        filtered_df["Player"].isin([player_1, player_2])
    ][[
        "Player",
        "Team",
        "Position",
        "Games",
        "Goals",
        "Assists",
        "Points",
        "Points Per Game",
        "Goals Per Game",
        "Assists Per Game",
        "Shots Per Game",
        "Shot Percentage"
    ]]

    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True
    )

else:
    st.warning("Not enough players available for comparison.")

# -----------------------------
# SHOTS VS GOALS
# -----------------------------

st.markdown("---")

st.subheader("Shot Volume vs Goal Scoring")

if len(filtered_df) > 0:

    fig2 = px.scatter(
        filtered_df,
        x="Shots",
        y="Goals",
        color="Position",
        hover_name="Player",
        hover_data=[
            "Team",
            "Games",
            "Points",
            "Shot Percentage"
        ],
        title="Shot Volume vs Goal Scoring",
        template="plotly_white"
    )

    fig2.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#111827")
    )

    st.plotly_chart(fig2, use_container_width=True)

else:
    st.warning("No data available for chart.")

# -----------------------------
# TOP OFFENSIVE PLAYERS TABLE
# -----------------------------

st.markdown("---")

st.subheader("Top Offensive Players")

if len(filtered_df) > 0:

    top_offense = filtered_df.sort_values(
        "Points Per Game",
        ascending=False
    ).head(15)

    st.dataframe(
        top_offense[
            [
                "Player",
                "Team",
                "Position",
                "Games",
                "Goals",
                "Assists",
                "Points",
                "Points Per Game",
                "Shot Percentage"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

else:
    st.warning("No players match your filters.")

# -----------------------------
# FULL PLAYER DATA
# -----------------------------

st.markdown("---")

st.subheader("Full Player Data")

st.dataframe(
    filtered_df.sort_values(
        metric_choice,
        ascending=False
    ),
    use_container_width=True,
    hide_index=True
)

# -----------------------------
# PROJECT SKILLS
# -----------------------------

st.markdown("---")

st.subheader("Project Skills Demonstrated")

st.write("""
This project demonstrates Python programming, API data collection,
CSV generation, data cleaning, sports analytics, interactive dashboard
design, filtering, ranking, data visualization, and rule-based scouting
report generation using Streamlit, Pandas, and Plotly.
""")
