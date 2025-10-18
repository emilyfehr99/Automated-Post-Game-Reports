library(dplyr)
library(ggplot2)

# Load and check data
goalie_data <- read.csv('/Users/emilyfehr8/Desktop/goalie stuff incl.csv')

# Verify column names
cat("Column names in goalie dataset:\n")
print(colnames(goalie_data))
if (any(colnames(goalie_data) == "")) {
  stop("Error: Empty column names detected in the dataset. Please fix the CSV file.")
}

# Validate required columns
required_cols <- c("ID", "start", "end", "duration", "pos_x", "pos_y", "player", "team", "action", "half")
missing_cols <- setdiff(required_cols, colnames(goalie_data))
if (length(missing_cols) > 0) {
  stop("Error: Missing required columns: ", paste(missing_cols, collapse = ", "))
}

# Sort data by start time
goalie_data <- goalie_data %>% arrange(start)

# Define zone limits
DZ_limit <- 22.86
NZ_limit <- 38.10

# Helper function to define zones
define_zone <- function(pos_x, team, goalie_team) {
  case_when(
    team == goalie_team & pos_x < -DZ_limit ~ "DZ",
    team == goalie_team & pos_x > NZ_limit ~ "OZ",
    team == goalie_team ~ "NZ",
    team != goalie_team & pos_x > DZ_limit ~ "DZ",
    team != goalie_team & pos_x < -NZ_limit ~ "OZ",
    TRUE ~ "NZ"
  )
}

# Helper function for save percentage
calc_save_pct <- function(saves, goals) {
  total <- saves + goals
  if_else(total > 0, (saves / total) * 100, NA_real_)
}

# Helper for slot area (high-danger)
is_slot <- function(pos_x, pos_y) {
  abs(pos_x) < 30 & abs(pos_y) < 15
}

# Identify goalies and their teams
goalie_team_data <- goalie_data %>%
  filter(action %in% c("Saves", "Goals against")) %>%
  group_by(player) %>%
  summarise(goalie_team = unique(team)[1])  # Assume first team is goalie's team
cat("Goalie teams:\n")
print(goalie_team_data)

goalies <- goalie_team_data$player
if (length(goalies) == 0) {
  stop("Error: No goalies found with 'Saves' or 'Goals against' actions.")
}

# Filter for goalie-specific data
goalie_data <- goalie_data %>% filter(player %in% goalies)

# Add goalie_team column
goalie_data <- goalie_data %>%
  left_join(goalie_team_data, by = "player")

# Add zone column
goalie_data <- goalie_data %>%
  mutate(zone = define_zone(pos_x, team, goalie_team))

# Debugging: Action frequencies
cat("Action frequencies for goalies:\n")
action_freq <- table(goalie_data$action)
print(action_freq)

# Check all unique actions (case-insensitive)
all_actions <- unique(tolower(goalie_data$action))
cat("All unique actions (case-insensitive):\n")
print(all_actions)

# CRITICAL FIX: Use 'Shots against' instead of 'Shots' for goalie analysis
cat("IMPORTANT: Using 'Shots against' instead of 'Shots' for goalie analysis\n")
cat("This is the correct action for shots faced by goalies\n")

# Validate coordinate ranges for Shots against
cat("pos_x range for Shots against:\n")
print(summary(goalie_data$pos_x[goalie_data$action == "Shots against"]))
cat("pos_y range for Shots against:\n")
print(summary(goalie_data$pos_y[goalie_data$action == "Shots against"]))

# Check slot shots - CORRECTED: Shots against are on goalie's team, not opposing team
slot_shots <- goalie_data %>%
  filter(action == "Shots against" & team == goalie_team & is_slot(pos_x, pos_y))
cat("Number of Shots against by goalie's team in slot (|pos_x| < 30, |pos_y| < 15):", nrow(slot_shots), "\n")
if (nrow(slot_shots) > 0) {
  cat("Sample of slot shots:\n")
  print(slot_shots %>% select(player, start, pos_x, pos_y, team, goalie_team, zone) %>% head(5))
} else {
  cat("Warning: No shots in slot by goalie's team. Check pos_x/pos_y ranges or slot definition.\n")
}

# 1. Save Percentage Metrics
# Overall Save Percentage
overall_save_pct <- goalie_data %>%
  group_by(player) %>%
  summarise(
    saves = sum(action == "Saves", na.rm = TRUE),
    goals_against = sum(action == "Goals against", na.rm = TRUE),
    save_pct = calc_save_pct(saves, goals_against)
  )
