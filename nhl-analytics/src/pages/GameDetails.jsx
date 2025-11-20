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

const PreGameHeatmap = ({ preGameData, homeTeam, awayTeam }) => (
    <section className="glass-card p-6">
        <div className="flex items-center gap-3 mb-6">
            <Target className="w-6 h-6 text-accent-cyan" />
            <h3 className="text-xl font-display font-bold">PRE-GAME INTEL: SHOT HEATMAP (L10 GAMES)</h3>
        </div>
        <div className="max-w-3xl mx-auto">
            <div className="relative aspect-[200/85] bg-white/5 rounded-xl border border-white/10 overflow-hidden">
                <img src="/rink.jpeg" alt="Rink" className="absolute inset-0 w-full h-full object-fill opacity-50" />

                {/* Home Team Points */}
                {preGameData.heatmaps.home?.goals_for?.map((point, i) => (
                    <div
                        key={`home-goal-${i}`}
                        className="absolute w-3 h-3 rounded-full border border-white shadow-lg z-20 transform -translate-x-1/2 -translate-y-1/2"
                        style={{
                            backgroundColor: getTeamColor(homeTeam.abbrev),
                            left: `${(point.x + 100) / 2}%`,
                            top: `${(42.5 - point.y) / 0.85}%`
                        }}
                    />
                ))}
                {preGameData.heatmaps.home?.shots_for?.map((point, i) => (
                    <div
                        key={`home-shot-${i}`}
                        className="absolute w-1.5 h-1.5 rounded-full opacity-60 blur-[0.5px] transform -translate-x-1/2 -translate-y-1/2"
                        style={{
                            backgroundColor: getTeamColor(homeTeam.abbrev),
                            left: `${(point.x + 100) / 2}%`,
                            top: `${(42.5 - point.y) / 0.85}%`
                        }}
                    />
                ))}

                {/* Away Team Points */}
                {preGameData.heatmaps.away?.goals_for?.map((point, i) => (
                    <div
                        key={`away-goal-${i}`}
                        className="absolute w-3 h-3 rounded-full border border-white shadow-lg z-20 transform -translate-x-1/2 -translate-y-1/2"
                        style={{
                            backgroundColor: getTeamColor(awayTeam.abbrev),
                            left: `${(point.x + 100) / 2}%`,
                            top: `${(42.5 - point.y) / 0.85}%`
                        }}
                    />
                ))}
                {preGameData.heatmaps.away?.shots_for?.map((point, i) => (
                    <div
                        key={`away-shot-${i}`}
                        className="absolute w-1.5 h-1.5 rounded-full opacity-60 blur-[0.5px] transform -translate-x-1/2 -translate-y-1/2"
                        style={{
                            backgroundColor: getTeamColor(awayTeam.abbrev),
                            left: `${(point.x + 100) / 2}%`,
                            top: `${(42.5 - point.y) / 0.85}%`
                        }}
                    />
                ))}

                <div className="absolute bottom-2 left-2 flex gap-4 bg-black/80 p-2 rounded-lg backdrop-blur-md border border-white/10 z-30 scale-90 origin-bottom-left">
                    <div className="flex items-center gap-2">
                        <div className="w-2.5 h-2.5 rounded-full border border-white" style={{ backgroundColor: getTeamColor(awayTeam.abbrev) }}></div>
                        <span className="text-[10px] font-mono text-white">{awayTeam.abbrev} G</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full opacity-60" style={{ backgroundColor: getTeamColor(awayTeam.abbrev) }}></div>
                        <span className="text-[10px] font-mono text-white">{awayTeam.abbrev} S</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-2.5 h-2.5 rounded-full border border-white" style={{ backgroundColor: getTeamColor(homeTeam.abbrev) }}></div>
                        <span className="text-[10px] font-mono text-white">{homeTeam.abbrev} G</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full opacity-60" style={{ backgroundColor: getTeamColor(homeTeam.abbrev) }}></div>
                        <span className="text-[10px] font-mono text-white">{homeTeam.abbrev} S</span>
                    </div>
                </div>
            </div>
        </div>
    </section>
);

