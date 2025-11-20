
// Advanced Metrics Utility
// Ported from Python implementation for NHL Analytics

// Constants for xG calculation
const SHOT_TYPE_MULTIPLIERS = {
    'snap': 1.137,
    'snap-shot': 1.137,
    'slap': 1.168,
    'slap-shot': 1.168,
    'slapshot': 1.168,
    'wrist': 0.865,
    'wrist-shot': 0.865,
    'tip-in': 0.697,
    'tip': 0.697,
    'deflected': 0.683,
    'deflection': 0.683,
    'backhand': 0.657,
    'wrap-around': 0.356,
    'wrap': 0.356,
};

// Post-game correlation weights for Win Probability
const POSTGAME_WEIGHTS = {
    'gs_diff': 0.6504,
    'power_play_diff': 0.3933,
    'corsi_diff': -0.3598,
    'hits_diff': -0.2434,
    'hdc_diff': 0.0747,
    'xg_diff': -0.0545,
    'pim_diff': 0.0173,
    'shots_diff': -0.0158,
};

/**
 * Calculate Expected Goals (xG) for a single shot
 * @param {Object} shotDetails - Details from the play event
 * @param {string} shotType - Type of shot
 * @returns {number} xG value
 */
export const calculateShotXG = (shotDetails, shotType = 'wrist') => {
    try {
        const x = shotDetails.xCoord || 0;
        const y = shotDetails.yCoord || 0;
        const type = (shotType || 'wrist').toLowerCase();

        // Calculate distance and angle
        const distance = Math.sqrt(x * x + y * y);
        const angle = Math.abs(y) / Math.max(Math.abs(x), 1);

        // Baseline xG based on distance
        let baseXG = 0.02;
        if (distance < 20) baseXG = 0.15;
        else if (distance < 35) baseXG = 0.08;
        else if (distance < 50) baseXG = 0.04;

        // Apply shot type multiplier
        const shotMultiplier = SHOT_TYPE_MULTIPLIERS[type] || 0.865;

        // Apply angle adjustment
        let angleMultiplier = 0.8;
        if (angle < 0.3) angleMultiplier = 1.2;
        else if (angle < 0.6) angleMultiplier = 1.0;

        const finalXG = baseXG * shotMultiplier * angleMultiplier;
        return Math.min(finalXG, 0.95);
    } catch (error) {
        console.error('Error calculating shot xG:', error);
        return 0.05;
    }
};

/**
 * Calculate Game Score for a single play
 * @param {Object} play - The play event
 * @returns {number} Game Score contribution
 */
export const calculatePlayGameScore = (play) => {
    const eventType = play.typeDescKey;

    switch (eventType) {
        case 'goal': return 0.75;
        case 'shot-on-goal': return 0.075;
        case 'blocked-shot': return 0.05;
        case 'penalty': return -0.15;
        case 'penalty-drawn': return 0.15;
        case 'takeaway': return 0.15;
        case 'giveaway': return -0.15;
        case 'hit': return 0.15;
        default: return 0.0;
    }
};

/**
 * Calculate Win Probability based on game stats
 * @param {Object} gameData - Combined boxscore and play-by-play data
 * @returns {Object} Win probability for away and home teams
 */
