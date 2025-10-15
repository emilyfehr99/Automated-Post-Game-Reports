# 📅 GitHub Actions Workflow Schedule

## ⏰ When the Workflow Runs

The workflow checks for completed games **every 10 minutes**, but intelligently skips during weekday off-hours when NHL games don't happen.

### ✅ **ACTIVE HOURS** (Workflow Runs)

#### Weekdays (Monday-Friday)
- **3:00 PM - 1:59 AM Central** (next day)
- Checks every 10 minutes during this window
- **Why:** Most NHL games are 6:00-9:00 PM starts, finishing by 1am even with OT

#### Weekends (Saturday-Sunday)
- **24/7** (all day, every day)
- Checks every 10 minutes
- **Why:** Weekend games can start earlier (matinee games)

---

### ⏸️ **SKIP HOURS** (Workflow Pauses)

#### Weekdays Only (Monday-Friday)
- **2:00 AM - 2:59 PM Central**
- Workflow runs but immediately exits to save resources
- **Why:** NHL games virtually never happen during these hours on weekdays

---

## 📊 Visual Schedule (Monday-Friday)

```
Central Time:
12am ████████████████████ ACTIVE (late games finishing)
1am  ████████████████████ ACTIVE (OT games wrapping up)
2am  ░░░░░░░░░░░░░░░░░░░░ SKIPPED (no games)
3am  ░░░░░░░░░░░░░░░░░░░░ SKIPPED
4am  ░░░░░░░░░░░░░░░░░░░░ SKIPPED
5am  ░░░░░░░░░░░░░░░░░░░░ SKIPPED
6am  ░░░░░░░░░░░░░░░░░░░░ SKIPPED
7am  ░░░░░░░░░░░░░░░░░░░░ SKIPPED
8am  ░░░░░░░░░░░░░░░░░░░░ SKIPPED
9am  ░░░░░░░░░░░░░░░░░░░░ SKIPPED
10am ░░░░░░░░░░░░░░░░░░░░ SKIPPED
11am ░░░░░░░░░░░░░░░░░░░░ SKIPPED
12pm ░░░░░░░░░░░░░░░░░░░░ SKIPPED
1pm  ░░░░░░░░░░░░░░░░░░░░ SKIPPED
2pm  ░░░░░░░░░░░░░░░░░░░░ SKIPPED
3pm  ████████████████████ ACTIVE (pre-game prep)
4pm  ████████████████████ ACTIVE
5pm  ████████████████████ ACTIVE
6pm  ████████████████████ ACTIVE (games starting)
7pm  ████████████████████ ACTIVE
8pm  ████████████████████ ACTIVE
9pm  ████████████████████ ACTIVE
10pm ████████████████████ ACTIVE (games finishing)
11pm ████████████████████ ACTIVE
```

## 📊 Visual Schedule (Saturday-Sunday)

```
Central Time:
12am ████████████████████ ACTIVE
1am  ████████████████████ ACTIVE
2am  ████████████████████ ACTIVE
...  ████████████████████ ACTIVE (all hours)
11pm ████████████████████ ACTIVE
```

---

## 💰 Resource Savings

### Before (24/7 checking):
- **144 runs/day** (every 10 min × 24 hours)
- **1,008 runs/week**

### After (smart scheduling):
- **Weekdays:** ~66 runs/day (11 active hours: 3pm-2am)
- **Weekends:** 144 runs/day (24 hours)
- **Weekly total:** ~618 runs/week

**Savings: ~390 workflow runs per week (~39% reduction)**

---

## 🧪 How It Works

1. **Every 10 minutes**, GitHub Actions triggers the workflow
2. **First step** checks current Central Time and day of week
3. **If weekday 2am-3pm:** Workflow exits immediately (takes ~2 seconds)
4. **Otherwise:** Full workflow runs (generates reports, posts to Twitter)

---

## 🔧 Technical Details

### Time Check Logic
```bash
CENTRAL_HOUR=$(TZ='America/Chicago' date +%H)
CENTRAL_DAY=$(TZ='America/Chicago' date +%u)  # 1=Mon, 7=Sun

# Skip if: (Mon-Fri) AND (2am-2:59pm)
if [ $CENTRAL_DAY -le 5 ] && [ $CENTRAL_HOUR -ge 2 ] && [ $CENTRAL_HOUR -lt 15 ]; then
  SKIP
else
  RUN
fi
```

### Day Codes
- `1` = Monday
- `2` = Tuesday
- `3` = Wednesday
- `4` = Thursday
- `5` = Friday
- `6` = Saturday
- `7` = Sunday

---

## 📝 Notes

- **All times in Central Time** (America/Chicago timezone)
- **Manual triggers** (`workflow_dispatch`) always run regardless of time
- **Late-night games** are covered (workflow runs until 2am, even OT games finish by then)
- **Matinee games** on weekends are covered (24/7 on Sat/Sun)
- **Playoff games** with unusual times are covered on weekends

---

**Last Updated:** October 15, 2025
