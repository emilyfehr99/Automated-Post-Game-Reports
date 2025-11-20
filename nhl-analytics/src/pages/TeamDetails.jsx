import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { nhlApi } from '../api/nhl';
import { Users, ArrowLeft, Shield, Crosshair, Goal, Activity, TrendingUp, Zap } from 'lucide-react';
import { motion } from 'framer-motion';
import clsx from 'clsx';

const PlayerCard = ({ player, delay }) => (
    <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay }}
    >
        <Link
            to={`/player/${player.id}`}
            className="block glass-card rounded-xl overflow-hidden group relative hover:border-accent-primary/50 transition-colors"
        >
            <div className="absolute top-0 right-0 p-3 z-10">
                <span className="font-mono text-xs font-bold text-white/50 group-hover:text-accent-primary transition-colors">
                    #{player.sweaterNumber}
                </span>
            </div>

            <div className="p-4 flex items-center gap-4 relative z-10">
                <div className="relative">
                    <div className="absolute inset-0 bg-accent-primary/20 blur-lg rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                    <img
                        src={player.headshot}
                        alt={player.firstName.default}
                        className="w-16 h-16 rounded-full bg-zinc-800 object-cover border border-white/10 group-hover:border-accent-primary/50 transition-colors relative z-10"
                    />
                </div>

                <div className="flex-1 min-w-0">
                    <h3 className="font-display font-bold text-base text-white truncate group-hover:text-glow-primary transition-all">
                        {player.firstName.default} {player.lastName.default}
                    </h3>
                    <div className="flex items-center gap-2 mt-1">
                        <span className="font-mono text-[10px] text-text-muted bg-white/5 px-1.5 py-0.5 rounded uppercase">
                            {player.positionCode}
                        </span>
                        {player.birthCountry && (
                            <span className="font-mono text-[10px] text-text-secondary">
                                {player.birthCountry}
                            </span>
                        )}
                    </div>
                </div>
            </div>

            {/* Card Background Effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-transparent to-accent-primary/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
        </Link>
    </motion.div>
);

const MetricCard = ({ label, value, subLabel, icon: Icon, colorClass = "text-accent-primary", percentile, rank }) => (
    <div className="glass-panel p-4 rounded-xl relative overflow-hidden group hover:bg-white/5 transition-colors">
        <div className={`absolute top-0 right-0 p-3 opacity-20 group-hover:opacity-40 transition-opacity ${colorClass}`}>
            <Icon size={24} />
        </div>
        <div className="relative z-10">
            <div className="text-text-secondary text-xs font-mono uppercase tracking-wider mb-1">{label}</div>
            <div className="flex items-baseline gap-2 mb-1">
                <div className={`text-2xl font-display font-bold ${colorClass}`}>{value}</div>
                {percentile !== undefined && (
                    <div className="text-xs font-mono text-text-muted">({percentile}th %ile)</div>
                )}
            </div>
            <div className="flex items-center justify-between text-[10px] font-mono">
                {subLabel && <span className="text-text-muted">{subLabel}</span>}
                {rank && <span className="text-accent-cyan">#{rank} NHL</span>}
            </div>
        </div>
    </div>
);

const TeamDetails = () => {
    const { id } = useParams();
    const [roster, setRoster] = useState(null);
    const [teamMetrics, setTeamMetrics] = useState(null);
    const [allTeamMetrics, setAllTeamMetrics] = useState({});
    const [loading, setLoading] = useState(true);

    // Calculate percentile for a metric
    const calculatePercentile = (value, metricKey, higherIsBetter = true) => {
        if (!value || !allTeamMetrics || Object.keys(allTeamMetrics).length === 0) return null;

        const values = Object.values(allTeamMetrics)
            .map(m => parseFloat(m[metricKey]))
            .filter(v => !isNaN(v))
            .sort((a, b) => a - b);

        if (values.length === 0) return null;

        const position = values.findIndex(v => v >= parseFloat(value));
        let percentile = Math.round((position / values.length) * 100);

        // If higher is better, invert the percentile
        if (higherIsBetter) {
            percentile = 100 - percentile;
        }

        return Math.min(99, Math.max(1, percentile));
    };

    // Calculate league rank
    const calculateRank = (value, metricKey, higherIsBetter = true) => {
        if (!value || !allTeamMetrics || Object.keys(allTeamMetrics).length === 0) return null;

        const sortedTeams = Object.entries(allTeamMetrics)
            .map(([team, metrics]) => ({ team, value: parseFloat(metrics[metricKey]) || 0 }))
            .filter(t => !isNaN(t.value))
            .sort((a, b) => higherIsBetter ? b.value - a.value : a.value - b.value);

        const rank = sortedTeams.findIndex(t => t.team === id) + 1;
        return rank > 0 ? rank : null;
    };

    useEffect(() => {
        const fetchTeamData = async () => {
            try {
                const [rosterData, metricsResponse] = await Promise.all([
                    nhlApi.getTeamDetails(id),
                    fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:5002'}/api/team-metrics`)
                ]);

                setRoster(rosterData);

                if (metricsResponse.ok) {
                    const allMetrics = await metricsResponse.json();
                    setAllTeamMetrics(allMetrics);
                    const teamMetric = allMetrics[id];
                    setTeamMetrics(teamMetric);
                }
            } catch (error) {
                console.error('Failed to fetch team details:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchTeamData();
        const intervalId = setInterval(fetchTeamData, 30000);
        return () => clearInterval(intervalId);
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

    if (!roster) return null;

    const forwards = roster.forwards || [];
    const defensemen = roster.defensemen || [];
    const goalies = roster.goalies || [];

    return (
        <div className="space-y-12 pb-12">
            {/* Header Banner */}
            <div className="relative rounded-3xl overflow-hidden bg-gradient-to-br from-bg-secondary to-bg-primary border border-white/5 p-8 md:p-12 shadow-2xl">
                <div className="absolute top-0 right-0 -mt-20 -mr-20 w-96 h-96 bg-accent-primary/10 rounded-full blur-3xl animate-pulse"></div>
                <div className="absolute bottom-0 left-0 -mb-20 -ml-20 w-80 h-80 bg-accent-secondary/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>

                <div className="relative z-10">
                    <Link to="/" className="inline-flex items-center gap-2 text-text-muted hover:text-white mb-8 transition-colors group">
                        <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
                        <span className="font-mono text-sm">BACK TO DASHBOARD</span>
                    </Link>

                    <div className="flex flex-col md:flex-row items-center gap-8 md:gap-12">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="relative"
                        >
                            <div className="absolute inset-0 bg-white/10 blur-3xl rounded-full"></div>
                            <img
                                src={`https://assets.nhle.com/logos/nhl/svg/${id}_light.svg`}
                                alt={id}
                                className="w-32 h-32 md:w-48 md:h-48 object-contain relative z-10 drop-shadow-2xl"
                            />
                        </motion.div>

                        <div className="text-center md:text-left">
                            <motion.h1
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="text-6xl md:text-8xl font-display font-black text-white tracking-tighter mb-2"
                            >
                                {id}
                            </motion.h1>
                            <div className="flex items-center justify-center md:justify-start gap-4">
                                <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-sm font-mono text-text-secondary">
                                    {forwards.length + defensemen.length + goalies.length} PLAYERS
                                </span>
                                <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-sm font-mono text-text-secondary">
                                    EST. 2024
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Team Advanced Metrics */}
            {teamMetrics && (
                <section>
                    <div className="flex items-center gap-3 mb-6">
                        <Activity className="w-6 h-6 text-accent-primary" />
                        <h2 className="text-2xl font-display font-bold tracking-wide text-white">PERFORMANCE METRICS</h2>
                        <div className="h-px flex-1 bg-gradient-to-r from-white/10 to-transparent" />
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                        <MetricCard
                            label="NEUTRAL ZONE SHOTS"
                            value={teamMetrics.nzs?.toFixed(1) || '-'}
                            subLabel="Per game"
                            icon={TrendingUp}
                            colorClass="text-accent-primary"
                            percentile={calculatePercentile(teamMetrics.nzs, 'nzs', true)}
                            rank={calculateRank(teamMetrics.nzs, 'nzs', true)}
                        />
                        <MetricCard
                            label="NZ SHOTS AGAINST"
                            value={teamMetrics.nztsa?.toFixed(1) || '-'}
                            subLabel="Per game"
                            icon={Shield}
                            colorClass="text-accent-secondary"
                            percentile={calculatePercentile(teamMetrics.nztsa, 'nztsa', false)}
                            rank={calculateRank(teamMetrics.nztsa, 'nztsa', false)}
                        />
                        <MetricCard
                            label="HIGH DANGER"
                            value={teamMetrics.hdc?.toFixed(1) || '-'}
                            subLabel="Per game"
                            icon={Crosshair}
                            colorClass="text-color-success"
                            percentile={calculatePercentile(teamMetrics.hdc, 'hdc', true)}
                            rank={calculateRank(teamMetrics.hdc, 'hdc', true)}
                        />
                        <MetricCard
                            label="HD AGAINST"
                            value={teamMetrics.hdca?.toFixed(1) || '-'}
                            subLabel="Per game"
                            icon={Shield}
                            colorClass="text-color-danger"
                            percentile={calculatePercentile(teamMetrics.hdca, 'hdca', false)}
                            rank={calculateRank(teamMetrics.hdca, 'hdca', false)}
                        />
                        <MetricCard
                            label="LATERAL MOVEMENT"
                            value={teamMetrics.lat?.toFixed(1) || '-'}
                            subLabel="Feet per play"
                            icon={Activity}
                            colorClass="text-accent-orange"
                            percentile={calculatePercentile(teamMetrics.lat, 'lat', true)}
                            rank={calculateRank(teamMetrics.lat, 'lat', true)}
                        />
                        <MetricCard
                            label="N-S MOVEMENT"
                            value={teamMetrics.long_movement?.toFixed(1) || '-'}
                            subLabel="Feet per play"
                            icon={Zap}
                            colorClass="text-blue-400"
                            percentile={calculatePercentile(teamMetrics.long_movement, 'long_movement', true)}
                            rank={calculateRank(teamMetrics.long_movement, 'long_movement', true)}
                        />
                    </div>
                </section>
            )}

            {/* Roster Sections */}
            <div className="space-y-12">
                {/* Forwards */}
                <section>
                    <div className="flex items-center gap-3 mb-6">
                        <Crosshair className="w-6 h-6 text-accent-primary" />
                        <h2 className="text-2xl font-display font-bold tracking-wide text-white">FORWARDS</h2>
                        <div className="h-px flex-1 bg-gradient-to-r from-white/10 to-transparent" />
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                        {forwards.map((player, i) => (
                            <PlayerCard key={player.id} player={player} delay={i * 0.05} />
                        ))}
                    </div>
                </section>

                {/* Defensemen */}
                <section>
                    <div className="flex items-center gap-3 mb-6">
                        <Shield className="w-6 h-6 text-accent-secondary" />
                        <h2 className="text-2xl font-display font-bold tracking-wide text-white">DEFENSEMEN</h2>
                        <div className="h-px flex-1 bg-gradient-to-r from-white/10 to-transparent" />
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                        {defensemen.map((player, i) => (
                            <PlayerCard key={player.id} player={player} delay={i * 0.05} />
                        ))}
                    </div>
                </section>

                {/* Goalies */}
                <section>
                    <div className="flex items-center gap-3 mb-6">
                        <Goal className="w-6 h-6 text-color-success" />
                        <h2 className="text-2xl font-display font-bold tracking-wide text-white">GOALIES</h2>
                        <div className="h-px flex-1 bg-gradient-to-r from-white/10 to-transparent" />
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                        {goalies.map((player, i) => (
                            <PlayerCard key={player.id} player={player} delay={i * 0.05} />
                        ))}
                    </div>
                </section>
            </div>
        </div>
    );
};

export default TeamDetails;
