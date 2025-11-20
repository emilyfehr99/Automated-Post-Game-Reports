import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { nhlApi } from '../api/nhl';
import { backendApi } from '../api/backend';
import { calculateWinProbability, processPeriodStats } from '../utils/advancedMetrics';
import { motion } from 'framer-motion';
import { TrendingUp, Target, Zap, Activity, Shield, Crosshair, ArrowLeft } from 'lucide-react';
import clsx from 'clsx';

import ErrorBoundary from '../components/ErrorBoundary';
import ShotChart from '../components/ShotChart';
// import { TeamLogo } from '../utils/teamLogos';

const GameDetailsContent = () => {
    const { id } = useParams();
    const [gameData, setGameData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [winProb, setWinProb] = useState(null);
    const [periodStats, setPeriodStats] = useState(null);
    const [isFutureGame, setIsFutureGame] = useState(false);
    const [isLiveGame, setIsLiveGame] = useState(false);
    const [liveData, setLiveData] = useState(null);
    const [teamStats, setTeamStats] = useState(null);
    const [advancedMetrics, setAdvancedMetrics] = useState(null);

    const fetchLiveData = async () => {
        try {
            const response = await fetch(`http://localhost:5002/api/live-game/${id}`);
            if (response.ok) {
                const data = await response.json();
                setLiveData(data);
            }
        } catch (error) {
            console.error('Failed to fetch live data:', error);
        }
    };

    useEffect(() => {
        let intervalId;

        const fetchGameData = async () => {
            try {
                const [data, metrics] = await Promise.all([
                    nhlApi.getGameCenter(id),
                    backendApi.getTeamMetrics()
                ]);

                setGameData(data);
                setAdvancedMetrics(metrics);

                // Check game state
                const gameState = data.boxscore?.gameState || 'FUT';
                let isFuture = gameState === 'FUT' || gameState === 'PRE';
                let isLive = gameState === 'LIVE' || gameState === 'CRIT';

                // DEBUG: Force Live Game for BOS vs ANA (2025020318) - REMOVED
                // if (id === '2025020318') { ...

                setIsFutureGame(isFuture);
                setIsLiveGame(isLive);

                if (isFuture && !isLive) {
                    // Fetch team season stats for pre-game analysis
                    const today = new Date().toISOString().split('T')[0];
                    const standingsData = await nhlApi.getStandings(today);

                    // Find both teams in standings
                    const awayAbbrev = data.boxscore?.awayTeam?.abbrev;
                    const homeAbbrev = data.boxscore?.homeTeam?.abbrev;

                    if (awayAbbrev && homeAbbrev) {
                        const awayTeamStats = standingsData.standings.find(
                            t => t.teamAbbrev.default === awayAbbrev
                        );
                        const homeTeamStats = standingsData.standings.find(
                            t => t.teamAbbrev.default === homeAbbrev
                        );

                        if (awayTeamStats && homeTeamStats) {
                            setTeamStats({
                                away: awayTeamStats,
                                home: homeTeamStats
                            });
                        } else {
                            console.warn('Could not find stats for one or both teams', { away: awayAbbrev, home: homeAbbrev });
                        }
                    }
                } else if (isLive) {
                    // Initial live data fetch
                    fetchLiveData();
                    // Set up polling
                    intervalId = setInterval(fetchLiveData, 30000); // Poll every 30s
                } else {
                    // POST-GAME: Fetch comprehensive metrics from backend
                    try {
                        const response = await fetch(`http://localhost:5002/api/live-game/${id}`);
                        if (response.ok) {
                            const postGameData = await response.json();
                            setLiveData(postGameData); // Reuse liveData state for post-game
                        } else {
                            // Fallback to local calculations if backend unavailable
                            const wp = calculateWinProbability(data);
                            const ps = processPeriodStats(data);
                            setWinProb(wp);
                            setPeriodStats(ps);
                        }
                    } catch (error) {
                        console.error('Failed to fetch post-game data from backend:', error);
                        // Fallback to local calculations
                        const wp = calculateWinProbability(data);
                        const ps = processPeriodStats(data);
                        setWinProb(wp);
                        setPeriodStats(ps);
                    }
                }
            } catch (error) {
                console.error('Failed to fetch game data:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchGameData();

        return () => {
            if (intervalId) clearInterval(intervalId);
        };
    }, [id]);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-[60vh]">
                <div className="h-16 w-16 rounded-full border-t-2 border-b-2 border-accent-cyan animate-spin"></div>
            </div>
        );
    }

    if (!gameData || !gameData.boxscore) {
        return (
            <div className="text-center text-gray-400 font-mono mt-20">
                Game data not available
            </div>
        );
    }

    const { boxscore } = gameData;
    const awayTeam = boxscore.awayTeam || { abbrev: 'UNK', score: 0, logo: '' };
    const homeTeam = boxscore.homeTeam || { abbrev: 'UNK', score: 0, logo: '' };

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="relative rounded-2xl overflow-hidden bg-zinc-900 border border-white/10 p-8 md:p-12">
                <div className="absolute inset-0 bg-grid-pattern opacity-20" />
                <div className="absolute top-0 right-0 w-96 h-96 bg-accent-magenta/10 rounded-full blur-[100px] -translate-y-1/2 translate-x-1/3" />

                <div className="relative z-10">
                    <Link to="/" className="inline-flex items-center gap-2 text-gray-400 hover:text-white mb-6 transition-colors group">
                        <ArrowLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
                        <span className="font-mono text-sm">BACK TO DASHBOARD</span>
                    </Link>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex items-center gap-4 mb-4"
                    >
                        <h1 className="text-4xl md:text-6xl font-sans font-bold text-white tracking-tighter">
                            {isLiveGame ? 'LIVE' : isFutureGame ? 'PRE-GAME' : 'POST GAME'} <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent-cyan to-accent-lime">REPORT</span>
                        </h1>
                        {isLiveGame && (
                            <span className="px-3 py-1 bg-red-500/20 text-red-400 border border-red-500/50 rounded-full text-sm font-bold animate-pulse">
                                ● LIVE
                            </span>
                        )}
                    </motion.div>

                    {/* Teams & Score */}
                    <div className="flex items-center justify-center gap-8 mt-8">
                        <Link to={`/team/${awayTeam.abbrev}`} className="flex flex-col items-center gap-2 group hover:scale-105 transition-transform">
                            <img src={awayTeam.logo} alt={awayTeam.abbrev} className="w-20 h-20 group-hover:drop-shadow-[0_0_15px_rgba(255,255,255,0.3)] transition-all" />
                            <span className="font-sans font-bold text-2xl text-white group-hover:text-accent-cyan transition-colors">{awayTeam.abbrev}</span>
                            <span className="text-5xl font-mono font-bold text-white">
                                {isLiveGame && liveData ? liveData.away_score : awayTeam.score}
                            </span>
                        </Link>

                        <div className="flex flex-col items-center">
                            <div className="text-gray-600 font-mono text-xl mb-2">VS</div>
                            {isLiveGame && liveData && (
                                <div className="text-accent-cyan font-mono text-sm">
                                    P{liveData.current_period} • {liveData.time_remaining}
                                </div>
                            )}
                        </div>

                        <Link to={`/team/${homeTeam.abbrev}`} className="flex flex-col items-center gap-2 group hover:scale-105 transition-transform">
                            <img src={homeTeam.logo} alt={homeTeam.abbrev} className="w-20 h-20 group-hover:drop-shadow-[0_0_15px_rgba(255,255,255,0.3)] transition-all" />
                            <span className="font-sans font-bold text-2xl text-white group-hover:text-accent-magenta transition-colors">{homeTeam.abbrev}</span>
                            <span className="text-5xl font-mono font-bold text-white">
                                {isLiveGame && liveData ? liveData.home_score : homeTeam.score}
                            </span>
                        </Link>
                    </div>
                </div>
            </div>

            {/* LIVE GAME CARD */}
            {isLiveGame && liveData && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="grid grid-cols-1 lg:grid-cols-3 gap-6"
                >
                    {/* Main Live Stats */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Win Probability Bar */}
                        <div className="glass-panel p-6 rounded-xl">
                            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                                <Activity className="text-accent-cyan" />
                                Live Win Probability
                            </h3>
                            <div className="flex justify-between mb-2">
                                <span className="font-mono text-gray-400">{liveData.away_team}</span>
                                <span className="font-mono font-bold text-white">{(liveData.away_prob * 100).toFixed(1)}%</span>
                                <span className="font-mono font-bold text-white">{(liveData.home_prob * 100).toFixed(1)}%</span>
                                <span className="font-mono text-gray-400">{liveData.home_team}</span>
                            </div>
                            <div className="h-4 bg-white/5 rounded-full overflow-hidden flex">
                                <div
                                    className="h-full bg-accent-cyan transition-all duration-500"
                                    style={{ width: `${liveData.away_prob * 100}%` }}
                                />
                                <div
                                    className="h-full bg-accent-magenta transition-all duration-500"
                                    style={{ width: `${liveData.home_prob * 100}%` }}
                                />
                            </div>
                            <div className="mt-4 text-center text-sm text-gray-400">
                                Confidence: <span className="text-accent-lime">{(liveData.confidence * 100).toFixed(0)}%</span>
                            </div>
                        </div>

                        {/* Advanced Metrics Grid - Core */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div className="glass-panel p-4 rounded-xl text-center">
                                <div className="text-gray-500 text-xs mb-1">xG</div>
                                <div className="flex justify-between items-end">
                                    <span className="text-accent-cyan font-mono font-bold">{liveData.advanced_metrics?.away_xg?.toFixed(2) || '-'}</span>
                                    <span className="text-accent-magenta font-mono font-bold">{liveData.advanced_metrics?.home_xg?.toFixed(2) || '-'}</span>
                                </div>
                            </div>
                            <div className="glass-panel p-4 rounded-xl text-center">
                                <div className="text-gray-500 text-xs mb-1">High Danger</div>
                                <div className="flex justify-between items-end">
                                    <span className="text-accent-cyan font-mono font-bold">{liveData.advanced_metrics?.away_hdc || 0}</span>
                                    <span className="text-accent-magenta font-mono font-bold">{liveData.advanced_metrics?.home_hdc || 0}</span>
                                </div>
                            </div>
                            <div className="glass-panel p-4 rounded-xl text-center">
                                <div className="text-gray-500 text-xs mb-1">Corsi %</div>
                                <div className="flex justify-between items-end">
                                    <span className="text-accent-cyan font-mono font-bold">{liveData.team_stats?.away_corsi_pct?.toFixed(1) || '-'}%</span>
                                    <span className="text-accent-magenta font-mono font-bold">{liveData.team_stats?.home_corsi_pct?.toFixed(1) || '-'}%</span>
                                </div>
                            </div>
                            <div className="glass-panel p-4 rounded-xl text-center">
                                <div className="text-gray-500 text-xs mb-1">Game Score</div>
                                <div className="flex justify-between items-end">
                                    <span className="text-accent-cyan font-mono font-bold">{liveData.advanced_metrics?.away_gs?.toFixed(1) || '-'}</span>
                                    <span className="text-accent-magenta font-mono font-bold">{liveData.advanced_metrics?.home_gs?.toFixed(1) || '-'}</span>
                                </div>
                            </div>
                        </div>

                        {/* Zone & Possession Metrics */}
                        <div className="glass-panel p-6 rounded-xl">
                            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                <Target className="text-accent-lime" size={18} />
                                Zone & Possession
                            </h3>
                            <div className="grid grid-cols-3 gap-4 text-sm">
                                <div className="text-center">
                                    <div className="text-gray-500 text-xs mb-1">O-Zone Shots</div>
                                    <div className="flex justify-between px-2">
                                        <span className="text-accent-cyan font-bold">{liveData.zone_metrics?.away_ozs || 0}</span>
                                        <span className="text-accent-magenta font-bold">{liveData.zone_metrics?.home_ozs || 0}</span>
                                    </div>
                                </div>
                                <div className="text-center">
                                    <div className="text-gray-500 text-xs mb-1">Neutral Zone Shots</div>
                                    <div className="flex justify-between px-2">
                                        <span className="text-accent-cyan font-bold">{liveData.zone_metrics?.away_nzs || 0}</span>
                                        <span className="text-accent-magenta font-bold">{liveData.zone_metrics?.home_nzs || 0}</span>
                                    </div>
                                </div>
                                <div className="text-center">
                                    <div className="text-gray-500 text-xs mb-1">Defensive Zone Shots</div>
                                    <div className="flex justify-between px-2">
                                        <span className="text-accent-cyan font-bold">{liveData.zone_metrics?.away_dzs || 0}</span>
                                        <span className="text-accent-magenta font-bold">{liveData.zone_metrics?.home_dzs || 0}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Movement & Pressure */}
                        <div className="glass-panel p-6 rounded-xl">
                            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                <TrendingUp className="text-accent-cyan" size={18} />
                                Movement & Pressure
                            </h3>
                            <div className="grid grid-cols-2 gap-6 text-sm">
                                <div>
                                    <div className="text-gray-500 text-xs mb-2 text-center">Shot Generation</div>
                                    <div className="space-y-2">
                                        <div className="flex justify-between items-center">
                                            <span className="text-accent-cyan font-bold">{liveData.zone_metrics?.away_rush || 0}</span>
                                            <span className="text-gray-400">Rush Chances</span>
                                            <span className="text-accent-magenta font-bold">{liveData.zone_metrics?.home_rush || 0}</span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-accent-cyan font-bold">{liveData.zone_metrics?.away_fc || 0}</span>
                                            <span className="text-gray-400">Forecheck</span>
                                            <span className="text-accent-magenta font-bold">{liveData.zone_metrics?.home_fc || 0}</span>
                                        </div>
                                    </div>
                                </div>
                                <div>
                                    <div className="text-gray-500 text-xs mb-2 text-center">Pre-Shot Movement (ft)</div>
                                    <div className="space-y-2">
                                        <div className="flex justify-between items-center">
                                            <span className="text-accent-cyan font-bold">{liveData.movement_metrics?.away_lateral?.toFixed(1) || '-'}</span>
                                            <span className="text-gray-400">Lateral</span>
                                            <span className="text-accent-magenta font-bold">{liveData.movement_metrics?.home_lateral?.toFixed(1) || '-'}</span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-accent-cyan font-bold">{liveData.movement_metrics?.away_longitudinal?.toFixed(1) || '-'}</span>
                                            <span className="text-gray-400">Longitudinal</span>
                                            <span className="text-accent-magenta font-bold">{liveData.movement_metrics?.home_longitudinal?.toFixed(1) || '-'}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Side Stats & Momentum */}
                    <div className="space-y-6">
                        {/* Momentum Factors */}
                        <div className="glass-panel p-6 rounded-xl">
                            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                                <Zap className="text-accent-lime" />
                                Momentum
                            </h3>
                            <div className="space-y-3">
                                {liveData.momentum && Object.entries(liveData.momentum).map(([key, value]) => (
                                    key !== 'total_momentum' && (
                                        <div key={key} className="flex items-center justify-between text-sm">
                                            <span className="text-gray-400 capitalize">{key.replace('_impact', '').replace('_', ' ')}</span>
                                            <span className={value > 0 ? "text-accent-cyan" : "text-accent-magenta"}>
                                                {(value * 100).toFixed(1)}%
                                            </span>
                                        </div>
                                    )
                                ))}
                            </div>
                        </div>

                        {/* Game Stats */}
                        <div className="glass-panel p-6 rounded-xl">
                            <h3 className="text-lg font-bold text-white mb-4">Game Stats</h3>
                            <div className="space-y-4">
                                <div className="flex justify-between text-sm">
                                    <span className="text-accent-cyan font-bold">{liveData.stats?.away?.shots || 0}</span>
                                    <span className="text-gray-500">Shots</span>
                                    <span className="text-accent-magenta font-bold">{liveData.stats?.home?.shots || 0}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-accent-cyan font-bold">{liveData.stats?.away?.hits || 0}</span>
                                    <span className="text-gray-500">Hits</span>
                                    <span className="text-accent-magenta font-bold">{liveData.stats?.home?.hits || 0}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-accent-cyan font-bold">{liveData.stats?.away?.faceoff_pct?.toFixed(1) || '-'}%</span>
                                    <span className="text-gray-500">Faceoffs</span>
                                    <span className="text-accent-magenta font-bold">{liveData.stats?.home?.faceoff_pct?.toFixed(1) || '-'}%</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-accent-cyan font-bold">{liveData.stats?.away?.pim || 0}</span>
                                    <span className="text-gray-500">PIM</span>
                                    <span className="text-accent-magenta font-bold">{liveData.stats?.home?.pim || 0}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-accent-cyan font-bold">{liveData.stats?.away?.power_play_pct?.toFixed(0) || 0}%</span>
                                    <span className="text-gray-500">PP%</span>
                                    <span className="text-accent-magenta font-bold">{liveData.stats?.home?.power_play_pct?.toFixed(0) || 0}%</span>
                                </div>
                            </div>
                        </div>

                        {/* Turnovers & Defense */}
                        <div className="glass-panel p-6 rounded-xl">
                            <h3 className="text-lg font-bold text-white mb-4">Defense</h3>
                            <div className="space-y-4">
                                <div className="flex justify-between text-sm">
                                    <span className="text-accent-cyan font-bold">{liveData.zone_metrics?.away_nzt || 0}</span>
                                    <span className="text-gray-500">NZ Turnovers</span>
                                    <span className="text-accent-magenta font-bold">{liveData.zone_metrics?.home_nzt || 0}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-accent-cyan font-bold">{liveData.zone_metrics?.away_nztsa || 0}</span>
                                    <span className="text-gray-500">NZT Shots Against</span>
                                    <span className="text-accent-magenta font-bold">{liveData.zone_metrics?.home_nztsa || 0}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-accent-cyan font-bold">{liveData.stats?.away?.blocked_shots || 0}</span>
                                    <span className="text-gray-500">Blocks</span>
                                    <span className="text-accent-magenta font-bold">{liveData.stats?.home?.blocked_shots || 0}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-accent-cyan font-bold">{liveData.stats?.away?.giveaways || 0}</span>
                                    <span className="text-gray-500">Giveaways</span>
                                    <span className="text-accent-magenta font-bold">{liveData.stats?.home?.giveaways || 0}</span>
                                </div>
                            </div>
                        </div>

                        {/* Goalie Stats */}
                        <div className="glass-panel p-6 rounded-xl">
                            <h3 className="text-lg font-bold text-white mb-4">Goalies</h3>
                            <div className="space-y-4">
                                <div className="flex justify-between text-sm border-b border-white/5 pb-2">
                                    <div className="text-left">
                                        <div className="text-accent-cyan font-bold">{liveData.goalie_stats?.away?.name || 'Away Goalie'}</div>
                                        <div className="text-xs text-gray-500">
                                            {liveData.goalie_stats?.away?.saves || 0} / {liveData.goalie_stats?.away?.shots || 0} SA
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-accent-magenta font-bold">{liveData.goalie_stats?.home?.name || 'Home Goalie'}</div>
                                        <div className="text-xs text-gray-500">
                                            {liveData.goalie_stats?.home?.saves || 0} / {liveData.goalie_stats?.home?.shots || 0} SA
                                        </div>
                                    </div>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-accent-cyan font-bold">{liveData.goalie_stats?.away?.save_pct?.toFixed(3) || '.000'}</span>
                                    <span className="text-gray-500">Sv%</span>
                                    <span className="text-accent-magenta font-bold">{liveData.goalie_stats?.home?.save_pct?.toFixed(3) || '.000'}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Period by Period Stats */}
                    <div className="lg:col-span-3 glass-panel p-6 rounded-xl">
                        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                            <Activity className="text-accent-cyan" />
                            Period by Period
                        </h3>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm text-left text-gray-400">
                                <thead className="text-xs text-gray-500 uppercase bg-white/5">
                                    <tr>
                                        <th className="px-4 py-3 rounded-l-lg">Period</th>
                                        <th className="px-4 py-3 text-center">Team</th>
                                        <th className="px-4 py-3 text-center">Goals</th>
                                        <th className="px-4 py-3 text-center">Shots</th>
                                        <th className="px-4 py-3 text-center">xG</th>
                                        <th className="px-4 py-3 text-center">Corsi</th>
                                        <th className="px-4 py-3 text-center">Hits</th>
                                        <th className="px-4 py-3 text-center rounded-r-lg">FO%</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {[1, 2, 3].map((period) => {
                                        // Find period data in breakdown array
                                        const periodData = liveData.period_breakdown?.find(p => p.period === period);
                                        const idx = period - 1; // 0-based index for arrays

                                        return (
                                            <React.Fragment key={period}>
                                                <tr className="border-b border-white/5">
                                                    <td rowSpan="2" className="px-4 py-3 font-bold text-white border-r border-white/5">
                                                        {period}
                                                    </td>
                                                    <td className="px-4 py-2 text-center font-bold text-accent-cyan">{liveData.away_team}</td>
                                                    <td className="px-4 py-2 text-center text-white">{periodData?.away_goals ?? '-'}</td>
                                                    <td className="px-4 py-2 text-center">{liveData.period_stats?.away?.shots?.[idx] ?? '-'}</td>
                                                    <td className="px-4 py-2 text-center">{periodData?.away_xg?.toFixed(2) ?? '-'}</td>
                                                    <td className="px-4 py-2 text-center">{liveData.period_stats?.away?.corsi_pct?.[idx]?.toFixed(1) ?? '-'}%</td>
                                                    <td className="px-4 py-2 text-center">{liveData.period_stats?.away?.hits?.[idx] ?? '-'}</td>
                                                    <td className="px-4 py-2 text-center">{liveData.period_stats?.away?.fo_pct?.[idx]?.toFixed(1) ?? '-'}%</td>
                                                </tr>
                                                <tr className="border-b border-white/10">
                                                    <td className="px-4 py-2 text-center font-bold text-accent-magenta">{liveData.home_team}</td>
                                                    <td className="px-4 py-2 text-center text-white">{periodData?.home_goals ?? '-'}</td>
                                                    <td className="px-4 py-2 text-center">{liveData.period_stats?.home?.shots?.[idx] ?? '-'}</td>
                                                    <td className="px-4 py-2 text-center">{periodData?.home_xg?.toFixed(2) ?? '-'}</td>
                                                    <td className="px-4 py-2 text-center">{liveData.period_stats?.home?.corsi_pct?.[idx]?.toFixed(1) ?? '-'}%</td>
                                                    <td className="px-4 py-2 text-center">{liveData.period_stats?.home?.hits?.[idx] ?? '-'}</td>
                                                    <td className="px-4 py-2 text-center">{liveData.period_stats?.home?.fo_pct?.[idx]?.toFixed(1) ?? '-'}%</td>
                                                </tr>
                                            </React.Fragment>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Scoring Summary - Full Width at Bottom of Live Card */}
                    <div className="lg:col-span-3 glass-panel p-6 rounded-xl">
                        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                            <Target className="text-accent-lime" />
                            Scoring Summary
                        </h3>
                        <div className="space-y-3">
                            {liveData.scoring_summary && liveData.scoring_summary.length > 0 ? (
                                liveData.scoring_summary.map((goal, idx) => (
                                    <div key={idx} className="flex items-center gap-4 bg-white/5 p-3 rounded-lg border border-white/5">
                                        <div className="font-mono text-gray-400 w-12">P{goal.period}</div>
                                        <div className="font-mono text-gray-400 w-16">{goal.time}</div>
                                        <div className={`font-bold ${goal.team === liveData.away_team ? 'text-accent-cyan' : 'text-accent-magenta'}`}>
                                            {goal.team}
                                        </div>
                                        <div className="flex-1 text-white">
                                            <span className="font-bold">{goal.scorer}</span>
                                            {goal.assists && goal.assists.length > 0 && (
                                                <span className="text-gray-400 text-sm ml-2">
                                                    ({goal.assists.join(', ')})
                                                </span>
                                            )}
                                        </div>
                                        <div className="font-mono font-bold text-white">
                                            {goal.away_score}-{goal.home_score}
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="text-center text-gray-500 py-4">No goals scored yet</div>
                            )}
                        </div>
                    </div>
                </motion.div>
            )}

            {/* Advanced Metrics Comparison (Pre-Game) */}
            {/* Advanced Metrics Comparison (Pre-Game) */}
            {isFutureGame && teamStats ? (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="mt-8 w-full"
                >
                    {/* Team Stats Comparison */}
                    <div className="glass-panel p-6 rounded-xl w-full">
                        <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                            <Target className="text-accent-cyan" />
                            Team Comparison
                        </h3>

                        <div className="space-y-4">
                            {/* Header with Logos */}
                            <div className="flex justify-between items-end mb-4 pb-4 border-b border-white/10">
                                <div className="flex flex-col items-center gap-2">
                                    <img src={awayTeam.logo} alt={awayTeam.abbrev} className="w-12 h-12" />
                                    <span className="font-bold text-white">{awayTeam.abbrev}</span>
                                </div>
                                <div className="text-gray-500 text-sm font-mono mb-2">VS</div>
                                <div className="flex flex-col items-center gap-2">
                                    <img src={homeTeam.logo} alt={homeTeam.abbrev} className="w-12 h-12" />
                                    <span className="font-bold text-white">{homeTeam.abbrev}</span>
                                </div>
                            </div>

                            <div className="flex justify-between items-center text-sm">
                                <span className="font-mono font-bold text-accent-cyan">{teamStats.away.wins}-{teamStats.away.losses}-{teamStats.away.otLosses}</span>
                                <span className="text-gray-400">Record</span>
                                <span className="font-mono font-bold text-accent-magenta">{teamStats.home.wins}-{teamStats.home.losses}-{teamStats.home.otLosses}</span>
                            </div>
                            <div className="flex justify-between items-center text-sm">
                                <span className="font-mono font-bold text-accent-cyan">{teamStats.away.points}</span>
                                <span className="text-gray-400">Points</span>
                                <span className="font-mono font-bold text-accent-magenta">{teamStats.home.points}</span>
                            </div>
                            <div className="flex justify-between items-center text-sm">
                                <span className="font-mono font-bold text-accent-cyan">{teamStats.away.goalDifferential}</span>
                                <span className="text-gray-400">Goal Diff</span>
                                <span className="font-mono font-bold text-accent-magenta">{teamStats.home.goalDifferential}</span>
                            </div>
                            <div className="flex justify-between items-center text-sm">
                                <span className="font-mono font-bold text-accent-cyan">{teamStats.away.l10Wins}-{teamStats.away.l10Losses}-{teamStats.away.l10OtLosses}</span>
                                <span className="text-gray-400">L10</span>
                                <span className="font-mono font-bold text-accent-magenta">{teamStats.home.l10Wins}-{teamStats.home.l10Losses}-{teamStats.home.l10OtLosses}</span>
                            </div>
                            <div className="flex justify-between items-center text-sm">
                                <span className="font-mono font-bold text-accent-cyan">{teamStats.away.streakCode}{teamStats.away.streakCount}</span>
                                <span className="text-gray-400">Streak</span>
                                <span className="font-mono font-bold text-accent-magenta">{teamStats.home.streakCode}{teamStats.home.streakCount}</span>
                            </div>

                            {/* Comprehensive Season Stats Comparison */}
                            <div className="mt-6 space-y-6">
                                {/* Offense & Defense */}
                                <div>
                                    <h4 className="text-sm font-bold text-gray-400 mb-3 uppercase tracking-wider border-b border-white/10 pb-1">Offense & Defense</h4>
                                    <div className="space-y-2">
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="font-mono font-bold text-accent-cyan">{advancedMetrics?.[awayTeam.abbrev]?.goals?.toFixed(2) || '-'}</span>
                                            <span className="text-gray-400">Goals/GP</span>
                                            <span className="font-mono font-bold text-accent-magenta">{advancedMetrics?.[homeTeam.abbrev]?.goals?.toFixed(2) || '-'}</span>
                                        </div>
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="font-mono font-bold text-accent-cyan">{advancedMetrics?.[awayTeam.abbrev]?.shots?.toFixed(1) || '-'}</span>
                                            <span className="text-gray-400">Shots/GP</span>
                                            <span className="font-mono font-bold text-accent-magenta">{advancedMetrics?.[homeTeam.abbrev]?.shots?.toFixed(1) || '-'}</span>
                                        </div>
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="font-mono font-bold text-accent-cyan">{advancedMetrics?.[awayTeam.abbrev]?.pp_pct?.toFixed(1) || '-'}%</span>
                                            <span className="text-gray-400">Power Play %</span>
                                            <span className="font-mono font-bold text-accent-magenta">{advancedMetrics?.[homeTeam.abbrev]?.pp_pct?.toFixed(1) || '-'}%</span>
                                        </div>
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="font-mono font-bold text-accent-cyan">{advancedMetrics?.[awayTeam.abbrev]?.pk_pct?.toFixed(1) || '-'}%</span>
                                            <span className="text-gray-400">Penalty Kill %</span>
                                            <span className="font-mono font-bold text-accent-magenta">{advancedMetrics?.[homeTeam.abbrev]?.pk_pct?.toFixed(1) || '-'}%</span>
                                        </div>
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="font-mono font-bold text-accent-cyan">{advancedMetrics?.[awayTeam.abbrev]?.fo_pct?.toFixed(1) || '-'}%</span>
                                            <span className="text-gray-400">Faceoff %</span>
                                            <span className="font-mono font-bold text-accent-magenta">{advancedMetrics?.[homeTeam.abbrev]?.fo_pct?.toFixed(1) || '-'}%</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Advanced Metrics */}
                                <div>
                                    <h4 className="text-sm font-bold text-gray-400 mb-3 uppercase tracking-wider border-b border-white/10 pb-1">Advanced Metrics</h4>
                                    <div className="space-y-2">
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="font-mono font-bold text-accent-cyan">{advancedMetrics?.[awayTeam.abbrev]?.xg?.toFixed(2) || '-'}</span>
                                            <span className="text-gray-400">xG/60</span>
                                            <span className="font-mono font-bold text-accent-magenta">{advancedMetrics?.[homeTeam.abbrev]?.xg?.toFixed(2) || '-'}</span>
                                        </div>
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="font-mono font-bold text-accent-cyan">{advancedMetrics?.[awayTeam.abbrev]?.hdc?.toFixed(1) || '-'}</span>
                                            <span className="text-gray-400">High Danger Chances</span>
                                            <span className="font-mono font-bold text-accent-magenta">{advancedMetrics?.[homeTeam.abbrev]?.hdc?.toFixed(1) || '-'}</span>
                                        </div>
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="font-mono font-bold text-accent-cyan">{advancedMetrics?.[awayTeam.abbrev]?.corsi_pct?.toFixed(1) || '-'}%</span>
                                            <span className="text-gray-400">Corsi %</span>
                                            <span className="font-mono font-bold text-accent-magenta">{advancedMetrics?.[homeTeam.abbrev]?.corsi_pct?.toFixed(1) || '-'}%</span>
                                        </div>
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="font-mono font-bold text-accent-cyan">{advancedMetrics?.[awayTeam.abbrev]?.gs?.toFixed(1) || '-'}</span>
                                            <span className="text-gray-400">Game Score/GP</span>
                                            <span className="font-mono font-bold text-accent-magenta">{advancedMetrics?.[homeTeam.abbrev]?.gs?.toFixed(1) || '-'}</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Zone Control */}
                                <div>
                                    <h4 className="text-sm font-bold text-gray-400 mb-3 uppercase tracking-wider border-b border-white/10 pb-1">Zone Control (Avg)</h4>
                                    <div className="space-y-2">
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="font-mono font-bold text-accent-cyan">{advancedMetrics?.[awayTeam.abbrev]?.ozs?.toFixed(1) || '-'}</span>
                                            <span className="text-gray-400">O-Zone Shots</span>
                                            <span className="font-mono font-bold text-accent-magenta">{advancedMetrics?.[homeTeam.abbrev]?.ozs?.toFixed(1) || '-'}</span>
                                        </div>
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="font-mono font-bold text-accent-cyan">{advancedMetrics?.[awayTeam.abbrev]?.nzs?.toFixed(1) || '-'}</span>
                                            <span className="text-gray-400">Neutral Zone Shots</span>
                                            <span className="font-mono font-bold text-accent-magenta">{advancedMetrics?.[homeTeam.abbrev]?.nzs?.toFixed(1) || '-'}</span>
                                        </div>
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="font-mono font-bold text-accent-cyan">{advancedMetrics?.[awayTeam.abbrev]?.dzs?.toFixed(1) || '-'}</span>
                                            <span className="text-gray-400">D-Zone Shots</span>
                                            <span className="font-mono font-bold text-accent-magenta">{advancedMetrics?.[homeTeam.abbrev]?.dzs?.toFixed(1) || '-'}</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Transition & Pressure */}
                                <div>
                                    <h4 className="text-sm font-bold text-gray-400 mb-3 uppercase tracking-wider border-b border-white/10 pb-1">Transition & Pressure</h4>
                                    <div className="space-y-2">
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="font-mono font-bold text-accent-cyan">{advancedMetrics?.[awayTeam.abbrev]?.nzts?.toFixed(1) || '-'}</span>
                                            <span className="text-gray-400">NZ Turnovers</span>
                                            <span className="font-mono font-bold text-accent-magenta">{advancedMetrics?.[homeTeam.abbrev]?.nzts?.toFixed(1) || '-'}</span>
                                        </div>
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="font-mono font-bold text-accent-cyan">{advancedMetrics?.[awayTeam.abbrev]?.nztsa?.toFixed(1) || '-'}</span>
                                            <span className="text-gray-400">NZT Shots Against</span>
                                            <span className="font-mono font-bold text-accent-magenta">{advancedMetrics?.[homeTeam.abbrev]?.nztsa?.toFixed(1) || '-'}</span>
                                        </div>
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="font-mono font-bold text-accent-cyan">{advancedMetrics?.[awayTeam.abbrev]?.rush?.toFixed(1) || '-'}</span>
                                            <span className="text-gray-400">Rush Chances</span>
                                            <span className="font-mono font-bold text-accent-magenta">{advancedMetrics?.[homeTeam.abbrev]?.rush?.toFixed(1) || '-'}</span>
                                        </div>
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="font-mono font-bold text-accent-cyan">{advancedMetrics?.[awayTeam.abbrev]?.fc?.toFixed(1) || '-'}</span>
                                            <span className="text-gray-400">Forecheck Chances</span>
                                            <span className="font-mono font-bold text-accent-magenta">{advancedMetrics?.[homeTeam.abbrev]?.fc?.toFixed(1) || '-'}</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Movement & Physical */}
                                <div>
                                    <h4 className="text-sm font-bold text-gray-400 mb-3 uppercase tracking-wider border-b border-white/10 pb-1">Movement & Physical</h4>
                                    <div className="space-y-2">
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="font-mono font-bold text-accent-cyan">{advancedMetrics?.[awayTeam.abbrev]?.lateral?.toFixed(1) || '-'}</span>
                                            <span className="text-gray-400">Lateral Movement</span>
                                            <span className="font-mono font-bold text-accent-magenta">{advancedMetrics?.[homeTeam.abbrev]?.lateral?.toFixed(1) || '-'}</span>
                                        </div>
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="font-mono font-bold text-accent-cyan">{advancedMetrics?.[awayTeam.abbrev]?.longitudinal?.toFixed(1) || '-'}</span>
                                            <span className="text-gray-400">Longitudinal Move</span>
                                            <span className="font-mono font-bold text-accent-magenta">{advancedMetrics?.[homeTeam.abbrev]?.longitudinal?.toFixed(1) || '-'}</span>
                                        </div>
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="font-mono font-bold text-accent-cyan">{advancedMetrics?.[awayTeam.abbrev]?.hits?.toFixed(1) || '-'}</span>
                                            <span className="text-gray-400">Hits/GP</span>
                                            <span className="font-mono font-bold text-accent-magenta">{advancedMetrics?.[homeTeam.abbrev]?.hits?.toFixed(1) || '-'}</span>
                                        </div>
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="font-mono font-bold text-accent-cyan">{advancedMetrics?.[awayTeam.abbrev]?.blocks?.toFixed(1) || '-'}</span>
                                            <span className="text-gray-400">Blocks/GP</span>
                                            <span className="font-mono font-bold text-accent-magenta">{advancedMetrics?.[homeTeam.abbrev]?.blocks?.toFixed(1) || '-'}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </motion.div>
            ) : (!isLiveGame && !isFutureGame && liveData) && (
                /* POST-GAME COMPREHENSIVE METRICS - Reuse Live Game Card Structure */
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="grid grid-cols-1 lg:grid-cols-3 gap-6"
                >
                    {/* Main Post-Game Stats */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Game Outcome Indicator */}
                        <div className="glass-panel p-4 rounded-xl text-center">
                            <div className="text-sm text-gray-400 mb-1">GAME ENDED IN</div>
                            <div className="text-2xl font-bold text-accent-lime">
                                {gameData.boxscore?.gameOutcome?.lastPeriodType === 'SO' ? 'SHOOTOUT' :
                                    gameData.boxscore?.gameOutcome?.lastPeriodType === 'OT' ? 'OVERTIME' :
                                        'REGULATION'}
                            </div>
                        </div>

                        {/* Win Probability Bar */}
                        <div className="glass-panel p-6 rounded-xl">
                            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                                <Activity className="text-accent-cyan" />
                                Final Win Probability
                            </h3>
                            <div className="flex justify-between mb-2">
                                <span className="font-mono text-gray-400">{liveData.away_team}</span>
                                <span className="font-mono font-bold text-white">{(liveData.away_prob * 100).toFixed(1)}%</span>
                                <span className="font-mono font-bold text-white">{(liveData.home_prob * 100).toFixed(1)}%</span>
                                <span className="font-mono text-gray-400">{liveData.home_team}</span>
                            </div>
                            <div className="h-4 bg-white/5 rounded-full overflow-hidden flex">
                                <div
                                    className="h-full bg-accent-cyan transition-all duration-500"
                                    style={{ width: `${liveData.away_prob * 100}%` }}
                                />
                                <div
                                    className="h-full bg-accent-magenta transition-all duration-500"
                                    style={{ width: `${liveData.home_prob * 100}%` }}
                                />
                            </div>
                        </div>

                        {/* Advanced Metrics Grid - Core */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div className="glass-panel p-4 rounded-xl text-center">
                                <div className="text-gray-500 text-xs mb-1">xG</div>
                                <div className="flex justify-between items-end">
                                    <span className="text-accent-cyan font-mono font-bold">{liveData.advanced_metrics?.away_xg?.toFixed(2) || '-'}</span>
                                    <span className="text-accent-magenta font-mono font-bold">{liveData.advanced_metrics?.home_xg?.toFixed(2) || '-'}</span>
                                </div>
                            </div>
                            <div className="glass-panel p-4 rounded-xl text-center">
                                <div className="text-gray-500 text-xs mb-1">High Danger</div>
                                <div className="flex justify-between items-end">
                                    <span className="text-accent-cyan font-mono font-bold">{liveData.advanced_metrics?.away_hdc || 0}</span>
                                    <span className="text-accent-magenta font-mono font-bold">{liveData.advanced_metrics?.home_hdc || 0}</span>
                                </div>
                            </div>
                            <div className="glass-panel p-4 rounded-xl text-center">
                                <div className="text-gray-500 text-xs mb-1">Corsi %</div>
                                <div className="flex justify-between items-end">
                                    <span className="text-accent-cyan font-mono font-bold">{liveData.advanced_metrics?.away_corsi_pct?.toFixed(1) || '-'}%</span>
                                    <span className="text-accent-magenta font-mono font-bold">{liveData.advanced_metrics?.home_corsi_pct?.toFixed(1) || '-'}%</span>
                                </div>
                            </div>
                            <div className="glass-panel p-4 rounded-xl text-center">
                                <div className="text-gray-500 text-xs mb-1">Game Score</div>
                                <div className="flex justify-between items-end">
                                    <span className="text-accent-cyan font-mono font-bold">{liveData.advanced_metrics?.away_gs?.toFixed(1) || '-'}</span>
                                    <span className="text-accent-magenta font-mono font-bold">{liveData.advanced_metrics?.home_gs?.toFixed(1) || '-'}</span>
                                </div>
                            </div>
                        </div>

                        {/* Zone & Possession Metrics */}
                        <div className="glass-panel p-6 rounded-xl">
                            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                <Target className="text-accent-lime" size={18} />
                                Zone Control
                            </h3>
                            <div className="grid grid-cols-3 gap-4 text-sm">
                                <div className="text-center">
                                    <div className="text-gray-500 text-xs mb-1">O-Zone Shots</div>
                                    <div className="flex justify-between px-2">
                                        <span className="text-accent-cyan font-bold">{liveData.zone_metrics?.away_ozs || 0}</span>
                                        <span className="text-accent-magenta font-bold">{liveData.zone_metrics?.home_ozs || 0}</span>
                                    </div>
                                </div>
                                <div className="text-center">
                                    <div className="text-gray-500 text-xs mb-1">Neutral Zone Shots</div>
                                    <div className="flex justify-between px-2">
                                        <span className="text-accent-cyan font-bold">{liveData.zone_metrics?.away_nzs || 0}</span>
                                        <span className="text-accent-magenta font-bold">{liveData.zone_metrics?.home_nzs || 0}</span>
                                    </div>
                                </div>
                                <div className="text-center">
                                    <div className="text-gray-500 text-xs mb-1">Defensive Zone Shots</div>
                                    <div className="flex justify-between px-2">
                                        <span className="text-accent-cyan font-bold">{liveData.zone_metrics?.away_dzs || 0}</span>
                                        <span className="text-accent-magenta font-bold">{liveData.zone_metrics?.home_dzs || 0}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Movement & Pressure */}
                        <div className="glass-panel p-6 rounded-xl">
                            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                <TrendingUp className="text-accent-cyan" size={18} />
                                Transition & Pressure
                            </h3>
                            <div className="grid grid-cols-2 gap-6 text-sm">
                                <div>
                                    <div className="text-gray-500 text-xs mb-2 text-center">Shot Generation</div>
                                    <div className="space-y-2">
                                        <div className="flex justify-between items-center">
                                            <span className="text-accent-cyan font-bold">{liveData.zone_metrics?.away_rush || 0}</span>
                                            <span className="text-gray-400">Rush Chances</span>
                                            <span className="text-accent-magenta font-bold">{liveData.zone_metrics?.home_rush || 0}</span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-accent-cyan font-bold">{liveData.zone_metrics?.away_fc || 0}</span>
                                            <span className="text-gray-400">Forecheck</span>
                                            <span className="text-accent-magenta font-bold">{liveData.zone_metrics?.home_fc || 0}</span>
                                        </div>
                                    </div>
                                </div>
                                <div>
                                    <div className="text-gray-500 text-xs mb-2 text-center">Pre-Shot Movement (ft)</div>
                                    <div className="space-y-2">
                                        <div className="flex justify-between items-center">
                                            <span className="text-accent-cyan font-bold">{liveData.movement_metrics?.away_lateral?.toFixed(1) || '-'}</span>
                                            <span className="text-gray-400">Lateral</span>
                                            <span className="text-accent-magenta font-bold">{liveData.movement_metrics?.home_lateral?.toFixed(1) || '-'}</span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-accent-cyan font-bold">{liveData.movement_metrics?.away_longitudinal?.toFixed(1) || '-'}</span>
                                            <span className="text-gray-400">Longitudinal</span>
                                            <span className="text-accent-magenta font-bold">{liveData.movement_metrics?.home_longitudinal?.toFixed(1) || '-'}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Side Stats */}
                    <div className="space-y-6">
                        {/* Game Stats */}
                        <div className="glass-panel p-6 rounded-xl">
                            <h3 className="text-lg font-bold text-white mb-4">Game Stats</h3>
                            <div className="space-y-4">
                                <div className="flex justify-between text-sm">
                                    <span className="text-accent-cyan font-bold">{liveData.stats?.away?.shots || 0}</span>
                                    <span className="text-gray-500">Shots</span>
                                    <span className="text-accent-magenta font-bold">{liveData.stats?.home?.shots || 0}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-accent-cyan font-bold">{liveData.stats?.away?.hits || 0}</span>
                                    <span className="text-gray-500">Hits</span>
                                    <span className="text-accent-magenta font-bold">{liveData.stats?.home?.hits || 0}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-accent-cyan font-bold">{liveData.stats?.away?.faceoff_pct?.toFixed(1) || '-'}%</span>
                                    <span className="text-gray-500">Faceoffs</span>
                                    <span className="text-accent-magenta font-bold">{liveData.stats?.home?.faceoff_pct?.toFixed(1) || '-'}%</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-accent-cyan font-bold">{liveData.stats?.away?.pim || 0}</span>
                                    <span className="text-gray-500">PIM</span>
                                    <span className="text-accent-magenta font-bold">{liveData.stats?.home?.pim || 0}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-accent-cyan font-bold">{liveData.stats?.away?.power_play_pct?.toFixed(0) || 0}%</span>
                                    <span className="text-gray-500">PP%</span>
                                    <span className="text-accent-magenta font-bold">{liveData.stats?.home?.power_play_pct?.toFixed(0) || 0}%</span>
                                </div>
                            </div>
                        </div>

                        {/* Turnovers & Defense */}
                        <div className="glass-panel p-6 rounded-xl">
                            <h3 className="text-lg font-bold text-white mb-4">Defense</h3>
                            <div className="space-y-4">
                                <div className="flex justify-between text-sm">
                                    <span className="text-accent-cyan font-bold">{liveData.zone_metrics?.away_nzt || 0}</span>
                                    <span className="text-gray-500">NZ Turnovers</span>
                                    <span className="text-accent-magenta font-bold">{liveData.zone_metrics?.home_nzt || 0}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-accent-cyan font-bold">{liveData.zone_metrics?.away_nztsa || 0}</span>
                                    <span className="text-gray-500">NZT Shots Against</span>
                                    <span className="text-accent-magenta font-bold">{liveData.zone_metrics?.home_nztsa || 0}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-accent-cyan font-bold">{liveData.stats?.away?.blocked_shots || 0}</span>
                                    <span className="text-gray-500">Blocks</span>
                                    <span className="text-accent-magenta font-bold">{liveData.stats?.home?.blocked_shots || 0}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-accent-cyan font-bold">{liveData.stats?.away?.giveaways || 0}</span>
                                    <span className="text-gray-500">Giveaways</span>
                                    <span className="text-accent-magenta font-bold">{liveData.stats?.home?.giveaways || 0}</span>
                                </div>
                            </div>
                        </div>

                        {/* Goalie Stats */}
                        <div className="glass-panel p-6 rounded-xl">
                            <h3 className="text-lg font-bold text-white mb-4">Goalies</h3>
                            <div className="space-y-4">
                                <div className="flex justify-between text-sm border-b border-white/5 pb-2">
                                    <div className="text-left">
                                        <div className="text-accent-cyan font-bold">{liveData.goalie_stats?.away?.name || 'Away Goalie'}</div>
                                        <div className="text-xs text-gray-500">
                                            {liveData.goalie_stats?.away?.saves || 0} / {liveData.goalie_stats?.away?.shots || 0} SA
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-accent-magenta font-bold">{liveData.goalie_stats?.home?.name || 'Home Goalie'}</div>
                                        <div className="text-xs text-gray-500">
                                            {liveData.goalie_stats?.home?.saves || 0} / {liveData.goalie_stats?.home?.shots || 0} SA
                                        </div>
                                    </div>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-accent-cyan font-bold">{liveData.goalie_stats?.away?.save_pct?.toFixed(3) || '.000'}</span>
                                    <span className="text-gray-500">Sv%</span>
                                    <span className="text-accent-magenta font-bold">{liveData.goalie_stats?.home?.save_pct?.toFixed(3) || '.000'}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Period by Period Stats - Full Width */}
                    <div className="lg:col-span-3 glass-panel p-6 rounded-xl">
                        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                            <Activity className="text-accent-cyan" />
                            Period by Period
                        </h3>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm text-left text-gray-400">
                                <thead className="text-xs text-gray-500 uppercase bg-white/5">
                                    <tr>
                                        <th className="px-4 py-3 rounded-l-lg">TEAM</th>
                                        <th className="px-4 py-3 text-center">P1</th>
                                        <th className="px-4 py-3 text-center">P2</th>
                                        <th className="px-4 py-3 text-center">P3</th>
                                        <th className="px-4 py-3 text-center rounded-r-lg">TOTAL</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {(() => {
                                        const p1 = liveData.period_breakdown?.find(p => p.period === 1);
                                        const p2 = liveData.period_breakdown?.find(p => p.period === 2);
                                        const p3 = liveData.period_breakdown?.find(p => p.period === 3);

                                        return (
                                            <>
                                                <tr className="border-b border-white/5">
                                                    <td className="px-4 py-3 font-bold text-white">{liveData.away_team} Goals</td>
                                                    <td className="px-4 py-3 text-center text-white">{p1?.away_goals ?? '-'}</td>
                                                    <td className="px-4 py-3 text-center text-white">{p2?.away_goals ?? '-'}</td>
                                                    <td className="px-4 py-3 text-center text-white">{p3?.away_goals ?? '-'}</td>
                                                    <td className="px-4 py-3 text-center font-bold text-accent-cyan">{liveData.away_score}</td>
                                                </tr>
                                                <tr className="border-b border-white/10">
                                                    <td className="px-4 py-3 font-bold text-white">{liveData.away_team} xG</td>
                                                    <td className="px-4 py-3 text-center">{p1?.away_xg?.toFixed(2) ?? '-'}</td>
                                                    <td className="px-4 py-3 text-center">{p2?.away_xg?.toFixed(2) ?? '-'}</td>
                                                    <td className="px-4 py-3 text-center">{p3?.away_xg?.toFixed(2) ?? '-'}</td>
                                                    <td className="px-4 py-3 text-center font-bold text-accent-cyan">{liveData.advanced_metrics?.away_xg?.toFixed(2) || '-'}</td>
                                                </tr>
                                                <tr className="border-b border-white/5">
                                                    <td className="px-4 py-3 font-bold text-white">{liveData.home_team} Goals</td>
                                                    <td className="px-4 py-3 text-center text-white">{p1?.home_goals ?? '-'}</td>
                                                    <td className="px-4 py-3 text-center text-white">{p2?.home_goals ?? '-'}</td>
                                                    <td className="px-4 py-3 text-center text-white">{p3?.home_goals ?? '-'}</td>
                                                    <td className="px-4 py-3 text-center font-bold text-accent-magenta">{liveData.home_score}</td>
                                                </tr>
                                                <tr className="border-b border-white/10">
                                                    <td className="px-4 py-3 font-bold text-white">{liveData.home_team} xG</td>
                                                    <td className="px-4 py-3 text-center">{p1?.home_xg?.toFixed(2) ?? '-'}</td>
                                                    <td className="px-4 py-3 text-center">{p2?.home_xg?.toFixed(2) ?? '-'}</td>
                                                    <td className="px-4 py-3 text-center">{p3?.home_xg?.toFixed(2) ?? '-'}</td>
                                                    <td className="px-4 py-3 text-center font-bold text-accent-magenta">{liveData.advanced_metrics?.home_xg?.toFixed(2) || '-'}</td>
                                                </tr>
                                            </>
                                        );
                                    })()}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Scoring Summary - Full Width */}
                    <div className="lg:col-span-3 glass-panel p-6 rounded-xl">
                        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                            <Target className="text-accent-lime" />
                            Scoring Summary
                        </h3>
                        <div className="space-y-3">
                            {liveData.scoring_summary && liveData.scoring_summary.length > 0 ? (
                                liveData.scoring_summary.map((goal, idx) => (
                                    <div key={idx} className="flex items-center gap-4 bg-white/5 p-3 rounded-lg border border-white/5">
                                        <div className="font-mono text-gray-400 w-12">P{goal.period}</div>
                                        <div className="font-mono text-gray-400 w-16">{goal.time}</div>
                                        <div className="font-mono text-white w-12">{goal.team}</div>
                                        <div className="flex-1 text-white">
                                            <span className="font-bold">{goal.scorer}</span>
                                            {goal.assists && goal.assists.length > 0 && (
                                                <span className="text-gray-400 text-sm ml-2">
                                                    ({goal.assists.join(', ')})
                                                </span>
                                            )}
                                        </div>
                                        <div className="font-mono font-bold text-white">
                                            {goal.away_score}-{goal.home_score}
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="text-center text-gray-500 py-4">No goals scored</div>
                            )}
                        </div>
                    </div>

                    {/* Shot Chart - Full Width */}
                    {liveData.shots_data && liveData.shots_data.length > 0 && (
                        <div className="lg:col-span-3 glass-panel p-6 rounded-xl">
                            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                                <Crosshair className="text-accent-cyan" />
                                Shot Chart
                            </h3>
                            <ShotChart
                                shotsData={liveData.shots_data}
                                awayTeam={liveData.away_team}
                                homeTeam={liveData.home_team}
                            />
                        </div>
                    )}
                </motion.div>
            )}


        </div>
    );
};

const GameDetails = () => (
    <ErrorBoundary>
        <GameDetailsContent />
    </ErrorBoundary>
);

export default GameDetails;
