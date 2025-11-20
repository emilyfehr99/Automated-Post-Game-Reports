import React, { useEffect, useState, useMemo } from 'react';
import { nhlApi } from '../api/nhl';
import { backendApi } from '../api/backend';
import { motion } from 'framer-motion';
import { Trophy, TrendingUp, TrendingDown, Minus, Activity } from 'lucide-react';
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
            {Object.entries(teamsByDivision).map(([division, teams], divIndex) => (
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
                                team.trend === 'down' ? 'text-danger' :
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
                                            <div className="text-[10px] text-text-muted font-mono mb-1">xG</div>
                                            <div className="text-sm font-bold text-white">
                                                {team.metrics?.xg ? parseFloat(team.metrics.xg).toFixed(1) : '-'}
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