print("Overall Save Percentage:")
print(overall_save_pct)

# Save Percentage by Zone
save_pct_by_zone <- goalie_data %>%
  filter(action %in% c("Saves", "Goals against")) %>%
  group_by(player, zone) %>%
  summarise(
    saves = sum(action == "Saves", na.rm = TRUE),
    goals_against = sum(action == "Goals against", na.rm = TRUE),
    save_pct = calc_save_pct(saves, goals_against)
  )
print("Save Percentage by Zone:")
print(save_pct_by_zone)

# Save Percentage by Half
save_pct_by_half <- goalie_data %>%
  filter(action %in% c("Saves", "Goals against")) %>%
  group_by(player, half) %>%
  summarise(
    saves = sum(action == "Saves", na.rm = TRUE),
    goals_against = sum(action == "Goals against", na.rm = TRUE),
    save_pct = calc_save_pct(saves, goals_against)
  )
print("Save Percentage by Half:")
print(save_pct_by_half)

# Save Percentage on Rebounds
rebound_sequences <- goalie_data %>%
  mutate(
    prev_action_1 = lag(action, 1),
    prev_action_2 = lag(action, 2),
    prev_action_3 = lag(action, 3),
    prev_action_4 = lag(action, 4),
    prev_action_5 = lag(action, 5)
  ) %>%
  filter(action %in% c("Saves", "Goals against") & 
           (prev_action_1 == "Saves" | prev_action_2 == "Saves" | 
              prev_action_3 == "Saves" | prev_action_4 == "Saves" | 
              prev_action_5 == "Saves"))
cat("Number of Rebound sequences (Saves within 5 actions):", nrow(rebound_sequences), "\n")
if (nrow(rebound_sequences) > 0) {
  cat("Sample of Rebound sequences:\n")
  print(rebound_sequences %>% select(player, start, action, prev_action_1, prev_action_2, prev_action_3, prev_action_4, prev_action_5) %>% head(5))
} else {
  cat("Warning: No rebound sequences found. Check action labels or extend action window.\n")
}

rebound_save_pct <- rebound_sequences %>%
  group_by(player) %>%
  summarise(
    saves = sum(action == "Saves", na.rm = TRUE),
    goals_against = sum(action == "Goals against", na.rm = TRUE),
    rebound_save_pct = calc_save_pct(saves, goals_against)
  )
print("Save Percentage on Rebounds:")
print(rebound_save_pct)

# Save Percentage After Pass - CORRECTED LOGIC
# Look for shots against (by goalie's team) that follow passes by the SAME team
pass_sequences <- goalie_data %>%
  mutate(
    prev_action_1 = lag(action, 1),
    prev_action_2 = lag(action, 2),
    prev_action_3 = lag(action, 3),
    prev_action_4 = lag(action, 4),
    prev_action_5 = lag(action, 5),
    next_action = lead(action, 1)
  ) %>%
  filter(action == "Shots against" & team == goalie_team &
           (tolower(prev_action_1) %in% tolower(c("Accurate passes", "Passes")) |
              tolower(prev_action_2) %in% tolower(c("Accurate passes", "Passes")) |
              tolower(prev_action_3) %in% tolower(c("Accurate passes", "Passes")) |
              tolower(prev_action_4) %in% tolower(c("Accurate passes", "Passes")) |
              tolower(prev_action_5) %in% tolower(c("Accurate passes", "Passes")))) %>%
  filter(next_action %in% c("Saves", "Goals against"))
cat("Number of Shots against by goalie's team following Passes within 5 actions:", nrow(pass_sequences), "\n")
if (nrow(pass_sequences) > 0) {
  cat("Sample of Pass sequences:\n")
  print(pass_sequences %>% select(player, start, action, prev_action_1, prev_action_2, prev_action_3, prev_action_4, prev_action_5, next_action, pos_x, pos_y, team, goalie_team) %>% head(5))
} else {
  cat("Warning: No pass sequences found. Check action labels, team filtering, or extend action window.\n")
}

save_pct_after_pass <- pass_sequences %>%
  group_by(player) %>%
  summarise(
    saves = sum(next_action == "Saves", na.rm = TRUE),
    goals_against = sum(next_action == "Goals against", na.rm = TRUE),
    save_pct_after_pass = calc_save_pct(saves, goals_against)
  )
print("Save Percentage After Pass:")
print(save_pct_after_pass)

