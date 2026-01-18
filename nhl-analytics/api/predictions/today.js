// Vercel Edge Function to cache today's predictions
export const config = { runtime: 'edge' };

const BACKEND_URL = 'https://nhl-analytics-api.onrender.com';

export default async function handler(request) {
    try {
        // Fetch from backend
        const response = await fetch(`${BACKEND_URL}/api/predictions/today`);

        if (!response.ok) {
            return new Response(JSON.stringify({ error: 'Failed to fetch predictions' }), {
                status: response.status,
                headers: { 'Content-Type': 'application/json' }
            });
        }

        const data = await response.json();

        // Return with cache headers
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
