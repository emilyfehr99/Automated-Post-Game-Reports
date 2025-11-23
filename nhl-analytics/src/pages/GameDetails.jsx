import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { useParams, Link } from 'react-router-dom';
import { nhlApi } from '../api/nhl';
import { backendApi } from '../api/backend';
import { motion } from 'framer-motion';
import { TrendingUp, Target, Zap, Activity, Shield, Crosshair, ArrowLeft, Clock, Users } from 'lucide-react';
import clsx from 'clsx';

import ErrorBoundary from '../components/ErrorBoundary';
import ShotChart from '../components/ShotChart';
import PeriodStatsTable from '../components/PeriodStatsTable';
import LinesPairings from '../components/LinesPairings';

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
const ComparisonRow = ({ label, awayVal, homeVal, format = (v) => v, awayTeam, homeTeam }) => {
    const awayNum = parseFloat(awayVal) || 0;
    const homeNum = parseFloat(homeVal) || 0;
    const total = awayNum + homeNum;
    const awayPct = total > 0 ? (awayNum / total) * 100 : 50;

    return (
        <div className="mb-4">
            <div className="flex justify-between text-sm font-mono mb-2">
                <div className="flex items-center gap-2">
                    {awayTeam && <img src={awayTeam.logo} alt={awayTeam.abbrev} className="w-6 h-6 opacity-60" />}
                    <span className={clsx(awayNum > homeNum ? "text-accent-primary font-bold" : "text-text-muted")}>
                        {format(awayVal)}
                    </span>
                </div>
                <span className="text-text-secondary uppercase text-xs tracking-wider">{label}</span>
                <div className="flex items-center gap-2">
                    <span className={clsx(homeNum > awayNum ? "text-accent-secondary font-bold" : "text-text-muted")}>
                        {format(homeVal)}
                    </span>
                    {homeTeam && <img src={homeTeam.logo} alt={homeTeam.abbrev} className="w-6 h-6 opacity-60" />}
                </div>
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

// Team Colors Mapping
const TEAM_COLORS = {
    ANA: '#F47A38', ARI: '#8C2633', BOS: '#FFB81C', BUF: '#FCB514', CGY: '#C8102E',
    CAR: '#CC0000', CHI: '#CF0A2C', COL: '#6F263D', CBJ: '#002654', DAL: '#006847',
    DET: '#CE1126', EDM: '#FF4C00', FLA: '#B9975B', LAK: '#111111', MIN: '#154734',
    MTL: '#AF1E2D', NSH: '#FFB81C', NJD: '#CE1126', NYI: '#00539B', NYR: '#0038A8',
    OTT: '#C52032', PHI: '#F74902', PIT: '#FCB514', SJS: '#006D75', SEA: '#99D9D9',
    STL: '#002F87', TBL: '#002868', TOR: '#00205B', UTA: '#71AFE5', VAN: '#00205B',
    VGK: '#B4975A', WPG: '#041E42', WSH: '#041E42'
};

const getTeamColor = (abbr) => TEAM_COLORS[abbr] || '#FFFFFF';

const METRICS_CONFIG = [
    { key: 'rank', liveKey: 'rank', label: 'RANK' },
    { key: 'gp', liveKey: 'games_played', label: 'GP' },
    { key: 'l10', liveKey: 'l10', label: 'L10' },
    { key: 'streak', liveKey: 'streak', label: 'STREAK' },
    { key: 'gf', liveKey: 'goals_for', label: 'GOALS FOR' },
    { key: 'ga', liveKey: 'goals_against', label: 'GOALS AGAINST' },
    { key: 'w', liveKey: 'wins', label: 'WINS' },
    { key: 'l', liveKey: 'losses', label: 'LOSSES' },
    { key: 'otl', liveKey: 'ot_losses', label: 'OT LOSSES' },
    { key: 'pts', liveKey: 'points', label: 'POINTS' },
    { key: 'pPct', liveKey: 'point_pct', label: 'POINT %', format: (v) => parseFloat(v || 0).toFixed(3) },
    { key: 'diff', liveKey: 'goal_diff', label: 'GOAL DIFF' },
    { key: 'gs', liveKey: 'game_score', label: 'GAME SCORE', format: (v) => parseFloat(v || 0).toFixed(1) },
    { key: 'xg', liveKey: 'xg', label: 'EXPECTED GOALS', format: (v) => parseFloat(v || 0).toFixed(2) },
    { key: 'hdc', liveKey: 'hdc', label: 'HIGH DANGER CHANCES' },
    { key: 'hdca', liveKey: 'hdca', label: 'HD CHANCES AGAINST' },
    { key: 'ozs', liveKey: 'ozs', label: 'OFF ZONE SHOTS' },
    { key: 'nzs', liveKey: 'nzs', label: 'NEUTRAL ZONE SHOTS' },
    { key: 'dzs', liveKey: 'dzs', label: 'DEF ZONE SHOTS' },
    { key: 'fc', liveKey: 'fc', label: 'FORECHECK SHOTS' },
    { key: 'rush', liveKey: 'rush', label: 'RUSH SHOTS' },
    { key: 'nzts', liveKey: 'nzts', label: 'NEUTRAL ZONE TURNOVERS' },
    { key: 'nztsa', liveKey: 'nztsa', label: 'NZ TURNOVERS/SA' },
    { key: 'lat', liveKey: 'lateral', label: 'LATERAL MOVEMENT', format: (v) => parseFloat(v || 0).toFixed(1) },
    { key: 'long_movement', liveKey: 'longitudinal', label: 'N-S MOVEMENT', format: (v) => parseFloat(v || 0).toFixed(1) },
    { key: 'shots', liveKey: 'shots', label: 'SHOTS ON GOAL' },
    { key: 'goals', liveKey: 'goals', label: 'GOALS', format: (v) => parseFloat(v || 0).toFixed(0) },
    { key: 'ga_gp', liveKey: 'ga_gp', label: 'GOALS AGAINST/GP', format: (v) => parseFloat(v || 0).toFixed(2) },
    { key: 'corsi_pct', liveKey: 'corsi_pct', label: 'CORSI %', format: (v) => v + '%' },
    { key: 'hits', liveKey: 'hits', label: 'HITS' },
    { key: 'blocks', liveKey: 'blocked_shots', label: 'BLOCKED SHOTS' },
    { key: 'giveaways', liveKey: 'giveaways', label: 'GIVEAWAYS' },
    { key: 'takeaways', liveKey: 'takeaways', label: 'TAKEAWAYS' },
    { key: 'pim', liveKey: 'pim', label: 'PIM' },
    { key: 'pp_pct', liveKey: 'pp_pct', label: 'POWER PLAY %', format: (v) => v + '%' },
    { key: 'pk_pct', liveKey: 'pk_pct', label: 'PENALTY KILL %', format: (v) => v + '%' },
    { key: 'fo_pct', liveKey: 'fo_pct', label: 'FACEOFF %', format: (v) => v + '%' },
];

const PreGameHeatmap = ({ preGameData, homeTeam, awayTeam }) => {
    const [hoveredPoint, setHoveredPoint] = React.useState(null);
    const [tooltipPos, setTooltipPos] = React.useState({ x: 0, y: 0 });
    const containerRef = React.useRef(null);

    const handlePointHover = (point, event, team) => {
        // Calculate position relative to viewport
        const mouseX = event.clientX;
        const mouseY = event.clientY;

        // Tooltip dimensions (approximate)
        const tooltipWidth = 220;
        const tooltipHeight = 120;

        // Calculate position with boundary detection
        let left = mouseX + 15;
        let top = mouseY - 10;

        // Keep tooltip within viewport bounds
        if (left + tooltipWidth > window.innerWidth) {
            left = mouseX - tooltipWidth - 15;
        }
        if (top + tooltipHeight > window.innerHeight) {
            top = window.innerHeight - tooltipHeight - 10;
        }
        if (top < 0) {
            top = 10;
        }

        setTooltipPos({ x: left, y: top });
        setHoveredPoint({ ...point, team });
    };

    const clearHover = () => {
        setHoveredPoint(null);
    };

    return (
        <section className="glass-card p-6">
            <div className="flex items-center gap-3 mb-6">
                <Target className="w-6 h-6 text-accent-cyan" />
                <h3 className="text-xl font-display font-bold">PRE-GAME INTEL: SHOT HEATMAP (L10 GAMES)</h3>
            </div>
            <div className="max-w-3xl mx-auto">
                <div ref={containerRef} className="relative aspect-[200/85] bg-white/5 rounded-xl border border-white/10 overflow-hidden">
                    <img src="/rink.jpeg" alt="Rink" className="absolute inset-0 w-full h-full object-fill" />

                    {/* Team Logos on Ice */}
                    <div className="absolute left-[15%] top-1/2 -translate-y-1/2 z-10">
                        <img src={awayTeam.logo} alt={awayTeam.abbrev} className="w-16 h-16 opacity-20" />
                    </div>
                    <div className="absolute right-[15%] top-1/2 -translate-y-1/2 z-10">
                        <img src={homeTeam.logo} alt={homeTeam.abbrev} className="w-16 h-16 opacity-20" />
                    </div>

                    {/* Home Team Points (Right Side) */}
                    {preGameData.heatmaps.home?.goals_for?.map((point, i) => (
                        <div
                            key={`home-goal-${i}`}
                            className="absolute w-3 h-3 rounded-full border border-white shadow-lg z-20 transform -translate-x-1/2 -translate-y-1/2 cursor-pointer hover:scale-150 transition-transform"
                            style={{
                                backgroundColor: getTeamColor(homeTeam.abbrev),
                                left: `${(Math.abs(point.x) + 100) / 2}%`,
                                top: `${(42.5 - point.y) / 0.85}%`
                            }}
                            onMouseEnter={(e) => handlePointHover(point, e, homeTeam.abbrev)}
                            onMouseLeave={clearHover}
                        />
                    ))}
                    {preGameData.heatmaps.home?.shots_for?.map((point, i) => (
                        <div
                            key={`home-shot-${i}`}
                            className="absolute w-1.5 h-1.5 rounded-full opacity-60 blur-[0.5px] transform -translate-x-1/2 -translate-y-1/2 cursor-pointer hover:scale-150 hover:opacity-100 transition-all"
                            style={{
                                backgroundColor: getTeamColor(homeTeam.abbrev),
                                left: `${(Math.abs(point.x) + 100) / 2}%`,
                                top: `${(42.5 - point.y) / 0.85}%`
                            }}
                            onMouseEnter={(e) => handlePointHover(point, e, homeTeam.abbrev)}
                            onMouseLeave={clearHover}
                        />
                    ))}

                    {/* Away Team Points (Left Side) */}
                    {preGameData.heatmaps.away?.goals_for?.map((point, i) => (
                        <div
                            key={`away-goal-${i}`}
                            className="absolute w-3 h-3 rounded-full border border-white shadow-lg z-20 transform -translate-x-1/2 -translate-y-1/2 cursor-pointer hover:scale-150 transition-transform"
                            style={{
                                backgroundColor: getTeamColor(awayTeam.abbrev),
                                left: `${(-Math.abs(point.x) + 100) / 2}%`,
                                top: `${(42.5 - point.y) / 0.85}%`
                            }}
                            onMouseEnter={(e) => handlePointHover(point, e, awayTeam.abbrev)}
                            onMouseLeave={clearHover}
                        />
                    ))}
                    {preGameData.heatmaps.away?.shots_for?.map((point, i) => (
                        <div
                            key={`away-shot-${i}`}
                            className="absolute w-1.5 h-1.5 rounded-full opacity-60 blur-[0.5px] transform -translate-x-1/2 -translate-y-1/2 cursor-pointer hover:scale-150 hover:opacity-100 transition-all"
                            style={{
                                backgroundColor: getTeamColor(awayTeam.abbrev),
                                left: `${(-Math.abs(point.x) + 100) / 2}%`,
                                top: `${(42.5 - point.y) / 0.85}%`
                            }}
                            onMouseEnter={(e) => handlePointHover(point, e, awayTeam.abbrev)}
                            onMouseLeave={clearHover}
                        />
                    ))}

                    {/* Tooltip */}
                    {/* Tooltip - Rendered via Portal */}
                    {hoveredPoint && createPortal(
                        <div
                            className="fixed z-[9999] bg-black/95 border border-white/20 rounded-lg p-3 shadow-2xl backdrop-blur-md min-w-[200px] max-w-[250px] pointer-events-none"
                            style={{
                                left: `${tooltipPos.x}px`,
                                top: `${tooltipPos.y}px`,
                            }}
                        >
                            <div className="text-xs font-mono space-y-1">
                                <div className="flex items-center gap-2 mb-2 pb-2 border-b border-white/10">
                                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: getTeamColor(hoveredPoint.team) }}></div>
                                    <span className="font-bold text-white">{hoveredPoint.team}</span>
                                </div>
                                {hoveredPoint.shooter && (
                                    <div className="text-text-muted">
                                        <span className="text-white font-semibold">{hoveredPoint.shooter}</span>
                                    </div>
                                )}
                                {hoveredPoint.xg !== undefined && (
                                    <div>
                                        <span className="text-accent-cyan">xG:</span>
                                        <span className="text-white ml-2">{(hoveredPoint.xg || 0).toFixed(2)}</span>
                                    </div>
                                )}
                                {hoveredPoint.shotType && (
                                    <div>
                                        <span className="text-accent-magenta">Shot Type:</span>
                                        <span className="text-white ml-2 capitalize">{hoveredPoint.shotType}</span>
                                    </div>
                                )}
                                {hoveredPoint.movement && (
                                    <div>
                                        <span className="text-accent-lime">Movement:</span>
                                        <span className="text-white ml-2 capitalize">{hoveredPoint.movement}</span>
                                    </div>
                                )}
                            </div>
                        </div>,
                        document.body
                    )}
                </div>
            </div>
        </section>
    );
};

