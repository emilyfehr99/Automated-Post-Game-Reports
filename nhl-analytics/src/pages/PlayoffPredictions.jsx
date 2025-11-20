import React, { useEffect, useState, useMemo } from 'react';
import { nhlApi } from '../api/nhl';
import { backendApi } from '../api/backend';
import { motion } from 'framer-motion';
import { Trophy, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import clsx from 'clsx';

const PlayoffPredictions = () => {
    const [standings, setStandings] = useState([]);
    const [teamMetrics, setTeamMetrics] = useState({});
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const today = new Date().toISOString().split('T')[0];
                const [standingsResult, metricsResult] = await Promise.allSettled([
                    nhlApi.getStandings(today),
                    backendApi.getTeamMetrics()
                ]);

                if (standingsResult.status === 'fulfilled') {
                    setStandings(standingsResult.value.standings || []);
                } else {
                    console.error('Standings fetch failed:', standingsResult.reason);
                }

                if (metricsResult.status === 'fulfilled') {
                    setTeamMetrics(metricsResult.value || {});
                } else {
                    console.warn('Metrics fetch failed:', metricsResult.reason);
                }
            } catch (error) {
                console.error('Failed to fetch data:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    // Calculate playoff probability
    const calculatePlayoffProb = (team, divisionRank, metrics) => {
        // Base probability from standings (50% weight)
        const pointsPct = team.pointPctg || 0;
        let standingsProb = 0;

        if (divisionRank <= 3) {
            standingsProb = 70 + (pointsPct * 25); // 70-95%
        } else if (divisionRank <= 6) {
            standingsProb = 30 + (pointsPct * 40); // 30-70%
        } else if (divisionRank <= 8) {
            standingsProb = 10 + (pointsPct * 20); // 10-30%
        } else {
            standingsProb = 1 + (pointsPct * 14); // 1-15%
        }

        // Recent form (20% weight)
        // Recent form (20% weight)
        const wins = team.l10Wins || 0;
        const formProb = (wins / 10) * 100;

        // Advanced metrics (20% weight)
        let metricsProb = 50; // Default
        if (metrics) {
            const gs = parseFloat(metrics.gs) || 0;
            const xg = parseFloat(metrics.xg) || 0;
            const corsi = parseFloat(metrics.corsi_pct) || 50;

            // Normalize metrics (assuming league average)
            const gsNorm = Math.min(100, (gs / 5) * 100); // 5 is good GS
            const xgNorm = Math.min(100, (xg / 3) * 100); // 3 is good xG
            const corsiNorm = corsi; // Already a percentage

            metricsProb = (gsNorm + xgNorm + corsiNorm) / 3;
        }

        // Games remaining (10% weight)
        const gamesPlayed = team.gamesPlayed || 0;
        const gamesRemaining = 82 - gamesPlayed;
        const remainingProb = gamesRemaining > 40 ? 50 : 50 + ((40 - gamesRemaining) / 40) * 50;

        // Combine with weights
        const rawProb = (
            standingsProb * 0.5 +
            formProb * 0.2 +
            metricsProb * 0.2 +
            remainingProb * 0.1
        );

        // Apply bounds (1% to 95%)
        return Math.max(1, Math.min(95, Math.round(rawProb)));
    };

    // Calculate trend
    const getTrend = (team) => {
        // Use l10Wins directly from the API response
        const wins = team.l10Wins || 0;

        if (wins >= 7) return 'up';
        if (wins <= 3) return 'down';
        return 'neutral';
    };

    // Group teams by division
    const teamsByDivision = useMemo(() => {
        const divisions = {};

        standings.forEach(team => {
            const division = team.divisionName || 'Unknown';
            if (!divisions[division]) {
                divisions[division] = [];
            }

            const metrics = teamMetrics[team.teamAbbrev?.default];
            const divisionRank = divisions[division].length + 1;
            const playoffProb = calculatePlayoffProb(team, divisionRank, metrics);
            const trend = getTrend(team);

            divisions[division].push({
                ...team,
                metrics,
                playoffProb,
                trend,
                divisionRank
            });
        });

        return divisions;
    }, [standings, teamMetrics]);

    if (loading) {
        return (
            <div className="min-h-screen bg-void pt-24 px-6">
                <div className="max-w-7xl mx-auto">
                    <div className="flex items-center justify-center h-64">
                        <div className="h-8 w-8 rounded-full border-t-2 border-b-2 border-accent-cyan animate-spin"></div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-void pt-24 px-6 pb-12">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-8"
                >
                    <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-accent-cyan via-accent-magenta to-accent-cyan bg-clip-text text-transparent">
                        Playoff Race
                    </h1>
                    <p className="text-gray-400 text-lg">
                        AI-powered playoff probability predictions based on standings, form, and advanced metrics
                    </p>
                </motion.div>

                {/* Divisions */}
                {Object.entries(teamsByDivision).map(([division, teams], divIndex) => (
                    <motion.div
                        key={division}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: divIndex * 0.1 }}
                        className="mb-12"
                    >
                        <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
                            <Trophy className="text-accent-cyan" size={24} />
                            {division}
                        </h2>

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            {teams.map((team, index) => {
                                const probColor = team.playoffProb > 70 ? 'text-green-400' :
                                    team.playoffProb > 40 ? 'text-yellow-400' :
                                        'text-red-400';

                                const TrendIcon = team.trend === 'up' ? TrendingUp :
                                    team.trend === 'down' ? TrendingDown :
                                        Minus;

                                const trendColor = team.trend === 'up' ? 'text-green-400' :
                                    team.trend === 'down' ? 'text-red-400' :
                                        'text-gray-400';

                                return (
                                    <motion.div
                                        key={team.teamAbbrev?.default}
                                        initial={{ opacity: 0, scale: 0.9 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        transition={{ delay: divIndex * 0.1 + index * 0.05 }}
                                        className={clsx(
                                            "glass-panel p-6 rounded-xl border transition-all hover:scale-105",
                                            team.playoffProb > 70 ? "border-green-400/30" :
                                                team.playoffProb > 40 ? "border-yellow-400/30" :
                                                    "border-red-400/30"
                                        )}
                                    >
                                        {/* Team Header */}
                                        <div className="flex items-center gap-3 mb-4">
                                            <img
                                                src={team.teamLogo}
                                                alt={team.teamName?.default}
                                                className="w-12 h-12"
                                            />
                                            <div className="flex-1">
                                                <h3 className="font-bold text-white text-sm">{team.teamName?.default}</h3>
                                                <p className="text-xs text-gray-400">
                                                    {team.wins}-{team.losses}-{team.otLosses} • {team.points} PTS • #{team.divisionRank}
                                                </p>
                                            </div>
                                        </div>

                                        {/* Playoff Probability */}
                                        <div className="text-center mb-4">
                                            <div className={clsx("text-4xl font-bold font-mono", probColor)}>
                                                {team.playoffProb}%
                                            </div>
                                            <div className="text-xs text-gray-500 uppercase tracking-wider">
                                                Playoff Chance
                                            </div>
                                        </div>

                                        {/* Trend */}
                                        <div className="flex items-center justify-center gap-2 mb-4">
                                            <TrendIcon className={trendColor} size={16} />
                                            <span className="text-xs text-gray-400">
                                                L10: {team.l10Wins ?? 0}-{team.l10Losses ?? 0}-{team.l10OtLosses ?? 0}
                                            </span>
                                        </div>

                                        {/* Key Metrics */}
                                        {team.metrics && (
                                            <div className="grid grid-cols-3 gap-2 text-xs">
                                                <div className="text-center">
                                                    <div className="text-gray-500">GS</div>
                                                    <div className="text-white font-mono">{team.metrics.gs || '-'}</div>
                                                </div>
                                                <div className="text-center">
                                                    <div className="text-gray-500">xG</div>
                                                    <div className="text-white font-mono">{team.metrics.xg || '-'}</div>
                                                </div>
                                                <div className="text-center">
                                                    <div className="text-gray-500">CF%</div>
                                                    <div className="text-white font-mono">{team.metrics.corsi_pct || '-'}</div>
                                                </div>
                                            </div>
                                        )}
                                    </motion.div>
                                );
                            })}
                        </div>
                    </motion.div>
                ))}

                {/* Footer */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 }}
                    className="mt-12 text-center text-gray-500 text-sm"
                >
                    <p>🤖 Probabilities calculated using standings (50%), recent form (20%), advanced metrics (20%), and games remaining (10%)</p>
                    <p className="mt-2">Probabilities range from 1% to 95% - no guarantees in hockey!</p>
                </motion.div>
            </div>
        </div>
    );
};

export default PlayoffPredictions;
