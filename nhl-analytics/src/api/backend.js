// Backend API client for pre-calculated metrics
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5002';

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
    }
};