export const calculateWinProbability = (gameData) => {
    try {
        const { boxscore, playByPlay } = gameData;
        const awayTeam = boxscore.awayTeam;
        const homeTeam = boxscore.homeTeam;

        // Calculate basic stats
        const awaySog = awayTeam.sog || 0;
        const homeSog = homeTeam.sog || 0;

        // Calculate advanced stats from play-by-play
        let awayXG = 0, homeXG = 0;
        let awayHDC = 0, homeHDC = 0;
        let awayGS = 0, homeGS = 0;
        let awayCorsi = 0, homeCorsi = 0;
        let awayHits = 0, homeHits = 0;
        let awayPIM = 0, homePIM = 0;

        if (playByPlay && playByPlay.plays) {
            playByPlay.plays.forEach(play => {
                const teamId = play.details?.eventOwnerTeamId;
                const type = play.typeDescKey;

                // Game Score & xG
                const gs = calculatePlayGameScore(play);

                if (teamId === awayTeam.id) {
                    awayGS += gs;
                    if (type === 'hit') awayHits++;
                    if (type === 'penalty') awayPIM += (play.details.duration || 2);
                } else if (teamId === homeTeam.id) {
                    homeGS += gs;
                    if (type === 'hit') homeHits++;
                    if (type === 'penalty') homePIM += (play.details.duration || 2);
                }

                // xG & HDC
                if (['shot-on-goal', 'goal', 'missed-shot', 'blocked-shot'].includes(type)) {
                    // Corsi
                    if (teamId === awayTeam.id) awayCorsi++;
                    else if (teamId === homeTeam.id) homeCorsi++;

                    // xG
                    if (['shot-on-goal', 'goal', 'missed-shot'].includes(type)) {
                        const xg = calculateShotXG(play.details, play.details?.shotType);
                        if (teamId === awayTeam.id) awayXG += xg;
                        else if (teamId === homeTeam.id) homeXG += xg;

                        // HDC (High Danger Chance)
                        const x = play.details?.xCoord || 0;
                        const y = play.details?.yCoord || 0;
                        if (Math.abs(x) > 75 && Math.abs(y) < 20) {
                            if (teamId === awayTeam.id) awayHDC++;
                            else if (teamId === homeTeam.id) homeHDC++;
                        }
                    }
                }
            });
        }

        // Calculate percentages
        const totalCorsi = awayCorsi + homeCorsi;
        const awayCorsiPct = totalCorsi > 0 ? (awayCorsi / totalCorsi) * 100 : 50;
        const homeCorsiPct = totalCorsi > 0 ? (homeCorsi / totalCorsi) * 100 : 50;

        // Power Play (simplified from boxscore if available, else estimated)
        // Note: Boxscore usually has this, but we'll use a simplified diff for now
        // Assuming boxscore has powerPlayConversion string "X/Y"
        const getPP = (str) => {
            if (!str) return 0;
            const [goals, attempts] = str.split('/').map(Number);
            return attempts > 0 ? (goals / attempts) * 100 : 0;
        };

        // Try to get PP from boxscore team stats if available, otherwise default to 0
        // The structure might vary, so we'll be safe
        const awayPP = 0; // Placeholder - would need deep parsing of boxscore stats
        const homePP = 0;

        // Calculate differences (Away - Home)
        const gsDiff = awayGS - homeGS;
        const xgDiff = awayXG - homeXG;
        const hdcDiff = awayHDC - homeHDC;
        const shotsDiff = awaySog - homeSog;
        const corsiDiff = awayCorsiPct - homeCorsiPct;
        const ppDiff = awayPP - homePP;
        const hitsDiff = awayHits - homeHits;
        const pimDiff = awayPIM - homePIM;

        // Calculate Score
        let score = 0;
        score += POSTGAME_WEIGHTS.gs_diff * (gsDiff * 0.1);
        score += POSTGAME_WEIGHTS.power_play_diff * (ppDiff * 0.01);
        score += POSTGAME_WEIGHTS.corsi_diff * (corsiDiff * 0.01);
        score += POSTGAME_WEIGHTS.hits_diff * (hitsDiff * 0.01);
        score += POSTGAME_WEIGHTS.hdc_diff * (hdcDiff * 0.05);
        score += POSTGAME_WEIGHTS.xg_diff * (xgDiff * 0.2);
        score += POSTGAME_WEIGHTS.pim_diff * (pimDiff * 0.01);
        score += POSTGAME_WEIGHTS.shots_diff * (shotsDiff * 0.02);

        // Sigmoid function
        const sigmoid = (x) => 1 / (1 + Math.exp(-x));

        const awayProb = sigmoid(score) * 100;
        const homeProb = (1 - sigmoid(score)) * 100;

        return {
            away: {
                probability: awayProb.toFixed(1),
                xg: awayXG.toFixed(2),
                gs: awayGS.toFixed(1),
                hdc: awayHDC,
                corsi: awayCorsiPct.toFixed(1)
            },
            home: {
                probability: homeProb.toFixed(1),
                xg: homeXG.toFixed(2),
                gs: homeGS.toFixed(1),
                hdc: homeHDC,
                corsi: homeCorsiPct.toFixed(1)
            }
        };

    } catch (error) {
        console.error('Error calculating win probability:', error);
        return {
            away: { probability: 50, xg: 0, gs: 0, hdc: 0, corsi: 50 },
            home: { probability: 50, xg: 0, gs: 0, hdc: 0, corsi: 50 }
        };
    }
};