# Save Percentage on High-Danger Shots - CORRECTED
# Using Shots against (by goalie's team) in slot area
high_danger_sequences <- goalie_data %>%
  mutate(
    prev_action = lag(action)
  ) %>%
  filter(action %in% c("Saves", "Goals against")) %>%
  filter(is_slot(pos_x, pos_y) | (tolower(prev_action) == tolower("Passes to the slot")))
cat("Number of High-Danger sequences (slot or Passes to slot):", nrow(high_danger_sequences), "\n")
if (nrow(high_danger_sequences) > 0) {
  cat("Sample of High-Danger sequences:\n")
  print(high_danger_sequences %>% select(player, start, action, pos_x, pos_y, prev_action, team, goalie_team) %>% head(5))
} else {
  cat("Warning: No high-danger sequences found. Check slot definition or Passes to the slot.\n")
}

high_danger_save_pct <- high_danger_sequences %>%
  group_by(player) %>%
  summarise(
    saves = sum(action == "Saves", na.rm = TRUE),
    goals_against = sum(action == "Goals against", na.rm = TRUE),
    high_danger_save_pct = calc_save_pct(saves, goals_against)
  )
print("Save Percentage on High-Danger Shots:")
print(high_danger_save_pct)

# NOTE: Power Play and Short-Handed shots are not present in this dataset
# These sections will return empty results but won't cause errors

# Save Percentage on Power Play Shots
pp_sequences <- goalie_data %>%
  mutate(
    prev_action_1 = lag(action, 1),
    prev_action_2 = lag(action, 2),
    prev_action_3 = lag(action, 3),
    prev_action_4 = lag(action, 4),
    prev_action_5 = lag(action, 5)
  ) %>%
  filter(action %in% c("Saves", "Goals against") & 
           (tolower(prev_action_1) == tolower("Power play shots") |
              tolower(prev_action_2) == tolower("Power play shots") |
              tolower(prev_action_3) == tolower("Power play shots") |
              tolower(prev_action_4) == tolower("Power play shots") |
              tolower(prev_action_5) == tolower("Power play shots")))
cat("Number of Power Play sequences (within 5 actions):", nrow(pp_sequences), "\n")

pp_save_pct <- pp_sequences %>%
  group_by(player) %>%
  summarise(
    saves = sum(action == "Saves", na.rm = TRUE),
    goals_against = sum(action == "Goals against", na.rm = TRUE),
    pp_save_pct = calc_save_pct(saves, goals_against)
  )
print("Save Percentage on Power Play Shots:")
print(pp_save_pct)

# Save Percentage on Short-Handed Shots
sh_sequences <- goalie_data %>%
  mutate(
    prev_action_1 = lag(action, 1),
    prev_action_2 = lag(action, 2),
    prev_action_3 = lag(action, 3),
    prev_action_4 = lag(action, 4),
    prev_action_5 = lag(action, 5)
  ) %>%
  filter(action %in% c("Saves", "Goals against") & 
           (tolower(prev_action_1) == tolower("Short-handed shots") |
              tolower(prev_action_2) == tolower("Short-handed shots") |
              tolower(prev_action_3) == tolower("Short-handed shots") |
              tolower(prev_action_4) == tolower("Short-handed shots") |
              tolower(prev_action_5) == tolower("Short-handed shots")))
cat("Number of Short-Handed sequences (within 5 actions):", nrow(sh_sequences), "\n")

sh_save_pct <- sh_sequences %>%
  group_by(player) %>%
  summarise(
    saves = sum(action == "Saves", na.rm = TRUE),
    goals_against = sum(action == "Goals against", na.rm = TRUE),
    sh_save_pct = calc_save_pct(saves, goals_against)
  )
print("Save Percentage on Short-Handed Shots:")
print(sh_save_pct)

# 2. Workload Metrics
# Shot Suppression Rate - CORRECTED: Shots against are by goalie's team
total_duration <- sum(goalie_data$duration, na.rm = TRUE)
if (total_duration == 0) {
  cat("Warning: Total duration is 0; Shot Suppression Rate and GAA may be NA.\n")
}
shot_suppression <- goalie_data %>%
  group_by(player, half) %>%
  summarise(
    shots_against = sum(action == "Shots against" & team == goalie_team, na.rm = TRUE),
    duration_half = sum(duration, na.rm = TRUE),
    shot_rate_per_min = if_else(duration_half > 0, shots_against / (duration_half / 60), NA_real_)
  )
print("Shot Suppression Rate by Half (Shots against by goalie's team):")
print(shot_suppression)

