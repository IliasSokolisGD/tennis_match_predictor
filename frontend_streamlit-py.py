import streamlit as st

import get_players
from database.database_interface import COURT_TYPE

st.title("Match Model Prediction")

with st.form(key="match_form"):
    st.subheader("Enter Player Information")

    surface_map = {
        "Clay": COURT_TYPE.CLAY,
        "Carpet": COURT_TYPE.CARPET,
        "Grass": COURT_TYPE.GRASS,
        "Hard": COURT_TYPE.HARD
    }

    selected_surface_label = st.selectbox("Select Surface Type", list(surface_map.keys()))

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Player 1")
        url1 = st.text_area("Enter player url", key="url1")
        wins_first_player = st.number_input("Wins vs Opponent", key="wins_first_player")
        odds1 = st.number_input("odds", key="odds1")

    with col2:
        st.markdown("### Player 2")
        url2 = st.text_area("Enter player url", key="url2")
        wins_second_player = st.number_input("Wins vs Opponent", key="wins_second_player")
        odds2 = st.number_input("odds", key="odds2")

    submitted = st.form_submit_button("Predict Match")
    if submitted:

        selected_surface_value = surface_map[selected_surface_label]
        st.text_area("Predicted output", value= get_players.get_players_and_output_probabilities(url1, url2, wins_first_player, wins_second_player, odds1, odds2, selected_surface_label))

        st.success("Prediction inputs submitted.")
        # Now you can pass these variables into your model
