import random
import itertools
import streamlit as st

# Definice týmů a jejich síly (0–100)
teams = {
    "Brazil": 92, "France": 90, "Spain": 88, "Germany": 87, "Argentina": 91, "Portugal": 86,
    "Italy": 85, "England": 89, "Netherlands": 84, "Belgium": 83, "Croatia": 82, "Uruguay": 81,
    "Denmark": 80, "Switzerland": 78, "USA": 77, "Mexico": 76, "Japan": 75, "South Korea": 74,
    "Morocco": 79, "Poland": 73, "Serbia": 72, "Czech Republic": 71, "Canada": 70, "Australia": 69
}

# Inicializace session state
if 'groups' not in st.session_state:
    st.session_state.groups = []
if 'group_results' not in st.session_state:
    st.session_state.group_results = {}
if 'round_index' not in st.session_state:
    st.session_state.round_index = 0
if 'user_team' not in st.session_state:
    st.session_state.user_team = None
if 'knockout_teams' not in st.session_state:
    st.session_state.knockout_teams = []
if 'knockout_round' not in st.session_state:
    st.session_state.knockout_round = 0

# Funkce

def reset_tournament():
    st.session_state.groups = [list(t) for t in itertools.islice(itertools.zip_longest(*[iter(teams)]*4), 6)]
    st.session_state.group_results = {
        f"Group {chr(65+i)}": {team: {"points": 0, "scored": 0, "conceded": 0} for team in group if team}
        for i, group in enumerate(st.session_state.groups)
    }
    st.session_state.round_index = 0
    st.session_state.knockout_teams = []
    st.session_state.knockout_round = 0


def simulate_match(team1, team2):
    strength1 = teams[team1]
    strength2 = teams[team2]
    score1 = max(0, int(random.gauss(strength1 / 20, 1.5)))
    score2 = max(0, int(random.gauss(strength2 / 20, 1.5)))
    while score1 == score2:
        score1 = max(0, int(random.gauss(strength1 / 20, 1.5)))
        score2 = max(0, int(random.gauss(strength2 / 20, 1.5)))
    return (score1, score2)


def play_group_match(group_id, team1, team2):
    if st.session_state.user_team in (team1, team2):
        st.subheader(f"Zápas: {team1} vs {team2}")
        s1 = st.number_input(f"Góly pro {team1}", min_value=0, max_value=20, key=f"{team1}_{team2}_s1")
        s2 = st.number_input(f"Góly pro {team2}", min_value=0, max_value=20, key=f"{team1}_{team2}_s2")
        submit = st.button(f"Potvrdit výsledek: {team1} vs {team2}", key=f"btn_{team1}_{team2}")
        if not submit:
            st.stop()
    else:
        s1, s2 = simulate_match(team1, team2)
        st.write(f"{team1} {s1} - {s2} {team2}")

    group = st.session_state.group_results[group_id]
    if s1 > s2:
        group[team1]["points"] += 3
    elif s2 > s1:
        group[team2]["points"] += 3
    else:
        group[team1]["points"] += 1
        group[team2]["points"] += 1
    group[team1]["scored"] += s1
    group[team1]["conceded"] += s2
    group[team2]["scored"] += s2
    group[team2]["conceded"] += s1


def simulate_group_round():
    round_index = st.session_state.round_index
    if round_index >= 3:
        st.info("Skupinová fáze je kompletní.")
        return
    st.header(f"Skupinové kolo {round_index + 1}")
    for i, group in enumerate(st.session_state.groups):
        group_id = f"Group {chr(65+i)}"
        matches = list(itertools.combinations(group, 2))
        rounds = [matches[0:2], matches[2:4], matches[4:6]]
        for match in rounds[round_index]:
            play_group_match(group_id, match[0], match[1])
    st.session_state.round_index += 1


def show_group_standings():
    st.subheader("Tabulky skupin")
    for group_id, results in st.session_state.group_results.items():
        st.markdown(f"### {group_id}")
        sorted_teams = sorted(
            results.items(),
            key=lambda x: (x[1]['points'], x[1]['scored'] - x[1]['conceded'], x[1]['scored']),
            reverse=True
        )
        st.table({
            team: {
                "Body": stats['points'],
                "GF": stats['scored'],
                "GA": stats['conceded'],
                "GD": stats['scored'] - stats['conceded']
            }
            for team, stats in sorted_teams
        })


def get_knockout_teams():
    qualified = []
    for group_id, results in st.session_state.group_results.items():
        sorted_teams = sorted(
            results.items(),
            key=lambda x: (x[1]['points'], x[1]['scored'] - x[1]['conceded'], x[1]['scored']),
            reverse=True
        )
        qualified.extend([team for team, _ in sorted_teams[:2]])
    random.shuffle(qualified)
    return qualified


def simulate_knockout_round():
    round_names = ["Osmifinále", "Čtvrtfinále", "Semifinále", "Finále"]
    round_number = st.session_state.knockout_round
    teams = st.session_state.knockout_teams
    if len(teams) <= 1:
        st.success(f"Vítěz turnaje: {teams[0]}")
        return
    st.header(round_names[round_number])
    winners = []
    for i in range(0, len(teams), 2):
        t1, t2 = teams[i], teams[i+1]
        s1, s2 = simulate_match(t1, t2)
        st.write(f"{t1} {s1} - {s2} {t2}")
        winners.append(t1 if s1 > s2 else t2)
    st.session_state.knockout_teams = winners
    st.session_state.knockout_round += 1

# Streamlit UI

st.title("FC 25 – Turnajový simulátor 5v5")
if st.button("🔄 Začít nový turnaj"):
    reset_tournament()
    st.session_state.user_team = st.selectbox("Zvol tým, za který chceš hrát", ["None"] + list(teams.keys()))
    if st.session_state.user_team == "None":
        st.session_state.user_team = None
    st.experimental_rerun()

if st.session_state.groups and st.session_state.round_index < 3:
    simulate_group_round()
    show_group_standings()

if st.session_state.round_index >= 3 and not st.session_state.knockout_teams:
    if st.button("Zahájit vyřazovací fázi"):
        st.session_state.knockout_teams = get_knockout_teams()
        st.experimental_rerun()

if st.session_state.knockout_teams:
    simulate_knockout_round()
