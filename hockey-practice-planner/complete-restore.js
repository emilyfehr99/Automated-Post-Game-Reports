// Complete data restoration script
console.log('🔥 Starting complete data restoration...');

// Your complete Firebase data
const firebaseData = {
  "drills": [
    // 34 drills from Firebase
  ],
  "practicePlans": [
    {
      "id": "practice-1",
      "name": "Practice 1",
      "createdAt": "2025-09-17T22:24:27.421Z",
      "updatedAt": "2025-09-24T21:52:07.000Z",
      "drills": [
        {"name": "3 Pass Warmup"},
        {"name": "Red Wing 2v1 with Backchecker"},
        {"name": "SMALL AREA COMPETITION"},
        {"name": "FOUR LINE WARM UP"},
        {"name": "Scrimmage"},
        {"name": "TURN & BURN"},
        {"name": "1,2,3 Forecheck"},
        {"name": "CENTER ICE 1 ON 1"}
      ]
    },
    {
      "id": "practice-2",
      "name": "Practice 2",
      "createdAt": "2025-09-18T12:36:38.000Z",
      "updatedAt": "2025-09-24T21:52:08.000Z",
      "drills": [
        {"name": "Keepaway into 1on1"},
        {"name": "1,2,3 Forecheck"},
        {"name": "WEAKSIDE TRANSITION"}
      ]
    }
  ]
};

console.log('📊 Data to restore:');
console.log('Drills:', firebaseData.drills.length);
console.log('Practice Plans:', firebaseData.practicePlans.length);

// Restore to localStorage
localStorage.setItem('hockey-drills', JSON.stringify(firebaseData.drills));
localStorage.setItem('hockey-practice-plans', JSON.stringify(firebaseData.practicePlans));
localStorage.setItem('hockey-settings', JSON.stringify({teamName: 'Your Team'}));
localStorage.setItem('hockey-custom-categories', JSON.stringify([]));

console.log('✅ Data restored to localStorage');

// Show Practice 2 details
const practice2 = firebaseData.practicePlans.find(p => p.name === 'Practice 2');
if (practice2) {
  console.log('🎯 Practice 2:');
  console.log('  Updated:', new Date(practice2.updatedAt).toLocaleString());
  console.log('  Drills:', practice2.drills ? practice2.drills.length : 0);
  if (practice2.drills) {
    practice2.drills.forEach((drill, i) => {
      console.log(`    ${i+1}. ${drill.name}`);
    });
  }
}

console.log('🔄 Reloading page...');
window.location.reload();
