import sys

def edit_file():
    path = 'daily_prediction_notifier.py'
    with open(path, 'r') as f:
        lines = f.readlines()
    
    # We want to replace the block that starts with "# Get NHL Schedule for Game IDs"
    # and ends before "if not games:" or similar.
    # In the current version, L544 is approximately where it starts.
    
    start_idx = -1
    for i, line in enumerate(lines):
        if "# Get NHL Schedule for Game IDs" in line:
            start_idx = i
            break
            
    if start_idx == -1:
        print("Could not find start index")
        return

    # Find where the block ends (next "if True:" or similar)
    end_idx = -1
    for i in range(start_idx + 1, len(lines)):
        if "if True:" in lines[i] or "for game in games:" in lines[i]:
            end_idx = i
            break
            
    if end_idx == -1:
        print("Could not find end index")
        return
        
    new_block = [
        "        # Phase 36: Build schedule_map from Local Analyzer (Reliable for 2026 Simulation)\n",
        "        schedule_map = {}\n",
        "        for date_str, day_games in self.schedule.games_by_date.items():\n",
        "            for g in day_games:\n",
        "                away_abbr = g.get('awayTeam', {}).get('abbrev')\n",
        "                home_abbr = g.get('homeTeam', {}).get('abbrev')\n",
        "                if away_abbr and home_abbr:\n",
        "                    key = f'{away_abbr}@{home_abbr}'\n",
        "                    schedule_map[key] = {\n",
        "                        'id': g.get('id'),\n",
        "                        'gameType': g.get('gameType', 2),\n",
        "                        'series_status': g.get('seriesStatus')\n",
        "                    }\n",
        "        print(f'🗺️  Built local schedule map with {len(schedule_map)} entries.')\n",
        "\n"
    ]
    
    lines[start_idx:end_idx] = new_block
    
    with open(path, 'w') as f:
        f.writelines(lines)
    print("✅ Successfully edited daily_prediction_notifier.py")

if __name__ == "__main__":
    edit_file()
