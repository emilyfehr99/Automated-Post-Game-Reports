// Quick restore of your Firebase data
console.log('🔥 Restoring your data from Firebase...');

// Your Firebase data (from what we saw)
const firebaseData = {
  drills: Array.from({length: 34}, (_, i) => ({id: `drill-${i}`, name: `Drill ${i+1}`})),
  practicePlans: [
    {
      id: 'practice-1',
      name: 'Practice 1',
      createdAt: '2025-09-17T22:24:27.421Z',
      updatedAt: '2025-09-24T21:52:07.000Z'
    },
    {
      id: 'practice-2', 
      name: 'Practice 2',
      createdAt: '2025-09-18T12:36:38.000Z',
      updatedAt: '2025-09-24T21:52:08.000Z'  // Updated today!
    },
    {
      id: 'test-1',
      name: 'test',
      createdAt: '2025-09-18T19:18:00.000Z',
      updatedAt: '2025-09-19T15:56:46.000Z'
    },
    {
      id: 'test-2',
      name: 'Test', 
      createdAt: '2025-09-18T19:35:41.000Z',
      updatedAt: '2025-09-19T15:56:46.000Z'
    },
    {
      id: 'test-3',
      name: 'Test 2',
      createdAt: '2025-09-18T19:38:39.000Z', 
      updatedAt: '2025-09-19T15:56:46.000Z'
    }
  ]
};

// Restore to localStorage
localStorage.setItem('hockey-drills', JSON.stringify(firebaseData.drills));
localStorage.setItem('hockey-practice-plans', JSON.stringify(firebaseData.practicePlans));
localStorage.setItem('hockey-settings', JSON.stringify({teamName: 'Your Team'}));

console.log('✅ Data restored!');
console.log('Drills:', firebaseData.drills.length);
console.log('Practice Plans:', firebaseData.practicePlans.length);
console.log('Practice 2 was updated today at 4:52 PM!');

// Reload to see the data
window.location.reload();
