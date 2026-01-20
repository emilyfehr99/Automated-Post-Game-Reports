// Backend API client for pre-calculated metrics
// Use Render backend in production, localhost in development
const BACKEND_URL = import.meta.env.MODE === 'production'
    ? 'https://nhl-analytics-api.onrender.com'
    : (import.meta.env.VITE_API_URL || 'http://localhost:5002');

export const backendApi = {
    /**
     * Get all team stats with advanced metrics
     */
    async getTeamStats() {
        const response = await fetch(`${BACKEND_URL}/api/team-stats`);
        if (!response.ok) throw new Error('Failed to fetch team stats');
        return response.json();
    },

    /**
     * Get stats for specific team
     */
    async getTeamStatsByAbbrev(abbrev) {
        const endpoint = import.meta.env.MODE === 'production'
            ? `/api/team-stats/${abbrev}`
            : `${BACKEND_URL}/api/team-stats/${abbrev}`;
        const response = await fetch(endpoint);
        if (!response.ok) throw new Error(`Failed to fetch stats for ${abbrev}`);
        return response.json();
    },

    /**
     * Get aggregated team metrics for all teams (optimized for Metrics page)
     */
    async getTeamMetrics() {
        // FAST LOAD: Fetch static JSON directly from public folder (Vercel CDN)
        try {
            // cache busting to ensure fresh data
            const response = await fetch(`/data/team_metrics.json?v=${new Date().getTime()}`);
            if (response.ok) {
                const data = await response.json();
                console.log('✅ Loaded static team metrics:', Object.keys(data).length, 'teams');
                return data;
            }
            throw new Error(`Static metrics status: ${response.status}`);
        } catch (e) {
            console.warn('⚠️ Static fetch failed, falling back to API:', e);
            // Fallback to API if static file missing
            const endpoint = import.meta.env.MODE === 'production'
                ? 'https://nhl-analytics-api.onrender.com/api/team-metrics'
                : 'http://localhost:5002/api/team-metrics';
            const response = await fetch(endpoint);
            if (!response.ok) throw new Error('Failed to fetch team metrics');
            return response.json();
        }
    },

    /**
     * Get NHL Edge data
     */
    async getEdgeData() {
        const endpoint = import.meta.env.MODE === 'production'
            ? '/api/edge-data'
            : `${BACKEND_URL}/api/edge-data`;
        const response = await fetch(endpoint);
        if (!response.ok) throw new Error('Failed to fetch edge data');
        return response.json();
    },

    /**
     * Get Edge data for specific team
     */
    async getEdgeDataByTeam(abbrev) {
        const endpoint = import.meta.env.MODE === 'production'
            ? `/api/edge-data/${abbrev}`
            : `${BACKEND_URL}/api/edge-data/${abbrev}`;
        const response = await fetch(endpoint);
        if (!response.ok) throw new Error(`Failed to fetch edge data for ${abbrev}`);
        return response.json();
    },

    /**
     * Get all predictions
     */
    async getPredictions() {
        // FAST LOAD: Fetch static JSON
        try {
            const response = await fetch('/data/predictions.json');
            if (response.ok) return response.json();
        } catch (e) { console.warn('Static predictions missing', e); }

        const response = await fetch(`${BACKEND_URL}/api/predictions`);
        if (!response.ok) throw new Error('Failed to fetch predictions');
        return response.json();
    },

    /**
     * Get today's predictions
     */
    async getTodayPredictions() {
        // Use local edge function in production, backend in development
        const endpoint = import.meta.env.MODE === 'production'
            ? '/api/predictions/today'
            : `${BACKEND_URL}/api/predictions/today`;

        const response = await fetch(endpoint);
        if (!response.ok) throw new Error('Failed to fetch today\'s predictions');
        return response.json();
    },

    /**
     * Get prediction for specific game
     */
    async getGamePrediction(gameId) {
        const endpoint = import.meta.env.MODE === 'production'
            ? `/api/predictions/game/${gameId}`
            : `${BACKEND_URL}/api/predictions/game/${gameId}`;
        const response = await fetch(endpoint);
        if (!response.ok) throw new Error(`Failed to fetch prediction for game ${gameId}`);
        return response.json();
    },

    /**
     * Get live game data including advanced metrics
     */
    async getLiveGame(gameId) {
        const endpoint = import.meta.env.MODE === 'production'
            ? `/api/live-game/${gameId}`
            : `${BACKEND_URL}/api/live-game/${gameId}`;
        const response = await fetch(endpoint);
        if (!response.ok) throw new Error(`Failed to fetch live game data for ${gameId}`);
        return response.json();
    },

    /**
     * Get team heatmap data
     */
    async getTeamHeatmap(teamAbbr) {
        const endpoint = import.meta.env.MODE === 'production'
            ? `/api/team-heatmap/${teamAbbr}`
            : `${BACKEND_URL}/api/team-heatmap/${teamAbbr}`;
        const response = await fetch(endpoint);
        if (!response.ok) throw new Error('Failed to fetch team heatmap');
        return response.json();
    },

    /**
     * Get historical stats
     */
    async getHistoricalStats() {
        const response = await fetch(`${BACKEND_URL}/api/historical-stats`);
        if (!response.ok) throw new Error('Failed to fetch historical stats');
        return response.json();
    },

    /**
     * Get stats for specific season
     */
    async getHistoricalStatsBySeason(season) {
        const response = await fetch(`${BACKEND_URL}/api/historical-stats/${season}`);
        if (!response.ok) throw new Error(`Failed to fetch stats for season ${season}`);
        return response.json();
    },

    /**
     * Health check
     */
    async healthCheck() {
        const response = await fetch(`${BACKEND_URL}/api/health`);
        if (!response.ok) throw new Error('Backend health check failed');
        return response.json();
    },

    /**
     * Get player stats from MoneyPuck
     */
    async getPlayerStats(season = '2025', type = 'regular', situation = 'all') {
        // Use edge function in production to avoid CORS
        const endpoint = import.meta.env.MODE === 'production'
            ? `/api/player-stats?season=${season}&type=${type}&situation=${situation}`
            : `${BACKEND_URL}/api/player-stats?season=${season}&type=${type}&situation=${situation}`;

        const response = await fetch(endpoint);
        if (!response.ok) throw new Error('Failed to fetch player stats');
        return response.json();
    },

    /**
     * Get playoff predictions
     */
    async getPlayoffPredictions() {
        const endpoint = import.meta.env.MODE === 'production'
            ? '/api/predictions/playoffs'
            : `${BACKEND_URL}/api/predictions/playoffs`;
        const response = await fetch(endpoint);
        if (!response.ok) throw new Error('Failed to fetch playoff predictions');
        return response.json();
    },

    /**
     * Get top performers for a team
     */
    async getTeamTopPerformers(teamAbbr) {
        try {
            // First try dedicated endpoint if it exists
            const endpoint = import.meta.env.MODE === 'production'
                ? `/api/team-performers/${teamAbbr}`
                : `${BACKEND_URL}/api/team-performers/${teamAbbr}`;
            const response = await fetch(endpoint);
            if (response.ok) return response.json();

            // Fallback: Fetch all player stats and filter
            // This is heavy but ensures we get data if the specific endpoint is missing
            console.log(`Dedicated endpoint failed for ${teamAbbr}, fetching all stats...`);
            const allStats = await this.getPlayerStats('2024', 'regular', 'all');

            // Filter for team and sort by points/game_score
            // MoneyPuck data usually has 'team' field
            if (allStats && Array.isArray(allStats.data)) {
                return allStats.data
                    .filter(p => p.team === teamAbbr)
                    .sort((a, b) => (b.points || 0) - (a.points || 0))
                    .slice(0, 5);
            }
            return [];
        } catch (error) {
            console.warn(`Failed to fetch team performers for ${teamAbbr}`, error);
            return [];
        }
    }
};