# Goals Against Average
gaa <- goalie_data %>%
  group_by(player) %>%
  summarise(
    goals_against = sum(action == "Goals against", na.rm = TRUE),
    gaa = if_else(total_duration > 0, goals_against / (total_duration / 60), NA_real_)
  )
print("Goals Against Average (per 60 minutes):")
print(gaa)

# High-Danger Shots Faced - CORRECTED: Shots against are by goalie's team
high_danger_shots_faced <- goalie_data %>%
  mutate(prev_action = lag(action)) %>%
  filter(action == "Shots against" & team == goalie_team & 
           (is_slot(pos_x, pos_y) | (tolower(prev_action) == tolower("Passes to the slot")))) %>%
  group_by(player) %>%
  summarise(high_danger_shots = n())
print("High-Danger Shots Faced (goalie's team):")
print(high_danger_shots_faced)

# Shot Location Metrics - CORRECTED: Shots against are by goalie's team
shot_locations <- goalie_data %>%
  filter(action == "Shots against" & team == goalie_team) %>%
  group_by(player) %>%
  summarise(
    shots = n(),
    avg_pos_x = mean(pos_x, na.rm = TRUE),
    avg_pos_y = mean(pos_y, na.rm = TRUE),
    var_pos_x = if_else(n() > 1, var(pos_x, na.rm = TRUE), NA_real_),
    var_pos_y = if_else(n() > 1, var(pos_y, na.rm = TRUE), NA_real_)
  )
print("Shot Location Metrics (Average and Variance, goalie's team):")
print(shot_locations)

# Visualization: Save Percentage Bar Chart
save_pct_data <- bind_rows(
  overall_save_pct %>% mutate(metric = "Overall"),
  save_pct_by_zone %>% rename(save_pct = save_pct) %>% mutate(metric = paste("Zone", zone)),
  rebound_save_pct %>% mutate(metric = "Rebound", save_pct = rebound_save_pct),
  save_pct_after_pass %>% mutate(metric = "After Pass", save_pct = save_pct_after_pass),
  high_danger_save_pct %>% mutate(metric = "High Danger", save_pct = high_danger_save_pct),
  pp_save_pct %>% mutate(metric = "Power Play", save_pct = pp_save_pct),
  sh_save_pct %>% mutate(metric = "Short-Handed", save_pct = sh_save_pct)
) %>% select(player, metric, save_pct) %>% filter(!is.na(save_pct))

if (nrow(save_pct_data) > 0) {
  ggplot(save_pct_data, aes(x = reorder(metric, save_pct), y = save_pct, fill = metric)) +
    geom_bar(stat = "identity") +
    facet_wrap(~player, scales = "free_y") +
    scale_fill_manual(values = c("Overall" = "#1f77b4", "Zone DZ" = "#ff7f0e", "Zone NZ" = "#2ca02c", 
                                 "Zone OZ" = "#d62728", "Rebound" = "#9467bd", "After Pass" = "#8c564b", 
                                 "High Danger" = "#7f7f7f", "Power Play" = "#bcbd22", 
                                 "Short-Handed" = "#17becf")) +
    labs(title = "Goalie Save Percentage Metrics by Player", 
         x = "Metric", 
         y = "Save Percentage (%)") +
    theme_minimal() +
    theme(legend.position = "none", 
          axis.text.x = element_text(angle = 45, hjust = 1, size = 8),
          strip.text = element_text(size = 10, face = "bold"))
} else {
  cat("Error: No valid save percentage data to plot. Check data for 'Saves' and 'Goals against'.\n")
}

# Summary of key findings
cat("\n=== SUMMARY OF KEY FINDINGS ===\n")
cat("1. Main issue: Dataset uses 'Shots against' instead of 'Shots' for goalie analysis\n")
cat("2. CRITICAL: 'Shots against' are recorded for the GOALIE'S TEAM, not opposing team\n")
cat("3. Missing actions: 'Power play shots', 'Short-handed shots', 'Passes to the slot'\n")
cat("4. Duration is constant (12) for all entries\n")
cat("5. High-danger shots in slot area: ", nrow(slot_shots), "\n")
cat("6. Total goalies analyzed: ", length(goalies), "\n")
cat("7. Overall save percentage range: ", round(min(overall_save_pct$save_pct, na.rm = TRUE), 2), "% to ", round(max(overall_save_pct$save_pct, na.rm = TRUE), 2), "%\n")
cat("8. Pass sequences found: ", nrow(pass_sequences), "\n")
cat("9. Rebound sequences found: ", nrow(rebound_sequences), "\n")
