import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import clsx from 'clsx';

const GameCard = ({ game, prediction, awayMetrics, homeMetrics }) => {
    const isLive = game.gameState === 'LIVE' || game.gameState === 'CRIT';

    // Handle both decimal (0.47) and percentage (47) formats
    const awayProbRaw = prediction?.predicted_away_win_prob || prediction?.calibrated_away_prob || 0;
    const homeProbRaw = prediction?.predicted_home_win_prob || prediction?.calibrated_home_prob || 0;

    // If value is > 1, it's already a percentage; otherwise multiply by 100
    const awayProb = awayProbRaw > 1 ? awayProbRaw.toFixed(1) : (awayProbRaw * 100).toFixed(1);
    const homeProb = homeProbRaw > 1 ? homeProbRaw.toFixed(1) : (homeProbRaw * 100).toFixed(1);

    const showProb = prediction && (awayProbRaw > 0 || homeProbRaw > 0);

    // Metrics comparison helper
    const MetricComparison = ({ label, awayValue, homeValue, higherIsBetter = true }) => {
        if (!awayValue || !homeValue) return null;

        const awayNum = parseFloat(awayValue);
        const homeNum = parseFloat(homeValue);
        const awayLeads = higherIsBetter ? awayNum > homeNum : awayNum < homeNum;
        const homeLeads = higherIsBetter ? homeNum > awayNum : homeNum < awayNum;

        return (
            <div className="flex items-center justify-between text-xs">
                <span className={clsx("font-mono", awayLeads ? "text-accent-cyan font-bold" : "text-gray-500")}>
                    {awayValue}
                </span>
                <span className="text-gray-600 font-mono mx-2">{label}</span>
                <span className={clsx("font-mono", homeLeads ? "text-accent-magenta font-bold" : "text-gray-500")}>
                    {homeValue}
                </span>
            </div>
        );
    };

    return (
        <Link to={`/game/${game.id}`}>
            <motion.div
                whileHover={{ scale: 1.02 }}
                className="glass-card rounded-xl p-6 relative overflow-hidden group cursor-pointer"
            >
                {/* Status Indicator */}
                <div className="absolute top-0 right-0 p-4">
                    {isLive ? (
                        <div className="flex items-center gap-2">
                            <span className="relative flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-magenta opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-accent-magenta"></span>
                            </span>
                            <span className="text-xs font-mono text-accent-magenta font-bold tracking-wider">LIVE</span>
                        </div>
                    ) : (
                        <span className="text-xs font-mono text-gray-500 tracking-wider">{game.gameState}</span>
                    )}
                </div>

                <div className="flex justify-between items-center mt-4">
                    {/* Away Team */}
                    <div className="flex flex-col items-center gap-3 w-1/3">
                        <img src={game.awayTeam.logo} alt={game.awayTeam.abbrev} className="w-16 h-16 drop-shadow-lg" />
                        <span className="font-sans font-bold text-2xl tracking-tighter">{game.awayTeam.abbrev}</span>
                        <span className="text-4xl font-mono font-bold text-white">{game.awayTeam.score || 0}</span>
                        {/* Win Probability */}
                        {showProb && !isLive && (
                            <div className="mt-2 px-3 py-1 rounded-full bg-accent-cyan/10 border border-accent-cyan/30">
                                <span className="text-xs font-mono text-accent-cyan font-bold">{awayProb}%</span>
                            </div>
                        )}
                    </div>

                    {/* VS / Time */}
                    <div className="flex flex-col items-center justify-center w-1/3">
                        <span className="text-xs font-mono text-gray-600 mb-2">VS</span>
                        {game.startTimeUTC && !isLive && (
                            <span className="text-sm font-mono text-accent-cyan border border-accent-cyan/30 px-2 py-1 rounded">
                                {new Date(game.startTimeUTC).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                        )}
                    </div>

                    {/* Home Team */}
                    <div className="flex flex-col items-center gap-3 w-1/3">
                        <img src={game.homeTeam.logo} alt={game.homeTeam.abbrev} className="w-16 h-16 drop-shadow-lg" />
                        <span className="font-sans font-bold text-2xl tracking-tighter">{game.homeTeam.abbrev}</span>
                        <span className="text-4xl font-mono font-bold text-white">{game.homeTeam.score || 0}</span>
                        {/* Win Probability */}
                        {showProb && !isLive && (
                            <div className="mt-2 px-3 py-1 rounded-full bg-accent-magenta/10 border border-accent-magenta/30">
                                <span className="text-xs font-mono text-accent-magenta font-bold">{homeProb}%</span>
                            </div>
                        )}
                    </div>
                </div>

                {/* Hover Glow Effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-in-out pointer-events-none" />
            </motion.div>
        </Link>
    );
};

export default GameCard;
