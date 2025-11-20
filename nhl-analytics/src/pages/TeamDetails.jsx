import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { nhlApi } from '../api/nhl';
import { Users, ArrowLeft, Shield, Crosshair, Goal } from 'lucide-react';
import { motion } from 'framer-motion';

const PlayerCard = ({ player, delay }) => (
    <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay }}
    >
        <Link
            to={`/player/${player.id}`}
            className="block glass-card rounded-xl overflow-hidden group relative"
        >
            <div className="absolute top-0 right-0 p-3 z-10">
                <span className="font-mono text-xs font-bold text-white/50 group-hover:text-accent-cyan transition-colors">
                    #{player.sweaterNumber}
                </span>
            </div>

            <div className="p-6 flex flex-col items-center relative z-10">
                <div className="relative mb-4">
                    <div className="absolute inset-0 bg-accent-cyan/20 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                    <img
                        src={player.headshot}
                        alt={player.firstName.default}
                        className="w-24 h-24 rounded-full bg-zinc-800 object-cover border-2 border-white/10 group-hover:border-accent-cyan/50 transition-colors relative z-10"
                    />
                </div>

                <h3 className="font-sans font-bold text-lg text-white text-center mb-1 group-hover:text-glow-cyan transition-all">
                    {player.firstName.default} {player.lastName.default}
                </h3>
                <span className="font-mono text-xs text-gray-400 bg-white/5 px-2 py-1 rounded">
                    {player.positionCode}
                </span>
            </div>

            {/* Card Background Effect */}
            <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-accent-cyan/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
        </Link>
    </motion.div>
);

const TeamDetails = () => {
    const { id } = useParams();
    const [roster, setRoster] = useState(null);
    const [teamMetrics, setTeamMetrics] = useState(null);
    const [loading, setLoading] = useState(true);

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
                    // Access metrics directly by team abbreviation
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

        // Poll for updates every 30 seconds
        const intervalId = setInterval(fetchTeamData, 30000);

        return () => clearInterval(intervalId);
    }, [id]);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-[60vh]">
                <div className="h-16 w-16 rounded-full border-t-2 border-b-2 border-accent-cyan animate-spin"></div>
            </div>
        );
    }

    if (!roster) return null;

    const forwards = roster.forwards || [];
    const defensemen = roster.defensemen || [];
    const goalies = roster.goalies || [];

    return (
        <div className="space-y-12">
            {/* Header Banner */}
            <div className="relative rounded-2xl overflow-hidden bg-zinc-900 border border-white/10 p-8 md:p-16">
                <div className="absolute inset-0 bg-grid-pattern opacity-30" />
                <div className="absolute top-0 right-0 w-96 h-96 bg-accent-cyan/10 rounded-full blur-[100px] -translate-y-1/2 translate-x-1/3" />

                <div className="relative z-10">
                    <Link to="/" className="inline-flex items-center gap-2 text-gray-400 hover:text-white mb-6 transition-colors group">
                        <ArrowLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
                        <span className="font-mono text-sm">BACK TO DASHBOARD</span>
                    </Link>

                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-6xl md:text-8xl font-sans font-bold text-white tracking-tighter"
                    >
                        {id} <span className="text-transparent bg-clip-text bg-gradient-to-r from-white/50 to-transparent">ROSTER</span>
                    </motion.h1>
                </div>
            </div>

            {/* Team Advanced Metrics */}
            {teamMetrics && (
                <div className="glass-card rounded-2xl p-8">
                    <h2 className="font-sans font-bold text-2xl text-white mb-6">
                        Team Advanced Metrics
                    </h2>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
                        <div className="text-center">
                            <div className="text-3xl font-bold text-accent-cyan">{teamMetrics.nzs?.toFixed(1) || '-'}</div>
                            <div className="text-sm text-gray-400 mt-1">NZS</div>
                        </div>
                        <div className="text-center">
                            <div className="text-3xl font-bold text-accent-cyan">{teamMetrics.nztsa?.toFixed(1) || '-'}</div>
                            <div className="text-sm text-gray-400 mt-1">NZTSA</div>
                        </div>
                        <div className="text-center">
                            <div className="text-3xl font-bold text-accent-cyan">{teamMetrics.hdc?.toFixed(1) || '-'}</div>
                            <div className="text-sm text-gray-400 mt-1">HDC</div>
                        </div>
                        <div className="text-center">
                            <div className="text-3xl font-bold text-accent-cyan">{teamMetrics.hdca?.toFixed(1) || '-'}</div>
                            <div className="text-sm text-gray-400 mt-1">HDCA</div>
                        </div>
                        <div className="text-center">
                            <div className="text-3xl font-bold text-accent-cyan">{teamMetrics.lat?.toFixed(2) || '-'}</div>
                            <div className="text-sm text-gray-400 mt-1">LAT</div>
                        </div>
                        <div className="text-center">
                            <div className="text-3xl font-bold text-accent-cyan">{teamMetrics.long_movenet?.toFixed(2) || '-'}</div>
                            <div className="text-sm text-gray-400 mt-1">LONG MOVE</div>
                        </div>
                    </div>
                </div>
            )}

            {/* Roster Sections */}
            <div className="space-y-12">
                {/* Forwards */}
                <section>
                    <div className="flex items-center gap-3 mb-6">
                        <Crosshair className="text-accent-cyan" />
                        <h2 className="text-2xl font-sans font-bold tracking-wide text-white">FORWARDS</h2>
                        <div className="h-px flex-1 bg-gradient-to-r from-accent-cyan/50 to-transparent" />
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                        {forwards.map((player, i) => (
                            <PlayerCard key={player.id} player={player} delay={i * 0.05} />
                        ))}
                    </div>
                </section>

                {/* Defensemen */}
                <section>
                    <div className="flex items-center gap-3 mb-6">
                        <Shield className="text-accent-magenta" />
                        <h2 className="text-2xl font-sans font-bold tracking-wide text-white">DEFENSEMEN</h2>
                        <div className="h-px flex-1 bg-gradient-to-r from-accent-magenta/50 to-transparent" />
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                        {defensemen.map((player, i) => (
                            <PlayerCard key={player.id} player={player} delay={i * 0.05} />
                        ))}
                    </div>
                </section>

                {/* Goalies */}
                <section>
                    <div className="flex items-center gap-3 mb-6">
                        <Goal className="text-accent-lime" />
                        <h2 className="text-2xl font-sans font-bold tracking-wide text-white">GOALIES</h2>
                        <div className="h-px flex-1 bg-gradient-to-r from-accent-lime/50 to-transparent" />
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
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
