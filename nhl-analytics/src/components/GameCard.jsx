import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { backendApi } from '../api/backend';
import clsx from 'clsx';

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

const GameCard = ({ game, prediction, awayMetrics, homeMetrics }) => {
    const [liveData, setLiveData] = useState(null);
    const isLive = game.gameState === 'LIVE' || game.gameState === 'CRIT';
    const isFinal = game.gameState === 'FINAL' || game.gameState === 'OFF';

    useEffect(() => {
        let mounted = true;
        if (isLive || isFinal) {
            backendApi.getLiveGame(game.id)
                .then(data => {
                    if (mounted) setLiveData(data);
                })
                .catch(err => console.error('Failed to fetch live game data for card:', err));
        }
        return () => { mounted = false; };
    }, [game.id, isLive, isFinal]);

    // Use live data if available, otherwise fall back to prediction
    const displayData = liveData || prediction;

    // Handle both decimal (0.47) and percentage (47) formats
    const awayProbRaw = displayData?.away_prob || displayData?.away_win_prob || displayData?.predicted_away_win_prob || displayData?.calibrated_away_prob || 0;
    const homeProbRaw = displayData?.home_prob || displayData?.home_win_prob || displayData?.predicted_home_win_prob || displayData?.calibrated_home_prob || 0;

    // If value is > 1, it's already a percentage; otherwise multiply by 100
    const awayProb = awayProbRaw > 1 ? awayProbRaw.toFixed(1) : (awayProbRaw * 100).toFixed(1);
    const homeProb = homeProbRaw > 1 ? homeProbRaw.toFixed(1) : (homeProbRaw * 100).toFixed(1);

    const showProb = displayData && (parseFloat(awayProb) > 0 || parseFloat(homeProb) > 0);

    return (
        <div className="block h-full relative group">
            <Link to={`/game/${game?.id}`} className="absolute inset-0 z-10" />

            <motion.div
                whileHover={{ y: -4, scale: 1.01 }}
                className="glass-card h-full relative overflow-hidden border border-white/5 hover:border-primary/30 transition-all duration-300 flex flex-col"
            >
                {/* Background Gradient Glow */}
                <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-accent-purple/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />

                {/* Status Badge */}
                <div className="absolute top-3 right-3 z-20 pointer-events-none">
                    {isLive ? (
                        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-accent-magenta/20 border border-accent-magenta/50 backdrop-blur-md">
                            <span className="relative flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-magenta opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-accent-magenta"></span>
                            </span>
                            <span className="text-xs font-display font-bold text-accent-magenta tracking-wider">LIVE</span>
                        </div>
                    ) : isFinal ? (
                        <div className="px-3 py-1 rounded-full bg-white/5 border border-white/10 backdrop-blur-md">
                            <span className="text-xs font-display text-gray-400 tracking-wider">FINAL</span>
                        </div>
                    ) : (
                        <div className="px-3 py-1 rounded-full bg-primary/10 border border-primary/30 backdrop-blur-md">
                            <span className="text-xs font-display text-primary tracking-wider">
                                {game?.startTimeUTC ? new Date(game.startTimeUTC).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'TBD'}
                            </span>
                        </div>
                    )}
                </div>

                <div className="p-6 flex flex-col h-full justify-between relative z-0 pointer-events-none">
                    {/* Teams Row */}
                    <div className="flex items-center justify-between mb-6 mt-8">
                        {/* Away Team */}
                        <div className="flex flex-col items-center gap-3 flex-1">
                            <div className="relative">
                                <div className="absolute inset-0 bg-accent-cyan/20 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                                <img
                                    src={game?.awayTeam?.logo || ''}
                                    alt={game?.awayTeam?.abbrev || 'Away'}
                                    className="w-28 h-28 object-contain drop-shadow-2xl relative z-10 transform group-hover:scale-110 transition-transform duration-300"
                                />
                            </div>
                            <div className="text-center">
                                <span className="font-display font-bold text-2xl tracking-tight block">{game?.awayTeam?.abbrev || 'AWAY'}</span>
                                {isLive || isFinal ? (
                                    <span className="text-4xl font-display font-bold text-white block mt-1 text-glow-cyan">{game?.awayTeam?.score ?? 0}</span>
                                ) : (
                                    <span className="text-sm text-gray-400 font-mono mt-1">AWAY</span>
                                )}
                            </div>
                        </div>

                        {/* VS / Divider */}
                        <div className="flex flex-col items-center justify-center px-4">
                            <span className="text-sm font-display text-gray-600 font-bold opacity-50">VS</span>
                        </div>

                        {/* Home Team */}
                        <div className="flex flex-col items-center gap-3 flex-1">
                            <div className="relative">
                                <div className="absolute inset-0 bg-accent-purple/20 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                                <img
                                    src={game?.homeTeam?.logo || ''}
                                    alt={game?.homeTeam?.abbrev || 'Home'}
                                    className="w-28 h-28 object-contain drop-shadow-2xl relative z-10 transform group-hover:scale-110 transition-transform duration-300"
                                />
                            </div>
                            <div className="text-center">
                                <span className="font-display font-bold text-2xl tracking-tight block">{game?.homeTeam?.abbrev || 'HOME'}</span>
                                {isLive || isFinal ? (
                                    <span className="text-4xl font-display font-bold text-white block mt-1 text-glow-magenta">{game?.homeTeam?.score ?? 0}</span>
                                ) : (
                                    <span className="text-sm text-gray-400 font-mono mt-1">HOME</span>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Win Probability Bar - All States */}
                    {showProb && (
                        <div className="mt-auto">
                            <div className="flex justify-between text-xs font-mono mb-2 px-1">
                                <span className="font-bold" style={{ color: getTeamColor(game?.awayTeam?.abbrev) }}>{awayProb}%</span>
                                <span className="text-gray-400">
                                    {isLive ? 'LIVE WIN PROBABILITY' : (isFinal ? 'FINAL WIN PROBABILITY' : 'WIN PROBABILITY')}
                                </span>
                                <span className="font-bold" style={{ color: getTeamColor(game?.homeTeam?.abbrev) }}>{homeProb}%</span>
                            </div>
                            <div className="h-2 bg-white/5 rounded-full overflow-hidden flex">
                                <div
                                    className="h-full transition-all duration-500"
                                    style={{
                                        width: `${awayProb}%`,
                                        backgroundColor: getTeamColor(game?.awayTeam?.abbrev)
                                    }}
                                />
                                <div
                                    className="h-full transition-all duration-500"
                                    style={{
                                        width: `${homeProb}%`,
                                        backgroundColor: getTeamColor(game?.homeTeam?.abbrev)
                                    }}
                                />
                            </div>
                        </div>
                    )}

                    {/* Live Game Stats Preview */}
                    {isLive && (
                        <div className="mt-4 grid grid-cols-3 gap-2 text-center text-xs font-mono text-gray-400 bg-white/5 rounded-lg p-2">
                            <div>
                                <div className="text-white font-bold">{game?.period || '1st'}</div>
                                <div className="text-[10px]">PER</div>
                            </div>
                            <div>
                                <div className="text-white font-bold">{game?.clock || '20:00'}</div>
                                <div className="text-[10px]">TIME</div>
                            </div>
                            <div>
                                <div className="text-white font-bold">{(game?.awayTeam?.sog || 0) + (game?.homeTeam?.sog || 0)}</div>
                                <div className="text-[10px]">SOG</div>
                            </div>
                        </div>
                    )}
                </div>
            </motion.div>
        </div>
    );
};

export default GameCard;
