import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { nhlApi } from '../api/nhl';
import { ArrowLeft, Activity, Ruler, Weight, Calendar, MapPin } from 'lucide-react';
import { motion } from 'framer-motion';
import AnalyticsChart from '../components/AnalyticsChart';

const StatBox = ({ label, value, delay }) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay }}
        className="glass-panel p-4 rounded-lg border-l-2 border-accent-cyan/50 hover:border-accent-cyan transition-colors"
    >
        <span className="block font-mono text-xs text-gray-500 uppercase tracking-wider mb-1">{label}</span>
        <span className="font-sans font-bold text-2xl text-white">{value}</span>
    </motion.div>
);

const PlayerDetails = () => {
    const { id } = useParams();
    const [player, setPlayer] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchPlayerData = async () => {
            try {
                const data = await nhlApi.getPlayerDetails(id);
                setPlayer(data);
            } catch (error) {
                console.error('Failed to fetch player details:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchPlayerData();
    }, [id]);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-[60vh]">
                <div className="h-16 w-16 rounded-full border-t-2 border-b-2 border-accent-magenta animate-spin"></div>
            </div>
        );
    }

    if (!player) return null;

    return (
        <div className="space-y-8">
            <Link to={`/team/${player.currentTeamAbbrev}`} className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors group">
                <ArrowLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
                <span className="font-mono text-sm">BACK TO TEAM</span>
            </Link>

            {/* Holographic Player Card */}
            <div className="relative glass-panel rounded-2xl p-8 md:p-12 overflow-hidden">
                <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-accent-cyan/5 rounded-full blur-[100px] -translate-y-1/2 translate-x-1/3" />

                <div className="relative z-10 flex flex-col md:flex-row items-center md:items-end gap-8 md:gap-12">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="relative"
                    >
                        <div className="absolute inset-0 bg-accent-cyan/20 blur-2xl rounded-full" />
                        <img
                            src={player.headshot}
                            alt={`${player.firstName.default} ${player.lastName.default}`}
                            className="w-48 h-48 md:w-64 md:h-64 rounded-full bg-zinc-900 object-cover border-4 border-white/10 relative z-10"
                        />
                        <div className="absolute bottom-0 right-0 bg-accent-cyan text-black font-mono font-bold text-xl px-3 py-1 rounded z-20">
                            #{player.sweaterNumber}
                        </div>
                    </motion.div>

                    <div className="flex-1 text-center md:text-left">
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.2 }}
                        >
                            <h1 className="text-5xl md:text-7xl font-sans font-bold text-white tracking-tighter mb-2 text-glow">
                                {player.firstName.default} <br />
                                <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-500">
                                    {player.lastName.default}
                                </span>
                            </h1>

                            <div className="flex flex-wrap justify-center md:justify-start gap-6 text-gray-400 font-mono text-sm mt-6">
                                <div className="flex items-center gap-2">
                                    <Ruler size={16} className="text-accent-cyan" />
                                    <span>{player.heightInInches}"</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Weight size={16} className="text-accent-magenta" />
                                    <span>{player.weightInPounds} lbs</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Calendar size={16} className="text-accent-lime" />
                                    <span>{player.birthDate}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <MapPin size={16} className="text-white" />
                                    <span>{player.birthCity.default}, {player.birthCountry}</span>
                                </div>
                            </div>
                        </motion.div>
                    </div>
                </div>
            </div>

            {/* Stats Grid */}
            <section>
                <div className="flex items-center gap-3 mb-6">
                    <Activity className="text-accent-cyan" />
                    <h2 className="text-2xl font-sans font-bold tracking-wide text-white">SEASON METRICS</h2>
                    <div className="h-px flex-1 bg-gradient-to-r from-accent-cyan/50 to-transparent" />
                </div>

                {player.featuredStats ? (
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                        {Object.entries(player.featuredStats.regularSeason.subSeason).map(([key, value], i) => (
                            <StatBox
                                key={key}
                                label={key.replace(/([A-Z])/g, ' $1').trim()}
                                value={value}
                                delay={i * 0.1}
                            />
                        ))}
                    </div>
                ) : (
                    <div className="glass-panel p-8 text-center text-gray-500 font-mono">
                        NO STATS AVAILABLE
                    </div>
                )}
            </section>

            {/* Charts */}
            {player.last5Games && (
                <section>
                    <h2 className="text-2xl font-sans font-bold tracking-wide text-white mb-6">PERFORMANCE TRENDS</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <AnalyticsChart
                            data={player.last5Games.map(g => ({ name: g.opponentAbbrev, points: g.points, goals: g.goals, assists: g.assists }))}
                            title="POINTS PRODUCTION"
                            dataKey="points"
                            color="#00f2ff"
                        />
                        <AnalyticsChart
                            data={player.last5Games.map(g => ({ name: g.opponentAbbrev, toi: parseFloat(g.toi.replace(':', '.')) }))}
                            title="TIME ON ICE (MIN)"
                            dataKey="toi"
                            color="#ff0055"
                        />
                    </div>
                </section>
            )}
        </div>
    );
};

export default PlayerDetails;