const constructPeriodStats = (metrics) => {
    if (!metrics || !metrics.away_period_stats) return null;

    const periods = [];
    // Get max length of any stat array to determine periods
    const maxLen = Math.max(
        (metrics.away_period_stats.shots || []).length,
        (metrics.home_period_stats.shots || []).length
    );

    for (let i = 0; i < maxLen; i++) {
        periods.push({
            period: i < 3 ? ['1st', '2nd', '3rd'][i] : (i === 3 ? 'OT' : 'SO'),
            away_stats: {
                goals: metrics.away_period_goals?.[i] || 0,
                shots: metrics.away_period_stats.shots?.[i] || 0,
                corsi: metrics.away_period_stats.corsi_pct?.[i] || 0,
                xg: metrics.away_xg_by_period?.[i] || 0,
                hits: metrics.away_period_stats.hits?.[i] || 0,
                faceoff_pct: metrics.away_period_stats.fo_pct?.[i] || 0,
                pim: metrics.away_period_stats.pim?.[i] || 0,
                blocked_shots: metrics.away_period_stats.bs?.[i] || 0,
                giveaways: metrics.away_period_stats.gv?.[i] || 0,
                takeaways: metrics.away_period_stats.tk?.[i] || 0,
                nzt: metrics.away_zone_metrics?.nz_turnovers?.[i] || 0,
                ozs: metrics.away_zone_metrics?.oz_originating_shots?.[i] || 0,
                rush: metrics.away_zone_metrics?.rush_sog?.[i] || 0
            },
            home_stats: {
                goals: metrics.home_period_goals?.[i] || 0,
                shots: metrics.home_period_stats.shots?.[i] || 0,
                corsi: metrics.home_period_stats.corsi_pct?.[i] || 0,
                xg: metrics.home_xg_by_period?.[i] || 0,
                hits: metrics.home_period_stats.hits?.[i] || 0,
                faceoff_pct: metrics.home_period_stats.fo_pct?.[i] || 0,
                pim: metrics.home_period_stats.pim?.[i] || 0,
                blocked_shots: metrics.home_period_stats.bs?.[i] || 0,
                giveaways: metrics.home_period_stats.gv?.[i] || 0,
                takeaways: metrics.home_period_stats.tk?.[i] || 0,
                nzt: metrics.home_zone_metrics?.nz_turnovers?.[i] || 0,
                ozs: metrics.home_zone_metrics?.oz_originating_shots?.[i] || 0,
                rush: metrics.home_zone_metrics?.rush_sog?.[i] || 0
            }
        });
    }
    return periods;
};

