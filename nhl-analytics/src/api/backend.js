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
        const response = await fetch(`${BACKEND_URL}/api/team-stats/${abbrev}`);
        if (!response.ok) throw new Error(`Failed to fetch stats for ${abbrev}`);
        return response.json();
    },

    /**
     * Get aggregated team metrics for all teams (optimized for Metrics page)
     */
    async getTeamMetrics() {
        const response = await fetch(`${BACKEND_URL}/api/team-metrics`);
        if (!response.ok) throw new Error('Failed to fetch team metrics');
        return response.json();
    },

    /**
     * Get NHL Edge data
     */
    async getEdgeData() {
        const response = await fetch(`${BACKEND_URL}/api/edge-data`);
        if (!response.ok) throw new Error('Failed to fetch edge data');
        return response.json();
    },

    /**
     * Get Edge data for specific team
     */
    async getEdgeDataByTeam(abbrev) {
        const response = await fetch(`${BACKEND_URL}/api/edge-data/${abbrev}`);
        if (!response.ok) throw new Error(`Failed to fetch edge data for ${abbrev}`);
        return response.json();
    },

    /**
     * Get all predictions
     */
    async getPredictions() {
        const response = await fetch(`${BACKEND_URL}/api/predictions`);
        if (!response.ok) throw new Error('Failed to fetch predictions');
        return response.json();
    },

    /**
     * Get today's predictions
     */
    async getTodayPredictions() {
        const response = await fetch(`${BACKEND_URL}/api/predictions/today`);
        if (!response.ok) throw new Error('Failed to fetch today\'s predictions');
        return response.json();
    },

    /**
     * Get prediction for specific game
     */
    async getGamePrediction(gameId) {
        const response = await fetch(`${BACKEND_URL}/api/predictions/game/${gameId}`);
        if (!response.ok) throw new Error(`Failed to fetch prediction for game ${gameId}`);
        return response.json();
    },

    /**
     * Get live game data including advanced metrics
     */
    async getLiveGame(gameId) {
        const response = await fetch(`${BACKEND_URL}/api/live-game/${gameId}`);
        if (!response.ok) throw new Error(`Failed to fetch live game data for ${gameId}`);
        return response.json();
    },

    /**
     * Get team heatmap data
     */
    async getTeamHeatmap(teamAbbr) {
        const response = await fetch(`${BACKEND_URL}/api/team-heatmap/${teamAbbr}`);
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
    async getPlayerStats(season = '2024', type = 'regular', situation = 'all') {
        const response = await fetch(`${BACKEND_URL}/api/player-stats?season=${season}&type=${type}&situation=${situation}`);
        if (!response.ok) throw new Error('Failed to fetch player stats');
        return response.json();
    },

    /**
     * Get top performers for a team
     */
    async getTeamTopPerformers(teamAbbr) {
        try {
            // First try dedicated endpoint if it exists
            const response = await fetch(`${BACKEND_URL}/api/team-performers/${teamAbbr}`);
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