/**
 * Process game data for period-by-period breakdown
 * @param {Object} gameData 
 */
export const processPeriodStats = (gameData) => {
    const { boxscore, playByPlay } = gameData;
    const periods = [1, 2, 3, 4, 5]; // 1-3, OT, SO
    const stats = {
        away: {},
        home: {}
    };

    // Initialize period stats
    periods.forEach(p => {
        stats.away[p] = { goals: 0, shots: 0, xg: 0, corsi: 0 };
        stats.home[p] = { goals: 0, shots: 0, xg: 0, corsi: 0 };
    });

    if (playByPlay && playByPlay.plays) {
        playByPlay.plays.forEach(play => {
            const period = play.periodDescriptor?.number;
            if (!period || period > 5) return;

            const teamId = play.details?.eventOwnerTeamId;
            const type = play.typeDescKey;
            const isAway = teamId === boxscore.awayTeam.id;
            const isHome = teamId === boxscore.homeTeam.id;

            if (!isAway && !isHome) return;

            const teamStats = isAway ? stats.away[period] : stats.home[period];

            if (type === 'goal') teamStats.goals++;
            if (type === 'shot-on-goal') teamStats.shots++;

            if (['shot-on-goal', 'goal', 'missed-shot', 'blocked-shot'].includes(type)) {
                teamStats.corsi++;
                if (['shot-on-goal', 'goal', 'missed-shot'].includes(type)) {
                    teamStats.xg += calculateShotXG(play.details, play.details?.shotType);
                }
            }
        });
    }

    return stats;
};

/**
 * Calculate advanced team metrics from recent games
 * @param {string} teamAbbrev - Team abbreviation
 * @param {Array} recentGames - Array of recent game IDs
 * @param {Function} fetchGameCenter - Function to fetch game data
 * @returns {Object} Advanced metrics for the team
 */
