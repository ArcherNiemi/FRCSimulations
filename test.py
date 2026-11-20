import pandas as pd

df = pd.read_csv("champsEpa.csv")

df_sorted = df.sort_values(by='epa')

stats = {"2026arc": {"average": 0, "count": 0},"2026cur": {"average": 0, "count": 0},"2026dal": {"average": 0, "count": 0},"2026gal": {"average": 0, "count": 0},"2026hop": {"average": 0, "count": 0},"2026joh": {"average": 0, "count": 0},"2026mil": {"average": 0, "count": 0},"2026new": {"average": 0, "count": 0}}
divisionTeams = {"2026arc": [],"2026cur": [],"2026dal": [],"2026gal": [],"2026hop": [],"2026joh": [],"2026mil": [],"2026new": []}

for index, row in df.iterrows():
    divisionTeams[row['event']].append({"teamNum": row['teamNum'], "epa": row['epa']})


for i,(division,teams) in enumerate(divisionTeams.items()):
    sortTeams = sorted(teams, key=lambda item: item["epa"], reverse=True)
    divisionTeams[division] = sortTeams

for i,(division,teams) in enumerate(divisionTeams.items()):
    sum = 0
    for i in range(2):
        team = teams[i]
        sum += team['epa']
        stats[division]['count'] += 1
    stats[division]['average'] = sum / stats[division]['count']

print(type(stats))
finalStats = dict(sorted(stats.items(), key=lambda item: item[1]["average"], reverse=True))

for i,(key,value) in enumerate(finalStats.items()):
    print(f"{key}: {value["average"]}")