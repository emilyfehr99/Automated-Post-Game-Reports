import React, { useEffect, useState } from 'react';
import { nhlApi } from '../api/nhl';
import { backendApi } from '../api/backend';
import { Calendar, Trophy, Activity, TrendingUp } from 'lucide-react';
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
                // Use local date to avoid UTC rollover issues
                const date = new Date();
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                const today = `${year}-${month}-${day}`;
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

                let fetchedGames = [];
                if (scheduleResult.status === 'fulfilled') {
                    fetchedGames = scheduleResult.value.gameWeek?.[0]?.games || [];
                } else {
                    console.error('Schedule fetch failed:', scheduleResult.reason);
                }

                setGames(fetchedGames);

                if (predictionsResult.status === 'fulfilled') {
                    // Create a map of predictions by game ID or team matchup
                    const predMap = {};
                    const preds = predictionsResult.value || [];
                    preds.forEach(pred => {
                        const key = `${pred.away_team}_${pred.home_team}`;
                        predMap[key] = pred;
                    });

                    // For finished and live games, fetch live data to get probabilities
                    const liveOrFinishedGames = fetchedGames.filter(g =>
                        ['FINAL', 'OFF', 'LIVE', 'CRIT'].includes(g.gameState)
                    );
                    const liveDataPromises = liveOrFinishedGames.map(game =>
                        backendApi.getLiveGame(game.id).catch(() => null)
                    );

                    const liveDataResults = await Promise.all(liveDataPromises);

                    // Update predictions with live data for finished/live games
                    liveOrFinishedGames.forEach((game, idx) => {
                        const liveData = liveDataResults[idx];
                        if (liveData) {
                            const key = `${game.awayTeam.abbrev}_${game.homeTeam.abbrev}`;
                            predMap[key] = {
                                ...predMap[key],
                                predicted_away_win_prob: liveData.away_prob,
                                predicted_home_win_prob: liveData.home_prob,
                                calibrated_away_prob: liveData.away_prob,
                                calibrated_home_prob: liveData.home_prob
                            };
                        }
                    });

                    console.log('Predictions map:', predMap);
                    console.log('Sample prediction:', Object.values(predMap)[0]);
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
        <div className="space-y-12 pb-12">
            {/* Hero Section */}
            <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-bg-secondary to-bg-primary border border-white/5 p-8 md:p-12 shadow-2xl">
                <div className="absolute top-0 right-0 -mt-20 -mr-20 w-96 h-96 bg-accent-purple/20 rounded-full blur-3xl animate-pulse"></div>
                <div className="absolute bottom-0 left-0 -mb-20 -ml-20 w-80 h-80 bg-accent-cyan/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>

                <div className="relative z-10">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                    >
                        <h1 className="text-5xl md:text-7xl font-display font-black tracking-tighter mb-4">
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400">NHL</span>
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent-cyan to-accent-purple ml-4">ANALYTICS</span>
                        </h1>
                        <p className="text-xl text-gray-400 max-w-2xl font-light leading-relaxed">
                            Advanced metrics, real-time win probabilities, and comprehensive post-game analysis powered by machine learning.
                        </p>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.2 }}
                        className="flex flex-wrap gap-4 mt-8"
                    >
                        <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-md">
                            <Activity className="w-4 h-4 text-accent-cyan" />
                            <span className="text-sm font-mono text-gray-300">LIVE PREDICTIONS</span>
                        </div>
                        <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-md">
                            <Trophy className="w-4 h-4 text-accent-magenta" />
                            <span className="text-sm font-mono text-gray-300">ADVANCED STATS</span>
                        </div>
                        <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-md">
                            <TrendingUp className="w-4 h-4 text-accent-lime" />
                            <span className="text-sm font-mono text-gray-300">MOMENTUM TRACKING</span>
                        </div>
                    </motion.div>
                </div>
            </section>

            {/* Today's Games Grid */}
            <section>
                <div className="flex items-center justify-between mb-8">
                    <h2 className="text-3xl font-display font-bold flex items-center gap-3">
                        <Calendar className="w-8 h-8 text-accent-cyan" />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400">TODAY'S ACTION</span>
                    </h2>
                    <div className="h-px flex-1 bg-gradient-to-r from-white/10 to-transparent ml-8"></div>
                </div>

                {games.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                        {games.map((game, index) => {
                            const predictionKey = `${game.awayTeam.abbrev}_${game.homeTeam.abbrev}`;
                            const prediction = predictions[predictionKey];

                            return (
                                <motion.div
                                    key={game.id}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ duration: 0.4, delay: index * 0.1 }}
                                >
                                    <GameCard
                                        game={game}
                                        prediction={prediction}
                                        awayMetrics={teamMetrics[game.awayTeam.abbrev]}
                                        homeMetrics={teamMetrics[game.homeTeam.abbrev]}
                                    />
                                </motion.div>
                            );
                        })}
                    </div>
                ) : (
                    <div className="glass-panel p-12 text-center">
                        <p className="text-gray-400 font-mono text-lg">NO GAMES SCHEDULED FOR TODAY</p>
                    </div>
                )}
            </section>

            {/* League Standings */}
            <section>
                <div className="flex items-center justify-between mb-8">
                    <h2 className="text-3xl font-display font-bold flex items-center gap-3">
                        <Trophy className="w-8 h-8 text-accent-magenta" />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400">LEAGUE STANDINGS</span>
                    </h2>
                    <div className="h-px flex-1 bg-gradient-to-r from-white/10 to-transparent ml-8"></div>
                </div>

                <div className="glass-card overflow-hidden rounded-2xl border border-white/5">
                    <StandingsTable standings={standings} />
                </div>
            </section>
        </div>
    );
};

export default Home;
