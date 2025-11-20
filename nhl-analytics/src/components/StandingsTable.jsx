import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const StandingsTable = ({ standings }) => {
    return (
        <div className="glass-panel rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
                <table className="w-full text-left">
                    <thead className="bg-white/5 text-gray-400 font-mono text-xs uppercase tracking-wider border-b border-white/5">
                        <tr>
                            <th className="p-4 font-medium">Rank</th>
                            <th className="p-4 font-medium">Team</th>
                            <th className="p-4 font-medium text-center">GP</th>
                            <th className="p-4 font-medium text-center">W</th>
                            <th className="p-4 font-medium text-center">L</th>
                            <th className="p-4 font-medium text-center">OTL</th>
                            <th className="p-4 font-medium text-center text-white">PTS</th>
                            <th className="p-4 font-medium text-center">Diff</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5 font-mono text-sm">
                        {standings.slice(0, 10).map((team, index) => (
                            <motion.tr
                                key={team.teamAbbrev.default}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: index * 0.05 }}
                                className="hover:bg-white/5 transition-colors group"
                            >
                                <td className="p-4 text-gray-500">{team.leagueSequence}</td>
                                <td className="p-4">
                                    <Link to={`/team/${team.teamAbbrev.default}`} className="flex items-center gap-3 hover:text-accent-cyan transition-colors">
                                        <img src={team.teamLogo} alt={team.teamName.default} className="w-8 h-8 drop-shadow-md group-hover:scale-110 transition-transform" />
                                        <span className="font-sans font-bold text-lg tracking-tight text-white">{team.teamName.default}</span>
                                    </Link>
                                </td>
                                <td className="p-4 text-center text-gray-400">{team.gamesPlayed}</td>
                                <td className="p-4 text-center text-accent-cyan">{team.wins}</td>
                                <td className="p-4 text-center text-accent-magenta">{team.losses}</td>
                                <td className="p-4 text-center text-gray-400">{team.otLosses}</td>
                                <td className="p-4 text-center font-bold text-white text-lg">{team.points}</td>
                                <td className="p-4 text-center text-gray-400">{team.goalDifferential}</td>
                            </motion.tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default StandingsTable;
