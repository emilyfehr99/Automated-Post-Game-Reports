import React, { useEffect, useState } from 'react';
import { nhlApi } from '../api/nhl';
import { backendApi } from '../api/backend';
import { Calendar, Trophy, Activity } from 'lucide-react';
import { motion } from 'framer-motion';
import GameCard from '../components/GameCard';
import StandingsTable from '../components/StandingsTable';

const Home = () => {
    const [standings, setStandings] = useState([]);
    const [games, setGames] = useState([]);
    const [predictions, setPredictions] = useState({});
    const [teamMetrics, setTeamMetrics] = useState({});
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const today = new Date().toISOString().split('T')[0];
                const [standingsResult, scheduleResult, predictionsResult, metricsResult] = await Promise.allSettled([
                    nhlApi.getStandings(today),
                    nhlApi.getSchedule(today),
                    backendApi.getTodayPredictions(),
                    backendApi.getTeamMetrics()
                ]);

                if (standingsResult.status === 'fulfilled') {
                    setStandings(standingsResult.value.standings || []);
                } else {
                    console.error('Standings fetch failed:', standingsResult.reason);
                }

                if (scheduleResult.status === 'fulfilled') {
                    const fetchedGames = scheduleResult.value.gameWeek?.[0]?.games || [];

                    // DEBUG: Add completed game from yesterday (STL vs TOR) for verification
                    const debugGame = {
                        id: 2025020307,
                        gameState: 'OFF',
                        startTimeUTC: '2025-11-19T00:00:00Z',
                        awayTeam: {
                            abbrev: 'STL',
                            logo: 'https://assets.nhle.com/logos/nhl/svg/STL_light.svg',
                            score: 2
                        },
                        homeTeam: {
                            abbrev: 'TOR',
                            logo: 'https://assets.nhle.com/logos/nhl/svg/TOR_light.svg',
                            score: 3
                        }
                    };

                    setGames([...fetchedGames, debugGame]);
                } else {
                    console.error('Schedule fetch failed:', scheduleResult.reason);
                }

                if (predictionsResult.status === 'fulfilled') {
                    // Create a map of predictions by game ID or team matchup
                    const predMap = {};
                    const preds = predictionsResult.value || [];
                    preds.forEach(pred => {
                        const key = `${pred.away_team}_${pred.home_team}`;
                        predMap[key] = pred;
                    });
                    setPredictions(predMap);
                } else {
                    console.warn('Predictions fetch failed:', predictionsResult.reason);
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

    if (loading) {
        return (
            <div className="flex items-center justify-center h-[60vh]">
                <div className="relative">
                    <div className="h-16 w-16 rounded-full border-t-2 border-b-2 border-accent-cyan animate-spin"></div>
                    <div className="absolute inset-0 h-16 w-16 rounded-full border-r-2 border-l-2 border-accent-magenta animate-spin-reverse opacity-50"></div>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-12">
            {/* Hero Section */}
            <section className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-zinc-900 to-black border border-white/10 p-8 md:p-12">
                <div className="absolute top-0 right-0 -mt-12 -mr-12 h-64 w-64 bg-accent-cyan/10 rounded-full blur-3xl animate-pulse-slow" />
                <div className="relative z-10">
                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-5xl md:text-7xl font-sans font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-500 mb-4"
                    >
                        MODEL
                    </motion.h1>
                    <p className="text-gray-400 font-mono max-w-xl text-lg">
                        Real-time tracking of NHL performance, game states, and advanced metrics.
                        <span className="block mt-2 text-accent-cyan/80 text-sm">
                            {new Date().toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                        </span>
                    </p>
                </div>
            </section>

            {/* Games Grid */}
            <section>
                <div className="flex items-center gap-3 mb-6">
                    <Activity className="text-accent-magenta" />
                    <h2 className="text-2xl font-sans font-bold tracking-wide text-white">TODAY'S ACTION</h2>
                    <div className="h-px flex-1 bg-gradient-to-r from-white/10 to-transparent" />
                </div>

                {games.length === 0 ? (
                    <div className="glass-panel p-8 text-center text-gray-500 font-mono">
                        NO GAMES SCHEDULED FOR TODAY
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {games.map((game, index) => {
                            const predKey = `${game.awayTeam.abbrev}_${game.homeTeam.abbrev}`;
                            const prediction = predictions[predKey];
                            const awayMetrics = teamMetrics[game.awayTeam.abbrev];
                            const homeMetrics = teamMetrics[game.homeTeam.abbrev];

                            return (
                                <motion.div
                                    key={game.id}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: index * 0.1 }}
                                >
                                    <GameCard
                                        game={game}
                                        prediction={prediction}
                                        awayMetrics={awayMetrics}
                                        homeMetrics={homeMetrics}
                                    />
                                </motion.div>
                            );
                        })}
                    </div>
                )}
            </section>

            {/* Standings Section */}
            <section>
                <div className="flex items-center gap-3 mb-6">
                    <Trophy className="text-accent-lime" />
                    <h2 className="text-2xl font-sans font-bold tracking-wide text-white">LEAGUE LEADERS</h2>
                    <div className="h-px flex-1 bg-gradient-to-r from-white/10 to-transparent" />
                </div>
                <StandingsTable standings={standings} />
            </section>
        </div>
    );
};

export default Home;