const GameDetailsContent = () => {
    const { id } = useParams();
    const [gameData, setGameData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [liveData, setLiveData] = useState(null);
    const [linesData, setLinesData] = useState({ away: null, home: null });
    const [activeTab, setActiveTab] = useState('overview');
    const [preGameData, setPreGameData] = useState({
        heatmaps: { home: [], away: [] },
        metrics: { home: {}, away: {} }
    });

    useEffect(() => {
        let mounted = true;

        const fetchGameData = async () => {
            try {
                const data = await nhlApi.getGameCenter(id);
                if (!mounted) return;
                setGameData(data);

                // If game is live or finished, fetch live data
                if (data?.boxscore?.gameState === 'LIVE' ||
                    data?.boxscore?.gameState === 'CRIT' ||
                    data?.boxscore?.gameState === 'FINAL' ||
                    data?.boxscore?.gameState === 'OFF') {
                    backendApi.getLiveGame(id)
                        .then(liveData => {
                            if (mounted) setLiveData(liveData);
                        })
                        .catch(() => null);
                }
                // If game is scheduled/pre-game, fetch pre-game data
                else if (data?.boxscore) {
                    const { homeTeam, awayTeam } = data.boxscore;
                    fetchPreGameData(homeTeam.abbrev, awayTeam.abbrev);
                }
            } catch (error) {
                console.error('Failed to fetch game data:', error);
            } finally {
                if (mounted) setLoading(false);
            }
        };

        const fetchPreGameData = async (homeAbbr, awayAbbr) => {
            try {
                const [homeHeatmap, awayHeatmap, allMetrics] = await Promise.all([
                    backendApi.getTeamHeatmap(homeAbbr),
                    backendApi.getTeamHeatmap(awayAbbr),
                    backendApi.getTeamMetrics()
                ]);

                if (mounted) {
                    setPreGameData({
                        heatmaps: {
                            home: homeHeatmap,
                            away: awayHeatmap
                        },
                        metrics: {
                            home: allMetrics[homeAbbr] || {},
                            away: allMetrics[awayAbbr] || {}
                        }
                    });
                }
            } catch (error) {
                console.error('Failed to fetch pre-game data:', error);
            }
        };

        fetchGameData();

        // Poll for updates every 30s
        const interval = setInterval(fetchGameData, 30000);

        return () => {
            mounted = false;
            clearInterval(interval);
        };
    }, [id]);

    // Fetch lines when game data is available
    useEffect(() => {
        if (gameData?.boxscore) {
            const awayAbbrev = gameData.boxscore.awayTeam?.abbrev;
            const homeAbbrev = gameData.boxscore.homeTeam?.abbrev;

            if (awayAbbrev && homeAbbrev) {
                const fetchLines = async () => {
                    try {
                        const [awayLinesResponse, homeLinesResponse] = await Promise.all([
                            fetch(`${import.meta.env.MODE === 'production' ? 'https://nhl-analytics-api.onrender.com' : (import.meta.env.VITE_API_URL || 'http://localhost:5002')}/api/lines/${awayAbbrev}`),
                            fetch(`${import.meta.env.MODE === 'production' ? 'https://nhl-analytics-api.onrender.com' : (import.meta.env.VITE_API_URL || 'http://localhost:5002')}/api/lines/${homeAbbrev}`)
                        ]);

                        const awayLines = await awayLinesResponse.json();
                        const homeLines = await homeLinesResponse.json();

                        if (!awayLines.error && !homeLines.error) {
                            setLinesData({ away: awayLines, home: homeLines });
                        }
                    } catch (e) {
                        console.error("Failed to fetch lines", e);
                    }
                };
                fetchLines();
            }
        }
    }, [gameData?.boxscore?.awayTeam?.abbrev, gameData?.boxscore?.homeTeam?.abbrev]);

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

    const boxscore = gameData?.boxscore || gameData?.game_center?.boxscore || {};
    const { awayTeam, homeTeam, gameState, period, clock } = boxscore;

    // Defensive check: if we don't have team data, show error
    if (!awayTeam || !homeTeam) {
        return (
            <div className="flex flex-col items-center justify-center h-[60vh] text-center">
                <h2 className="text-2xl font-display font-bold mb-4">Game Data Incomplete</h2>
                <p className="text-text-muted mb-4">Unable to load team information</p>
                <Link to="/" className="px-6 py-2 rounded-lg bg-accent-primary text-bg-primary font-bold hover:bg-accent-secondary transition-colors">
                    Back to Dashboard
                </Link>
            </div>
        );
    }

    const isLive = gameState === 'LIVE' || gameState === 'CRIT';
    const isFinal = gameState === 'FINAL' || gameState === 'OFF';


    const renderTabContent = () => {
        // PRE-GAME CONTENT
        if (!isLive && !isFinal) {
            switch (activeTab) {
                case 'lines':
                    return (
                        <LinesPairings
                            boxscore={gameData.boxscore}
                            awayTeam={awayTeam}
                            homeTeam={homeTeam}
                            awayLines={linesData.away}
                            homeLines={linesData.home}
                        />
                    );
                case 'visuals':
                    return (
                        <PreGameHeatmap
                            preGameData={preGameData}
                            homeTeam={homeTeam}
                            awayTeam={awayTeam}
                        />
                    );
                case 'advanced':
                    return (
                        <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <MetricCard title="OFFENSE" icon={Zap}>
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="GAME SCORE"
                                    awayVal={preGameData.metrics.away?.gs}
                                    homeVal={preGameData.metrics.home?.gs}
                                    format={v => parseFloat(v || 0).toFixed(1)}
                                />
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="GOALS/GP"
                                    awayVal={preGameData.metrics.away?.goals}
                                    homeVal={preGameData.metrics.home?.goals}
                                    format={v => parseFloat(v || 0).toFixed(2)}
                                />
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="xGOALS/GP"
                                    awayVal={preGameData.metrics.away?.xg}
                                    homeVal={preGameData.metrics.home?.xg}
                                    format={v => parseFloat(v || 0).toFixed(2)}
                                />
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="SHOTS/GP"
                                    awayVal={preGameData.metrics.away?.shots}
                                    homeVal={preGameData.metrics.home?.shots}
                                    format={v => parseFloat(v || 0).toFixed(1)}
                                />
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="HIGH DANGER"
                                    awayVal={preGameData.metrics.away?.hdc}
                                    homeVal={preGameData.metrics.home?.hdc}
                                    format={v => parseFloat(v || 0).toFixed(1)}
                                />
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="OFF ZONE SHOTS"
                                    awayVal={preGameData.metrics.away?.ozs}
                                    homeVal={preGameData.metrics.home?.ozs}
                                />
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="RUSH CHANCES"
                                    awayVal={preGameData.metrics.away?.rush}
                                    homeVal={preGameData.metrics.home?.rush}
                                />
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="FORECHECK"
                                    awayVal={preGameData.metrics.away?.fc}
                                    homeVal={preGameData.metrics.home?.fc}
                                />
                            </MetricCard>

                            <MetricCard title="DEFENSE" icon={Shield}>
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="GA/GP"
                                    awayVal={preGameData.metrics.away?.ga_gp}
                                    homeVal={preGameData.metrics.home?.ga_gp}
                                    format={v => parseFloat(v || 0).toFixed(2)}
                                />
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="PENALTY KILL"
                                    awayVal={preGameData.metrics.away?.pk_pct}
                                    homeVal={preGameData.metrics.home?.pk_pct}
                                    format={v => v + '%'}
                                />
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="CORSI %"
                                    awayVal={preGameData.metrics.away?.corsi_pct}
                                    homeVal={preGameData.metrics.home?.corsi_pct}
                                    format={v => v + '%'}
                                />
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="HD AGAINST"
                                    awayVal={preGameData.metrics.away?.hdca}
                                    homeVal={preGameData.metrics.home?.hdca}
                                    format={v => parseFloat(v || 0).toFixed(1)}
                                />
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="DEF ZONE SHOTS"
                                    awayVal={preGameData.metrics.away?.dzs}
                                    homeVal={preGameData.metrics.home?.dzs}
                                />
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="BLOCKS/GP"
                                    awayVal={preGameData.metrics.away?.blocks}
                                    homeVal={preGameData.metrics.home?.blocks}
                                    format={v => parseFloat(v || 0).toFixed(1)}
                                />
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="TAKEAWAYS"
                                    awayVal={preGameData.metrics.away?.takeaways}
                                    homeVal={preGameData.metrics.home?.takeaways}
                                    format={v => parseFloat(v || 0).toFixed(1)}
                                />
                            </MetricCard>

                            <MetricCard title="TRANSITION & POSSESSION" icon={Activity} className="md:col-span-2">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div>
                                        <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                            label="FACEOFF %"
                                            awayVal={preGameData.metrics.away?.fo_pct}
                                            homeVal={preGameData.metrics.home?.fo_pct}
                                            format={v => v + '%'}
                                        />
                                        <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                            label="NZ TURNOVERS"
                                            awayVal={preGameData.metrics.away?.nzts}
                                            homeVal={preGameData.metrics.home?.nzts}
                                        />
                                        <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                            label="NZTSA"
                                            awayVal={preGameData.metrics.away?.nztsa}
                                            homeVal={preGameData.metrics.home?.nztsa}
                                            format={v => parseFloat(v || 0).toFixed(1)}
                                        />
                                        <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                            label="GIVEAWAYS"
                                            awayVal={preGameData.metrics.away?.giveaways}
                                            homeVal={preGameData.metrics.home?.giveaways}
                                            format={v => parseFloat(v || 0).toFixed(1)}
                                        />
                                        <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                            label="HITS/GP"
                                            awayVal={preGameData.metrics.away?.hits}
                                            homeVal={preGameData.metrics.home?.hits}
                                            format={v => parseFloat(v || 0).toFixed(1)}
                                        />
                                    </div>
                                    <div>
                                        <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                            label="LATERAL MOVEMENT"
                                            awayVal={preGameData.metrics.away?.lat}
                                            homeVal={preGameData.metrics.home?.lat}
                                            format={v => parseFloat(v || 0).toFixed(1)}
                                        />
                                        <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                            label="N-S MOVEMENT"
                                            awayVal={preGameData.metrics.away?.long_movement}
                                            homeVal={preGameData.metrics.home?.long_movement}
                                            format={v => parseFloat(v || 0).toFixed(1)}
                                        />
                                        <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                            label="NEUTRAL ZONE"
                                            awayVal={preGameData.metrics.away?.nzs}
                                            homeVal={preGameData.metrics.home?.nzs}
                                        />
                                        <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                            label="POWER PLAY %"
                                            awayVal={preGameData.metrics.away?.pp_pct}
                                            homeVal={preGameData.metrics.home?.pp_pct}
                                            format={v => v + '%'}
                                        />
                                    </div>
                                </div>
                            </MetricCard>
                        </section>
                    );
                case 'overview': // Show metrics AND heatmap in overview for pre-game
                default:
                    return (
                        <div className="space-y-8">
                            <PreGameHeatmap
                                preGameData={preGameData}
                                homeTeam={homeTeam}
                                awayTeam={awayTeam}
                            />

                            <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <MetricCard title="ADVANCED METRICS" icon={Activity} className="md:col-span-2">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-4">
                                        {METRICS_CONFIG.map(metric => (
                                            <ComparisonRow
                                                key={metric.key}
                                                awayTeam={awayTeam}
                                                homeTeam={homeTeam}
                                                label={metric.label}
                                                awayVal={preGameData.metrics.away?.[metric.key]}
                                                homeVal={preGameData.metrics.home?.[metric.key]}
                                                format={metric.format}
                                            />
                                        ))}
                                    </div>
                                </MetricCard>
                            </section>
                        </div>
                    );
            }
        }

        // LIVE/FINAL CONTENT
        switch (activeTab) {
            case 'visuals':
                return (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        <div className="lg:col-span-3">
                            <section className="glass-card p-6">
                                <div className="flex items-center gap-3 mb-6">
                                    <Target className="w-6 h-6 text-accent-secondary" />
                                    <h3 className="text-xl font-display font-bold">SHOT MAP</h3>
                                </div>
                                <div className="aspect-[2/1] bg-white/5 rounded-xl overflow-hidden relative">
                                    <ShotChart
                                        shots={liveData?.live_metrics?.shots_data || []}
                                        homeTeam={homeTeam.abbrev}
                                        awayTeam={awayTeam.abbrev}
                                    />
                                </div>
                            </section>
                        </div>
                    </div>
                );
            case 'advanced':
                return (
                    <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <MetricCard title="ADVANCED METRICS" icon={Activity} className="md:col-span-2">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-4">
                                {METRICS_CONFIG.map(metric => (
                                    <ComparisonRow
                                        key={metric.key}
                                        awayTeam={awayTeam}
                                        homeTeam={homeTeam}
                                        label={metric.label}
                                        awayVal={liveData?.live_metrics?.[`away_${metric.liveKey}`]}
                                        homeVal={liveData?.live_metrics?.[`home_${metric.liveKey}`]}
                                        format={metric.format}
                                    />
                                ))}
                            </div>
                        </MetricCard>
                    </section>
                );
            case 'lines':
                return (
                    <LinesPairings
                        boxscore={liveData?.live_metrics?.boxscore || gameData?.boxscore}
                        awayTeam={awayTeam}
                        homeTeam={homeTeam}
                    />
                );
            case 'overview':
            default:
                return (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Left Column - Main Stats */}
                        <div className="lg:col-span-2 space-y-8">
                            {/* Period Stats Table */}
                            <section>
                                <div className="flex items-center gap-3 mb-6">
                                    <Clock className="w-6 h-6 text-accent-primary" />
                                    <h3 className="text-xl font-display font-bold">PERIOD PERFORMANCE</h3>
                                </div>
                                {liveData?.live_metrics ? (
                                    <PeriodStatsTable
                                        periodStats={constructPeriodStats(liveData.live_metrics)}
                                        awayTeam={awayTeam}
                                        homeTeam={homeTeam}
                                    />
                                ) : (
                                    <div className="glass-card p-6 text-center text-text-muted">
                                        No period stats available yet.
                                    </div>
                                )}
                            </section>
                        </div>

                        {/* Right Column - Visuals & Players */}
                        <div className="space-y-8">
                            {/* Win Probability Card (Live & Finished Games) */}
                            {(isFinal || isLive) && liveData && (
                                <section className="glass-card p-6">
                                    <div className="flex items-center gap-3 mb-6">
                                        <TrendingUp className="w-6 h-6 text-accent-primary" />
                                        <h3 className="text-xl font-display font-bold">{isLive ? 'LIVE WIN PROBABILITY' : 'FINAL WIN PROBABILITY'}</h3>
                                    </div>
                                    <div className="space-y-4">
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-3">
                                                <img src={awayTeam.logo} alt={awayTeam.abbrev} className="w-8 h-8" />
                                                <span className="font-display font-bold">{awayTeam.abbrev}</span>
                                            </div>
                                            <div className="text-right">
                                                <div className="text-3xl font-display font-bold text-accent-primary">
                                                    {((liveData.away_prob || 0) * 100).toFixed(1)}%
                                                </div>
                                            </div>
                                        </div>
                                        <div className="h-2 bg-white/5 rounded-full overflow-hidden flex">
                                            <div
                                                className="h-full transition-all duration-500"
                                                style={{
                                                    width: `${(liveData.away_prob || 0) * 100}%`,
                                                    backgroundColor: getTeamColor(awayTeam.abbrev)
                                                }}
                                            />
                                            <div
                                                className="h-full transition-all duration-500"
                                                style={{
                                                    width: `${(liveData.home_prob || 0) * 100}%`,
                                                    backgroundColor: getTeamColor(homeTeam.abbrev)
                                                }}
                                            />
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-3">
                                                <img src={homeTeam.logo} alt={homeTeam.abbrev} className="w-8 h-8" />
                                                <span className="font-display font-bold">{homeTeam.abbrev}</span>
                                            </div>
                                            <div className="text-right">
                                                <div className="text-3xl font-display font-bold text-accent-secondary">
                                                    {((liveData.home_prob || 0) * 100).toFixed(1)}%
                                                </div>
                                            </div>
                                        </div>
                                        <div className="text-center text-xs text-text-muted font-mono mt-4">
                                            Model Confidence: {((liveData.confidence || 0) * 100).toFixed(1)}%
                                        </div>
                                    </div>
                                </section>
                            )}

                            {/* Shot Chart Preview */}
                            <section className="glass-card p-6">
                                <div className="flex items-center gap-3 mb-6">
                                    <Target className="w-6 h-6 text-accent-secondary" />
                                    <h3 className="text-xl font-display font-bold">SHOT MAP</h3>
                                </div>
                                <div className="aspect-[2/1] bg-white/5 rounded-xl overflow-hidden relative">
                                    <ShotChart
                                        shots={liveData?.live_metrics?.shots_data || []}
                                        homeTeam={homeTeam.abbrev}
                                        awayTeam={awayTeam.abbrev}
                                    />
                                </div>
                            </section>
                        </div>
                    </div>
                );
        }
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
                            <img src={awayTeam.logo} alt={awayTeam.abbrev} className="w-32 h-32 md:w-40 md:h-40 object-contain drop-shadow-2xl" />
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

                            <div className="mt-4 flex flex-col items-center gap-2">
                                {isLive ? (
                                    <>
                                        <span className="relative flex h-2 w-2">
                                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-color-success opacity-75"></span>
                                            <span className="relative inline-flex rounded-full h-2 w-2 bg-color-success"></span>
                                        </span>
                                        <span className="font-mono text-color-success font-bold">{period} - {clock?.timeRemaining || '00:00'}</span>
                                    </>
                                ) : isFinal ? (
                                    <span className="font-mono text-text-muted font-bold">FINAL</span>
                                ) : (
                                    <div className="text-center">
                                        <div className="font-mono text-primary font-bold text-sm">
                                            {gameData?.boxscore?.startTimeUTC ? new Date(gameData.boxscore.startTimeUTC).toLocaleString('en-US', {
                                                weekday: 'short',
                                                month: 'short',
                                                day: 'numeric',
                                                hour: 'numeric',
                                                minute: '2-digit'
                                            }) : 'TBD'}
                                        </div>
                                        {gameData?.boxscore?.venue?.default && (
                                            <div className="font-mono text-text-muted text-xs mt-1">
                                                {gameData.boxscore.venue.default}
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Home Team */}
                        <div className="flex flex-col items-center gap-4 flex-1">
                            <img src={homeTeam.logo} alt={homeTeam.abbrev} className="w-32 h-32 md:w-40 md:h-40 object-contain drop-shadow-2xl" />
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

            {/* Sticky Navigation Bar */}
            <nav className="sticky top-0 z-40 bg-bg-primary/95 backdrop-blur-md border-b border-white/10 mb-8">
                <div className="flex gap-4 overflow-x-auto py-4 px-6 scrollbar-hide">
                    <a href="#overview" className="px-4 py-2 font-display font-bold text-sm text-text-muted hover:text-accent-primary transition-colors whitespace-nowrap">
                        OVERVIEW
                    </a>
                    {(isLive || isFinal) && (
                        <a href="#stats" className="px-4 py-2 font-display font-bold text-sm text-text-muted hover:text-accent-primary transition-colors whitespace-nowrap">
                            STATS
                        </a>
                    )}
                    <a href="#advanced" className="px-4 py-2 font-display font-bold text-sm text-text-muted hover:text-accent-primary transition-colors whitespace-nowrap">
                        ADVANCED
                    </a>
                    {(isLive || isFinal) && (
                        <a href="#shot-map" className="px-4 py-2 font-display font-bold text-sm text-text-muted hover:text-accent-primary transition-colors whitespace-nowrap">
                            SHOT MAP
                        </a>
                    )}
                    <a href="#lines" className="px-4 py-2 font-display font-bold text-sm text-text-muted hover:text-accent-primary transition-colors whitespace-nowrap">
                        LINES
                    </a>
                </div>
            </nav>

            {/* All Content Sections */}
            <div className="space-y-12">
                {/* OVERVIEW SECTION */}
                <section id="overview">
                    {!isLive && !isFinal ? (
                        // Pre-game overview
                        <div className="space-y-8">
                            <PreGameHeatmap
                                preGameData={preGameData}
                                homeTeam={homeTeam}
                                awayTeam={awayTeam}
                            />
                        </div>
                    ) : (
                        // Live/Final game overview
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                            <div className="lg:col-span-2 space-y-8">
                                <section>
                                    <div className="flex items-center gap-3 mb-6">
                                        <Clock className="w-6 h-6 text-accent-primary" />
                                        <h3 className="text-xl font-display font-bold">PERIOD PERFORMANCE</h3>
                                    </div>
                                    {liveData?.live_metrics ? (
                                        <PeriodStatsTable
                                            periodStats={constructPeriodStats(liveData.live_metrics)}
                                            awayTeam={awayTeam}
                                            homeTeam={homeTeam}
                                        />
                                    ) : (
                                        <div className="glass-card p-6 text-center text-text-muted">
                                            No period stats available yet.
                                        </div>
                                    )}
                                </section>
                            </div>

                            <div className="space-y-8">
                                {(isFinal || isLive) && liveData && (
                                    <section className="glass-card p-6">
                                        <div className="flex items-center gap-3 mb-6">
                                            <TrendingUp className="w-6 h-6 text-accent-primary" />
                                            <h3 className="text-xl font-display font-bold">{isLive ? 'LIVE WIN PROBABILITY' : 'FINAL WIN PROBABILITY'}</h3>
                                        </div>
                                        <div className="space-y-4">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center gap-3">
                                                    <img src={awayTeam.logo} alt={awayTeam.abbrev} className="w-8 h-8" />
                                                    <span className="font-display font-bold">{awayTeam.abbrev}</span>
                                                </div>
                                                <div className="text-right">
                                                    <div className="text-3xl font-display font-bold text-accent-primary">
                                                        {((liveData.away_prob || 0) * 100).toFixed(1)}%
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="h-2 bg-white/5 rounded-full overflow-hidden flex">
                                                <div
                                                    className="h-full bg-accent-primary transition-all duration-500"
                                                    style={{ width: `${(liveData.away_prob || 0) * 100}%` }}
                                                />
                                                <div
                                                    className="h-full bg-accent-secondary transition-all duration-500"
                                                    style={{ width: `${(liveData.home_prob || 0) * 100}%` }}
                                                />
                                            </div>
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center gap-3">
                                                    <img src={homeTeam.logo} alt={homeTeam.abbrev} className="w-8 h-8" />
                                                    <span className="font-display font-bold">{homeTeam.abbrev}</span>
                                                </div>
                                                <div className="text-right">
                                                    <div className="text-3xl font-display font-bold text-accent-secondary">
                                                        {((liveData.home_prob || 0) * 100).toFixed(1)}%
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="text-center text-xs text-text-muted font-mono mt-4">
                                                Model Confidence: {((liveData.confidence || 0) * 100).toFixed(1)}%
                                            </div>
                                        </div>
                                    </section>
                                )}
                            </div>
                        </div>
                    )}
                </section>

                {/* ADVANCED METRICS SECTION */}
                <section id="advanced">
                    <div className="flex items-center gap-3 mb-6">
                        <Activity className="w-6 h-6 text-accent-primary" />
                        <h2 className="text-2xl font-display font-bold">ADVANCED METRICS</h2>
                    </div>
                    {!isLive && !isFinal ? (
                        // Pre-game advanced metrics
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <MetricCard title="OFFENSE" icon={Zap}>
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="GAME SCORE"
                                    awayVal={preGameData.metrics.away?.gs}
                                    homeVal={preGameData.metrics.home?.gs}
                                    format={v => parseFloat(v || 0).toFixed(1)}
                                />
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="GOALS/GP"
                                    awayVal={preGameData.metrics.away?.goals}
                                    homeVal={preGameData.metrics.home?.goals}
                                    format={v => parseFloat(v || 0).toFixed(2)}
                                />
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="xGOALS/GP"
                                    awayVal={preGameData.metrics.away?.xg}
                                    homeVal={preGameData.metrics.home?.xg}
                                    format={v => parseFloat(v || 0).toFixed(2)}
                                />
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="SHOTS/GP"
                                    awayVal={preGameData.metrics.away?.shots}
                                    homeVal={preGameData.metrics.home?.shots}
                                    format={v => parseFloat(v || 0).toFixed(1)}
                                />
                            </MetricCard>

                            <MetricCard title="DEFENSE" icon={Shield}>
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="GA/GP"
                                    awayVal={preGameData.metrics.away?.ga_gp}
                                    homeVal={preGameData.metrics.home?.ga_gp}
                                    format={v => parseFloat(v || 0).toFixed(2)}
                                />
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="PENALTY KILL"
                                    awayVal={preGameData.metrics.away?.pk_pct}
                                    homeVal={preGameData.metrics.home?.pk_pct}
                                    format={v => v + '%'}
                                />
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="CORSI %"
                                    awayVal={preGameData.metrics.away?.corsi_pct}
                                    homeVal={preGameData.metrics.home?.corsi_pct}
                                    format={v => v + '%'}
                                />
                            </MetricCard>
                        </div>
                    ) : (
                        // Live/Final advanced metrics
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <MetricCard title="SHOT QUALITY" icon={Crosshair}>
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="EXPECTED GOALS (xG)"
                                    awayVal={liveData?.live_metrics?.away_xg}
                                    homeVal={liveData?.live_metrics?.home_xg}
                                    format={(v) => parseFloat(v || 0).toFixed(2)}
                                />
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="HIGH DANGER CHANCES"
                                    awayVal={liveData?.live_metrics?.away_hdc}
                                    homeVal={liveData?.live_metrics?.home_hdc}
                                />
                            </MetricCard>

                            <MetricCard title="PRESSURE" icon={Zap}>
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="OFFENSIVE ZONE SHOTS"
                                    awayVal={liveData?.live_metrics?.away_ozs}
                                    homeVal={liveData?.live_metrics?.home_ozs}
                                />
                                <ComparisonRow awayTeam={awayTeam} homeTeam={homeTeam}
                                    label="RUSH CHANCES"
                                    awayVal={liveData?.live_metrics?.away_rush}
                                    homeVal={liveData?.live_metrics?.home_rush}
                                />
                            </MetricCard>
                        </div>
                    )}
                </section>

                {/* SHOT MAP SECTION (Live/Final only) */}
                {(isLive || isFinal) && (
                    <section id="shot-map">
                        <div className="flex items-center gap-3 mb-6">
                            <Target className="w-6 h-6 text-accent-secondary" />
                            <h2 className="text-2xl font-display font-bold">SHOT MAP</h2>
                        </div>
                        <div className="glass-card p-6">
                            <div className="aspect-[2/1] bg-white/5 rounded-xl overflow-hidden relative">
                                <ShotChart
                                    shots={liveData?.live_metrics?.shots_data || []}
                                    homeTeam={homeTeam.abbrev}
                                    awayTeam={awayTeam.abbrev}
                                />
                            </div>
                        </div>
                    </section>
                )}

                {/* LINES & PAIRINGS SECTION */}
                <section id="lines">
                    <div className="flex items-center gap-3 mb-6">
                        <Users className="w-6 h-6 text-accent-primary" />
                        <h2 className="text-2xl font-display font-bold">LINES & PAIRINGS</h2>
                    </div>
                    <LinesPairings
                        boxscore={gameData?.boxscore}
                        awayTeam={awayTeam}
                        homeTeam={homeTeam}
                        awayLines={linesData.away}
                        homeLines={linesData.home}
                    />
                </section>
            </div>
        </div>
    );
};

const GameDetails = () => {
    return (
        <ErrorBoundary>
            <GameDetailsContent />
        </ErrorBoundary>
    );
};

export default GameDetails;
