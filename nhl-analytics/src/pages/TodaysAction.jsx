import React, { useEffect, useState } from 'react';
import { backendApi } from '../api/backend';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Clock, Target } from 'lucide-react';
import clsx from 'clsx';

const TodaysAction = () => {
    const [predictions, setPredictions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchPredictions = async () => {
            try {
                const data = await backendApi.getTodayPredictions();
                setPredictions(data);
                setLoading(false);
            } catch (err) {
                console.error('Failed to fetch predictions:', err);
                setError('Failed to load predictions');
                setLoading(false);
            }
        };

        fetchPredictions();
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen bg-void pt-24 px-6">
                <div className="max-w-7xl mx-auto">
                    <div className="flex items-center justify-center h-64">
                        <div className="h-8 w-8 rounded-full border-t-2 border-b-2 border-accent-cyan animate-spin"></div>
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-void pt-24 px-6">
                <div className="max-w-7xl mx-auto">
                    <div className="glass-panel p-8 rounded-2xl border border-accent-magenta/30">
                        <p className="text-accent-magenta text-center">{error}</p>
                    </div>
                </div>
            </div>
        );
    }

    const getConfidenceColor = (confidence) => {
        switch (confidence?.toLowerCase()) {
            case 'high':
                return 'text-accent-cyan';
            case 'medium':
                return 'text-accent-magenta';
            case 'low':
                return 'text-gray-400';
            default:
                return 'text-gray-400';
        }
    };

    const getConfidenceIcon = (confidence) => {
        switch (confidence?.toLowerCase()) {
            case 'high':
                return '🔥';
            case 'medium':
                return '⚡';
            case 'low':
                return '💭';
            default:
                return '⚡';
        }
    };

    return (
        <div className="min-h-screen bg-void pt-24 px-6 pb-12">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-8"
                >
                    <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-accent-cyan via-accent-magenta to-accent-cyan bg-clip-text text-transparent">
                        Today's Action
                    </h1>
                    <p className="text-gray-400 text-lg">
                        AI-powered predictions for today's NHL games
                    </p>
                </motion.div>

                {/* Stats Summary */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
                >
                    <div className="glass-panel p-6 rounded-xl border border-accent-cyan/30">
                        <div className="flex items-center gap-3 mb-2">
                            <Target className="text-accent-cyan" size={24} />
                            <span className="text-gray-400">Games Today</span>
                        </div>
                        <p className="text-3xl font-bold text-white">{predictions.length}</p>
                    </div>
                    <div className="glass-panel p-6 rounded-xl border border-accent-magenta/30">
                        <div className="flex items-center gap-3 mb-2">
                            <TrendingUp className="text-accent-magenta" size={24} />
                            <span className="text-gray-400">Model Accuracy</span>
                        </div>
                        <p className="text-3xl font-bold text-white">58.0%</p>
                    </div>
                    <div className="glass-panel p-6 rounded-xl border border-accent-cyan/30">
                        <div className="flex items-center gap-3 mb-2">
                            <Clock className="text-accent-cyan" size={24} />
                            <span className="text-gray-400">Updated</span>
                        </div>
                        <p className="text-3xl font-bold text-white">6:30 AM</p>
                    </div>
                </motion.div>

                {/* Predictions Grid */}
                {predictions.length === 0 ? (
                    <div className="glass-panel p-12 rounded-2xl border border-white/10 text-center">
                        <p className="text-gray-400 text-lg">No games scheduled for today</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {predictions.map((game, index) => {
                            const awayProbRaw = game.predicted_away_win_prob || game.calibrated_away_prob || 0;
                            const homeProbRaw = game.predicted_home_win_prob || game.calibrated_home_prob || 0;

                            // Handle both decimal (0.47) and percentage (47) formats
                            const awayProb = awayProbRaw > 1 ? awayProbRaw : awayProbRaw * 100;
                            const homeProb = homeProbRaw > 1 ? homeProbRaw : homeProbRaw * 100;

                            const isFavorite = awayProb > homeProb ? 'away' : 'home';
                            const spread = Math.abs(awayProb - homeProb);

                            return (
                                <motion.div
                                    key={index}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.1 + index * 0.05 }}
                                    className="glass-panel p-6 rounded-xl border border-white/10 hover:border-accent-cyan/50 transition-all duration-300"
                                >
                                    {/* Game Header */}
                                    <div className="flex items-center justify-between mb-4">
                                        <span className="text-gray-400 text-sm">
                                            {game.start_time || 'TBD'}
                                        </span>
                                        <span className={clsx('text-sm font-mono', getConfidenceColor(game.confidence))}>
                                            {getConfidenceIcon(game.confidence)} {game.confidence?.toUpperCase() || 'MEDIUM'}
                                        </span>
                                    </div>

                                    {/* Teams */}
                                    <div className="space-y-4">
                                        {/* Away Team */}
                                        <div className={clsx(
                                            'flex items-center justify-between p-4 rounded-lg transition-all',
                                            isFavorite === 'away' ? 'bg-accent-cyan/10 border border-accent-cyan/30' : 'bg-white/5'
                                        )}>
                                            <div className="flex items-center gap-3">
                                                <span className="text-xl font-bold text-white">
                                                    {game.away_team || 'TBD'}
                                                </span>
                                                {isFavorite === 'away' && (
                                                    <span className="text-accent-cyan text-xs font-mono">FAVORITE</span>
                                                )}
                                            </div>
                                            <div className="text-right">
                                                <div className="text-2xl font-bold text-white">
                                                    {awayProb.toFixed(1)}%
                                                </div>
                                                {isFavorite === 'away' && (
                                                    <div className="text-accent-cyan text-xs">
                                                        +{spread.toFixed(1)}%
                                                    </div>
                                                )}
                                            </div>
                                        </div>

                                        {/* VS Divider */}
                                        <div className="flex items-center justify-center">
                                            <span className="text-gray-600 font-mono text-sm">@</span>
                                        </div>

                                        {/* Home Team */}
                                        <div className={clsx(
                                            'flex items-center justify-between p-4 rounded-lg transition-all',
                                            isFavorite === 'home' ? 'bg-accent-magenta/10 border border-accent-magenta/30' : 'bg-white/5'
                                        )}>
                                            <div className="flex items-center gap-3">
                                                <span className="text-xl font-bold text-white">
                                                    {game.home_team || 'TBD'}
                                                </span>
                                                {isFavorite === 'home' && (
                                                    <span className="text-accent-magenta text-xs font-mono">FAVORITE</span>
                                                )}
                                            </div>
                                            <div className="text-right">
                                                <div className="text-2xl font-bold text-white">
                                                    {homeProb.toFixed(1)}%
                                                </div>
                                                {isFavorite === 'home' && (
                                                    <div className="text-accent-magenta text-xs">
                                                        +{spread.toFixed(1)}%
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Upset Risk */}
                                    {game.upset_probability && (
                                        <div className="mt-4 pt-4 border-t border-white/10">
                                            <div className="flex items-center justify-between text-sm">
                                                <span className="text-gray-400">Upset Risk</span>
                                                <span className="text-accent-magenta font-mono">
                                                    {(game.upset_probability * 100).toFixed(1)}%
                                                </span>
                                            </div>
                                        </div>
                                    )}
                                </motion.div>
                            );
                        })}
                    </div>
                )}

                {/* Footer */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 }}
                    className="mt-12 text-center text-gray-500 text-sm"
                >
                    <p>🤖 Powered by Self-Learning AI Model • Updated Daily at 6:30 AM CT</p>
                </motion.div>
            </div>
        </div>
    );
};

export default TodaysAction;
