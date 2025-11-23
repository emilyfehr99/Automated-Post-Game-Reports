import React from 'react';
import clsx from 'clsx';

const PeriodStatsTable = ({ periodStats, awayTeam, homeTeam }) => {
    // Defensive check: ensure periodStats is an array
    if (!periodStats || !Array.isArray(periodStats) || periodStats.length === 0) {
        return null;
    }

    const metrics = [
        { key: 'goals', label: 'GF', tooltip: 'Goals For' },
        { key: 'shots', label: 'S', tooltip: 'Shots on Goal' },
        { key: 'corsi', label: 'CF%', tooltip: 'Corsi For %' },
        { key: 'xg', label: 'xG', tooltip: 'Expected Goals' },
        { key: 'hits', label: 'HITS', tooltip: 'Hits' },
        { key: 'faceoff_pct', label: 'FO%', tooltip: 'Faceoff Win %' },
        { key: 'pim', label: 'PIM', tooltip: 'Penalty Minutes' },
        { key: 'blocked_shots', label: 'BLK', tooltip: 'Blocked Shots' },
        { key: 'giveaways', label: 'GV', tooltip: 'Giveaways' },
        { key: 'takeaways', label: 'TK', tooltip: 'Takeaways' },
        { key: 'nzt', label: 'NZT', tooltip: 'Neutral Zone Turnovers' },
        { key: 'ozs', label: 'OZS', tooltip: 'Offensive Zone Shots' },
        { key: 'rush', label: 'RUSH', tooltip: 'Rush Shots' }
    ];

    // Calculate totals safely
    const totals = metrics.reduce((acc, metric) => {
        acc[metric.key] = {
            away: periodStats.reduce((sum, p) => sum + (parseFloat(p?.away_stats?.[metric.key]) || 0), 0),
            home: periodStats.reduce((sum, p) => sum + (parseFloat(p?.home_stats?.[metric.key]) || 0), 0)
        };

        // Special handling for percentages (average them)
        if (['corsi', 'faceoff_pct'].includes(metric.key)) {
            acc[metric.key].away /= periodStats.length;
            acc[metric.key].home /= periodStats.length;
        }
        return acc;
    }, {});

    return (
        <div className="glass-card overflow-hidden rounded-2xl border border-white/5">
            <div className="overflow-x-auto">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="bg-white/5 border-b border-white/10">
                            <th className="py-4 px-6 text-left font-display font-bold text-gray-400">METRIC</th>
                            {periodStats.map((period, idx) => (
                                <th key={idx} className="py-4 px-4 text-center font-display font-bold text-gray-400">
                                    {period.period}
                                </th>
                            ))}
                            <th className="py-4 px-6 text-center font-display font-bold text-white bg-white/5">TOTAL</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {metrics.map((metric) => (
                            <tr key={metric.key} className="hover:bg-white/5 transition-colors">
                                <td className="py-3 px-6 font-mono text-gray-400 font-medium" title={metric.tooltip}>
                                    {metric.label}
                                </td>
                                {periodStats.map((period, idx) => {
                                    const awayVal = parseFloat(period.away_stats[metric.key]) || 0;
                                    const homeVal = parseFloat(period.home_stats[metric.key]) || 0;
                                    const isPct = ['corsi', 'faceoff_pct'].includes(metric.key);

                                    return (
                                        <td key={idx} className="py-3 px-4">
                                            <div className="flex items-center justify-center gap-3 font-mono text-xs">
                                                <div className="flex items-center gap-1.5">
                                                    <img src={awayTeam?.logo} alt={awayTeam?.abbrev} className="w-5 h-5 opacity-80" />
                                                    <span className={clsx(awayVal > homeVal ? "text-accent-primary font-bold" : "text-text-muted")}>
                                                        {isPct ? awayVal.toFixed(1) + '%' : (metric.key === 'xg' ? awayVal.toFixed(2) : awayVal)}
                                                    </span>
                                                </div>
                                                <span className="text-text-secondary">|</span>
                                                <div className="flex items-center gap-1.5">
                                                    <span className={clsx(homeVal > awayVal ? "text-accent-secondary font-bold" : "text-text-muted")}>
                                                        {isPct ? homeVal.toFixed(1) + '%' : (metric.key === 'xg' ? homeVal.toFixed(2) : homeVal)}
                                                    </span>
                                                    <img src={homeTeam?.logo} alt={homeTeam?.abbrev} className="w-5 h-5 opacity-80" />
                                                </div>
                                            </div>
                                        </td>
                                    );
                                })}
                                <td className="py-3 px-6 bg-white/5">
                                    <div className="flex items-center justify-center gap-3 font-mono text-xs font-bold">
                                        <span className="text-accent-primary">
                                            {['corsi', 'faceoff_pct'].includes(metric.key)
                                                ? totals[metric.key].away.toFixed(1) + '%'
                                                : (metric.key === 'xg' ? totals[metric.key].away.toFixed(2) : totals[metric.key].away)}
                                        </span>
                                        <span className="text-text-muted">|</span>
                                        <span className="text-accent-secondary">
                                            {['corsi', 'faceoff_pct'].includes(metric.key)
                                                ? totals[metric.key].home.toFixed(1) + '%'
                                                : (metric.key === 'xg' ? totals[metric.key].home.toFixed(2) : totals[metric.key].home)}
                                        </span>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            <div className="bg-white/5 px-6 py-3 border-t border-white/10 flex justify-between items-center text-xs font-mono text-text-muted">
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-accent-primary"></div>
                    <span>{awayTeam?.abbrev}</span>
                </div>
                <span>PERIOD BREAKDOWN</span>
                <div className="flex items-center gap-2">
                    <span>{homeTeam?.abbrev}</span>
                    <div className="w-2 h-2 rounded-full bg-accent-secondary"></div>
                </div>
            </div>
        </div>
    );
};

export default PeriodStatsTable;
