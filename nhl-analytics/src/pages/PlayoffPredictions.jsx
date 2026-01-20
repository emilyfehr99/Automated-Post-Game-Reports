import React, { useEffect, useState, useMemo } from 'react';
import { nhlApi } from '../api/nhl';
import { backendApi } from '../api/backend';
import { motion } from 'framer-motion';
import { Trophy, TrendingUp, TrendingDown, Minus, Activity } from 'lucide-react';
import clsx from 'clsx';

const PlayoffPredictions = () => {
    // State management
    const [divisions, setDivisions] = useState({});
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Fetch standings and backend predictions concurrently
                const [standingsResult, predictionsResult] = await Promise.allSettled([
                    nhlApi.getStandings(new Date().toISOString().split('T')[0]),
                    backendApi.getPlayoffPredictions() // New API call
                ]);

                const standingsData = standingsResult.status === 'fulfilled' ? standingsResult.value.standings : [];
                const predictionsData = predictionsResult.status === 'fulfilled' ? predictionsResult.value : [];

                // Map predictions for easy lookup
                const predictionsMap = {};
                if (Array.isArray(predictionsData)) {
                    predictionsData.forEach(p => {
                        predictionsMap[p.teamAbbrev] = p;
                    });
                }

                // Process data into divisions
                const processedDivisions = {};

                standingsData.forEach(team => {
                    const division = team.divisionName || 'Unknown';
                    const abbr = team.teamAbbrev?.default;
                    if (!processedDivisions[division]) processedDivisions[division] = [];

                    // Get prediction from backend or fallback logic if missing (e.g. during dev/failed fetch)
                    const backendPrediction = predictionsMap[abbr];
                    let playoffProb = 0;

                    if (backendPrediction) {
                        playoffProb = backendPrediction.playoffProb;
                    } else {
                        // Maintain fallback logic just in case backend is empty
                        // Base probability from standings (50% weight)
                        const divisionRank = processedDivisions[division].length + 1; // Approx rank
                        const pointsPct = team.pointPctg || 0;
                        let standingsProb = 0;

                        if (divisionRank <= 3) {
                            standingsProb = 70 + (pointsPct * 25);
                        } else if (divisionRank <= 6) {
                            standingsProb = 30 + (pointsPct * 40);
                        } else if (divisionRank <= 8) {
                            standingsProb = 10 + (pointsPct * 20);
                        } else {
                            standingsProb = 1 + (pointsPct * 14);
                        }

                        // Recent form (20% weight)
                        const wins = team.l10Wins || 0;
                        const formProb = (wins / 10) * 100;

                        // Simple weighted sum
                        playoffProb = Math.round((standingsProb * 0.7) + (formProb * 0.3));
                        playoffProb = Math.max(1, Math.min(95, playoffProb));
                    }

                    // Determine trend
                    const l10Wins = team.l10Wins || 0;
                    const trend = l10Wins >= 7 ? 'up' : l10Wins <= 3 ? 'down' : 'neutral';

                    processedDivisions[division].push({
                        ...team,
                        playoffProb,
                        trend,
                        metrics: backendPrediction?.metrics || {}
                    });
                });

                // Sort teams within divisions by points (standard standings order)
                Object.keys(processedDivisions).forEach(div => {
                    processedDivisions[div].sort((a, b) => b.points - a.points);
                });

                setDivisions(processedDivisions);
            } catch (error) {
                console.error('Error fetching playoff data:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-[60vh]">
                <div className="relative">
                    <div className="h-16 w-16 rounded-full border-t-2 border-b-2 border-accent-primary animate-spin"></div>
                    <div className="absolute inset-0 h-16 w-16 rounded-full border-r-2 border-l-2 border-accent-secondary animate-spin-reverse opacity-50"></div>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-12 pb-12">
            {/* Header */}
            <div className="relative rounded-3xl overflow-hidden bg-gradient-to-r from-bg-secondary to-bg-primary border border-white/5 p-8 md:p-12 shadow-2xl">
                <div className="absolute top-0 right-0 w-96 h-96 bg-accent-primary/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3"></div>

                <div className="relative z-10">
                    <h1 className="text-5xl md:text-7xl font-display font-black text-white tracking-tighter mb-4">
                        PLAYOFF <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent-primary to-accent-secondary">RACE</span>
                    </h1>
                    <p className="text-text-muted font-mono text-lg max-w-2xl">
                        AI-powered playoff probability predictions combining standings, recent form, and advanced analytics.
                    </p>
                </div>
            </div>

            {/* Divisions */}
            {Object.entries(divisions).map(([division, teams], divIndex) => (
                <motion.div
                    key={division}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: divIndex * 0.1 }}
                    className="space-y-6"
                >
                    <div className="flex items-center gap-3">
                        <Trophy className="w-6 h-6 text-accent-primary" />
                        <h2 className="text-2xl font-display font-bold text-white tracking-wide">
                            {division.toUpperCase()}
                        </h2>
                        <div className="h-px flex-1 bg-gradient-to-r from-white/10 to-transparent" />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {teams.map((team, index) => {
                            const probColor = team.playoffProb > 70 ? 'text-success' :
                                team.playoffProb > 40 ? 'text-warning' :
                                    'text-danger';

                            const TrendIcon = team.trend === 'up' ? TrendingUp :
                                team.trend === 'down' ? TrendingDown :
                                    Minus;

                            const trendColor = team.trend === 'up' ? 'text-success' :
                                team.trend === 'down' ? 'text-red-500' :
                                    'text-text-muted';

                            return (
                                <motion.div
                                    key={team.teamAbbrev?.default}
                                    initial={{ opacity: 0, scale: 0.9 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ delay: divIndex * 0.1 + index * 0.05 }}
                                    className={clsx(
                                        "glass-card p-6 rounded-xl relative group hover:border-accent-primary/30 transition-all duration-300",
                                        team.playoffProb > 80 && "border-success/30 bg-success/5"
                                    )}
                                >
                                    {/* Team Header */}
                                    <div className="flex items-center gap-4 mb-6">
                                        <img
                                            src={team.teamLogo}
                                            alt={team.teamName?.default}
                                            className="w-16 h-16 object-contain drop-shadow-lg group-hover:scale-110 transition-transform"
                                        />
                                        <div className="flex-1 min-w-0">
                                            <h3 className="font-display font-bold text-white text-lg truncate">{team.teamName?.default}</h3>
                                            <div className="flex items-center gap-2 mt-1">
                                                <span className="px-2 py-0.5 rounded bg-white/5 text-xs font-mono text-text-muted">
                                                    {team.wins}-{team.losses}-{team.otLosses}
                                                </span>
                                                <span className="text-xs font-mono text-accent-primary">
                                                    {team.points} PTS
                                                </span>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Playoff Probability */}
                                    <div className="text-center mb-6 relative">
                                        <div className="absolute inset-0 bg-white/5 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
                                        <div className={clsx("text-5xl font-display font-bold relative z-10", probColor)}>
                                            {team.playoffProb}%
                                        </div>
                                        <div className="text-xs text-text-muted font-mono uppercase tracking-wider mt-1">
                                            Playoff Chance
                                        </div>
                                    </div>

                                    {/* Metrics Grid */}
                                    <div className="grid grid-cols-4 gap-2 pt-4 border-t border-white/5">
                                        <div className="text-center">
                                            <div className="text-[10px] text-text-muted font-mono mb-1">TREND</div>
                                            <div className="flex justify-center">
                                                <TrendIcon className={trendColor} size={16} />
                                            </div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-[10px] text-text-muted font-mono mb-1">L10</div>
                                            <div className="text-sm font-bold text-white">
                                                {team.l10Wins || 0}-{team.l10Losses !== undefined ? team.l10Losses : (10 - (team.l10Wins || 0))}
                                            </div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-[10px] text-text-muted font-mono mb-1">Strength</div>
                                            <div className="text-sm font-bold text-white">
                                                {team.metrics?.strength_score ? team.metrics.strength_score : '-'}
                                            </div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-[10px] text-text-muted font-mono mb-1">CF%</div>
                                            <div className="text-sm font-bold text-white">
                                                {team.metrics?.corsi_pct ? parseFloat(team.metrics.corsi_pct).toFixed(1) : '-'}
                                            </div>
                                        </div>
                                    </div>
                                </motion.div>
                            );
                        })}
                    </div>
                </motion.div>
            ))}
        </div>
    );
};

export default PlayoffPredictions;
