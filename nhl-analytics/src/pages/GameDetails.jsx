import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { nhlApi } from '../api/nhl';
import { backendApi } from '../api/backend';
import { motion } from 'framer-motion';
import { TrendingUp, Target, Zap, Activity, Shield, Crosshair, ArrowLeft, Clock, Users } from 'lucide-react';
import clsx from 'clsx';

import ErrorBoundary from '../components/ErrorBoundary';
import ShotChart from '../components/ShotChart';
import PeriodStatsTable from '../components/PeriodStatsTable';

const GameDetailsContent = () => {
    const { id } = useParams();
    const [gameData, setGameData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [liveData, setLiveData] = useState(null);
    const [activeTab, setActiveTab] = useState('overview');

    useEffect(() => {
        const fetchGameData = async () => {
            try {
                const [data, liveGameData] = await Promise.all([
                    nhlApi.getGameCenter(id),
                    backendApi.getLiveGame(id).catch(() => null)
                ]);

                setGameData(data);
                setLiveData(liveGameData);
            } catch (error) {
                console.error('Failed to fetch game data:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchGameData();
        // Poll for live data every 30s if game is live
        const interval = setInterval(() => {
            if (gameData?.boxscore?.gameState === 'LIVE' || gameData?.boxscore?.gameState === 'CRIT') {
                backendApi.getLiveGame(id)
                    .then(data => setLiveData(data))
                    .catch(err => console.error('Polling error:', err));
            }
        }, 30000);

        return () => clearInterval(interval);
    }, [id, gameData?.boxscore?.gameState]);

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

    if (!gameData) {
        return (
            <div className="flex flex-col items-center justify-center h-[60vh] text-center">
                <h2 className="text-2xl font-display font-bold mb-4">Game Data Not Available</h2>
                <Link to="/" className="px-6 py-2 rounded-lg bg-accent-primary text-bg-primary font-bold hover:bg-accent-secondary transition-colors">
                    Back to Dashboard
                </Link>
            </div>
        );
    }

    const { awayTeam, homeTeam, gameState, period, clock } = gameData.boxscore || {};
    const isLive = gameState === 'LIVE' || gameState === 'CRIT';
    const isFinal = gameState === 'FINAL' || gameState === 'OFF';

    // Helper for metric cards
    const MetricCard = ({ title, icon: Icon, children, className }) => (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={clsx("glass-card p-6", className)}
        >
            <div className="flex items-center gap-3 mb-4">
                <div className="p-2 rounded-lg bg-white/5">
                    <Icon className="w-5 h-5 text-accent-primary" />
                </div>
                <h3 className="font-display font-bold text-lg tracking-wide">{title}</h3>
            </div>
            {children}
        </motion.div>
    );

    // Helper for comparison rows
    const ComparisonRow = ({ label, awayVal, homeVal, format = (v) => v }) => {
        const awayNum = parseFloat(awayVal) || 0;
        const homeNum = parseFloat(homeVal) || 0;
        const total = awayNum + homeNum;
        const awayPct = total > 0 ? (awayNum / total) * 100 : 50;

        return (
            <div className="mb-4">
                <div className="flex justify-between text-sm font-mono mb-2">
                    <span className={clsx(awayNum > homeNum ? "text-accent-primary font-bold" : "text-text-muted")}>
                        {format(awayVal)}
                    </span>
                    <span className="text-text-secondary uppercase text-xs tracking-wider">{label}</span>
                    <span className={clsx(homeNum > awayNum ? "text-accent-secondary font-bold" : "text-text-muted")}>
                        {format(homeVal)}
                    </span>
                </div>
                <div className="h-1.5 bg-white/5 rounded-full overflow-hidden flex">
                    <div
                        className="h-full bg-accent-primary transition-all duration-500"
                        style={{ width: `${awayPct}%` }}
                    />
                    <div
                        className="h-full bg-accent-secondary transition-all duration-500"
                        style={{ width: `${100 - awayPct}%` }}
                    />
                </div>
            </div>
        );
    };

    return (
        <div className="space-y-8 pb-12">
            {/* Header Section */}
            <div className="relative rounded-3xl overflow-hidden bg-gradient-to-b from-bg-secondary to-bg-primary border border-white/5 shadow-2xl">
                {/* Background Effects */}
                <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
                    <div className="absolute top-0 left-1/4 w-96 h-96 bg-accent-primary/10 rounded-full blur-3xl -translate-y-1/2"></div>
                    <div className="absolute top-0 right-1/4 w-96 h-96 bg-accent-secondary/10 rounded-full blur-3xl -translate-y-1/2"></div>
                </div>

                <div className="relative z-10 p-8 md:p-12">
                    <Link to="/" className="inline-flex items-center gap-2 text-text-muted hover:text-white mb-8 transition-colors group">
                        <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
                        <span className="font-mono text-sm">BACK TO DASHBOARD</span>
                    </Link>

                    <div className="flex flex-col md:flex-row items-center justify-between gap-8">
                        {/* Away Team */}
                        <div className="flex flex-col items-center gap-4 flex-1">
                            <img src={awayTeam.logo} alt={awayTeam.abbrev} className="w-24 h-24 md:w-32 md:h-32 object-contain drop-shadow-2xl" />
                            <div className="text-center">
                                <h2 className="text-4xl md:text-5xl font-display font-bold tracking-tighter">{awayTeam.abbrev}</h2>
                                <p className="text-text-muted font-mono mt-1">AWAY</p>
                            </div>
                        </div>

                        {/* Score / Status */}
                        <div className="flex flex-col items-center justify-center px-8 py-4 bg-white/5 rounded-2xl backdrop-blur-md border border-white/5 min-w-[200px]">
                            {isLive || isFinal ? (
                                <div className="flex items-center gap-8">
                                    <span className="text-6xl md:text-7xl font-display font-bold text-white team-gradient-text" style={{ '--team-primary': 'var(--color-accent-primary)' }}>{awayTeam.score}</span>
                                    <div className="h-12 w-px bg-white/10"></div>
                                    <span className="text-6xl md:text-7xl font-display font-bold text-white team-gradient-text" style={{ '--team-primary': 'var(--color-accent-secondary)' }}>{homeTeam.score}</span>
                                </div>
                            ) : (
                                <div className="text-4xl font-display font-bold text-text-muted">VS</div>
                            )}

                            <div className="mt-4 flex items-center gap-2">
                                {isLive ? (
                                    <>
                                        <span className="relative flex h-2 w-2">
                                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-color-success opacity-75"></span>
                                            <span className="relative inline-flex rounded-full h-2 w-2 bg-color-success"></span>
                                        </span>
                                        <span className="font-mono text-color-success font-bold">{period} - {clock}</span>
                                    </>
                                ) : (
                                    <span className="font-mono text-text-muted">{gameState}</span>
                                )}
                            </div>
                        </div>

                        {/* Home Team */}
                        <div className="flex flex-col items-center gap-4 flex-1">
                            <img src={homeTeam.logo} alt={homeTeam.abbrev} className="w-24 h-24 md:w-32 md:h-32 object-contain drop-shadow-2xl" />
                            <div className="text-center">
                                <h2 className="text-4xl md:text-5xl font-display font-bold tracking-tighter">{homeTeam.abbrev}</h2>
                                <p className="text-text-muted font-mono mt-1">HOME</p>
                            </div>
                        </div>
                    </div>

                    {/* Win Probability Bar */}
                    {liveData?.prediction && (
                        <div className="mt-12 max-w-3xl mx-auto">
                            <div className="flex justify-between text-sm font-mono mb-3">
                                <span className="text-accent-primary font-bold">
                                    {(liveData.prediction.calibrated_away_prob * 100).toFixed(1)}% WIN PROB
                                </span>
                                <span className="text-accent-secondary font-bold">
                                    {(liveData.prediction.calibrated_home_prob * 100).toFixed(1)}% WIN PROB
                                </span>
                            </div>
                            <div className="h-3 bg-white/5 rounded-full overflow-hidden flex relative">
                                <div
                                    className="h-full bg-gradient-to-r from-accent-primary to-blue-500 relative"
                                    style={{ width: `${liveData.prediction.calibrated_away_prob * 100}%` }}
                                >
                                    <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
                                </div>
                                <div
                                    className="h-full bg-gradient-to-l from-accent-secondary to-purple-500 relative"
                                    style={{ width: `${liveData.prediction.calibrated_home_prob * 100}%` }}
                                >
                                    <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
                                </div>

                                {/* Center Marker */}
                                <div className="absolute top-0 bottom-0 left-1/2 w-px bg-white/50 transform -translate-x-1/2 z-10"></div>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Navigation Tabs */}
            <div className="flex justify-center gap-4 border-b border-white/10 pb-1">
                {['overview', 'advanced', 'visuals', 'rosters'].map((tab) => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={clsx(
                            "px-6 py-3 font-display font-bold tracking-wide text-sm transition-all relative",
                            activeTab === tab ? "text-white" : "text-text-muted hover:text-text-secondary"
                        )}
                    >
                        {tab.toUpperCase()}
                        {activeTab === tab && (
                            <motion.div
                                layoutId="activeTab"
                                className="absolute bottom-0 left-0 right-0 h-0.5 bg-accent-primary shadow-[0_0_10px_var(--color-accent-primary)]"
                            />
                        )}
                    </button>
                ))}
            </div>

            {/* Content Sections */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column - Main Stats */}
                <div className="lg:col-span-2 space-y-8">
                    {/* Period Stats Table */}
                    <section>
                        <div className="flex items-center gap-3 mb-6">
                            <Clock className="w-6 h-6 text-accent-primary" />
                            <h3 className="text-xl font-display font-bold">PERIOD PERFORMANCE</h3>
                        </div>
                        {liveData?.period_stats ? (
                            <PeriodStatsTable
                                periodStats={liveData.period_stats}
                                awayTeam={awayTeam}
                                homeTeam={homeTeam}
                            />
                        ) : (
                            <div className="glass-card p-6 text-center text-text-muted">
                                No period stats available yet.
                            </div>
                        )}
                    </section>

                    {/* Advanced Metrics Grid */}
                    <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <MetricCard title="SHOT QUALITY" icon={Crosshair}>
                            <ComparisonRow
                                label="EXPECTED GOALS (xG)"
                                awayVal={liveData?.advanced_metrics?.xg?.away_total}
                                homeVal={liveData?.advanced_metrics?.xg?.home_total}
                                format={(v) => parseFloat(v || 0).toFixed(2)}
                            />
                            <ComparisonRow
                                label="HIGH DANGER CHANCES"
                                awayVal={liveData?.advanced_metrics?.shot_quality?.high_danger_shots?.away}
                                homeVal={liveData?.advanced_metrics?.shot_quality?.high_danger_shots?.home}
                            />
                            <ComparisonRow
                                label="SHOOTING %"
                                awayVal={liveData?.advanced_metrics?.shot_quality?.shooting_percentage?.away}
                                homeVal={liveData?.advanced_metrics?.shot_quality?.shooting_percentage?.home}
                                format={(v) => v + '%'}
                            />
                        </MetricCard>

                        <MetricCard title="PRESSURE" icon={Zap}>
                            <ComparisonRow
                                label="OFFENSIVE ZONE SHOTS"
                                awayVal={liveData?.advanced_metrics?.pressure?.oz_shots?.away}
                                homeVal={liveData?.advanced_metrics?.pressure?.oz_shots?.home}
                            />
                            <ComparisonRow
                                label="SUSTAINED PRESSURE"
                                awayVal={liveData?.advanced_metrics?.pressure?.sustained_pressure?.away}
                                homeVal={liveData?.advanced_metrics?.pressure?.sustained_pressure?.home}
                            />
                            <ComparisonRow
                                label="RUSH CHANCES"
                                awayVal={liveData?.advanced_metrics?.pressure?.rush_shots?.away}
                                homeVal={liveData?.advanced_metrics?.pressure?.rush_shots?.home}
                            />
                        </MetricCard>

                        <MetricCard title="DEFENSE" icon={Shield}>
                            <ComparisonRow
                                label="BLOCKED SHOTS"
                                awayVal={liveData?.advanced_metrics?.defense?.blocked_shots?.away}
                                homeVal={liveData?.advanced_metrics?.defense?.blocked_shots?.home}
                            />
                            <ComparisonRow
                                label="TAKEAWAYS"
                                awayVal={liveData?.advanced_metrics?.defense?.takeaways?.away}
                                homeVal={liveData?.advanced_metrics?.defense?.takeaways?.home}
                            />
                            <ComparisonRow
                                label="GIVEAWAYS"
                                awayVal={liveData?.advanced_metrics?.defense?.giveaways?.away}
                                homeVal={liveData?.advanced_metrics?.defense?.giveaways?.home}
                            />
                        </MetricCard>

                        <MetricCard title="MOVEMENT" icon={Activity}>
                            <ComparisonRow
                                label="LATERAL MOVEMENT"
                                awayVal={liveData?.advanced_metrics?.movement?.lateral_movement?.away}
                                homeVal={liveData?.advanced_metrics?.movement?.lateral_movement?.home}
                                format={(v) => parseFloat(v || 0).toFixed(1)}
                            />
                            <ComparisonRow
                                label="N-S MOVEMENT"
                                awayVal={liveData?.advanced_metrics?.movement?.longitudinal_movement?.away}
                                homeVal={liveData?.advanced_metrics?.movement?.longitudinal_movement?.home}
                                format={(v) => parseFloat(v || 0).toFixed(1)}
                            />
                        </MetricCard>
                    </section>
                </div>

                {/* Right Column - Visuals & Players */}
                <div className="space-y-8">
                    {/* Shot Chart */}
                    <section className="glass-card p-6">
                        <div className="flex items-center gap-3 mb-6">
                            <Target className="w-6 h-6 text-accent-secondary" />
                            <h3 className="text-xl font-display font-bold">SHOT MAP</h3>
                        </div>
                        <div className="aspect-[2/1] bg-white/5 rounded-xl overflow-hidden relative">
                            <ShotChart
                                shots={liveData?.shots_data || []}
                                homeTeam={homeTeam.abbrev}
                                awayTeam={awayTeam.abbrev}
                            />
                        </div>
                        <div className="flex justify-center gap-6 mt-4 text-xs font-mono text-text-muted">
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-full bg-accent-primary"></div>
                                <span>{awayTeam.abbrev} GOAL</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-full border border-accent-primary"></div>
                                <span>{awayTeam.abbrev} SHOT</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-full bg-accent-secondary"></div>
                                <span>{homeTeam.abbrev} GOAL</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-full border border-accent-secondary"></div>
                                <span>{homeTeam.abbrev} SHOT</span>
                            </div>
                        </div>
                    </section>

                    {/* Top Players */}
                    <section className="glass-card p-6">
                        <div className="flex items-center gap-3 mb-6">
                            <Users className="w-6 h-6 text-color-success" />
                            <h3 className="text-xl font-display font-bold">TOP PERFORMERS</h3>
                        </div>
                        <div className="space-y-4">
                            {liveData?.top_players?.map((player, idx) => (
                                <div key={idx} className="flex items-center gap-4 p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors">
                                    <div className="font-display font-bold text-2xl text-white/20 w-8 text-center">
                                        {idx + 1}
                                    </div>
                                    <div className="flex-1">
                                        <div className="font-bold text-white">{player.player}</div>
                                        <div className="text-xs font-mono text-text-muted flex gap-2">
                                            <span>{player.team}</span>
                                            <span>•</span>
                                            <span>{player.position}</span>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div className="font-mono font-bold text-color-success">{player.game_score?.toFixed(1)} GS</div>
                                        <div className="text-xs font-mono text-text-muted">{player.xg?.toFixed(2)} xG</div>
                                    </div>
                                </div>
                            ))}
                            {!liveData?.top_players && (
                                <div className="text-center text-text-muted py-4">No player data available</div>
                            )}
                        </div>
                    </section>
                </div>
            </div>
        </div>
    );
};

const GameDetails = () => (
    <ErrorBoundary>
        <GameDetailsContent />
    </ErrorBoundary>
);

export default GameDetails;
