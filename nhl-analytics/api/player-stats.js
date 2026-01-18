// Vercel Edge Function to cache player stats
export const config = { runtime: 'edge' };

const BACKEND_URL = 'https://nhl-analytics-api.onrender.com';

export default async function handler(request) {
    const url = new URL(request.url);
    const season = url.searchParams.get('season') || '2024';
    const type = url.searchParams.get('type') || 'regular';
    const situation = url.searchParams.get('situation') || 'all';

    try {
        // Fetch from backend
        const response = await fetch(`${BACKEND_URL}/api/player-stats?season=${season}&type=${type}&situation=${situation}`);

        if (!response.ok) {
            return new Response(JSON.stringify({ error: 'Failed to fetch player stats' }), {
                status: response.status,
                headers: { 'Content-Type': 'application/json' }
            });
        }

        const data = await response.json();

        // Return with cache headers - 5 min cache for player stats
        return new Response(JSON.stringify(data), {
            status: 200,
            headers: {
                'Content-Type': 'application/json',
                'Cache-Control': 's-maxage=300, stale-while-revalidate=600',
                'Access-Control-Allow-Origin': '*',
            }
        });
    } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
            status: 500,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}
