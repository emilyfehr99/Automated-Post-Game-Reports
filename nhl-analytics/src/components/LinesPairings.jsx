import React from 'react';
import { Users } from 'lucide-react';

const LinesPairings = ({ boxscore, awayTeam, homeTeam, awayLines, homeLines }) => {
    const renderMoneyPuckLines = (lines, label) => {
        if (!lines || lines.length === 0) return null;
        return (
            <div className="mb-6">
                <h4 className="text-sm font-display font-bold text-text-muted mb-3 uppercase tracking-wider border-b border-white/10 pb-2">{label}</h4>
                <div className="space-y-3">
                    {lines.map((line, idx) => (
                        <div key={idx} className="p-3 rounded-lg bg-white/5 border border-white/5 hover:border-white/10 transition-colors">
                            <div className="flex flex-wrap gap-2 mb-2">
                                {line.players.map((p, pIdx) => (
                                    <span key={pIdx} className="font-mono text-sm font-bold text-white">
                                        {p.name.replace('.', '. ')}
                                        {pIdx < line.players.length - 1 && <span className="text-gray-500 mx-1">-</span>}
                                    </span>
                                ))}
                            </div>
                            <div className="flex items-center gap-4 text-xs text-gray-400 font-mono">
                                <span title="Time on Ice">TOI: {(line.icetime / 60).toFixed(1)}m</span>
                                <span title="Expected Goals %">xG%: {(line.xg_pct * 100).toFixed(1)}%</span>
                                <span title="Goals For - Goals Against">G: {line.goals_for}-{line.goals_against}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    if (awayLines && homeLines) {
        return (
            <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Away Team Lines */}
                <div className="glass-card p-6">
                    <div className="flex items-center gap-3 mb-6">
                        <Users className="w-6 h-6 text-accent-primary" />
                        <h3 className="text-xl font-display font-bold">{awayTeam?.name?.default || awayTeam?.abbrev} LINES</h3>
                    </div>
                    <div className="space-y-4">
                        {renderMoneyPuckLines(awayLines.forwards, 'Forward Lines')}
                        {renderMoneyPuckLines(awayLines.defense, 'Defense Pairings')}
                    </div>
                </div>

                {/* Home Team Lines */}
                <div className="glass-card p-6">
                    <div className="flex items-center gap-3 mb-6">
                        <Users className="w-6 h-6 text-accent-secondary" />
                        <h3 className="text-xl font-display font-bold">{homeTeam?.name?.default || homeTeam?.abbrev} LINES</h3>
                    </div>
                    <div className="space-y-4">
                        {renderMoneyPuckLines(homeLines.forwards, 'Forward Lines')}
                        {renderMoneyPuckLines(homeLines.defense, 'Defense Pairings')}
                    </div>
                </div>
            </section>
        );
    }

    if (!boxscore?.playerByGameStats) {
        return (
            <div className="glass-card p-6 text-center text-text-muted">
                <div className="flex flex-col items-center gap-2">
                    <Users className="w-8 h-8 opacity-50" />
                    <p>Lines and pairings data not available yet.</p>
                </div>
            </div>
        );
    }

    const awayPlayers = boxscore.playerByGameStats.awayTeam || {};
    const homePlayers = boxscore.playerByGameStats.homeTeam || {};

    const renderPlayerLine = (players, label) => {
        if (!players || players.length === 0) return null;

        return (
            <div className="mb-4">
                <h4 className="text-sm font-display font-bold text-text-muted mb-2 uppercase">{label}</h4>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {players.map((player, idx) => (
                        <div key={idx} className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                            <div className="font-mono text-sm text-white">
                                #{player.sweaterNumber} {player.name?.default || 'Unknown'}
                            </div>
                            <div className="text-xs text-text-muted">{player.position}</div>
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    return (
        <section className="space-y-6">
            {/* Away Team Lines */}
            <div className="glass-card p-6">
                <div className="flex items-center gap-3 mb-6">
                    <Users className="w-6 h-6 text-accent-primary" />
                    <h3 className="text-xl font-display font-bold">{awayTeam?.name?.default || awayTeam?.abbrev} LINES</h3>
                </div>
                <div className="space-y-4">
                    {renderPlayerLine(awayPlayers.forwards, 'Forwards')}
                    {renderPlayerLine(awayPlayers.defense, 'Defense')}
                    {renderPlayerLine(awayPlayers.goalies, 'Goalies')}
                </div>
            </div>

            {/* Home Team Lines */}
            <div className="glass-card p-6">
                <div className="flex items-center gap-3 mb-6">
                    <Users className="w-6 h-6 text-accent-secondary" />
                    <h3 className="text-xl font-display font-bold">{homeTeam?.name?.default || homeTeam?.abbrev} LINES</h3>
                </div>
                <div className="space-y-4">
                    {renderPlayerLine(homePlayers.forwards, 'Forwards')}
                    {renderPlayerLine(homePlayers.defense, 'Defense')}
                    {renderPlayerLine(homePlayers.goalies, 'Goalies')}
                </div>
            </div>
        </section>
    );
};

export default LinesPairings;
