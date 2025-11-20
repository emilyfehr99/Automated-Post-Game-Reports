const BASE_URL = 'https://api-web.nhle.com/v1';

async function verifyEndpoints() {
    try {
        console.log('--- Verifying Endpoints Deeply ---');

        // Standings
        console.log('Fetching Standings...');
        const standingsRes = await fetch(`${BASE_URL}/standings/now`);
        const standingsData = await standingsRes.json();
        if (standingsData.standings && standingsData.standings.length > 0) {
            console.log('First Standings Item:', JSON.stringify(standingsData.standings[0], null, 2));
        } else {
            console.log('No standings found.');
        }

        // Schedule
        const today = new Date().toISOString().split('T')[0];
        console.log(`Fetching Schedule for ${today}...`);
        const scheduleRes = await fetch(`${BASE_URL}/schedule/${today}`);
        const scheduleData = await scheduleRes.json();

        if (scheduleData.gameWeek && scheduleData.gameWeek.length > 0) {
            const todayGames = scheduleData.gameWeek.find(day => day.date === today);
            if (todayGames && todayGames.games && todayGames.games.length > 0) {
                console.log('First Game Item:', JSON.stringify(todayGames.games[0], null, 2));
            } else {
                console.log('No games found for today in gameWeek.');
                console.log('First gameWeek day:', JSON.stringify(scheduleData.gameWeek[0], null, 2));
            }
        } else {
            console.log('No gameWeek data found.');
        }

    } catch (e) {
        console.error('Error:', e);
    }
}

verifyEndpoints();
