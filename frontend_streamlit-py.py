import streamlit as st

from database.database_interface import COURT_TYPE
from training_set_preparation import predict_winner

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
        age1 = st.number_input("Age", min_value=10, max_value=60, key="age1")
        weight1 = st.number_input("Weight (kg)", min_value=30, max_value=150, key="weight1")
        height1 = st.number_input("Height (cm)", min_value=100, max_value=250, key="height1")
        turned_pro1 = st.number_input("Year Turned Pro", min_value=1980, max_value=2025, key="turned_pro1")
        rank1 = st.number_input("Rank", min_value=1, key="rank1")
        rank_points1 = st.number_input("Rank Points", min_value=0, key="rank_points1")
        aces1 = st.number_input("Aces", key="aces1")
        double_faults1 = st.number_input("Double Faults", key="df1")
        first_serve1 = st.number_input("First Serve %", min_value=0, max_value=100, key="fs1")
        first_serve_points_won1 = st.number_input("1st Serve Points Won %", min_value=0, max_value=100, key="fspw1")
        second_serve_points_won1 = st.number_input("2nd Serve Points Won %", min_value=0, max_value=100, key="ssp1")
        break_points_faced1 = st.number_input("Break Points Faced", key="bpf1")
        break_points_saved1 = st.number_input("Break Points Saved", key="bps1")
        service_games_played1 = st.number_input("Service Games Played", key="sgp1")
        service_games_won1 = st.number_input("Service Games Won", key="sgw1")
        total_service_points_won1 = st.number_input("Total Service Points Won %", min_value=0, max_value=100, key="tspw1")
        first_serve_return_points_won1 = st.number_input("1st Serve Return Points Won %", min_value=0, max_value=100, key="fsrpw1")
        second_serve_return_points_won1 = st.number_input("2nd Serve Return Points Won %", min_value=0, max_value=100, key="ssrpw1")
        break_points_opportunities1 = st.number_input("Break Point Opportunities", key="bpo1")
        break_points_converted1 = st.number_input("Break Points Converted", key="bpc1")
        return_games_played1 = st.number_input("Return Games Played", key="rgp1")
        return_games_won1 = st.number_input("Return Games Won", key="rgw1")
        return_points_won1 = st.number_input("Return Points Won %", min_value=0, max_value=100, key="rpw1")
        total_points_won1 = st.number_input("Total Points Won %", min_value=0, max_value=100, key="tpw1")
        wins_first_player = st.number_input("Wins vs Opponent", key="wins_first_player")
        odds1 = st.number_input("odds", key="odds1")

    with col2:
        st.markdown("### Player 2")
        age2 = st.number_input("Age", min_value=10, max_value=60, key="age2")
        weight2 = st.number_input("Weight (kg)", min_value=30, max_value=150, key="weight2")
        height2 = st.number_input("Height (cm)", min_value=100, max_value=250, key="height2")
        turned_pro2 = st.number_input("Year Turned Pro", min_value=1980, max_value=2025, key="turned_pro2")
        rank2 = st.number_input("Rank", min_value=1, key="rank2")
        rank_points2 = st.number_input("Rank Points", min_value=0, key="rank_points2")
        aces2 = st.number_input("Aces", key="aces2")
        double_faults2 = st.number_input("Double Faults", key="df2")
        first_serve2 = st.number_input("First Serve %", min_value=0, max_value=100, key="fs2")
        first_serve_points_won2 = st.number_input("1st Serve Points Won %", min_value=0, max_value=100, key="fspw2")
        second_serve_points_won2 = st.number_input("2nd Serve Points Won %", min_value=0, max_value=100, key="ssp2")
        break_points_faced2 = st.number_input("Break Points Faced", key="bpf2")
        break_points_saved2 = st.number_input("Break Points Saved", key="bps2")
        service_games_played2 = st.number_input("Service Games Played", key="sgp2")
        service_games_won2 = st.number_input("Service Games Won", key="sgw2")
        total_service_points_won2 = st.number_input("Total Service Points Won %", min_value=0, max_value=100, key="tspw2")
        first_serve_return_points_won2 = st.number_input("1st Serve Return Points Won %", min_value=0, max_value=100, key="fsrpw2")
        second_serve_return_points_won2 = st.number_input("2nd Serve Return Points Won %", min_value=0, max_value=100, key="ssrpw2")
        break_points_opportunities2 = st.number_input("Break Point Opportunities", key="bpo2")
        break_points_converted2 = st.number_input("Break Points Converted", key="bpc2")
        return_games_played2 = st.number_input("Return Games Played", key="rgp2")
        return_games_won2 = st.number_input("Return Games Won", key="rgw2")
        return_points_won2 = st.number_input("Return Points Won %", min_value=0, max_value=100, key="rpw2")
        total_points_won2 = st.number_input("Total Points Won %", min_value=0, max_value=100, key="tpw2")
        wins_second_player = st.number_input("Wins vs Opponent", key="wins_second_player")
        odds2 = st.number_input("odds", key="odds2")

    submitted = st.form_submit_button("Predict Match")
    if submitted:
        player1_data = (
            age1,
            weight1,
            height1,
            turned_pro1,
            rank1,
            rank_points1,
            aces1,
            double_faults1,
            first_serve1,
            first_serve_points_won1,
            second_serve_points_won1,
            break_points_faced1,
            break_points_saved1,
            service_games_played1,
            service_games_won1,
            total_service_points_won1,
            first_serve_return_points_won1,
            second_serve_return_points_won1,
            break_points_opportunities1,
            break_points_converted1,
            return_games_played1,
            return_games_won1,
            return_points_won1,
            total_points_won1,
            odds1
        )

        # Tuple for Player 2 (same logic as above)
        player2_data = (
            age2,
            weight2,
            height2,
            turned_pro2,
            rank2,
            rank_points2,
            aces2,
            double_faults2,
            first_serve2,
            first_serve_points_won2,
            second_serve_points_won2,
            break_points_faced2,
            break_points_saved2,
            service_games_played2,
            service_games_won2,
            total_service_points_won2,
            first_serve_return_points_won2,
            second_serve_return_points_won2,
            break_points_opportunities2,
            break_points_converted2,
            return_games_played2,
            return_games_won2,
            return_points_won2,
            total_points_won2,
            odds2
        )

        selected_surface_value = surface_map[selected_surface_label]
        st.text_area("Predicted output", value=predict_winner(player1_data, player2_data,selected_surface_value,wins_first_player, wins_second_player))

        st.success("Prediction inputs submitted.")
        # Now you can pass these variables into your model
