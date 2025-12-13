
def print_analysis():
    print("📊 **Performance Analysis: Yesterday (Dec 9th)**")
    print("=" * 50)

    games = [
        # (Away, Home, PredAwayScore, PredHomeScore, PredConfidenceTeam, ActualAway, ActualHome, ActualWinner)
        ("TBL", "MTL", 3, 4, "TBL", 6, 1, "TBL"),
        ("NJD", "OTT", 4, 3, "NJD", 4, 3, "NJD"),
        ("VGK", "NYI", 3, 5, "VGK", 4, 5, "NYI"),
        ("SJS", "PHI", 4, 3, "SJS", 1, 4, "PHI"),
        ("ANA", "PIT", 5, 4, "ANA", 4, 3, "ANA"),
        ("CBJ", "CAR", 4, 5, "CBJ", 1, 4, "CAR"),
        ("BOS", "STL", 3, 2, "BOS", 5, 2, "BOS"),
        ("DAL", "WPG", 5, 4, "DAL", 4, 3, "DAL"),
        ("BUF", "EDM", 2, 6, "BUF", 4, 3, "BUF"),
        ("COL", "NSH", 4, 3, "COL", 3, 4, "NSH"),
    ]

    correct_winner = 0
    correct_score_winner = 0
    exact_score = 0
    close_score = 0 

    for g in games:
        away, home, pa, ph, p_fav, aa, ah, a_win = g
        
        # Determine Predicted Winner based on Confidence
        pred_win_conf = p_fav
        
        # Determine Predicted Winner based on Score
        pred_win_score = away if pa > ph else home
        
        # Check Accuracy
        is_conf_correct = (pred_win_conf == a_win)
        is_score_correct = (pred_win_score == a_win)
        is_exact = (pa == aa and ph == ah)
        
        # Close check (within 1 goal)
        is_close = (abs(pa - aa) <= 1 and abs(ph - ah) <= 1)
        
        if is_conf_correct: correct_winner += 1
        if is_score_correct: correct_score_winner += 1
        if is_exact: exact_score += 1
        if is_close: close_score += 1
        
        icon = "✅" if is_conf_correct else "❌"
        score_icon = "🎯" if is_exact else "⚠️" if not is_score_correct else "✅"
        
        print(f"\n{icon} **{away} @ {home}**")
        print(f"   • Prediction: {p_fav} Video | Score: {away} {pa}-{ph} {home}")
        print(f"   • Actual:     {a_win} Won   | Score: {away} {aa}-{ah} {home}")
        
        if is_exact:
            print("   🔥 **EXACT SCORE PREDICTION!**")
        elif is_conf_correct and not is_score_correct:
             print("   ⚠️ Mixed Signal: Confidence got winner, Score model predicted loss.")
        elif not is_conf_correct and is_score_correct:
             print("   💡 **Insight**: Score Model correctly predicted the upset!")
             
    print("\n" + "=" * 50)
    print("📈 **Summary Statistics**")
    print(f"🏆 Confidence Model Accuracy: {correct_winner}/10 ({correct_winner*10:.0f}%)")
    print(f"🔢 Score Model Accuracy:      {correct_score_winner}/10 ({correct_score_winner*10:.0f}%)")
    print(f"🎯 Exact Scores Predicted:    {exact_score}")
    print(f"🤏 Close Predictions (±1):    {close_score}")

if __name__ == "__main__":
    print_analysis()