export const calculateTeamSeasonMetrics = async (teamAbbrev, recentGames, fetchGameCenter) => {
    const metrics = {
        gs: 0,
        nzts: 0,
        ozs: 0,
        nzs: 0,
        dzs: 0,
        fc: 0,
        rush: 0,
        gamesProcessed: 0
    };

    try {
        // Process up to 10 most recent games
        const gamesToProcess = recentGames.slice(0, 10);

        for (const gameId of gamesToProcess) {
            try {
                const gameData = await fetchGameCenter(gameId);
                const { boxscore, playByPlay } = gameData;

                if (!playByPlay || !playByPlay.plays) continue;

                // Determine if team is away or home
                const isAway = boxscore.awayTeam.abbrev === teamAbbrev;
                const teamId = isAway ? boxscore.awayTeam.id : boxscore.homeTeam.id;

                // Process each play
                playByPlay.plays.forEach(play => {
                    const eventTeamId = play.details?.eventOwnerTeamId;
                    if (eventTeamId !== teamId) return;

                    const type = play.typeDescKey;
                    const x = play.details?.xCoord || 0;
                    const y = play.details?.yCoord || 0;

                    // Game Score
                    metrics.gs += calculatePlayGameScore(play);

                    // Zone-based shot tracking
                    if (['shot-on-goal', 'goal'].includes(type)) {
                        // Determine zone (simplified)
                        if (Math.abs(x) > 75) metrics.ozs++;
                        else if (Math.abs(x) > 25) metrics.nzs++;
                        else metrics.dzs++;

                        // Rush vs Forecheck/Cycle (simplified heuristic)
                        // In a real implementation, we'd look at previous plays
                        // For now, use distance as proxy: far shots = rush, close = cycle
                        const distance = Math.sqrt(x * x + y * y);
                        if (distance > 60) metrics.rush++;
                        else metrics.fc++;
                    }

                    // Neutral zone turnovers to shots (simplified)
                    if (type === 'giveaway' && Math.abs(x) < 25) {
                        metrics.nzts++;
                    }
                });

                metrics.gamesProcessed++;
            } catch (error) {
                console.error(`Error processing game ${gameId}:`, error);
            }
        }

        // Average per game
        if (metrics.gamesProcessed > 0) {
            metrics.gs = (metrics.gs / metrics.gamesProcessed).toFixed(1);
            metrics.nzts = Math.round(metrics.nzts / metrics.gamesProcessed);
            metrics.ozs = Math.round(metrics.ozs / metrics.gamesProcessed);
            metrics.nzs = Math.round(metrics.nzs / metrics.gamesProcessed);
            metrics.dzs = Math.round(metrics.dzs / metrics.gamesProcessed);
            metrics.fc = Math.round(metrics.fc / metrics.gamesProcessed);
            metrics.rush = Math.round(metrics.rush / metrics.gamesProcessed);
        }

    } catch (error) {
        console.error('Error calculating team season metrics:', error);
    }

    return metrics;
};

/**
 * Calculate advanced metrics for all teams
 * @param {Array} standings - Standings data
 * @param {Function} fetchSchedule - Function to fetch schedule
 * @param {Function} fetchGameCenter - Function to fetch game data
 * @returns {Object} Map of team abbrev to advanced metrics
 */
export const calculateAllTeamsMetrics = async (standings, fetchSchedule, fetchGameCenter) => {
    const metricsMap = {};

    try {
        // Get recent dates (last 14 days)
        const dates = [];
        for (let i = 0; i < 14; i++) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            dates.push(date.toISOString().split('T')[0]);
        }

        // Fetch all schedules
        const schedules = await Promise.all(
            dates.map(date => fetchSchedule(date).catch(() => ({ gameWeek: [] })))
        );

        // Build game history for each team
        const teamGames = {};
        schedules.forEach(schedule => {
            if (!schedule.gameWeek || !schedule.gameWeek[0]) return;

            schedule.gameWeek[0].games?.forEach(game => {
                if (game.gameState !== 'OFF') return; // Only completed games

                const awayAbbrev = game.awayTeam.abbrev;
                const homeAbbrev = game.homeTeam.abbrev;

                if (!teamGames[awayAbbrev]) teamGames[awayAbbrev] = [];
                if (!teamGames[homeAbbrev]) teamGames[homeAbbrev] = [];

                teamGames[awayAbbrev].push(game.id);
                teamGames[homeAbbrev].push(game.id);
            });
        });

        // Calculate metrics for each team (process in batches to avoid overwhelming the API)
        const teams = standings.map(t => t.teamAbbrev.default);

        for (const teamAbbrev of teams) {
            const recentGames = teamGames[teamAbbrev] || [];
            metricsMap[teamAbbrev] = await calculateTeamSeasonMetrics(
                teamAbbrev,
                recentGames,
                fetchGameCenter
            );

            // Small delay to avoid rate limiting
            await new Promise(resolve => setTimeout(resolve, 100));
        }

    } catch (error) {
        console.error('Error calculating all teams metrics:', error);
    }

    return metricsMap;
};
