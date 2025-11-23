import React from 'react';
import clsx from 'clsx';

const PeriodStatsTable = ({ periodStats, awayTeam, homeTeam, currentPeriod }) => {
    // Debug logging
    React.useEffect(() => {
        console.log('PeriodStatsTable received:', {
            periodStats,
            isArray: Array.isArray(periodStats),
            length: periodStats?.length,
            firstPeriod: periodStats?.[0],
            currentPeriod
        });
    }, [periodStats, currentPeriod]);
    
    // Show empty table structure when no data
    const hasData = periodStats && Array.isArray(periodStats) && periodStats.length > 0;
    
    // Filter periods to only show active/completed periods
    // If currentPeriod is provided, only show periods <= currentPeriod
    // Also always show OT/SO if they exist (they're marked as 'OT' or 'SO' strings)
    // CRITICAL: If currentPeriod is 3 or higher, show all numeric periods (game is complete)
    const filteredPeriodStats = hasData ? periodStats.filter(period => {
        const periodNum = period.period;
        // Always show OT and SO if they exist
        if (periodNum === 'OT' || periodNum === 'SO') {
            return true;
        }
        // For numeric periods, only show if <= currentPeriod
        // If currentPeriod is 3, show all periods (game is complete)
        const periodInt = parseInt(periodNum);
        if (!isNaN(periodInt)) {
            // If currentPeriod is 3 or higher, show all periods (game is complete)
            if (currentPeriod >= 3) {
                return true;
            }
            return currentPeriod ? periodInt <= currentPeriod : true;
        }
        return true;
    }) : [];
    
    // If no data, show empty table structure
    if (!hasData) {
        const emptyMetrics = [
            { key: 'goals', label: 'GF' },
            { key: 'ga', label: 'GA' },
            { key: 'shots', label: 'S' },
            { key: 'corsi', label: 'CF%' },
            { key: 'xg', label: 'xGF' },
            { key: 'xga', label: 'xGA' },
            { key: 'hits', label: 'HITS' },
            { key: 'faceoff_pct', label: 'FO%' },
            { key: 'pim', label: 'PIM' },
            { key: 'blocked_shots', label: 'BLK' },
            { key: 'giveaways', label: 'GV' },
            { key: 'takeaways', label: 'TK' },
            { key: 'nzt', label: 'NZT' },
            { key: 'nztsa', label: 'NZTSA' },
            { key: 'ozs', label: 'OZS' },
            { key: 'dzs', label: 'DZS' },
            { key: 'nzs', label: 'NZS' },
            { key: 'rush', label: 'RUSH' },
            { key: 'fc', label: 'FC' }
        ];

        return (
            <div className="glass-card overflow-hidden rounded-2xl border border-white/5">
                <div className="overflow-x-auto scrollbar-thin scrollbar-thumb-gray-600/30 scrollbar-track-transparent hover:scrollbar-thumb-gray-500/40" style={{
                    scrollbarWidth: 'thin',
                    scrollbarColor: 'rgba(75, 85, 99, 0.3) transparent'
                }}>
                    <style>{`
                        .overflow-x-auto::-webkit-scrollbar {
                            height: 6px;
                        }
                        .overflow-x-auto::-webkit-scrollbar-track {
                            background: transparent;
                        }
                        .overflow-x-auto::-webkit-scrollbar-thumb {
                            background: rgba(75, 85, 99, 0.3);
                            border-radius: 3px;
                            border: 1px solid rgba(255, 255, 255, 0.1);
                        }
                        .overflow-x-auto::-webkit-scrollbar-thumb:hover {
                            background: rgba(75, 85, 99, 0.4);
                        }
                    `}</style>
                    <table className="w-full text-sm min-w-[800px]">
                        <thead>
                            <tr className="bg-white/5 border-b border-white/10">
                                <th className="py-4 px-4 text-center font-display font-bold text-gray-400 sticky left-0 bg-gray-900/80 backdrop-blur-sm z-20 border-r border-white/20 shadow-[2px_0_4px_rgba(0,0,0,0.3)]">PERIOD</th>
                                <th className="py-4 px-4 text-center font-display font-bold text-gray-400 sticky left-[80px] bg-gray-900/80 backdrop-blur-sm z-20 border-r border-white/20 shadow-[2px_0_4px_rgba(0,0,0,0.3)]">TEAM</th>
                                {emptyMetrics.map((metric) => (
                                    <th key={metric.key} className="py-4 px-3 text-center font-display font-bold text-gray-400 whitespace-nowrap">
                                        {metric.label}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {[1, 2, 3].map((periodNum) => (
                                <React.Fragment key={periodNum}>
                                    <tr className="hover:bg-white/5 transition-colors">
                                        <td className="py-2 px-4 text-center font-mono text-gray-400 font-medium sticky left-0 bg-gray-900/80 backdrop-blur-sm z-20 border-r border-white/20 shadow-[2px_0_4px_rgba(0,0,0,0.3)]" rowSpan={2}>
                                            {periodNum}
                                        </td>
                                        <td className="py-2 px-4 text-center sticky left-[80px] bg-gray-900/80 backdrop-blur-sm z-20 border-r border-white/20 shadow-[2px_0_4px_rgba(0,0,0,0.3)]">
                                            {awayTeam?.logo ? (
                                                <img 
                                                    src={awayTeam.logo} 
                                                    alt={awayTeam.abbrev || 'AWAY'} 
                                                    className="w-6 h-6 mx-auto object-contain"
                                                />
                                            ) : (
                                                <span className="font-mono text-xs text-accent-primary font-bold">
                                                    {awayTeam?.abbrev || 'AWAY'}
                                                </span>
                                            )}
                                        </td>
                                        {emptyMetrics.map((metric) => (
                                            <td key={metric.key} className="py-2 px-3 text-center">
                                                <div className="font-mono text-xs text-text-muted">-</div>
                                            </td>
                                        ))}
                                    </tr>
                                    <tr className="hover:bg-white/5 transition-colors">
                                        <td className="py-2 px-4 text-center sticky left-[80px] bg-gray-900/80 backdrop-blur-sm z-20 border-r border-white/20 shadow-[2px_0_4px_rgba(0,0,0,0.3)]">
                                            {homeTeam?.logo ? (
                                                <img 
                                                    src={homeTeam.logo} 
                                                    alt={homeTeam.abbrev || 'HOME'} 
                                                    className="w-6 h-6 mx-auto object-contain"
                                                />
                                            ) : (
                                                <span className="font-mono text-xs text-accent-secondary font-bold">
                                                    {homeTeam?.abbrev || 'HOME'}
                                                </span>
                                            )}
                                        </td>
                                        {emptyMetrics.map((metric) => (
                                            <td key={metric.key} className="py-2 px-3 text-center">
                                                <div className="font-mono text-xs text-text-muted">-</div>
                                            </td>
                                        ))}
                                    </tr>
                                </React.Fragment>
                            ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
    }

    const metrics = [
        { key: 'goals', label: 'GF', tooltip: 'Goals For', isPercentage: false, isDecimal: false },
        { key: 'ga', label: 'GA', tooltip: 'Goals Against', isPercentage: false, isDecimal: false },
        { key: 'shots', label: 'S', tooltip: 'Shots on Goal', isPercentage: false, isDecimal: false },
        { key: 'corsi', label: 'CF%', tooltip: 'Corsi For %', isPercentage: true, isDecimal: false },
        { key: 'xg', label: 'xGF', tooltip: 'Expected Goals For', isPercentage: false, isDecimal: true },
        { key: 'xga', label: 'xGA', tooltip: 'Expected Goals Against', isPercentage: false, isDecimal: true },
        { key: 'hits', label: 'HITS', tooltip: 'Hits', isPercentage: false, isDecimal: false },
        { key: 'faceoff_pct', label: 'FO%', tooltip: 'Faceoff Win %', isPercentage: true, isDecimal: false },
        { key: 'pim', label: 'PIM', tooltip: 'Penalty Minutes', isPercentage: false, isDecimal: false },
        { key: 'blocked_shots', label: 'BLK', tooltip: 'Blocked Shots', isPercentage: false, isDecimal: false },
        { key: 'giveaways', label: 'GV', tooltip: 'Giveaways', isPercentage: false, isDecimal: false },
        { key: 'takeaways', label: 'TK', tooltip: 'Takeaways', isPercentage: false, isDecimal: false },
        { key: 'nzt', label: 'NZT', tooltip: 'Neutral Zone Turnovers', isPercentage: false, isDecimal: false },
        { key: 'nztsa', label: 'NZTSA', tooltip: 'Neutral Zone Turnover Shots Against', isPercentage: false, isDecimal: false },
        { key: 'ozs', label: 'OZS', tooltip: 'Offensive Zone Shots', isPercentage: false, isDecimal: false },
        { key: 'dzs', label: 'DZS', tooltip: 'Defensive Zone Shots', isPercentage: false, isDecimal: false },
        { key: 'nzs', label: 'NZS', tooltip: 'Neutral Zone Shots', isPercentage: false, isDecimal: false },
        { key: 'rush', label: 'RUSH', tooltip: 'Rush Shots on Goal', isPercentage: false, isDecimal: false },
        { key: 'fc', label: 'FC', tooltip: 'Forecheck Cycle Shots', isPercentage: false, isDecimal: false }
    ];

    // Calculate totals safely (using filtered periods)
    const totals = metrics.reduce((acc, metric) => {
        acc[metric.key] = {
            away: filteredPeriodStats.reduce((sum, p) => sum + (parseFloat(p?.away_stats?.[metric.key]) || 0), 0),
            home: filteredPeriodStats.reduce((sum, p) => sum + (parseFloat(p?.home_stats?.[metric.key]) || 0), 0)
        };

        // Special handling for percentages (average them)
        if (metric.isPercentage && filteredPeriodStats.length > 0) {
            acc[metric.key].away /= filteredPeriodStats.length;
            acc[metric.key].home /= filteredPeriodStats.length;
        }
        return acc;
    }, {});

    return (
        <div className="glass-card overflow-hidden rounded-2xl border border-white/5">
            <div className="overflow-x-auto scrollbar-thin scrollbar-thumb-gray-600/30 scrollbar-track-transparent hover:scrollbar-thumb-gray-500/40" style={{
                scrollbarWidth: 'thin',
                scrollbarColor: 'rgba(75, 85, 99, 0.3) transparent'
            }}>
                <style>{`
                    .overflow-x-auto::-webkit-scrollbar {
                        height: 6px;
                    }
                    .overflow-x-auto::-webkit-scrollbar-track {
                        background: transparent;
                    }
                    .overflow-x-auto::-webkit-scrollbar-thumb {
                        background: rgba(75, 85, 99, 0.3);
                        border-radius: 3px;
                        border: 1px solid rgba(255, 255, 255, 0.1);
                    }
                    .overflow-x-auto::-webkit-scrollbar-thumb:hover {
                        background: rgba(75, 85, 99, 0.4);
                    }
                `}</style>
                <table className="w-full text-sm min-w-[800px]">
                    <thead>
                        <tr className="bg-white/5 border-b border-white/10">
                            <th className="py-4 px-4 text-center font-display font-bold text-gray-400 sticky left-0 bg-gray-900/80 backdrop-blur-sm z-20 border-r border-white/20 shadow-[2px_0_4px_rgba(0,0,0,0.3)]">PERIOD</th>
                            <th className="py-4 px-4 text-center font-display font-bold text-gray-400 sticky left-[80px] bg-gray-900/80 backdrop-blur-sm z-20 border-r border-white/20 shadow-[2px_0_4px_rgba(0,0,0,0.3)]">TEAM</th>
                            {metrics.map((metric) => (
                                <th key={metric.key} className="py-4 px-3 text-center font-display font-bold text-gray-400 whitespace-nowrap" title={metric.tooltip}>
                                    {metric.label}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {filteredPeriodStats.map((period, periodIdx) => {
                            return (
                                <React.Fragment key={periodIdx}>
                                    {/* Away Team Row */}
                                    <tr className="hover:bg-white/5 transition-colors">
                                        <td className="py-2 px-4 text-center font-mono text-gray-400 font-medium sticky left-0 bg-gray-900/80 backdrop-blur-sm z-20 border-r border-white/20 shadow-[2px_0_4px_rgba(0,0,0,0.3)]" rowSpan={2}>
                                            {period.period}
                                        </td>
                                        <td className="py-2 px-4 text-center sticky left-[80px] bg-gray-900/80 backdrop-blur-sm z-20 border-r border-white/20 shadow-[2px_0_4px_rgba(0,0,0,0.3)]">
                                            {awayTeam?.logo ? (
                                                <img 
                                                    src={awayTeam.logo} 
                                                    alt={awayTeam.abbrev || 'AWAY'} 
                                                    className="w-6 h-6 mx-auto object-contain"
                                                />
                                            ) : (
                                                <span className="font-mono text-xs text-accent-primary font-bold">
                                                    {awayTeam?.abbrev || 'AWAY'}
                                                </span>
                                            )}
                                        </td>
                                        {metrics.map((metric) => {
                                            const awayVal = parseFloat(period.away_stats[metric.key]) || 0;
                                            const homeVal = parseFloat(period.home_stats[metric.key]) || 0;
                                            const isWinner = awayVal > homeVal;
                                            
                                            let displayValue;
                                            if (metric.isPercentage) {
                                                displayValue = awayVal.toFixed(1) + '%';
                                            } else if (metric.isDecimal) {
                                                displayValue = awayVal.toFixed(2);
                                            } else {
                                                displayValue = Math.round(awayVal);
                                            }

                                            return (
                                                <td key={metric.key} className="py-2 px-3 text-center">
                                                    <div className="font-mono text-xs">
                                                        <span className={clsx(
                                                            isWinner ? "text-accent-primary font-bold" : "text-text-muted"
                                                        )}>
                                                            {displayValue}
                                                </span>
                                            </div>
                                        </td>
                                    );
                                })}
                                    </tr>
                                    {/* Home Team Row */}
                                    <tr className="hover:bg-white/5 transition-colors">
                                        <td className="py-2 px-4 text-center sticky left-[80px] bg-gray-900/80 backdrop-blur-sm z-20 border-r border-white/20 shadow-[2px_0_4px_rgba(0,0,0,0.3)]">
                                            {homeTeam?.logo ? (
                                                <img 
                                                    src={homeTeam.logo} 
                                                    alt={homeTeam.abbrev || 'HOME'} 
                                                    className="w-6 h-6 mx-auto object-contain"
                                                />
                                            ) : (
                                                <span className="font-mono text-xs text-accent-secondary font-bold">
                                                    {homeTeam?.abbrev || 'HOME'}
                                                </span>
                                            )}
                                        </td>
                                        {metrics.map((metric) => {
                                            const awayVal = parseFloat(period.away_stats[metric.key]) || 0;
                                            const homeVal = parseFloat(period.home_stats[metric.key]) || 0;
                                            const isWinner = homeVal > awayVal;
                                            
                                            let displayValue;
                                            if (metric.isPercentage) {
                                                displayValue = homeVal.toFixed(1) + '%';
                                            } else if (metric.isDecimal) {
                                                displayValue = homeVal.toFixed(2);
                                            } else {
                                                displayValue = Math.round(homeVal);
                                            }

                                            return (
                                                <td key={metric.key} className="py-2 px-3 text-center">
                                                    <div className="font-mono text-xs">
                                                        <span className={clsx(
                                                            isWinner ? "text-accent-secondary font-bold" : "text-text-muted"
                                                        )}>
                                                            {displayValue}
                                        </span>
                                    </div>
                                </td>
                                            );
                                        })}
                            </tr>
                                </React.Fragment>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default PeriodStatsTable;