const GameDetailsContent = () => {
    const { id } = useParams();
    const [gameData, setGameData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [liveData, setLiveData] = useState(null);
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

                // If game is live, fetch live data
                if (data?.boxscore?.gameState === 'LIVE' || data?.boxscore?.gameState === 'CRIT') {
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


    const renderTabContent = () => {
        // PRE-GAME CONTENT
        if (!isLive && !isFinal) {
            switch (activeTab) {
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
                                <ComparisonRow
                                    label="GOALS/GP"
                                    awayVal={preGameData.metrics.away?.goals}
                                    homeVal={preGameData.metrics.home?.goals}
                                    format={v => parseFloat(v || 0).toFixed(2)}
                                />
                                <ComparisonRow
                                    label="xGOALS/GP"
                                    awayVal={preGameData.metrics.away?.xg}
                                    homeVal={preGameData.metrics.home?.xg}
                                    format={v => parseFloat(v || 0).toFixed(2)}
                                />
                                <ComparisonRow
                                    label="SHOTS/GP"
                                    awayVal={preGameData.metrics.away?.shots}
                                    homeVal={preGameData.metrics.home?.shots}
                                    format={v => parseFloat(v || 0).toFixed(1)}
                                />
                                <ComparisonRow
                                    label="POWER PLAY"
                                    awayVal={preGameData.metrics.away?.pp_pct}
                                    homeVal={preGameData.metrics.home?.pp_pct}
                                    format={v => v + '%'}
                                />
                                <ComparisonRow
                                    label="OFF ZONE SHOTS"
                                    awayVal={preGameData.metrics.away?.ozs}
                                    homeVal={preGameData.metrics.home?.ozs}
                                />
                                <ComparisonRow
                                    label="HIGH DANGER"
                                    awayVal={preGameData.metrics.away?.hdc}
                                    homeVal={preGameData.metrics.home?.hdc}
                                    format={v => parseFloat(v || 0).toFixed(1)}
                                />
                                <ComparisonRow
                                    label="RUSH CHANCES"
                                    awayVal={preGameData.metrics.away?.rush}
                                    homeVal={preGameData.metrics.home?.rush}
                                />
                            </MetricCard>

                            <MetricCard title="DEFENSE" icon={Shield}>
                                <ComparisonRow
                                    label="GA/GP"
                                    awayVal={preGameData.metrics.away?.ga_gp}
                                    homeVal={preGameData.metrics.home?.ga_gp}
                                    format={v => parseFloat(v || 0).toFixed(2)}
                                />
                                <ComparisonRow
                                    label="PENALTY KILL"
                                    awayVal={preGameData.metrics.away?.pk_pct}
                                    homeVal={preGameData.metrics.home?.pk_pct}
                                    format={v => v + '%'}
                                />
                                <ComparisonRow
                                    label="CORSI %"
                                    awayVal={preGameData.metrics.away?.corsi_pct}
                                    homeVal={preGameData.metrics.home?.corsi_pct}
                                    format={v => v + '%'}
                                />
                                <ComparisonRow
                                    label="HD AGAINST"
                                    awayVal={preGameData.metrics.away?.hdca}
                                    homeVal={preGameData.metrics.home?.hdca}
                                    format={v => parseFloat(v || 0).toFixed(1)}
                                />
                                <ComparisonRow
                                    label="BLOCKS/GP"
                                    awayVal={preGameData.metrics.away?.blocks}
                                    homeVal={preGameData.metrics.home?.blocks}
                                    format={v => parseFloat(v || 0).toFixed(1)}
                                />
                                <ComparisonRow
                                    label="TAKEAWAYS"
                                    awayVal={preGameData.metrics.away?.takeaways}
                                    homeVal={preGameData.metrics.home?.takeaways}
                                    format={v => parseFloat(v || 0).toFixed(1)}
                                />
                            </MetricCard>

                            <MetricCard title="TRANSITION & POSSESSION" icon={Activity} className="md:col-span-2">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div>
                                        <ComparisonRow
                                            label="FACEOFF %"
                                            awayVal={preGameData.metrics.away?.fo_pct}
                                            homeVal={preGameData.metrics.home?.fo_pct}
                                            format={v => v + '%'}
                                        />
                                        <ComparisonRow
                                            label="GIVEAWAYS"
                                            awayVal={preGameData.metrics.away?.giveaways}
                                            homeVal={preGameData.metrics.home?.giveaways}
                                            format={v => parseFloat(v || 0).toFixed(1)}
                                        />
                                        <ComparisonRow
                                            label="HITS/GP"
                                            awayVal={preGameData.metrics.away?.hits}
                                            homeVal={preGameData.metrics.home?.hits}
                                            format={v => parseFloat(v || 0).toFixed(1)}
                                        />
                                    </div>
                                    <div>
                                        <ComparisonRow
                                            label="LATERAL MOVEMENT"
                                            awayVal={preGameData.metrics.away?.lat}
                                            homeVal={preGameData.metrics.home?.lat}
                                            format={v => parseFloat(v || 0).toFixed(1)}
                                        />
                                        <ComparisonRow
                                            label="N-S MOVEMENT"
                                            awayVal={preGameData.metrics.away?.long_movement}
                                            homeVal={preGameData.metrics.home?.long_movement}
                                            format={v => parseFloat(v || 0).toFixed(1)}
                                        />
                                        <ComparisonRow
                                            label="NZ TURNOVERS"
                                            awayVal={preGameData.metrics.away?.nzts}
                                            homeVal={preGameData.metrics.home?.nzts}
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
                                <MetricCard title="OFFENSE" icon={Zap}>
                                    <ComparisonRow
                                        label="GOALS/GP"
                                        awayVal={preGameData.metrics.away?.goals}
                                        homeVal={preGameData.metrics.home?.goals}
                                        format={v => parseFloat(v || 0).toFixed(2)}
                                    />
                                    <ComparisonRow
                                        label="xGOALS/GP"
                                        awayVal={preGameData.metrics.away?.xg}
                                        homeVal={preGameData.metrics.home?.xg}
                                        format={v => parseFloat(v || 0).toFixed(2)}
                                    />
                                    <ComparisonRow
                                        label="SHOTS/GP"
                                        awayVal={preGameData.metrics.away?.shots}
                                        homeVal={preGameData.metrics.home?.shots}
                                        format={v => parseFloat(v || 0).toFixed(1)}
                                    />
                                    <ComparisonRow
                                        label="POWER PLAY"
                                        awayVal={preGameData.metrics.away?.pp_pct}
                                        homeVal={preGameData.metrics.home?.pp_pct}
                                        format={v => v + '%'}
                                    />
                                    <ComparisonRow
                                        label="OFF ZONE SHOTS"
                                        awayVal={preGameData.metrics.away?.ozs}
                                        homeVal={preGameData.metrics.home?.ozs}
                                    />
                                </MetricCard>

                                <MetricCard title="DEFENSE" icon={Shield}>
                                    <ComparisonRow
                                        label="GA/GP"
                                        awayVal={preGameData.metrics.away?.ga_gp}
                                        homeVal={preGameData.metrics.home?.ga_gp}
                                        format={v => parseFloat(v || 0).toFixed(2)}
                                    />
                                    <ComparisonRow
                                        label="PENALTY KILL"
                                        awayVal={preGameData.metrics.away?.pk_pct}
                                        homeVal={preGameData.metrics.home?.pk_pct}
                                        format={v => v + '%'}
                                    />
                                    <ComparisonRow
                                        label="CORSI %"
                                        awayVal={preGameData.metrics.away?.corsi_pct}
                                        homeVal={preGameData.metrics.home?.corsi_pct}
                                        format={v => v + '%'}
                                    />
                                    <ComparisonRow
                                        label="HD AGAINST"
                                        awayVal={preGameData.metrics.away?.hdca}
                                        homeVal={preGameData.metrics.home?.hdca}
                                        format={v => parseFloat(v || 0).toFixed(1)}
                                    />
                                    <ComparisonRow
                                        label="BLOCKS/GP"
                                        awayVal={preGameData.metrics.away?.blocks}
                                        homeVal={preGameData.metrics.home?.blocks}
                                        format={v => parseFloat(v || 0).toFixed(1)}
                                    />
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
                                        shots={liveData?.shots_data || []}
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
                );
            case 'rosters':
                return (
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
                        </div>

                        {/* Right Column - Visuals & Players */}
                        <div className="space-y-8">
                            {/* Shot Chart Preview */}
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

            {/* Main Content Area */}
            <div className="min-h-[400px]">
                {renderTabContent()}
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
