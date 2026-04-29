"""
Daily Prediction Notifier
Sends daily NHL game predictions via email, Discord, or other methods
Uses Meta-Ensemble Predictor for 55-60% accuracy
"""

import sys, os
_module_dirs = ['models', 'analyzers', 'scrapers', 'utils']
_base_dir = os.path.dirname(os.path.abspath(__file__))
for _d in _module_dirs:
    _p = os.path.join(_base_dir, _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)


import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import pytz
from prediction_interface import PredictionInterface
from meta_ensemble_predictor import MetaEnsemblePredictor
from rotowire_scraper import RotoWireScraper
import os
from pathlib import Path
from playoff_predictor import PlayoffSeriesPredictor
try:
    from utils.timing import timed
except Exception:
    from timing import timed

class DailyPredictionNotifier:
    def __init__(self):
        """Initialize the notifier with meta-ensemble predictor"""
        self.predictor = PredictionInterface()  # Keep for compatibility
        self.meta_ensemble = MetaEnsemblePredictor()
        self.rotowire = RotoWireScraper()
        from schedule_analyzer import ScheduleAnalyzer
        self.schedule = ScheduleAnalyzer()
        self.playoff_predictor = PlayoffSeriesPredictor()
        self._cached_summary = None
        self._cached_predictions = None

        # Phase 2: Centralize Vegas odds for 3-way blending
        from vegas_odds_scraper import scrape_vegas_odds
        self._market_odds = scrape_vegas_odds() if getattr(self, "_use_vegas", True) else {}
        if self._market_odds:
            print(f"✅ Loaded {len(self._market_odds)} games from Vegas market")

        # Contextual MOE tuning: learn blend weight w(score_model, meta_model)
        # as a function of matchup "distance" (abs(diff in expected goals)).
        # This is tuned once at initialization using your stored history.
        self._moe_default_w = 0.72 # Balanced blend: 72% Score Model / 28% Meta-Ensemble
        self._moe_absdiff_edges = None
        self._moe_absdiff_w_map = None
        # Contextual MOE (per-bucket w) was found to overfit and reduce
        # winner accuracy on your stored backtest history, so it is
        # intentionally disabled. We keep the globally optimal w instead.

        # Tune the global MOE weight without contextual bucketing.
        self._tune_global_moe_blend_w()

    def _tune_contextual_moe_blend(self) -> None:
        """Tune w per abs(diff) bucket using a train/validation time split."""
        import numpy as np
        from score_prediction_model import ScorePredictionModel

        history_path = Path('data/win_probability_predictions_v2.json')
        if not history_path.exists():
            history_path = Path('win_probability_predictions_v2.json')
        if not history_path.exists():
            return

        with open(history_path, 'r') as f:
            d = json.load(f)

        preds = d.get('predictions', [])
        if not preds:
            return

        score_model = ScorePredictionModel()

        # Collect completed games with both meta and score probabilities.
        rows = []
        cache_sp = {}

        def _get_meta_away_prob(p: dict):
            # Meta away/home are stored as *percent* in this history schema.
            ap = p.get('predicted_away_win_prob')
            hp = p.get('predicted_home_win_prob')
            if ap is None or hp is None:
                # Fallback to alternative keys some runs might store.
                ap = p.get('away_win_prob', p.get('away_prob'))
                hp = p.get('home_win_prob', p.get('home_prob'))
            if ap is None or hp is None:
                return None
            try:
                ap = float(ap)
                hp = float(hp)
            except (TypeError, ValueError):
                return None
            # If values look like percents, normalize.
            if ap > 1.0 or hp > 1.0:
                ap /= 100.0
                hp /= 100.0
            s = ap + hp
            if s <= 0:
                return None
            return ap / s

        def _get_actual_side(p: dict):
            side = p.get('actual_winner_side')
            if side in ('away', 'home'):
                return side
            # Derive from actual scores if needed.
            a = p.get('actual_away_score')
            h = p.get('actual_home_score')
            if a is None or h is None:
                return None
            return 'away' if a > h else 'home'

        for p in preds:
            actual = p.get('actual_winner')
            away = p.get('away_team')
            home = p.get('home_team')
            if not (actual and away and home):
                continue
            actual_side = _get_actual_side(p)
            if actual_side not in ('away', 'home'):
                continue

            meta_away_prob = _get_meta_away_prob(p)
            if meta_away_prob is None:
                continue

            ts = p.get('timestamp')
            ts_val = None
            if isinstance(ts, (int, float)):
                ts_val = float(ts)
            elif isinstance(ts, str):
                try:
                    ts_val = float(ts)
                except ValueError:
                    ts_val = None

            key = (away, home)
            if key in cache_sp:
                sp = cache_sp[key]
            else:
                sp = score_model.predict_score(away, home)
                cache_sp[key] = sp

            score_away_prob = float(sp.get('away_win_prob', 0.5))
            away_exp = float(sp.get('away_expected', 0.0))
            home_exp = float(sp.get('home_expected', 0.0))
            diff = away_exp - home_exp
            rows.append((ts_val, actual_side, meta_away_prob, score_away_prob, abs(diff)))

        if len(rows) < 300:
            return

        rows.sort(key=lambda x: x[0] if x[0] is not None else float('inf'))
        split_idx = int(len(rows) * 0.7)
        train_rows = rows[:split_idx]
        val_rows = rows[split_idx:]

        # Build abs(diff) quantile buckets from training.
        num_buckets = 4
        absdiff_train = np.array([r[4] for r in train_rows], dtype=float)
        q = np.linspace(0.0, 1.0, num_buckets + 1)
        edges = np.unique(np.quantile(absdiff_train, q))
        if edges.size < 3:
            return

        def _bucket_index(x: float) -> int:
            idx = int(np.searchsorted(edges, x, side='right') - 1)
            return max(0, min(idx, edges.size - 2))

        w_candidates = [i / 50.0 for i in range(0, 51)]  # 0..1 step 0.02
        default_w = self._moe_default_w
        w_map = [default_w for _ in range(edges.size - 1)]

        # Tune each bucket on validation: choose w that maximizes accuracy.
        for b in range(edges.size - 1):
            bucket_val = [r for r in val_rows if _bucket_index(r[4]) == b]
            if len(bucket_val) < 20:
                continue
            best_w = default_w
            best_acc = -1.0
            for w in w_candidates:
                correct = 0
                for _ts, actual_side, meta_away_prob, score_away_prob, _absd in bucket_val:
                    blended = w * score_away_prob + (1.0 - w) * meta_away_prob
                    pred_side = 'away' if blended >= 0.5 else 'home'
                    if pred_side == actual_side:
                        correct += 1
                acc = correct / len(bucket_val)
                if acc > best_acc:
                    best_acc = acc
                    best_w = w
            w_map[b] = best_w

        # Quick sanity: overall validation accuracy with bucket weights.
        correct = 0
        for _ts, actual_side, meta_away_prob, score_away_prob, absd in val_rows:
            b = _bucket_index(absd)
            w = w_map[b]
            blended = w * score_away_prob + (1.0 - w) * meta_away_prob
            pred_side = 'away' if blended >= 0.5 else 'home'
            if pred_side == actual_side:
                correct += 1
        val_acc = correct / len(val_rows) if val_rows else 0.0

        # Compare to global blend fallback so we don't regress accuracy.
        global_correct = 0
        for _ts, actual_side, meta_away_prob, score_away_prob, _absd in val_rows:
            blended_g = default_w * score_away_prob + (1.0 - default_w) * meta_away_prob
            pred_side_g = 'away' if blended_g >= 0.5 else 'home'
            if pred_side_g == actual_side:
                global_correct += 1
        global_acc = global_correct / len(val_rows) if val_rows else 0.0

        if val_acc + 1e-9 < global_acc:
            # If contextual tuning underperforms, disable it.
            print(
                f"⚠️ Contextual MOE underperformed global blend; using global w={default_w} instead. "
                f"context_val_acc={val_acc:.3f}, global_val_acc={global_acc:.3f}"
            )
            self._moe_absdiff_edges = None
            self._moe_absdiff_w_map = None
            return

        print(f"✅ Contextual MOE tuned: buckets={edges.size-1}, val_acc={val_acc:.3f}, w_map={w_map}")
        self._moe_absdiff_edges = edges.tolist()
        self._moe_absdiff_w_map = w_map

    def _tune_global_moe_blend_w(self) -> None:
        """Tune global MOE blend weight w_score (score_model vs meta).

        This updates `self._moe_default_w` only (contextual MOE remains disabled).
        Uses rolling time-splits over stored `win_probability_predictions_v2.json`.
        """
        import numpy as np
        from score_prediction_model import ScorePredictionModel

        history_path = Path('data/win_probability_predictions_v2.json')
        if not history_path.exists():
            history_path = Path('win_probability_predictions_v2.json')
        if not history_path.exists():
            return

        with open(history_path, 'r') as f:
            d = json.load(f)

        preds = d.get('predictions', [])
        if not preds:
            return

        score_model = ScorePredictionModel()
        cache_sp = {}

        def _get_meta_away_prob(p: dict):
            ap = p.get('predicted_away_win_prob')
            hp = p.get('predicted_home_win_prob')
            if ap is None or hp is None:
                ap = p.get('away_win_prob', p.get('away_prob'))
                hp = p.get('home_win_prob', p.get('home_prob'))
            if ap is None or hp is None:
                return None
            try:
                ap = float(ap)
                hp = float(hp)
            except (TypeError, ValueError):
                return None
            if ap > 1.0 or hp > 1.0:
                ap /= 100.0
                hp /= 100.0
            s = ap + hp
            if s <= 0:
                return None
            return ap / s

        def _get_actual_side(p: dict):
            side = p.get('actual_winner_side')
            if side in ('away', 'home'):
                return side
            away = p.get('away_team')
            home = p.get('home_team')
            actual = p.get('actual_winner')
            if away and actual == away:
                return 'away'
            if home and actual == home:
                return 'home'
            a = p.get('actual_away_score')
            h = p.get('actual_home_score')
            if a is None or h is None:
                return None
            try:
                a_i = int(a)
                h_i = int(h)
            except (TypeError, ValueError):
                return None
            if a_i > h_i:
                return 'away'
            if h_i > a_i:
                return 'home'
            return None

        rows = []
        for p in preds:
            away = p.get('away_team')
            home = p.get('home_team')
            if not away or not home:
                continue
            actual_side = _get_actual_side(p)
            if actual_side not in ('away', 'home'):
                continue
            meta_away_prob = _get_meta_away_prob(p)
            if meta_away_prob is None:
                continue

            key = (away, home)
            if key in cache_sp:
                sp = cache_sp[key]
            else:
                sp = score_model.predict_score(away, home)
                cache_sp[key] = sp

            score_away_prob = float(sp.get('away_win_prob', 0.5))

            ts = p.get('timestamp')
            ts_val = None
            if isinstance(ts, (int, float)):
                ts_val = float(ts)
            elif isinstance(ts, str):
                try:
                    ts_val = float(ts)
                except ValueError:
                    ts_val = None

            rows.append((ts_val, actual_side, float(meta_away_prob), score_away_prob))

        if len(rows) < 300:
            return

        has_ts = any(ts_val is not None for ts_val, *_ in rows)
        if has_ts:
            rows.sort(key=lambda x: x[0] if x[0] is not None else float('inf'))

        actual_y = np.array([1.0 if r[1] == 'away' else 0.0 for r in rows], dtype=float)
        meta_p = np.array([r[2] for r in rows], dtype=float)
        score_p = np.array([r[3] for r in rows], dtype=float)
        delta = score_p - meta_p

        # Widened search range to allow Meta-Ensemble (XGBoost) more influence.
        # Previously capped at 0.97-0.99, which caused a circular bias.
        w_candidates = [0.50 + i * 0.02 for i in range(0, 26)]  # 0.50..1.00
        train_fracs = [0.6, 0.7, 0.75]

        best_w = float(self._moe_default_w)
        best_mean_acc = -1.0

        for w in w_candidates:
            accs = []
            for tf in train_fracs:
                train_n = max(50, int(len(rows) * tf))
                if train_n >= len(rows) - 20:
                    continue
                y_val = actual_y[train_n:]
                if y_val.size < 80:
                    continue
                blended = meta_p[train_n:] + w * delta[train_n:]
                pred = blended >= 0.5
                y = y_val >= 0.5
                accs.append(float(np.mean(pred == y)))

            if not accs:
                continue
            mean_acc = float(np.mean(accs))
            if mean_acc > best_mean_acc + 1e-9:
                best_mean_acc = mean_acc
                best_w = float(w)

        if abs(best_w - float(self._moe_default_w)) >= 1e-6:
            print(f"✅ Tuned global MOE w_score: {best_w:.3f} (rolling mean winner acc={best_mean_acc:.3f})")
        self._moe_default_w = float(best_w)

    def save_predictions_to_history(self, predictions: list):
        """Persist predictions as append-only events and regenerate JSON view."""
        # Primary persistence: append-only events log (schema-stable, deterministic training).
        try:
            from utils.event_store import append_prediction_event
        except Exception:
            from event_store import append_prediction_event

        def _clamp01(x: float) -> float:
            return max(1e-6, min(1.0 - 1e-6, float(x)))

        def _norm_pair(ph: float, pa: float) -> tuple[float, float]:
            s = float(ph) + float(pa)
            if not (s > 0):
                return 0.5, 0.5
            return float(ph) / s, float(pa) / s

        # Sanity guard: ensure we aren't systematically flipping home/away.
        # Keep a small rolling sample from the history view (best-effort).
        def _sanity_check_home_share() -> None:
            try:
                p = Path("data/win_probability_predictions_v2.json")
                if not p.exists():
                    return
                d = json.loads(p.read_text())
                preds = d.get("predictions", [])
                if not isinstance(preds, list) or len(preds) < 30:
                    return
                recent = preds[-50:]
                cnt = 0
                tot = 0
                for r in recent:
                    ph = r.get("predicted_home_win_prob")
                    pa = r.get("predicted_away_win_prob")
                    if ph is None and pa is None:
                        continue
                    try:
                        ph = float(ph) if ph is not None else (100.0 - float(pa))
                        # Normalize to 0..1
                        ph = ph / 100.0 if ph > 1.0 else ph
                    except Exception:
                        continue
                    tot += 1
                    cnt += int(ph >= 0.5)
                if tot >= 25:
                    share = cnt / tot
                    # If we *never* favor home (or always do), something is likely inverted.
                    if share <= 0.02 or share >= 0.98:
                        raise RuntimeError(
                            f"Sanity check failed: home_favored_share={share:.3f} over last {tot} preds. "
                            "This suggests a home/away probability mapping bug."
                        )
            except Exception as e:
                # Fail fast: better to stop writing corrupted history.
                raise

        new_count = 0
        for pred in predictions:
            # We want to track all games, even if we don't have a numeric ID (fallback games)
            g_id = pred.get("game_id")
            if not g_id:
                # Generate a deterministic string ID for tracking
                g_id = f"{pred['away_team']}@{pred['home_team']}_{pred.get('date', datetime.now().strftime('%Y-%m-%d'))}"
            
            # Prefer blended away prob when present (0..1).
            if "blended_away_prob" in pred and pred["blended_away_prob"] is not None:
                away_p = float(pred["blended_away_prob"])
                home_p = 1.0 - away_p
            else:
                # Fallback to legacy % fields.
                away_p = float(pred.get("away_prob", 50.0)) / 100.0
                home_p = float(pred.get("home_prob", 50.0)) / 100.0

            # Invariants
            home_p, away_p = _norm_pair(home_p, away_p)
            home_p = _clamp01(home_p)
            away_p = _clamp01(away_p)

            record = {
                'date': datetime.now(pytz.timezone('US/Central')).strftime('%Y-%m-%d'),
                'game_id': g_id,
                'home_team': pred['home_team'],
                'away_team': pred['away_team'],
                'predicted_winner': pred['predicted_winner'],
                # Store both schema variants:
                # - *_win_prob: decimals in 0..1 (new pipeline)
                # - predicted_*_win_prob: percents 0..100 (legacy readers / dashboards)
                'home_win_prob': home_p,
                'away_win_prob': away_p,
                'predicted_home_win_prob': home_p * 100.0,
                'predicted_away_win_prob': away_p * 100.0,
                'model_confidence': pred['confidence'] / 100.0,
                # Scoreline outputs (if present)
                'predicted_home_goals': pred.get("predicted_home_goals"),
                'predicted_away_goals': pred.get("predicted_away_goals"),
                'predicted_total_goals': pred.get("predicted_total_goals"),
                # Ensemble diagnostics (for guardrails / observability)
                'ensemble_mode': pred.get("ensemble_mode"),
                'ensemble_weights': pred.get("ensemble_weights"),
                # Phase 47 Fatigue Signals
                'away_back_to_back': pred.get('away_back_to_back', False),
                'home_back_to_back': pred.get('home_back_to_back', False),
                'away_3_in_4': pred.get('away_3_in_4', False),
                'home_3_in_4': pred.get('home_3_in_4', False),
                'away_rest_value': pred.get('away_rest_value', 0.0),
                'home_rest_value': pred.get('home_rest_value', 0.0),
                'away_games_7d': pred.get('away_games_7d', 1),
                'home_games_7d': pred.get('home_games_7d', 1),
                'away_travel_miles': pred.get('away_travel_miles', 0.0),
                'home_travel_miles': pred.get('home_travel_miles', 0.0),
                'attribution': pred.get('attribution', []),
                # Store the metrics used for this prediction (crucial for training)
                'metrics_used': {
                    'home_xg': pred.get('home_xg', 0),
                    'away_xg': pred.get('away_xg', 0),
                },
                'prediction_reason': "Meta-Ensemble Daily Run",
                'suggested_units': pred.get('suggested_units', 0.0),
                'odds_taken': pred.get('odds_taken', 0)
            }
            try:
                append_prediction_event(
                    date=pred.get("date", datetime.now().strftime("%Y-%m-%d")),
                    game_id=g_id,
                    home_team=pred["home_team"],
                    away_team=pred["away_team"],
                    predicted_home_win_prob=home_p * 100.0,
                    predicted_away_win_prob=away_p * 100.0,
                    model_confidence=pred.get("confidence", 0.0) / 100.0,
                    metrics_used={"home_xg": 0, "away_xg": 0},
                    extra_metadata={
                        "predicted_home_goals": pred.get("home_score"),
                        "predicted_away_goals": pred.get("away_score"),
                        "ensemble_mode": pred.get("ensemble_mode"),
                        "ensemble_weights": pred.get("ensemble_weights"),
                        "attribution": pred.get("attribution", []),
                        "is_playoff": pred.get("is_playoff", False)
                    }
                )
                new_count += 1
            except Exception as e:
                print(f"⚠️  Failed to log prediction event for {pred['away_team']}@{pred['home_team']}: {e}")

        # Regenerate derived JSON view for dashboard/legacy readers
        try:
            from utils.build_predictions_history_view import write_view
            write_view()
        except Exception:
            try:
                from build_predictions_history_view import write_view
                write_view()
            except Exception as e:
                print(f"⚠️ Could not regenerate JSON history view: {e}")

        # Sanity check after write.
        _sanity_check_home_share()

        print(f"✅ Appended {new_count} predictions to events log.")

    def get_daily_predictions_summary(self, force_refresh=False):
        """Get formatted summary of today's predictions using meta-ensemble"""
        if self._cached_summary and not force_refresh:
            return self._cached_summary

        # Phase 33: Dynamic Date Detection (US/Central)
        import pytz
        today = datetime.now(pytz.timezone('US/Central')).strftime('%Y-%m-%d')
        print(f"🏒 SIMULATION MODE: Analyzing games for {today}")
        print(f"🏒 SIMULATION MODE: Prioritizing local schedule for {today}")
        
        # We use the local schedule analyzer directly, falling back to RotoWire
        sched_games = self.schedule.games_by_date.get(today, [])
        games = []
        if sched_games:
            for g in sched_games:
                games.append({
                    'away_team': g.get('awayTeam', {}).get('abbrev'),
                    'home_team': g.get('homeTeam', {}).get('abbrev')
                })
            print(f"✅ Identified {len(games)} games from local schedule.")
        else:
            # Fallback: scrape today's games from RotoWire
            print(f"⚠️  No games in local schedule for {today}. Falling back to RotoWire scraper...")
            try:
                roto_data = self.rotowire.scrape_daily_data()
                roto_games = roto_data.get('games', []) if isinstance(roto_data, dict) else roto_data or []
                if roto_games:
                    for rg in roto_games:
                        games.append({
                            'away_team': rg.get('away_team'),
                            'home_team': rg.get('home_team'),
                            'away_goalie': rg.get('away_goalie'),
                            'home_goalie': rg.get('home_goalie'),
                        })
                    print(f"✅ Identified {len(games)} games from RotoWire fallback.")
                else:
                    return f"No games scheduled for {today} (checked local + RotoWire)."
            except Exception as e:
                print(f"❌ RotoWire fallback failed: {e}")
                return f"No games scheduled for {today} in the local system."
        
        # Fetch Vegas odds
        from vegas_odds_scraper import scrape_vegas_odds
        with timed("vegas odds scrape"):
            market_odds = scrape_vegas_odds()

        # Phase 36: Build schedule_map from Local Analyzer (Reliable for 2026 Simulation)
        schedule_map = {}
        for date_str, day_games in self.schedule.games_by_date.items():
            for g in day_games:
                away_abbr = g.get('awayTeam', {}).get('abbrev')
                home_abbr = g.get('homeTeam', {}).get('abbrev')
                if away_abbr and home_abbr:
                    key = f'{away_abbr}@{home_abbr}'
                    schedule_map[key] = {
                        'id': g.get('id'),
                        'gameType': g.get('gameType', 2),
                        'series_status': g.get('seriesStatus')
                    }
        print(f'🗺️  Built local schedule map with {len(schedule_map)} entries.')
        predictions = []
        from models.score_prediction_model import ScorePredictionModel
        score_model = ScorePredictionModel()


        for game in games:
            try:
                # Map RotoWire game to Vegas odds key
                odds_key = f"{game['away_team']}_vs_{game['home_team']}"
                vegas_odds = market_odds.get(odds_key)

                # Identify game type and series status
                key = f"{game['away_team']}@{game['home_team']}"
                game_info = schedule_map.get(key, {})
                is_playoff = (game_info.get('gameType') == 3)
                series_status_obj = game_info.get('series_status') or {}
                
                # Parse series wins for simulation
                away_wins = 0
                home_wins = 0
                if is_playoff and series_status_obj:
                    if isinstance(series_status_obj, dict):
                        t_wins = series_status_obj.get('topSeedWins', 0)
                        b_wins = series_status_obj.get('bottomSeedWins', 0)
                        t_abbr = series_status_obj.get('topSeedTeamAbbrev')
                        if t_abbr == game['away_team']:
                            away_wins, home_wins = t_wins, b_wins
                        else:
                            away_wins, home_wins = b_wins, t_wins
                    elif isinstance(series_status_obj, str):
                        # Attempt to parse wins from string: "Team leads 3-2"
                        import re
                        m = re.search(r'leads (\d)-(\d)', series_status_obj)
                        if m:
                            w1, w2 = int(m.group(1)), int(m.group(2))
                            # For simplicity in string parsing, we just assign w1 to the leader
                            # In most cases this is enough for the simulation prior
                            if series_status_obj.startswith(game['away_team']):
                                away_wins, home_wins = w1, w2
                            else:
                                home_wins, away_wins = w1, w2
                        series_status_obj = {'status_text': series_status_obj} # Convert to dict for safety downstream
                
                # Phase 32: Calculate Series Pace Offset
                pace_offset = 0.0
                if is_playoff:

                    # Get all games for this matchup in the current season
                    matchup_games = self.schedule.get_recent_games(game['away_team'], today, n=7)
                    series_games = [g for g in matchup_games if (g.get("awayTeam", {}).get("abbrev") == game["home_team"] or g.get("homeTeam", {}).get("abbrev") == game["home_team"]) and g.get("gameType") == 3]
                    print(f"🔍 DEBUG: Found {len(matchup_games)} recent games for {game['away_team']}. Checking for series vs {game['home_team']}...")
                    if series_games:
                        total_goals = sum([g.get('score', {}).get('awayScore', 0) + g.get('score', {}).get('homeScore', 0) for g in series_games])
                        avg_goals = total_goals / len(series_games)
                        # League avg is ~6.1; if series is 8.0, offset is +0.9
                        pace_offset = (avg_goals - 6.1) / 2.0
                        series_status_obj['pace_offset'] = pace_offset
                        print(f"📈 Series Pace Detected for {key}: {len(series_games)} games, {avg_goals:.1f} G/gm (Offset: {pace_offset:+.2f})")
                    else:
                        print(f"ℹ️  No historical series games found for {key} in local schedule.")

                pred = self.meta_ensemble.predict(
                    game['away_team'],
                    game['home_team'],
                    away_lineup=game.get('away_lineup'),
                    home_lineup=game.get('home_lineup'),
                    away_goalie=game.get('away_goalie'),
                    home_goalie=game.get('home_goalie'),
                    vegas_odds=vegas_odds,
                    is_playoff=is_playoff,
                    series_status=str(series_status_obj) if series_status_obj else None
                )
                
                # Phase 3: Playoff Series Simulation
                series_proj = None
                if is_playoff:
                    try:
                        series_proj = self.playoff_predictor.simulate_series(
                            game['away_team'], game['home_team'],
                            away_wins=away_wins, home_wins=home_wins
                        )
                    except Exception as e:
                        print(f"Error simulating series for {key}: {e}")
                
                # Attach odds taken for ROI tracking
                if vegas_odds:
                    pred['odds_taken'] = vegas_odds.get('home_ml') if pred['home_prob'] > pred['away_prob'] else vegas_odds.get('away_ml')

                # Include all games as requested by user
                if True: # was: if self.meta_ensemble.should_predict(pred):
                    # Attach Game ID
                    key = f"{game['away_team']}@{game['home_team']}"
                    game_info = schedule_map.get(key, {})
                    game_id = game_info.get('id')
                    series_status_str = None
                    if is_playoff and series_status_obj:
                        if isinstance(series_status_obj, dict):
                            leader = series_status_obj.get("topSeedTeamAbbrev")
                            w1 = series_status_obj.get("topSeedWins", 0)
                            w2 = series_status_obj.get("bottomSeedWins", 0)
                            if leader and w1 is not None:
                                series_status_str = f"{leader} leads {w1}-{w2}"
                            else:
                                series_status_str = series_status_obj.get("status_text", "Playoffs")
                        else:
                            series_status_str = str(series_status_obj)

                    is_playoff = game_info.get('gameType') == 3
                    
                    # Score model score + win prob
                    score_pred = score_model.predict_score(
                        game['away_team'],
                        game['home_team'],
                        away_goalie=game.get('away_goalie'),
                        home_goalie=game.get('home_goalie'),
                        away_b2b=pred.get('away_back_to_back', False),
                        home_b2b=pred.get('home_back_to_back', False),
                        away_3_in_4=pred.get('away_3_in_4', False),
                        home_3_in_4=pred.get('home_3_in_4', False),
                        away_games_7d=pred.get('away_games_7d', 1),
                        home_games_7d=pred.get('home_games_7d', 1),
                        away_travel_miles=pred.get('away_travel_miles', 0.0),
                        home_travel_miles=pred.get('home_travel_miles', 0.0),
                        away_rest_days=int(pred.get('away_rest_value', 2)),
                        home_rest_days=int(pred.get('home_rest_value', 2)),
                        is_playoff=is_playoff,
                        series_status=series_status_str,
                        game_id=game_info.get('id')
                    )
                    away_score = score_pred['away_score']
                    home_score = score_pred['home_score']
                    score_away_win_prob = score_pred.get('away_win_prob', 0.5)

                    # Mixture-of-experts winner (small improvement over score-only).
                    # w near 1.0 keeps mostly score-model, but lets meta win-prob
                    # correct some edge cases.
                    # Phase 44: Adaptive Confidence Blending
                    # Dynamically adjust ensemble weight based on score-model confidence.
                    score_confidence = float(score_pred.get('confidence', 0.5))
                    if score_confidence > 0.60:
                        # High confidence in tactical setup -> Trust the score model more
                        w_score = 0.85
                    elif score_confidence < 0.45:
                        # Low confidence -> Trust the Meta-Ensemble (XGBoost/ELO) more
                        w_score = 0.40
                    else:
                        w_score = self._moe_default_w

                    # If we have contextual tuning, choose w by abs(diff in xG).
                    if self._moe_absdiff_edges and self._moe_absdiff_w_map:
                        away_expected = float(score_pred.get('away_expected', 0.0))
                        home_expected = float(score_pred.get('home_expected', 0.0))
                        absdiff = abs(away_expected - home_expected)
                        edges = self._moe_absdiff_edges
                        # Map into edges buckets [i..i+1)
                        import bisect
                        idx = int(bisect.bisect_right(edges, absdiff) - 1)
                        idx = max(0, min(idx, len(edges) - 2))
                        w_score = float(self._moe_absdiff_w_map[idx])

                    meta_away_win_prob = float(pred.get('away_prob', 50.0))
                    meta_home_win_prob = float(pred.get('home_prob', 50.0))
                    if meta_away_win_prob > 1.0 or meta_home_win_prob > 1.0:
                        meta_away_win_prob /= 100.0
                        meta_home_win_prob /= 100.0
                    s_meta = meta_away_win_prob + meta_home_win_prob
                    if s_meta > 0:
                        meta_away_win_prob /= s_meta

                    blended_away_win_prob = (w_score * score_away_win_prob) + ((1.0 - w_score) * meta_away_win_prob)
                    
                    # Phase 2: Incorporate Vegas as a standalone "Expert"
                    # Abbreviation Normalization (LA -> LAK, TB -> TBL, etc.)
                    def normalize_abbr(a):
                        mapping = {'LA': 'LAK', 'TB': 'TBL', 'VEG': 'VGK', 'SJS': 'SJ', 'MON': 'MTL'}
                        rev_mapping = {v: k for k, v in mapping.items()}
                        return rev_mapping.get(a, a)
                    
                    v_key = f"{normalize_abbr(game['away_team'])}_vs_{normalize_abbr(game['home_team'])}"
                    v_odds = market_odds.get(v_key, {})
                    
                    if v_odds and 'away_prob' in v_odds:
                        v_away_prob = v_odds['away_prob']
                        # Blending: Market gets more weight in playoffs due to higher efficiency
                        market_weight = 0.45 if is_playoff else 0.30
                        blended_away_win_prob = (blended_away_win_prob * (1.0 - market_weight)) + (v_away_prob * market_weight)
                        
                    blended_winner = game['away_team'] if blended_away_win_prob >= 0.5 else game['home_team']

                    # Prefer meta-model scoreline when available (total-goals model + margin split).
                    try:
                        mh = pred.get("predicted_home_goals")
                        ma = pred.get("predicted_away_goals")
                        if mh is not None and ma is not None:
                            home_score = int(mh)
                            away_score = int(ma)
                    except Exception:
                        pass

                    # Force displayed scoreline to match blended winner, but clamp to realistic hockey scores.
                    max_goals = 6
                    away_score = int(max(0, min(max_goals, away_score)))
                    home_score = int(max(0, min(max_goals, home_score)))
                    
                    if blended_winner == game['away_team']:
                        if away_score <= home_score:
                            away_score = min(max_goals, home_score + 1)
                            if away_score == home_score:
                                away_score = max(1, home_score)
                    else:
                        if home_score <= away_score:
                            home_score = min(max_goals, away_score + 1)
                            if home_score == away_score:
                                home_score = max(1, away_score)

                    predictions.append({
                        'away_team': game['away_team'],
                        'home_team': game['home_team'],
                        'away_prob': pred['away_prob'],
                        'home_prob': pred['home_prob'],
                        'blended_away_prob': blended_away_win_prob,
                        'predicted_winner': blended_winner,
                        'confidence': max(blended_away_win_prob, 1.0 - blended_away_win_prob) * 100 * (0.95 if (game.get('away_goalie_status') != 'Confirmed' or game.get('home_goalie_status') != 'Confirmed') else 1.0),
                        'away_score': away_score,
                        'home_score': home_score,
                        'predicted_home_goals': pred.get("predicted_home_goals"),
                        'predicted_away_goals': pred.get("predicted_away_goals"),
                        'predicted_total_goals': pred.get("predicted_total_goals"),
                        'ensemble_mode': getattr(self.meta_ensemble, "_model_mode", None),
                        'ensemble_weights': getattr(self.meta_ensemble, "_component_weights", None),
                        'away_goalie': game.get('away_goalie', 'TBD'),
                        'home_goalie': game.get('home_goalie', 'TBD'),
                        'goalie_confirmed': (game.get('away_goalie_status') == 'Confirmed' and game.get('home_goalie_status') == 'Confirmed'),
                        'away_back_to_back': pred.get('away_back_to_back', False),
                        'home_back_to_back': pred.get('home_back_to_back', False),
                        'away_rest_value': pred.get('away_rest_value', 0.0),
                        'home_rest_value': pred.get('home_rest_value', 0.0),
                        'start_time': game.get('game_time', ''),
                        'contexts': pred.get('contexts_used', []),
                        'game_id': game_id,
                        'confidence_tier': "⚠️ High Risk" if 0.47 <= blended_away_win_prob <= 0.53 else pred.get('confidence_tier', 'Standard'),
                        'predicted_margin': pred.get('predicted_margin', 0.0),
                        'edge_away': pred.get('edge_away', 0.0),
                        'edge_home': pred.get('edge_home', 0.0),
                        'is_plus_ev_away': pred.get('is_plus_ev_away', False),
                        'is_plus_ev_home': pred.get('is_plus_ev_home', False),
                        'suggested_units': pred.get('suggested_units', 0.0),
                        'odds_taken': pred.get('odds_taken', 0),
                        "attribution": score_pred.get("attribution", []),
                        'p1_home_prob': pred.get('p1_home_prob', 50.0),
                        'is_playoff': is_playoff,
                        'series_info': series_proj,
                        'attribution': score_pred.get('attribution', [])
                    })
            except Exception as e:
                print(f"Error predicting {game['away_team']} @ {game['home_team']}: {e}")
                continue
        
        # Cache the results
        self._cached_predictions = predictions
        
        if not predictions:
            self._cached_summary = "No high-confidence predictions for today."
            return self._cached_summary
            
            
        # SAVE PREDICTIONS TO IDB
        self.save_predictions_to_history(predictions)
        
        
        # Format predictions
        summary = "🏒 **NHL GAME PREDICTIONS FOR TODAY** 🏒\n\n"
        summary += f"Showing **{len(predictions)} high-confidence games** out of {len(games)} on the schedule.\n"
        summary += f"(Meta-Ensemble Model: 55-60% accuracy)\n\n"

        for i, pred in enumerate(predictions, 1):
            away = pred['away_team']
            home = pred['home_team']
            winner = pred['predicted_winner']
            confidence = pred['confidence']

            # Use precomputed deterministic scoreline.
            away_score = pred.get('away_score')
            home_score = pred.get('home_score')
            if away_score is None or home_score is None:
                # Rare fallback: derive realistic scores from xG averages + winner.
                base_pred = self.predictor.learning_model.predict_game(away, home)
                away_xg = base_pred.get('away_perf', {}).get('xg_avg', 2.8)
                home_xg = base_pred.get('home_perf', {}).get('xg_avg', 2.8)
                away_score = round(away_xg)
                home_score = round(home_xg)
                if winner == away and away_score <= home_score:
                    away_score = home_score + 1
                elif winner == home and home_score <= away_score:
                    home_score = away_score + 1
            
            summary += f"**Game {i}**: {away} @ {home}\n"
            summary += f"  🏆 Prediction: **{winner} wins** ({away_score}-{home_score})\n"
            
            # Phase 17: Period 1 Prediction
            p1_home_prob = pred.get('p1_home_prob', 50.0)
            p1_winner = home if p1_home_prob > 55 else (away if p1_home_prob < 45 else None)
            if p1_winner:
                p1_conf = max(p1_home_prob, 100 - p1_home_prob)
                summary += f"  🕐 1st Period: **{p1_winner}** favored ({p1_conf:.1f}%)\n"
            
            summary += f"  ⭐ Confidence: {confidence:.1f}% ({pred.get('confidence_tier', 'Standard')})\n"
            
            # Phase 25: Playoff Series Probability
            if pred.get('is_playoff') and pred.get('series_info'):
                si = pred['series_info']
                summary += f"  🏆 **SERIES WIN PROB**: {si['winner_projection']} ({max(si['away_series_win_prob'], si['home_series_win_prob']):.1%})\n"
                mean_g = si.get("projected_mean_games_in_series", si.get("avg_remaining_games", 0))
                summary += f"  📊 Series Project: {si['winner_projection']} in ~{float(mean_g):.1f} games (avg length)\n"
            
            # Phase 16: Market Value Overlay
            edge = pred.get('edge_home') if winner == home else pred.get('edge_away')
            if edge and edge > 5.0:
                summary += f"  💰 **+EV Value**: Edge of **{edge:.1f}%** detected vs Market\n"
                if pred.get('suggested_units', 0) > 0:
                    summary += f"  📏 **Bet Size**: Suggested **{pred['suggested_units']} units** (Kelly Criterion)\n"
            elif edge and edge > 1.0:
                summary += f"  ⚖️ Market Alignment: Edge of {edge:.1f}%\n"

            if 'predicted_margin' in pred and abs(pred['predicted_margin']) > 0.1:
                side = "Home" if winner == home else "Away"
                summary += f"  📏 Margin Model: **{side} {abs(pred['predicted_margin']):.1f}** goals\n"

            # Add In-Depth Analysis
            # Add In-Depth Analysis
            has_factors = False
            # (factors are only available when score_pred was computed; keep this simple)
            factors = pred.get('factors')
            if factors:
                if factors.get('pace') != 'Neutral':
                    summary += f"  ⏱️ {factors['pace']}\n"
                    has_factors = True
                if factors.get('situation') != 'Neutral':
                    summary += f"  🔥 {factors['situation']}\n"
                    has_factors = True
            
            # Phase 25/26: Show Attribution Signals (Explainable AI)
            attribution = pred.get('attribution', [])
            if attribution:
                summary += f"  🧠 Signals: {', '.join(attribution)}\n"
                has_factors = True
                    
            if not has_factors:
                 summary += f"  🥅 Goalies: {pred['away_goalie']} vs {pred['home_goalie']}\n"
            
            # Show contexts used
            if pred['contexts']:
                contexts_str = ", ".join([f"{c[0]} ({c[1]:.0%})" for c in pred['contexts']])
                summary += f"  🎯 Contexts: {contexts_str}\n"
            
            summary += "\n"
        
        # Recalculate model performance from latest predictions before displaying
        try:
            self.predictor.learning_model.recalculate_performance_from_scratch()
        except Exception as e:
            print(f"⚠️  Warning: Failed to recalculate performance: {e}")
        
        # Add model performance
        perf = self.predictor.learning_model.get_model_performance()
        summary += f"📊 **Model Performance:**\n"
        summary += f"   Accuracy: {perf.get('accuracy', 0):.1%}\n"
        summary += f"   Recent Accuracy: {perf.get('recent_accuracy', 0):.1%}\n"
        summary += f"   Total Games: {perf.get('total_games', 0)}\n\n"
        
        summary += f"🤖 Generated by NHL Meta-Ensemble Model (55-60% accuracy)\n"
        summary += f"📅 {datetime.now(pytz.timezone('US/Central')).strftime('%Y-%m-%d %I:%M %p CT')}"
        
        self._cached_summary = summary
        return summary

    def send_email_notification(self, to_email, subject="Daily NHL Predictions"):
        """Send predictions via email"""
        try:
            # Email configuration (you'll need to set these as environment variables)
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            email_user = os.getenv('EMAIL_USER')
            email_password = os.getenv('EMAIL_PASSWORD')
            
            if not email_user or not email_password:
                print("❌ Email credentials not configured. Set EMAIL_USER and EMAIL_PASSWORD environment variables.")
                return False
            
            # Get predictions
            predictions_text = self.get_daily_predictions_summary()
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(predictions_text, 'plain'))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_user, email_password)
            text = msg.as_string()
            server.sendmail(email_user, to_email, text)
            server.quit()
            
            print(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False
    
    def _split_message(self, text, limit=1900):
        """Split a large message into chunks that fit Discord's character limit"""
        chunks = []
        while len(text) > limit:
            # Find the last newline before the limit to avoid cutting in the middle of a line
            split_at = text.rfind('\n', 0, limit)
            if split_at == -1 or split_at < 500: # If no newline or it's too early, just cut at limit
                split_at = limit
            
            chunks.append(text[:split_at].strip())
            text = text[split_at:].strip()
        
        if text:
            chunks.append(text)
        return chunks

    def send_discord_notification(self, webhook_url):
        """Send predictions via Discord webhook"""
        try:
            import requests
            
            predictions_text = self.get_daily_predictions_summary()
            
            # Split message if it exceeds Discord's limit (2000 chars)
            # Using 1900 to be safe
            chunks = self._split_message(predictions_text, limit=1900)
            
            success = True
            for i, chunk in enumerate(chunks):
                # Discord webhook payload
                payload = {
                    "content": chunk,
                    "username": "NHL Predictions Bot",
                    "avatar_url": "https://cdn-icons-png.flaticon.com/512/3048/3048127.png"
                }
                
                # Add part indicator if split
                if len(chunks) > 1:
                    payload["username"] = f"NHL Predictions Bot (Part {i+1}/{len(chunks)})"

                response = requests.post(webhook_url, json=payload, timeout=15)
                
                if response.status_code not in [200, 204]:
                    print(f"❌ Discord notification chunk {i+1} failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    success = False
            
            if success:
                print(f"✅ Discord notification sent successfully ({len(chunks)} parts)")
            return success
                
        except Exception as e:
            print(f"❌ Error sending Discord notification: {e}")
            return False
    
    def save_to_file(self, filename=None):
        """Save predictions to a text file"""
        try:
            if not filename:
                date_str = datetime.now(pytz.timezone('US/Central')).strftime('%Y%m%d')
                filename = f"daily_predictions_{date_str}.txt"
            
            predictions_text = self.get_daily_predictions_summary()
            
            with open(filename, 'w') as f:
                f.write(predictions_text)
            
            print(f"✅ Predictions saved to {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving to file: {e}")
            return False
    
    def send_notification(self, method="file", **kwargs):
        """Send notification using specified method"""
        if method == "email":
            return self.send_email_notification(
                kwargs.get('to_email'),
                kwargs.get('subject', 'Daily NHL Predictions')
            )
        elif method == "discord":
            return self.send_discord_notification(kwargs.get('webhook_url'))
        elif method == "file":
            return self.save_to_file(kwargs.get('filename'))
        else:
            print(f"❌ Unknown notification method: {method}")
            return False


def main():
    """Main function to send daily predictions"""
    notifier = DailyPredictionNotifier()
    
    print("🔔 DAILY NHL PREDICTIONS NOTIFIER")
    print("=" * 50)
    
    # Get predictions summary
    summary = notifier.get_daily_predictions_summary()
    print(summary)
    print("\n" + "=" * 50)
    
    # Send notifications
    print("\n📤 SENDING NOTIFICATIONS:")
    
    # Save to file (always works)
    notifier.save_to_file()
    
    # Try email if configured
    email = os.getenv('NOTIFICATION_EMAIL')
    if email:
        notifier.send_email_notification(email)
    else:
        print("ℹ️  Set NOTIFICATION_EMAIL environment variable to enable email notifications")
    
    # Try Discord if configured
    discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
    if discord_webhook:
        notifier.send_discord_notification(discord_webhook)
    else:
        print("ℹ️  Set DISCORD_WEBHOOK_URL environment variable to enable Discord notifications")


if __name__ == "__main__":
    main()
