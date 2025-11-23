import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Clock, Calendar } from 'lucide-react';
import { nhlApi } from '../api/nhl';

const LiveGameTicker = () => {
    const [games, setGames] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchGames = async () => {
            try {
                // Use local date to avoid UTC rollover issues
                const date = new Date();
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                const today = `${year}-${month}-${day}`;
                const data = await nhlApi.getSchedule(today);
                setGames(data.games || []);
            } catch (error) {
                console.error('Failed to fetch live games:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchGames();
        const interval = setInterval(fetchGames, 60000); // Update every minute
        return () => clearInterval(interval);
    }, []);

    if (loading) return null;
    if (games.length === 0) return null;

    return (
        <div className="w-full bg-bg-secondary/50 border-b border-white/5 backdrop-blur-sm overflow-hidden">
            <div className="max-w-7xl mx-auto px-4 py-2">
                <div className="flex items-center gap-4 overflow-x-auto scrollbar-hide">
                    <div className="flex items-center gap-2 text-accent-primary whitespace-nowrap">
                        <div className="w-2 h-2 rounded-full bg-accent-primary animate-pulse" />
                        <span className="text-xs font-mono font-bold tracking-wider">LIVE ACTION</span>
                    </div>

                    <div className="h-4 w-px bg-white/10" />

                    <div className="flex gap-6">
                        {games.map((game) => (
                            <div key={game.id} className="flex items-center gap-3 min-w-fit group cursor-pointer hover:bg-white/5 px-3 py-1 rounded-lg transition-colors">
                                <div className="flex flex-col items-end">
                                    <span className="text-xs font-bold text-white">{game.awayTeam.abbrev}</span>
                                    <span className="text-[10px] text-text-muted">
                                        {game.awayTeam.score || 0}
                                    </span>
                                </div>
                                <div className="text-[10px] font-mono text-text-muted">VS</div>
                                <div className="flex flex-col items-start">
                                    <span className="text-xs font-bold text-white">{game.homeTeam.abbrev}</span>
                                    <span className="text-[10px] text-text-muted">
                                        {game.homeTeam.score || 0}
                                    </span>
                                </div>
                                <div className="ml-2 px-2 py-0.5 rounded bg-white/5 text-[10px] font-mono text-accent-secondary">
                                    {game.gameState === 'LIVE' || game.gameState === 'IN_PROGRESS' ? (
                                        <span className="text-green-400 animate-pulse">
                                            {game.periodDescriptor?.number}P {game.clock?.timeRemaining}
                                        </span>
                                    ) : (
                                        <span>{game.startTimeUTC ? new Date(game.startTimeUTC).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'TBD'}</span>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LiveGameTicker;
