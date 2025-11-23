import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import clsx from 'clsx';
import { nhlApi } from '../api/nhl';
import { backendApi } from '../api/backend';

// Team primary colors (hex)
const TEAM_COLORS = {
    'TBL': '#002868', 'NSH': '#FFB81C', 'EDM': '#041E42', 'FLA': '#C8102E',
    'COL': '#6F263D', 'DAL': '#006847', 'BOS': '#FFB81C', 'TOR': '#00205B',
    'MTL': '#AF1E2D', 'OTT': '#C8102E', 'BUF': '#002654', 'DET': '#CE1126',
    'CAR': '#CE1126', 'WSH': '#041E42', 'PIT': '#FFB81C', 'NYR': '#0038A8',
    'NYI': '#00539B', 'NJD': '#CE1126', 'PHI': '#F74902', 'CBJ': '#002654',
    'STL': '#002F87', 'MIN': '#154734', 'WPG': '#041E42', 'VGK': '#B4975A',
    'SJS': '#006D75', 'LAK': '#111111', 'ANA': '#F47A38', 'CGY': '#C8102E',
    'VAN': '#00205B', 'SEA': '#001628', 'UTA': '#000000', 'CHI': '#CF0A2C'
};

const GameCard = ({ game, prediction, awayMetrics, homeMetrics }) => {
    const [liveGameData, setLiveGameData] = useState(null);
    const [finalGameData, setFinalGameData] = useState(null);
    const isLive = game?.gameState === 'LIVE' || game?.gameState === 'CRIT';
    const isFinal = game?.gameState === 'FINAL' || game?.gameState === 'OFF';
    
    // Poll for live updates if game is live
    useEffect(() => {
        if (isLive && game?.id) {
            // Initial fetch - get both boxscore and live game data for likelihood calculation
            Promise.all([
                nhlApi.getGameCenter(game.id).catch(() => null),
                backendApi.getLiveGame(game.id).catch(() => null)
            ]).then(([boxscoreData, liveData]) => {
                if (boxscoreData?.boxscore) {
                    setLiveGameData(boxscoreData.boxscore);
                }
                if (liveData) {
                    console.log('Live game data received:', liveData);
                    console.log('Live win probability (top level):', liveData.live_win_probability);
                    console.log('Live win probability (in live_metrics):', liveData.live_metrics?.live_win_probability);
                    console.log('All keys in liveData:', Object.keys(liveData));
                    setFinalGameData(liveData);
                }
            }).catch(err => console.error('Error updating game card:', err));
            
            const interval = setInterval(() => {
                Promise.all([
                    nhlApi.getGameCenter(game.id).catch(() => null),
                    backendApi.getLiveGame(game.id).catch(() => null)
                ]).then(([boxscoreData, liveData]) => {
                    if (boxscoreData?.boxscore) {
                        setLiveGameData(boxscoreData.boxscore);
                    }
                    if (liveData) {
                        console.log('Live game data updated:', liveData);
                        console.log('Live win probability (top level):', liveData.live_win_probability);
                        console.log('Live win probability (in live_metrics):', liveData.live_metrics?.live_win_probability);
                        setFinalGameData(liveData);
                    }
                }).catch(err => console.error('Error updating game card:', err));
            }, 10000); // Update every 10 seconds
            
            return () => clearInterval(interval);
        }
    }, [isLive, game?.id]);

    // Fetch actual game data for completed games (one-time fetch)
    // The backend calculates postgame_win_probability using the exact formula from pdf_report_generator.calculate_win_probability()
    // which uses POSTGAME correlation weights and calculates Game Score from play-by-play data
    useEffect(() => {
        if (isFinal && game?.id && !finalGameData) {
            // Fetch both boxscore and live game data for actual metrics
            Promise.all([
                nhlApi.getGameCenter(game.id).catch(() => null),
                backendApi.getLiveGame(game.id).catch(() => null)
            ]).then(([boxscoreData, liveData]) => {
                if (boxscoreData?.boxscore) {
                    setLiveGameData(boxscoreData.boxscore);
                }
                if (liveData) {
                    console.log('Final game data received:', liveData);
                    console.log('Postgame win probability from API (calculated by backend using report generator formula):', liveData.postgame_win_probability);
                    
                    // The backend should return postgame_win_probability calculated using:
                    // - Game Score from play-by-play (0.75×G + 0.075×SOG + 0.05×BLK + 0.15×PD - 0.15×PT)
                    // - xG from play-by-play
                    // - HDC from play-by-play
                    // - Period stats (Corsi, PP%, hits, PIM)
                    // - POSTGAME correlation weights
                    // - Sigmoid conversion to probabilities
                    
                    setFinalGameData(liveData);
                }
            }).catch(err => console.error('Error fetching final game data:', err));
        }
    }, [isFinal, game?.id, finalGameData]);

    // Handle both decimal (0.47) and percentage (47) formats
    const awayProbRaw = prediction?.predicted_away_win_prob || prediction?.calibrated_away_prob || prediction?.away_win_prob || 0;
    const homeProbRaw = prediction?.predicted_home_win_prob || prediction?.calibrated_home_prob || prediction?.home_win_prob || 0;

    // If value is > 1, it's already a percentage; otherwise multiply by 100
    const awayProb = awayProbRaw > 1 ? parseFloat(awayProbRaw) : parseFloat(awayProbRaw * 100);
    const homeProb = homeProbRaw > 1 ? parseFloat(homeProbRaw) : parseFloat(homeProbRaw * 100);

    // Show probability if we have a prediction and valid probability values
    const showProb = prediction && (awayProbRaw !== 0 || homeProbRaw !== 0) && (awayProbRaw !== undefined && homeProbRaw !== undefined);
    
    // Get team colors
    const awayColor = TEAM_COLORS[game?.awayTeam?.abbrev] || '#00D4FF';
    const homeColor = TEAM_COLORS[game?.homeTeam?.abbrev] || '#FF00FF';
    
    // Get game time and arena
    const gameTime = game?.startTimeUTC ? new Date(game.startTimeUTC).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', timeZoneName: 'short' }) : null;
    const arenaName = game?.venue?.default || game?.venueName || null;

    return (
        <Link to={`/game/${game?.id}`} className="block h-full">
            <motion.div
                whileHover={{ y: -4, scale: 1.01 }}
                className="glass-card h-full relative overflow-hidden group border border-white/5 hover:border-primary/30 transition-all duration-300"
            >
                {/* Background Gradient Glow */}
                <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-accent-purple/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                {/* Status Badge */}
                <div className="absolute top-3 right-3 z-10">
                    {isLive ? (
                        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-accent-magenta/20 border border-accent-magenta/50 backdrop-blur-md">
                            <span className="relative flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-magenta opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-accent-magenta"></span>
                            </span>
                            <span className="text-xs font-display font-bold text-accent-magenta tracking-wider">
                                Period {liveGameData?.periodDescriptor?.number || liveGameData?.period || '1'} - {liveGameData?.clock?.timeRemaining || liveGameData?.clock || '20:00'}
                            </span>
                        </div>
                    ) : isFinal ? (
                        <div className="px-3 py-1 rounded-full bg-white/5 border border-white/10 backdrop-blur-md">
                            <span className="text-xs font-display text-gray-400 tracking-wider">FINAL</span>
                        </div>
                    ) : (
                        <div className="px-3 py-1 rounded-full bg-primary/10 border border-primary/30 backdrop-blur-md">
                            <span className="text-xs font-display text-primary tracking-wider">
                                {gameTime || 'TBD'}
                            </span>
                        </div>
                    )}
                </div>

                <div className="p-6 flex flex-col h-full justify-between relative z-0">
                    {/* Teams Row */}
                    <div className="flex items-center justify-between mb-6 mt-2">
                        {/* Away Team */}
                        <div className="flex flex-col items-center gap-3 flex-1">
                            <div className="relative">
                                <div className="absolute inset-0 bg-accent-cyan/20 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                                <img
                                    src={game?.awayTeam?.logo || ''}
                                    alt={game?.awayTeam?.abbrev || 'Away'}
                                    className="w-20 h-20 object-contain drop-shadow-2xl relative z-10 transform group-hover:scale-110 transition-transform duration-300"
                                />
                            </div>
                            <div className="text-center w-full">
                                <span className="font-display font-bold text-2xl tracking-tight block">{game?.awayTeam?.abbrev || 'AWAY'}</span>
                                {isLive || isFinal ? (
                                    <span className="text-4xl font-display font-bold text-white block mt-1 text-glow-cyan">
                                        {finalGameData?.away_score ?? finalGameData?.live_metrics?.away_score ?? liveGameData?.awayTeam?.score ?? game?.awayTeam?.score ?? 0}
                                    </span>
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
                                    className="w-20 h-20 object-contain drop-shadow-2xl relative z-10 transform group-hover:scale-110 transition-transform duration-300"
                                />
                            </div>
                            <div className="text-center w-full">
                                <span className="font-display font-bold text-2xl tracking-tight block">{game?.homeTeam?.abbrev || 'HOME'}</span>
                                {isLive || isFinal ? (
                                    <span className="text-4xl font-display font-bold text-white block mt-1 text-glow-magenta">
                                        {finalGameData?.home_score ?? finalGameData?.live_metrics?.home_score ?? liveGameData?.homeTeam?.score ?? game?.homeTeam?.score ?? 0}
                                    </span>
                                ) : (
                                    <span className="text-sm text-gray-400 font-mono mt-1">HOME</span>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Win Probability Bar - Pre-game predictions for upcoming games */}
                    {showProb && !isLive && !isFinal && prediction && (
                        <div className="mt-4">
                            <div className="flex justify-between text-xs font-mono mb-2 px-1">
                                <span className="font-bold" style={{ color: awayColor }}>{awayProb.toFixed(1)}%</span>
                                <span className="text-gray-500">WIN PROBABILITY</span>
                                <span className="font-bold" style={{ color: homeColor }}>{homeProb.toFixed(1)}%</span>
                            </div>
                            <div className="h-3 bg-white/5 rounded-full overflow-hidden relative flex">
                                <div
                                    className="h-full relative"
                                    style={{ 
                                        width: `${awayProb}%`,
                                        backgroundColor: awayColor
                                    }}
                                >
                                    <div className="absolute inset-0 bg-white/20 animate-pulse" />
                                </div>
                                <div
                                    className="h-full relative"
                                    style={{ 
                                        width: `${homeProb}%`,
                                        backgroundColor: homeColor
                                    }}
                                >
                                    <div className="absolute inset-0 bg-white/20 animate-pulse" />
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Post-Game Win Probability Bar - Actual calculated probability for completed games */}
                    {isFinal && finalGameData?.postgame_win_probability && (
                        <div className="mt-4">
                            <div className="flex justify-between text-xs font-mono mb-2 px-1">
                                <span className="font-bold" style={{ color: awayColor }}>
                                    {finalGameData.postgame_win_probability.away_probability.toFixed(1)}%
                                </span>
                                <span className="text-gray-500">LIKELIHOOD OF WINNING</span>
                                <span className="font-bold" style={{ color: homeColor }}>
                                    {finalGameData.postgame_win_probability.home_probability.toFixed(1)}%
                                </span>
                            </div>
                            <div className="h-3 bg-white/5 rounded-full overflow-hidden relative flex">
                                <div
                                    className="h-full relative"
                                    style={{ 
                                        width: `${finalGameData.postgame_win_probability.away_probability}%`,
                                        backgroundColor: awayColor
                                    }}
                                >
                                    <div className="absolute inset-0 bg-white/20" />
                                </div>
                                <div
                                    className="h-full relative"
                                    style={{ 
                                        width: `${finalGameData.postgame_win_probability.home_probability}%`,
                                        backgroundColor: homeColor
                                    }}
                                >
                                    <div className="absolute inset-0 bg-white/20" />
                                </div>
                            </div>
                        </div>
                    )}


                    {/* Live Game Likelihood of Winning Bar - Replaces PER, TIME, SOG */}
                    {isLive && (() => {
                        const winProb = finalGameData?.live_win_probability;
                        console.log('GameCard render check - isLive:', isLive, 'winProb:', winProb, 'finalGameData keys:', finalGameData ? Object.keys(finalGameData) : 'no data');
                        
                        if (winProb) {
                            return (
                                <div className="mt-auto">
                                    <div>
                                        <div className="flex justify-between text-xs font-mono mb-2 px-1">
                                            <span className="font-bold" style={{ color: awayColor }}>
                                                {winProb.away_probability.toFixed(1)}%
                                            </span>
                                            <span className="text-gray-500">LIKELIHOOD OF WINNING</span>
                                            <span className="font-bold" style={{ color: homeColor }}>
                                                {winProb.home_probability.toFixed(1)}%
                                            </span>
                                        </div>
                                        <div className="h-3 bg-white/5 rounded-full overflow-hidden relative flex">
                                            <div
                                                className="h-full relative"
                                                style={{ 
                                                    width: `${winProb.away_probability}%`,
                                                    backgroundColor: awayColor
                                                }}
                                            >
                                                <div className="absolute inset-0 bg-white/20 animate-pulse" />
                                            </div>
                                            <div
                                                className="h-full relative"
                                                style={{ 
                                                    width: `${winProb.home_probability}%`,
                                                    backgroundColor: homeColor
                                                }}
                                            >
                                                <div className="absolute inset-0 bg-white/20 animate-pulse" />
                                            </div>
                                        </div>
                                        {/* SOG per team with logos below progress bar */}
                                        <div className="mt-2 flex items-center justify-between text-xs font-mono">
                                            <div className="flex items-center gap-1.5">
                                                <img src={game?.awayTeam?.logo || ''} alt={game?.awayTeam?.abbrev || 'Away'} className="w-4 h-4 object-contain" />
                                                <span className="text-white font-bold">{liveGameData?.awayTeam?.sog ?? game?.awayTeam?.sog ?? finalGameData?.live_metrics?.away_shots ?? finalGameData?.away_shots ?? 0}</span>
                                                <span className="text-gray-400">SOG</span>
                                            </div>
                                            <div className="flex items-center gap-1.5">
                                                <img src={game?.homeTeam?.logo || ''} alt={game?.homeTeam?.abbrev || 'Home'} className="w-4 h-4 object-contain" />
                                                <span className="text-white font-bold">{liveGameData?.homeTeam?.sog ?? game?.homeTeam?.sog ?? finalGameData?.live_metrics?.home_shots ?? finalGameData?.home_shots ?? 0}</span>
                                                <span className="text-gray-400">SOG</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            );
                        }
                        
                        // Fallback to PER, TIME, SOG if likelihood not available yet
                        return (
                            <div className="mt-auto">
                                <div className="grid grid-cols-3 gap-2 text-center text-xs font-mono text-gray-400 bg-white/5 rounded-lg p-2">
                                    <div>
                                        <div className="text-white font-bold">Period {liveGameData?.periodDescriptor?.number || liveGameData?.period || '1'}</div>
                                        <div className="text-[10px]">PER</div>
                                    </div>
                                    <div>
                                        <div className="text-white font-bold">{liveGameData?.clock?.timeRemaining || liveGameData?.clock || '20:00'}</div>
                                        <div className="text-[10px]">TIME</div>
                                    </div>
                                    <div>
                                        <div className="text-white font-bold">{((liveGameData?.awayTeam?.sog ?? game?.awayTeam?.sog) || 0) + ((liveGameData?.homeTeam?.sog ?? game?.homeTeam?.sog) || 0)}</div>
                                        <div className="text-[10px]">SOG</div>
                                    </div>
                                </div>
                            </div>
                        );
                    })()}

                </div>
            </motion.div>
        </Link>
    );
};

export default GameCard;
