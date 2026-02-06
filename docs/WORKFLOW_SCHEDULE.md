# 📅 GitHub Actions Workflow Schedule

## ⏰ When the Workflow Runs

The workflow checks for completed games **every 10 minutes** during active hours, and intelligently skips execution during off-hours to suffice user requirements.

### ✅ **ACTIVE HOURS** (Workflow Runs)

#### Weekdays (Monday-Friday)
- **8:00 PM - 1:59 AM Central** (next day)
- Checks every 10 minutes during this window
- **Why:** Focuses on evening games and avoids unnecessary daytime checks.

#### Weekends (Saturday-Sunday) & Holidays
- **11:30 AM - 1:59 AM Central** (next day)
- Checks every 10 minutes during this window
- **Why:** Accommodates early start times (matinee games) on weekends and holidays.

### ⏸️ **SKIP HOURS** (Workflow Pauses)

#### Weekdays
- **2:00 AM - 7:59 PM Central**
- Workflow runs but immediately exits.

#### Weekends & Holidays
- **2:00 AM - 11:29 AM Central**
- Workflow runs but immediately exits.

---

## 📊 Visual Schedule (Monday-Friday)

```
Central Time:
12am ████████████████████ ACTIVE (late games finishing)
1am  ████████████████████ ACTIVE (OT games wrapping up)
2am  ░░░░░░░░░░░░░░░░░░░░ SKIPPED
...
7pm  ░░░░░░░░░░░░░░░░░░░░ SKIPPED
8pm  ████████████████████ ACTIVE (Prime time)
9pm  ████████████████████ ACTIVE
10pm ████████████████████ ACTIVE
11pm ████████████████████ ACTIVE
```

## 📊 Visual Schedule (Saturday-Sunday & Holidays)

```
Central Time:
12am ████████████████████ ACTIVE
1am  ████████████████████ ACTIVE
2am  ░░░░░░░░░░░░░░░░░░░░ SKIPPED
...
11am ░░░░░░░░░░░░░░░░░░░░ SKIPPED (until 11:30)
12pm ████████████████████ ACTIVE
1pm  ████████████████████ ACTIVE
...
11pm ████████████████████ ACTIVE
```

---

## 🔧 Technical Details

### Logic
The script `github_actions_runner.py` determines the current Central Time and checks:
1. Is it a Weekend?
2. Is it a known Holiday? (Fixed dates + Dynamic Thanksgiving/Labor Day/Memorial Day)

**If Off-Day (Weekend/Holiday):**
- Checks if time is between 11:30 AM and 02:00 AM.

**If Weekday:**
- Checks if time is between 08:00 PM and 02:00 AM.

### Holidays Handled
- New Year's Day (Jan 1)
- Memorial Day (Late May)
- Independence Day (July 4)
- Labor Day (Early Sep)
- Veterans/Remembrance Day (Nov 11)
- Thanksgiving (Late Nov)
- Christmas Eve/Day (Dec 24-25)
- Boxing Day (Dec 26)
- New Year's Eve (Dec 31)

---

**Last Updated:** February 6, 2026
