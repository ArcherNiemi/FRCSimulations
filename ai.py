import numpy as np
import pandas as pd
import tba

# SETTINGS
eventKey = "2026iacf"
startMatch = 52
endMatch = 71
simulations = 10000

teamList = np.array([
    3928,10439,11219,3055,4260,5935,6805,7531,8766,6419,4728,7257,
    5442,4646,2847,2654,1108,167,6147,5041,525,7848,967,2227,3267,
    648,59,5914,11312,8821,8822,11241,5275,11210,6420,3723,9092,
    5837,9061,9570,1997,10476,3298,5141,5557,5576,5809,6455,7038,
    8737,8770,9543,9579
])

num_teams = len(teamList)
num_matches = endMatch - startMatch + 1

team_to_idx = {team: i for i, team in enumerate(teamList)}

# LOAD MATCHES
allMatches = sorted(tba.get_event_matches(eventKey), key=lambda m: m['match_number'])
qualMatches = [m for m in allMatches if m["comp_level"] == "qm"]

# PRECOMPUTE MATCH TEAM INDICES
match_teams = np.zeros((num_matches, 6), dtype=np.int32)

for i in range(num_matches):
    match = qualMatches[startMatch + i - 1]
    teams = (
        match["alliances"]["red"]["team_keys"] +
        match["alliances"]["blue"]["team_keys"]
    )
    match_teams[i] = [team_to_idx[int(t[3:])] for t in teams]

# LOAD TEAM STATS
df = pd.read_csv("data.csv")

team_avg = np.zeros(num_teams)
team_std = np.zeros(num_teams)
team_n   = np.zeros(num_teams)

for i, team in enumerate(teamList):
    scores = df.loc[df["Team Number"] == team]["Points"].values
    if len(scores) == 0:
        scores = np.array([0])
    team_avg[i] = np.mean(scores)
    team_std[i] = np.std(scores)
    team_n[i]   = len(scores)

rng = np.random.default_rng()

# =========================
# 🔥 SIMULATION ARRAYS
# =========================

scores = np.zeros((simulations, num_matches, 2))   # [sim, match, alliance]
rps    = np.zeros((simulations, num_matches, 2))   # RP per alliance
team_rp = np.zeros((simulations, num_teams))       # total RP per team

# =========================
# 🚀 SIMULATION LOOP
# =========================

for sim in range(simulations):

    for m in range(num_matches):

        teams = match_teams[m]

        # simulate robot scores
        robot_scores = np.zeros(6)

        for i in range(6):
            idx = teams[i]
            if team_n[idx] > 1:
                robot_scores[i] = (
                    team_std[idx] * rng.standard_t(team_n[idx] - 1)
                    + team_avg[idx]
                )
            else:
                robot_scores[i] = rng.uniform(team_avg[idx]/2, team_avg[idx]*1.5)

        red_score = robot_scores[:3].sum()
        blue_score = robot_scores[3:].sum()

        scores[sim, m, 0] = red_score
        scores[sim, m, 1] = blue_score

        # win
        red_win = red_score > blue_score
        blue_win = not red_win

        def calc_rp(win, pts):
            return (3 if win else 0) + (1 if pts > 100 else 0) + (1 if pts > 360 else 0)

        red_rp = calc_rp(red_win, red_score)
        blue_rp = calc_rp(blue_win, blue_score)

        rps[sim, m, 0] = red_rp
        rps[sim, m, 1] = blue_rp

        # assign RP to teams
        team_rp[sim, teams[:3]] += red_rp
        team_rp[sim, teams[3:]] += blue_rp

# =========================
# 📊 RESULTS (NO DICTS)
# =========================

# rankings per simulation
ranks = np.argsort(-team_rp, axis=1)

# average rank
avg_rank = np.zeros(num_teams)
avg_rp   = np.mean(team_rp, axis=0)

for t in range(num_teams):
    avg_rank[t] = np.mean(np.where(ranks == t)[1] + 1)

# =========================
# OUTPUT
# =========================

results_df = pd.DataFrame({
    "team": teamList,
    "avg_rank": avg_rank,
    "avg_rp": avg_rp
}).sort_values("avg_rank")

results_df.to_csv("results_numpy.csv", index=False)