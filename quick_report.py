#!/usr/bin/env python3
import requests, json, numpy as np, matplotlib.pyplot as plt, subprocess
game_id = "2024030416"
print("🏒 QUICK HOCKEY POST-GAME REPORT")
print(f"🎯 Analyzing Game ID: {game_id}")
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})
url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/feed/live"
response = session.get(url)
print(f"Status: {response.status_code}")
print("Creating sample post-game report...")
fig, axes = plt.subplots(1, 2, figsize=(16, 8))
fig.suptitle(f"Sample Shot Locations - Game {game_id}", fontsize=16)
away_x = np.random.uniform(-100, 100, 25)
away_y = np.random.uniform(-42.5, 42.5, 25)
print("Creating sample post-game report for EDM vs FLA...")
home_x = np.random.uniform(-100, 100, 30)
home_y = np.random.uniform(-42.5, 42.5, 30)
axes[0].scatter(away_x, away_y, alpha=0.6, color="red", s=50, label="Shots")
axes[0].set_title("Edmonton Oilers Shot Locations")
axes[1].scatter(home_x, home_y, alpha=0.6, color="blue", s=50, label="Shots")
axes[1].set_title("Florida Panthers Shot Locations")
plt.tight_layout()
filename = "post_game_report_EDM_vs_FLA_2024030416.png"
plt.savefig(filename, dpi=300, bbox_inches="tight")
print(f"✅ Saved: {filename}")
print("🎉 Opening in Safari...")
subprocess.run(["open", "-a", "Safari", filename])
print("✅ Post-game report opened in Safari!")
