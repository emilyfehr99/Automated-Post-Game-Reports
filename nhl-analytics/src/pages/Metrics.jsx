import React, { useEffect, useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { nhlApi } from '../api/nhl';
import { backendApi } from '../api/backend';
import { motion } from 'framer-motion';
import { ArrowUpDown, ArrowUp, ArrowDown, Search } from 'lucide-react';
import clsx from 'clsx';

const SortIcon = ({ column, sortConfig }) => {
    if (sortConfig.key !== column) {
        return <ArrowUpDown size={14} className="text-text-muted opacity-50 group-hover:opacity-100" />;
    }
    return sortConfig.direction === 'ascending' ?
        <ArrowUp size={14} className="text-accent-primary" /> :
        <ArrowDown size={14} className="text-accent-primary" />;
};

const Metrics = () => {
    const [viewMode, setViewMode] = useState('teams'); // 'teams' or 'players'
    const [data, setData] = useState([]);
    const [playerData, setPlayerData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [loadingAdvanced, setLoadingAdvanced] = useState(false);
    const [loadingPlayers, setLoadingPlayers] = useState(false);
    const [playerError, setPlayerError] = useState(null);
    const [advancedMetrics, setAdvancedMetrics] = useState({});
    const [sortConfig, setSortConfig] = useState({ key: 'points', direction: 'descending' });
    const [filter, setFilter] = useState('');
    const [backendAvailable, setBackendAvailable] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Use current date to avoid redirect issues
                // Use local date to avoid UTC rollover issues
                const date = new Date();
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                const today = `${year}-${month}-${day}`;
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

    // Fetch player stats when switching to players view
    useEffect(() => {
        if (viewMode === 'players' && playerData.length === 0) {
            const fetchPlayerStats = async () => {
                setLoadingPlayers(true);
                setPlayerError(null);
                try {
                    // Add timeout to prevent infinite loading
                    const timeoutPromise = new Promise((_, reject) =>
                        setTimeout(() => reject(new Error('Request timeout')), 30000)
                    );

                    const players = await Promise.race([
                        backendApi.getPlayerStats(),
                        timeoutPromise
                    ]);

                    setPlayerData(Array.isArray(players) ? players : []);
                } catch (error) {
                    console.error('Failed to fetch player stats:', error);
                    setPlayerError(error.message || 'Failed to load player stats. Please try again later.');
                    setPlayerData([]);
                } finally {
                    setLoadingPlayers(false);
                }
            };
            fetchPlayerStats();
        }
    }, [viewMode]);

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

    const sortedPlayerData = useMemo(() => {
        let sortableItems = [...playerData];

        if (sortConfig.key !== null) {
            sortableItems.sort((a, b) => {
                let aValue = a[sortConfig.key];
                let bValue = b[sortConfig.key];

                if (aValue === undefined || aValue === null || aValue === '-') aValue = -Infinity;
                if (bValue === undefined || bValue === null || bValue === '-') bValue = -Infinity;

                if (typeof aValue === 'string') aValue = aValue.toLowerCase();
                if (typeof bValue === 'string') bValue = bValue.toLowerCase();

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
            item.team.toLowerCase().includes(filter.toLowerCase())
        );
    }, [playerData, sortConfig, filter]);

    const getHeatmapColor = (value, min, max, inverse = false) => {
        // Simple normalization for color coding
        // This is a simplified version; for production, use a proper scale
        const normalized = (value - min) / (max - min);
        const intensity = inverse ? 1 - normalized : normalized;

        if (intensity > 0.8) return 'text-accent-primary font-bold';
        if (intensity < 0.2) return 'text-accent-secondary font-bold';
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
                <div className="h-16 w-16 rounded-full border-t-2 border-b-2 border-accent-primary animate-spin"></div>
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
        { key: 'hdca', label: 'HDCA', align: 'center', advanced: true, tooltip: 'High Danger Chances Against' },

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
        { key: 'lat', label: 'LAT', align: 'center', advanced: true, tooltip: 'Lateral Movement' },
        { key: 'long_movement', label: 'LONG', align: 'center', advanced: true, tooltip: 'Longitudinal Movement' },

        // Shooting
        { key: 'shots', label: 'SOG', align: 'center', advanced: true, tooltip: 'Shots on Goal' },
        { key: 'goals', label: 'G/G', align: 'center', advanced: true, tooltip: 'Goals per Game' },
        { key: 'ga_gp', label: 'GA/GP', align: 'center', advanced: true, tooltip: 'Goals Against per Game' },

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

    const playerColumns = [
        { key: 'teamLogo', label: '', align: 'center' },
        { key: 'name', label: 'PLAYER', align: 'left' },
        { key: 'team', label: 'TEAM', align: 'center' },
        { key: 'position', label: 'POS', align: 'center' },
        { key: 'games_played', label: 'GP', align: 'center' },
        { key: 'goals', label: 'G', align: 'center', highlight: true },
        { key: 'assists', label: 'A', align: 'center' },
        { key: 'points', label: 'PTS', align: 'center', highlight: true },
        { key: 'shots', label: 'SOG', align: 'center' },
        { key: 'icetime', label: 'TOI', align: 'center', format: (v) => Math.round(v / 60) + 'm' },
        { key: 'game_score', label: 'GS', align: 'center', advanced: true, tooltip: 'Game Score' },
        { key: 'xgoals', label: 'xG', align: 'center', advanced: true, tooltip: 'Expected Goals' },
        { key: 'xgoals_pct', label: 'xG%', align: 'center', advanced: true, tooltip: 'Expected Goals %' },
        { key: 'corsi_pct', label: 'CF%', align: 'center', advanced: true, tooltip: 'Corsi For %' },
        { key: 'I_F_shotAttempts', label: 'iSA', align: 'center', advanced: true, tooltip: 'Individual Shot Attempts' },
        { key: 'I_F_highDangerShots', label: 'iHDS', align: 'center', advanced: true, tooltip: 'Individual High Danger Shots' },
        { key: 'I_F_highDangerxGoals', label: 'iHDxG', align: 'center', advanced: true, tooltip: 'Individual High Danger xGoals' },
        { key: 'I_F_highDangerGoals', label: 'iHDG', align: 'center', advanced: true, tooltip: 'Individual High Danger Goals' },
        { key: 'onIce_corsiPercentage', label: 'onCF%', align: 'center', advanced: true, tooltip: 'On-Ice Corsi For %' },
        { key: 'onIce_xGoalsPercentage', label: 'onxG%', align: 'center', advanced: true, tooltip: 'On-Ice Expected Goals %' },
    ];

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="relative rounded-3xl overflow-hidden bg-gradient-to-r from-bg-secondary to-bg-primary border border-white/5 p-8 md:p-12 shadow-2xl mb-8">
                <div className="absolute top-0 right-0 w-96 h-96 bg-success/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3"></div>

                <div className="relative z-10 flex flex-col md:flex-row justify-between items-end gap-8">
                    <div>
                        <h1 className="text-5xl md:text-7xl font-display font-black text-white tracking-tighter mb-4">
                            LEAGUE <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent-primary to-success">METRICS</span>
                        </h1>
                        <p className="text-text-muted font-mono text-lg max-w-2xl">
                            {viewMode === 'teams' ? 'Comprehensive team statistics, advanced analytics, and performance trends.' : 'Individual player statistics, advanced metrics, and performance data.'}
                        </p>

                        {/* Toggle between Teams and Players */}
                        <div className="flex gap-2 mt-6">
                            <button
                                onClick={() => setViewMode('teams')}
                                className={`px-6 py-2 rounded-lg font-display font-bold transition-all ${viewMode === 'teams' ? 'bg-accent-primary text-bg-primary' : 'bg-white/10 text-text-muted hover:bg-white/20'}`}
                            >
                                TEAMS
                            </button>
                            <button
                                onClick={() => setViewMode('players')}
                                className={`px-6 py-2 rounded-lg font-display font-bold transition-all ${viewMode === 'players' ? 'bg-accent-primary text-bg-primary' : 'bg-white/10 text-text-muted hover:bg-white/20'}`}
                            >
                                PLAYERS
                            </button>
                        </div>
                    </div>

                    <div className="relative w-full md:w-72">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-accent-primary" size={20} />
                        <input
                            type="text"
                            placeholder={viewMode === 'teams' ? 'Search teams...' : 'Search players...'}
                            value={filter}
                            onChange={(e) => setFilter(e.target.value)}
                            className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-12 pr-4 text-white font-mono text-sm focus:outline-none focus:border-accent-primary/50 focus:bg-white/10 transition-all placeholder:text-text-muted"
                        />
                    </div>
                </div>
            </div>

            {/* Loading Advanced Metrics Banner */}
            {loadingAdvanced && (
                <div className="glass-panel p-4 rounded-xl border border-accent-primary/30 bg-accent-primary/5 flex items-center gap-3 animate-pulse">
                    <div className="h-4 w-4 rounded-full border-t-2 border-b-2 border-accent-primary animate-spin"></div>
                    <span className="font-mono text-sm text-accent-primary">
                        Loading advanced metrics from backend...
                    </span>
                </div>
            )}

            {/* Backend Unavailable Warning */}
            {!backendAvailable && !loadingAdvanced && (
                <div className="glass-panel p-4 rounded-xl border border-danger/30 bg-danger/5 flex items-center gap-3">
                    <span className="font-mono text-sm text-danger">
                        ⚠️ Backend API unavailable. Advanced metrics will not be displayed.
                    </span>
                </div>
            )}

            {/* Data Table */}
            <div className="glass-card rounded-2xl overflow-hidden border border-white/10 shadow-2xl">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="bg-white/5 border-b border-white/10">
                                {(viewMode === 'teams' ? columns : playerColumns).map((col) => (
                                    <th
                                        key={col.key}
                                        onClick={() => handleSort(col.key)}
                                        className={clsx(
                                            "p-4 text-text-muted font-display font-bold tracking-wider text-xs uppercase cursor-pointer hover:text-white transition-colors group select-none whitespace-nowrap",
                                            col.align === 'center' ? 'text-center' : 'text-left',
                                            sortConfig.key === col.key && "text-accent-primary bg-white/5"
                                        )}
                                        title={col.tooltip}
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
                            {viewMode === 'players' ? (
                                sortedPlayerData.map((player, index) => (
                                    <motion.tr
                                        key={`${player.name}-${player.team}`}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: index * 0.005 }}
                                        className="hover:bg-white/5 transition-colors group"
                                    >
                                        {/* Team Logo */}
                                        <td className="p-4 text-center">
                                            <div className="w-6 h-6 rounded-full" style={{ backgroundColor: getTeamColor(player.team) }} />
                                        </td>
                                        <td className="p-4 font-bold text-white">{player.name}</td>
                                        <td className="p-4 text-center text-text-muted">{player.team}</td>
                                        <td className="p-4 text-center text-text-muted">{player.position}</td>
                                        <td className="p-4 text-center text-text-muted">{player.games_played}</td>
                                        <td className="p-4 text-center text-accent-primary font-bold bg-white/5">{player.goals}</td>
                                        <td className="p-4 text-center text-text-muted">{player.assists}</td>
                                        <td className="p-4 text-center text-white font-bold">{player.points}</td>
                                        <td className="p-4 text-center text-text-muted">{player.shots}</td>
                                        <td className="p-4 text-center text-text-muted">{Math.round(player.icetime / 60)}m</td>
                                        <td className="p-4 text-center text-accent-secondary">{displayMetric(player.game_score)}</td>
                                        <td className="p-4 text-center text-text-muted">{displayMetric(player.xgoals)}</td>
                                        <td className="p-4 text-center text-text-muted">{displayMetric(player.xgoals_pct)}%</td>
                                        <td className="p-4 text-center text-text-muted">{displayMetric(player.corsi_pct)}%</td>
                                        <td className="p-4 text-center text-text-muted">{displayMetric(player.I_F_shotAttempts)}</td>
                                        <td className="p-4 text-center text-text-muted">{displayMetric(player.I_F_highDangerShots)}</td>
                                        <td className="p-4 text-center text-text-muted">{displayMetric(player.I_F_highDangerxGoals)}</td>
                                        <td className="p-4 text-center text-text-muted">{displayMetric(player.I_F_highDangerGoals)}</td>
                                        <td className="p-4 text-center text-text-muted">{displayMetric(player.onIce_corsiPercentage)}%</td>
                                        <td className="p-4 text-center text-text-muted">{displayMetric(player.onIce_xGoalsPercentage)}%</td>
                                    </motion.tr>
                                ))
                            ) : (
                                // Existing team rows remain unchanged
                                sortedData.map((team, index) => (
                                    <motion.tr
                                        key={team.abbrev}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: index * 0.02 }}
                                        className="hover:bg-white/5 transition-colors group"
                                    >
                                        <td className="p-4 text-center text-text-muted">{team.rank}</td>
                                        <td className="p-4">
                                            <Link to={`/team/${team.abbrev}`} className="flex items-center gap-3 group-hover:opacity-80 transition-opacity">
                                                <img src={team.logo} alt={team.abbrev} className="w-6 h-6 opacity-80 group-hover:opacity-100 group-hover:scale-110 transition-all" />
                                                <span className="font-sans font-bold text-white group-hover:text-accent-primary transition-colors">{team.name}</span>
                                            </Link>
                                        </td>
                                        <td className="p-4 text-center text-text-muted">{team.gp}</td>
                                        <td className="p-4 text-center text-white">{team.w}</td>
                                        <td className="p-4 text-center text-text-muted">{team.l}</td>
                                        <td className="p-4 text-center text-text-muted">{team.otl}</td>
                                        <td className="p-4 text-center font-bold text-lg text-white bg-white/5">{team.pts}</td>
                                        <td className="p-4 text-center text-text-muted">{team.pPct}</td>
                                        <td className={clsx("p-4 text-center", getHeatmapColor(team.gf, stats.gf.min, stats.gf.max))}>{team.gf}</td>
                                        <td className={clsx("p-4 text-center", getHeatmapColor(team.ga, stats.ga.min, stats.ga.max, true))}>{team.ga}</td>
                                        <td className={clsx("p-4 text-center", team.diff > 0 ? "text-success" : team.diff < 0 ? "text-danger" : "text-text-muted")}>
                                            {team.diff > 0 ? '+' : ''}{team.diff}
                                        </td>
                                        <td className="p-4 text-center text-text-muted">{team.l10}</td>
                                        <td className="p-4 text-center text-white">{team.streak}</td>

                                        {/* Advanced Metrics - Core */}
                                        <td className="p-4 text-center text-accent-primary bg-white/5" title="Game Score">
                                            {loadingAdvanced ? '...' : displayMetric(team.gs)}
                                        </td>
                                        <td className="p-4 text-center text-text-muted" title="Expected Goals">
                                            {loadingAdvanced ? '...' : displayMetric(team.xg)}
                                        </td>
                                        <td className="p-4 text-center text-text-muted" title="High Danger Chances">
                                            {loadingAdvanced ? '...' : displayMetric(team.hdc)}
                                        </td>
                                        <td className="p-4 text-center text-text-muted" title="High Danger Chances Against">
                                            {loadingAdvanced ? '...' : displayMetric(team.hdca)}
                                        </td>

                                        {/* Zone Metrics */}
                                        <td className="p-4 text-center text-text-muted" title="Offensive Zone Shots">
                                            {loadingAdvanced ? '...' : displayMetric(team.ozs)}
                                        </td>
                                        <td className="p-4 text-center text-text-muted" title="Neutral Zone Shots">
                                            {loadingAdvanced ? '...' : displayMetric(team.nzs)}
                                        </td>
                                        <td className="p-4 text-center text-text-muted" title="Defensive Zone Shots">
                                            {loadingAdvanced ? '...' : displayMetric(team.dzs)}
                                        </td>

                                        {/* Shot Generation */}
                                        <td className="p-4 text-center text-text-muted" title="Forecheck/Cycle Shots">
                                            {loadingAdvanced ? '...' : displayMetric(team.fc)}
                                        </td>
                                        <td className="p-4 text-center text-text-muted" title="Rush Shots">
                                            {loadingAdvanced ? '...' : displayMetric(team.rush)}
                                        </td>

                                        {/* Turnovers */}
                                        <td className="p-4 text-center text-text-muted" title="Neutral Zone Turnovers">
                                            {loadingAdvanced ? '...' : displayMetric(team.nzts)}
                                        </td>
                                        <td className="p-4 text-center text-text-muted" title="NZ Turnovers to Shots Against">
                                            {loadingAdvanced ? '...' : displayMetric(team.nztsa)}
                                        </td>

                                        {/* Movement */}
                                        <td className="p-4 text-center text-text-muted" title="Lateral Movement">
                                            {loadingAdvanced ? '...' : displayMetric(team.lat)}
                                        </td>
                                        <td className="p-4 text-center text-text-muted" title="Longitudinal Movement">
                                            {loadingAdvanced ? '...' : displayMetric(team.long_movement)}
                                        </td>

                                        {/* Shooting */}
                                        <td className="p-4 text-center text-text-muted" title="Shots on Goal">
                                            {loadingAdvanced ? '...' : displayMetric(team.shots)}
                                        </td>
                                        <td className="p-4 text-center text-text-muted" title="Goals per Game">
                                            {loadingAdvanced ? '...' : displayMetric(team.goals)}
                                        </td>
                                        <td className="p-4 text-center text-text-muted" title="Goals Against per Game">
                                            {loadingAdvanced ? '...' : displayMetric(team.ga_gp)}
                                        </td>

                                        {/* Possession */}
                                        <td className="p-4 text-center text-text-muted" title="Corsi For %">
                                            {loadingAdvanced ? '...' : displayMetric(team.corsi_pct)}
                                        </td>

                                        {/* Physical */}
                                        <td className="p-4 text-center text-text-muted" title="Hits per Game">
                                            {loadingAdvanced ? '...' : displayMetric(team.hits)}
                                        </td>
                                        <td className="p-4 text-center text-text-muted" title="Blocked Shots">
                                            {loadingAdvanced ? '...' : displayMetric(team.blocks)}
                                        </td>
                                        <td className="p-4 text-center text-text-muted" title="Giveaways">
                                            {loadingAdvanced ? '...' : displayMetric(team.giveaways)}
                                        </td>
                                        <td className="p-4 text-center text-text-muted" title="Takeaways">
                                            {loadingAdvanced ? '...' : displayMetric(team.takeaways)}
                                        </td>
                                        <td className="p-4 text-center text-text-muted" title="Penalty Minutes">
                                            {loadingAdvanced ? '...' : displayMetric(team.pim)}
                                        </td>

                                        {/* Special Teams */}
                                        <td className="p-4 text-center text-text-muted" title="Power Play %">
                                            {loadingAdvanced ? '...' : displayMetric(team.pp_pct)}
                                        </td>
                                        <td className="p-4 text-center text-text-muted" title="Penalty Kill %">
                                            {loadingAdvanced ? '...' : displayMetric(team.pk_pct)}
                                        </td>
                                        <td className="p-4 text-center text-text-muted" title="Faceoff %">
                                            {loadingAdvanced ? '...' : displayMetric(team.fo_pct)}
                                        </td>
                                    </motion.tr>
                                ))
                            )}
                        </tbody>
                    </table>
                    {viewMode === 'players' && loadingPlayers && (
                        <div className="p-8 text-center">
                            <div className="inline-block h-8 w-8 rounded-full border-t-2 border-b-2 border-accent-primary animate-spin"></div>
                            <p className="mt-2 text-text-muted">Loading player stats...</p>
                        </div>
                    )}
                    {viewMode === 'players' && playerError && !loadingPlayers && (
                        <div className="p-8 text-center">
                            <div className="glass-panel p-4 rounded-xl border border-danger/30 bg-danger/5 inline-block">
                                <p className="font-mono text-sm text-danger">⚠️ {playerError}</p>
                                <button
                                    onClick={() => window.location.reload()}
                                    className="mt-3 px-4 py-2 rounded-lg bg-accent-primary text-bg-primary font-bold hover:bg-accent-secondary transition-colors text-sm"
                                >
                                    Retry
                                </button>
                            </div>
                        </div>
                    )}
                    {viewMode === 'players' && !loadingPlayers && !playerError && sortedPlayerData.length === 0 && (
                        <div className="p-8 text-center text-text-muted">
                            No players found matching your search.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Metrics;
