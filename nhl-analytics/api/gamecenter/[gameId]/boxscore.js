// Vercel Edge Function to cache NHL game center boxscore
export const config = { runtime: 'edge' };

const BACKEND_URL = 'https://nhl-analytics-api.onrender.com';

export default async function handler(request) {
    const url = new URL(request.url);
    const pathParts = url.pathname.split('/');
    const gameId = pathParts[pathParts.length - 2]; // Get gameId from path

    try {
        // Fetch from backend
        const response = await fetch(`${BACKEND_URL}/api/nhl/gamecenter/${gameId}/boxscore`);

        if (!response.ok) {
            return new Response(JSON.stringify({ error: 'Failed to fetch boxscore' }), {
                status: response.status,
                headers: { 'Content-Type': 'application/json' }
            });
        }

        const data = await response.json();

        // Return with cache headers - shorter cache for live games
        return new Response(JSON.stringify(data), {
            status: 200,
            headers: {
                'Content-Type': 'application/json',
                'Cache-Control': 's-maxage=60, stale-while-revalidate=120',
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
