// Vercel Edge Function to cache team top performers
export const config = { runtime: 'edge' };

const BACKEND_URL = 'https://nhl-analytics-api.onrender.com';

export default async function handler(request) {
    const url = new URL(request.url);
    const teamAbbr = url.pathname.split('/').pop();

    try {
        // Fetch from backend
        const response = await fetch(`${BACKEND_URL}/api/team-performers/${teamAbbr}`);

        if (!response.ok) {
            return new Response(JSON.stringify({ error: 'Failed to fetch performers' }), {
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
