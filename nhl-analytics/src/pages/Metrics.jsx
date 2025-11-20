import React, { useEffect, useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { nhlApi } from '../api/nhl';
import { backendApi } from '../api/backend';
import { motion } from 'framer-motion';
import { ArrowUpDown, ArrowUp, ArrowDown, Search } from 'lucide-react';
import clsx from 'clsx';

const SortIcon = ({ column, sortConfig }) => {
    if (sortConfig.key !== column) {
        return <ArrowUpDown size={14} className="text-gray-600 opacity-50 group-hover:opacity-100" />;
    }
    return sortConfig.direction === 'ascending' ?
        <ArrowUp size={14} className="text-accent-cyan" /> :
        <ArrowDown size={14} className="text-accent-cyan" />;
};

const Metrics = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [loadingAdvanced, setLoadingAdvanced] = useState(false);
    const [advancedMetrics, setAdvancedMetrics] = useState({});
    const [sortConfig, setSortConfig] = useState({ key: 'points', direction: 'descending' });
    const [filter, setFilter] = useState('');
    const [backendAvailable, setBackendAvailable] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Use current date to avoid redirect issues
                const today = new Date().toISOString().split('T')[0];
                const standingsData = await nhlApi.getStandings(today);

                const processedData = standingsData.standings.map(team => ({
                    rank: team.leagueSequence,
                    name: team.teamName.default,
                    abbrev: team.teamAbbrev.default,
                    logo: team.teamLogo,
                    gp: team.gamesPlayed,
                    w: team.wins,
                    l: team.losses,
                    otl: team.otLosses,
                    pts: team.points,
                    pPct: team.pointPctg.toFixed(3),
                    gf: team.goalFor,
                    ga: team.goalAgainst,
                    diff: team.goalDifferential,
                    l10: `${team.l10Wins}-${team.l10Losses}-${team.l10OtLosses}`,
                    streak: `${team.streakCode}${team.streakCount}`,
                    rw: team.regulationWins,
                    row: team.regulationPlusOtWins,
                }));
                setData(processedData);
                setLoading(false);

                // Try to fetch advanced metrics from backend
                setLoadingAdvanced(true);
                try {
                    const metrics = await backendApi.getTeamMetrics();
                    setAdvancedMetrics(metrics);
                    setBackendAvailable(true);
                } catch (error) {
                    console.warn('Backend API not available, advanced metrics will not be shown:', error);
                    setBackendAvailable(false);
                }
                setLoadingAdvanced(false);
            } catch (error) {
                console.error('Failed to fetch metrics data:', error);
                setLoading(false);
                setLoadingAdvanced(false);
            }
        };

        fetchData();
    }, []);

    const handleSort = (key) => {
        setSortConfig((prev) => ({
            key,
            direction: prev.key === key && prev.direction === 'ascending' ? 'descending' : 'ascending',
        }));
    };

    // Helper to display metric value, showing "—" for zeros
    const displayMetric = (value) => {
        if (value === undefined || value === null || value === 0 || value === 0.0 || value === '0.0') {
            return '—';
        }
        return value;
    };

    const sortedData = useMemo(() => {
        // Merge basic data with advanced metrics
        let sortableItems = data.map(item => {
            const advanced = advancedMetrics[item.abbrev] || {};
            return { ...item, ...advanced };
        });

        if (sortConfig.key !== null) {
            sortableItems.sort((a, b) => {
                let aValue = a[sortConfig.key];
                let bValue = b[sortConfig.key];

                // Handle numeric strings if necessary, though most should be numbers now
                // Handle null/undefined
                if (aValue === undefined || aValue === null || aValue === '-') aValue = -Infinity;
                if (bValue === undefined || bValue === null || bValue === '-') bValue = -Infinity;

                if (aValue < bValue) {
                    return sortConfig.direction === 'ascending' ? -1 : 1;
                }
                if (aValue > bValue) {
                    return sortConfig.direction === 'ascending' ? 1 : -1;
                }
                return 0;
            });
        }
        return sortableItems.filter(item =>
            item.name.toLowerCase().includes(filter.toLowerCase()) ||
            item.abbrev.toLowerCase().includes(filter.toLowerCase())
        );
    }, [data, advancedMetrics, sortConfig, filter]);

    const getHeatmapColor = (value, min, max, inverse = false) => {
        // Simple normalization for color coding
        // This is a simplified version; for production, use a proper scale
        const normalized = (value - min) / (max - min);
        const intensity = inverse ? 1 - normalized : normalized;

        if (intensity > 0.8) return 'text-accent-cyan font-bold';
        if (intensity < 0.2) return 'text-accent-magenta font-bold';
        return 'text-white';
    };

    // Calculate min/max for heatmaps
    const stats = useMemo(() => {
        if (data.length === 0) return {};
        return {
            gf: { min: Math.min(...data.map(d => d.gf)), max: Math.max(...data.map(d => d.gf)) },
            ga: { min: Math.min(...data.map(d => d.ga)), max: Math.max(...data.map(d => d.ga)) },
            diff: { min: Math.min(...data.map(d => d.diff)), max: Math.max(...data.map(d => d.diff)) },
        };
    }, [data]);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-[60vh]">
                <div className="h-16 w-16 rounded-full border-t-2 border-b-2 border-accent-cyan animate-spin"></div>
            </div>
        );
    }

    const columns = [
        { key: 'rank', label: 'RK', align: 'center' },
        { key: 'name', label: 'TEAM', align: 'left' },
        { key: 'gp', label: 'GP', align: 'center' },
        { key: 'w', label: 'W', align: 'center' },
        { key: 'l', label: 'L', align: 'center' },
        { key: 'otl', label: 'OTL', align: 'center' },
        { key: 'pts', label: 'PTS', align: 'center', highlight: true },
        { key: 'pPct', label: 'P%', align: 'center' },
        { key: 'gf', label: 'GF', align: 'center' },
        { key: 'ga', label: 'GA', align: 'center' },
        { key: 'diff', label: 'DIFF', align: 'center' },
        { key: 'l10', label: 'L10', align: 'center' },
        { key: 'streak', label: 'STRK', align: 'center' },

        // Advanced Metrics - Core
        { key: 'gs', label: 'GS', align: 'center', advanced: true, tooltip: 'Game Score' },
        { key: 'xg', label: 'xG', align: 'center', advanced: true, tooltip: 'Expected Goals' },
        { key: 'hdc', label: 'HDC', align: 'center', advanced: true, tooltip: 'High Danger Chances' },

        // Zone Metrics
        { key: 'ozs', label: 'OZS', align: 'center', advanced: true, tooltip: 'Offensive Zone Shots' },
        { key: 'nzs', label: 'NZS', align: 'center', advanced: true, tooltip: 'Neutral Zone Shots' },
        { key: 'dzs', label: 'DZS', align: 'center', advanced: true, tooltip: 'Defensive Zone Shots' },

        // Shot Generation
        { key: 'fc', label: 'FC', align: 'center', advanced: true, tooltip: 'Forecheck/Cycle Shots' },
        { key: 'rush', label: 'RUSH', align: 'center', advanced: true, tooltip: 'Rush Shots' },

        // Turnovers
        { key: 'nzts', label: 'NZT', align: 'center', advanced: true, tooltip: 'Neutral Zone Turnovers' },
        { key: 'nztsa', label: 'NZTSA', align: 'center', advanced: true, tooltip: 'NZ Turnovers to Shots Against' },

        // Movement
        { key: 'lateral', label: 'LAT', align: 'center', advanced: true, tooltip: 'Lateral Movement' },
        { key: 'longitudinal', label: 'LONG', align: 'center', advanced: true, tooltip: 'Longitudinal Movement' },

        // Shooting
        { key: 'shots', label: 'SOG', align: 'center', advanced: true, tooltip: 'Shots on Goal' },
        { key: 'goals', label: 'G/G', align: 'center', advanced: true, tooltip: 'Goals per Game' },

        // Possession
        { key: 'corsi_pct', label: 'CF%', align: 'center', advanced: true, tooltip: 'Corsi For %' },

        // Physical
        { key: 'hits', label: 'HITS', align: 'center', advanced: true, tooltip: 'Hits per Game' },
        { key: 'blocks', label: 'BLK', align: 'center', advanced: true, tooltip: 'Blocked Shots' },
        { key: 'giveaways', label: 'GV', align: 'center', advanced: true, tooltip: 'Giveaways' },
        { key: 'takeaways', label: 'TK', align: 'center', advanced: true, tooltip: 'Takeaways' },
        { key: 'pim', label: 'PIM', align: 'center', advanced: true, tooltip: 'Penalty Minutes' },

        // Special Teams
        { key: 'pp_pct', label: 'PP%', align: 'center', advanced: true, tooltip: 'Power Play %' },
        { key: 'pk_pct', label: 'PK%', align: 'center', advanced: true, tooltip: 'Penalty Kill %' },
        { key: 'fo_pct', label: 'FO%', align: 'center', advanced: true, tooltip: 'Faceoff %' },
    ];

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-end gap-4">
                <div>
                    <h1 className="text-4xl font-sans font-bold text-white tracking-tighter mb-2">
                        LEAGUE <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent-cyan to-accent-lime">METRICS</span>
                    </h1>
                    <p className="text-gray-400 font-mono text-sm">
                        Comprehensive team statistics and performance data.
                    </p>
                </div>

                <div className="relative w-full md:w-64">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={16} />
                    <input
                        type="text"
                        placeholder="Filter teams..."
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                        className="w-full bg-white/5 border border-white/10 rounded-full py-2 pl-10 pr-4 text-white font-mono text-sm focus:outline-none focus:border-accent-cyan/50 transition-colors"
                    />
                </div>
            </div>

            {/* Loading Advanced Metrics Banner */}
            {loadingAdvanced && (
                <div className="glass-panel p-4 rounded-xl border border-accent-cyan/30 bg-accent-cyan/5">
                    <div className="flex items-center gap-3">
                        <div className="h-4 w-4 rounded-full border-t-2 border-b-2 border-accent-cyan animate-spin"></div>
                        <span className="font-mono text-sm text-accent-cyan">
                            Loading advanced metrics from backend...
                        </span>
                    </div>
                </div>
            )}

            {/* Backend Unavailable Warning */}
            {!backendAvailable && !loadingAdvanced && (
                <div className="glass-panel p-4 rounded-xl border border-accent-magenta/30 bg-accent-magenta/5">
                    <div className="flex items-center gap-3">
                        <span className="font-mono text-sm text-accent-magenta">
                            ⚠️ Backend API unavailable. Advanced metrics (GS, NZTS, OZS, etc.) will not be displayed. Start the Flask server with: <code className="bg-white/10 px-2 py-1 rounded">python /Users/emilyfehr8/CascadeProjects/api_server.py</code>
                        </span>
                    </div>
                </div>
            )}

            {/* Data Table */}
            <div className="glass-panel rounded-xl overflow-hidden border border-white/10">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm font-mono">
                        <thead>
                            <tr className="bg-white/5 border-b border-white/10">
                                {columns.map((col) => (
                                    <th
                                        key={col.key}
                                        onClick={() => handleSort(col.key)}
                                        className={clsx(
                                            "p-4 text-gray-400 font-medium cursor-pointer hover:text-white transition-colors group select-none whitespace-nowrap",
                                            col.align === 'center' ? 'text-center' : 'text-left',
                                            sortConfig.key === col.key && "text-accent-cyan bg-white/5"
                                        )}
                                    >
                                        <div className={clsx("flex items-center gap-1", col.align === 'center' && "justify-center")}>
                                            {col.label}
                                            <SortIcon column={col.key} sortConfig={sortConfig} />
                                        </div>
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {sortedData.map((team, index) => (
                                <motion.tr
                                    key={team.abbrev}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: index * 0.02 }}
                                    className="hover:bg-white/5 transition-colors group"
                                >
                                    <td className="p-4 text-center text-gray-500">{team.rank}</td>
                                    <td className="p-4">
                                        <Link to={`/team/${team.abbrev}`} className="flex items-center gap-3 group-hover:opacity-80 transition-opacity">
                                            <img src={team.logo} alt={team.abbrev} className="w-6 h-6 opacity-80 group-hover:opacity-100 group-hover:scale-110 transition-all" />
                                            <span className="font-sans font-bold text-white group-hover:text-accent-cyan transition-colors">{team.name}</span>
                                        </Link>
                                    </td>
                                    <td className="p-4 text-center text-gray-400">{team.gp}</td>
                                    <td className="p-4 text-center text-white">{team.w}</td>
                                    <td className="p-4 text-center text-gray-400">{team.l}</td>
                                    <td className="p-4 text-center text-gray-400">{team.otl}</td>
                                    <td className="p-4 text-center font-bold text-lg text-white bg-white/5">{team.pts}</td>
                                    <td className="p-4 text-center text-gray-400">{team.pPct}</td>
                                    <td className={clsx("p-4 text-center", getHeatmapColor(team.gf, stats.gf.min, stats.gf.max))}>{team.gf}</td>
                                    <td className={clsx("p-4 text-center", getHeatmapColor(team.ga, stats.ga.min, stats.ga.max, true))}>{team.ga}</td>
                                    <td className={clsx("p-4 text-center", team.diff > 0 ? "text-accent-lime" : team.diff < 0 ? "text-accent-magenta" : "text-gray-400")}>
                                        {team.diff > 0 ? '+' : ''}{team.diff}
                                    </td>
                                    <td className="p-4 text-center text-gray-400">{team.l10}</td>
                                    <td className="p-4 text-center text-white">{team.streak}</td>

                                    {/* Advanced Metrics - Core */}
                                    <td className="p-4 text-center text-accent-cyan bg-white/5" title="Game Score">
                                        {loadingAdvanced ? '...' : displayMetric(team.gs)}
                                    </td>
                                    <td className="p-4 text-center text-gray-400" title="Expected Goals">
                                        {loadingAdvanced ? '...' : displayMetric(team.xg)}
                                    </td>
                                    <td className="p-4 text-center text-gray-400" title="High Danger Chances">
                                        {loadingAdvanced ? '...' : displayMetric(team.hdc)}
                                    </td>

                                    {/* Zone Metrics */}
                                    <td className="p-4 text-center text-gray-400" title="Offensive Zone Shots">
                                        {loadingAdvanced ? '...' : displayMetric(team.ozs)}
                                    </td>
                                    <td className="p-4 text-center text-gray-400" title="Neutral Zone Shots">
                                        {loadingAdvanced ? '...' : displayMetric(team.nzs)}
                                    </td>
                                    <td className="p-4 text-center text-gray-400" title="Defensive Zone Shots">
                                        {loadingAdvanced ? '...' : displayMetric(team.dzs)}
                                    </td>

                                    {/* Shot Generation */}
                                    <td className="p-4 text-center text-gray-400" title="Forecheck/Cycle Shots">
                                        {loadingAdvanced ? '...' : displayMetric(team.fc)}
                                    </td>
                                    <td className="p-4 text-center text-gray-400" title="Rush Shots">
                                        {loadingAdvanced ? '...' : displayMetric(team.rush)}
                                    </td>

                                    {/* Turnovers */}
                                    <td className="p-4 text-center text-gray-400" title="Neutral Zone Turnovers">
                                        {loadingAdvanced ? '...' : displayMetric(team.nzts)}
                                    </td>
                                    <td className="p-4 text-center text-gray-400" title="NZ Turnovers to Shots Against">
                                        {loadingAdvanced ? '...' : displayMetric(team.nztsa)}
                                    </td>

                                    {/* Movement */}
                                    <td className="p-4 text-center text-gray-400" title="Lateral Movement">
                                        {loadingAdvanced ? '...' : displayMetric(team.lateral)}
                                    </td>
                                    <td className="p-4 text-center text-gray-400" title="Longitudinal Movement">
                                        {loadingAdvanced ? '...' : displayMetric(team.longitudinal)}
                                    </td>

                                    {/* Shooting */}
                                    <td className="p-4 text-center text-gray-400" title="Shots on Goal">
                                        {loadingAdvanced ? '...' : displayMetric(team.shots)}
                                    </td>
                                    <td className="p-4 text-center text-gray-400" title="Goals per Game">
                                        {loadingAdvanced ? '...' : displayMetric(team.goals)}
                                    </td>

                                    {/* Possession */}
                                    <td className="p-4 text-center text-gray-400" title="Corsi For %">
                                        {loadingAdvanced ? '...' : displayMetric(team.corsi_pct)}
                                    </td>

                                    {/* Physical */}
                                    <td className="p-4 text-center text-gray-400" title="Hits per Game">
                                        {loadingAdvanced ? '...' : displayMetric(team.hits)}
                                    </td>
                                    <td className="p-4 text-center text-gray-400" title="Blocked Shots">
                                        {loadingAdvanced ? '...' : displayMetric(team.blocks)}
                                    </td>
                                    <td className="p-4 text-center text-gray-400" title="Giveaways">
                                        {loadingAdvanced ? '...' : displayMetric(team.giveaways)}
                                    </td>
                                    <td className="p-4 text-center text-gray-400" title="Takeaways">
                                        {loadingAdvanced ? '...' : displayMetric(team.takeaways)}
                                    </td>
                                    <td className="p-4 text-center text-gray-400" title="Penalty Minutes">
                                        {loadingAdvanced ? '...' : displayMetric(team.pim)}
                                    </td>

                                    {/* Special Teams */}
                                    <td className="p-4 text-center text-gray-400" title="Power Play %">
                                        {loadingAdvanced ? '...' : displayMetric(team.pp_pct)}
                                    </td>
                                    <td className="p-4 text-center text-gray-400" title="Penalty Kill %">
                                        {loadingAdvanced ? '...' : displayMetric(team.pk_pct)}
                                    </td>
                                    <td className="p-4 text-center text-gray-400" title="Faceoff %">
                                        {loadingAdvanced ? '...' : displayMetric(team.fo_pct)}
                                    </td>
                                </motion.tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default Metrics;
