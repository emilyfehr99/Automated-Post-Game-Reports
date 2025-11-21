const BASE_URL = '/api'; // Vite proxy to NHL API
const BACKEND_URL = import.meta.env.VITE_API_URL || 'http://localhost:5002'; // Backend server

export const nhlApi = {
    async getStandings(date) {
        try {
            // Use local date if no date provided
            let dateStr = date;
            if (!dateStr) {
                const d = new Date();
                const year = d.getFullYear();
                const month = String(d.getMonth() + 1).padStart(2, '0');
                const day = String(d.getDate()).padStart(2, '0');
                dateStr = `${year}-${month}-${day}`;
            }
            const response = await fetch(`${BASE_URL}/standings/${dateStr}`);
            if (!response.ok) throw new Error('Failed to fetch standings');
            return await response.json();
        } catch (error) {
            console.error('Error fetching standings:', error);
            throw error;
        }
    },

    async getSchedule(date) {
        try {
            // date format: YYYY-MM-DD
            const response = await fetch(`${BASE_URL}/schedule/${date}`);
            if (!response.ok) throw new Error('Failed to fetch schedule');
            return await response.json();
        } catch (error) {
            console.error('Error fetching schedule:', error);
            throw error;
        }
    },

    async getTeamDetails(teamId) {
        try {
            // Use backend proxy to avoid CORS
            const response = await fetch(`${BACKEND_URL}/api/team-roster/${teamId}`);
            if (!response.ok) throw new Error('Failed to fetch team details');
            return await response.json();
        } catch (error) {
            console.error('Error fetching team details:', error);
            throw error;
        }
    },

    async getPlayerDetails(playerId) {
        try {
            const response = await fetch(`${BASE_URL}/player/${playerId}/landing`);
            if (!response.ok) throw new Error('Failed to fetch player details');
            return await response.json();
        } catch (error) {
            console.error('Error fetching player details:', error);
            throw error;
        }
    },

    async getGameCenter(gameId) {
        try {
            // Fetch both boxscore and play-by-play
            const [boxscoreResponse, pbpResponse] = await Promise.all([
                fetch(`${BASE_URL}/gamecenter/${gameId}/boxscore`),
                fetch(`${BASE_URL}/gamecenter/${gameId}/play-by-play`)
            ]);

            if (!boxscoreResponse.ok || !pbpResponse.ok) throw new Error('Failed to fetch game data');

            const boxscore = await boxscoreResponse.json();
            const playByPlay = await pbpResponse.json();

            return {
                boxscore,
                playByPlay
            };
        } catch (error) {
            console.error('Error fetching game center data:', error);
            throw error;
        }
    },

    async getPlayerStats(season = '20242025', gameType = 2, limit = 100) {
        try {
            // Fetch skater stats leaders
            // gameType: 2 = regular season, 3 = playoffs
            const response = await fetch(`${BASE_URL}/skater-stats-leaders/${season}/${gameType}?limit=${limit}`);
            if (!response.ok) throw new Error('Failed to fetch player stats');
            return await response.json();
        } catch (error) {
            console.error('Error fetching player stats:', error);
            throw error;
        }
    }
};
