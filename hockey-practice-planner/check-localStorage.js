
// Check current localStorage data
console.log('Current localStorage data:');
console.log('Drills:', localStorage.getItem('hockey-drills') ? JSON.parse(localStorage.getItem('hockey-drills')).length : 'None');
console.log('Practice Plans:', localStorage.getItem('hockey-practice-plans') ? JSON.parse(localStorage.getItem('hockey-practice-plans')).length : 'None');
console.log('Settings:', localStorage.getItem('hockey-settings') ? 'Present' : 'None');

