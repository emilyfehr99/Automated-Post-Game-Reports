// Copy and paste this entire script into your browser console at http://localhost:3000

console.log('🔥 Starting data restoration...');

// Step 1: Check current data
console.log('Current localStorage data:');
console.log('Drills:', localStorage.getItem('hockey-drills') ? JSON.parse(localStorage.getItem('hockey-drills')).length : 'None');
console.log('Practice Plans:', localStorage.getItem('hockey-practice-plans') ? JSON.parse(localStorage.getItem('hockey-practice-plans')).length : 'None');

// Step 2: Restore data from Firebase
async function restoreFromFirebase() {
    try {
        // Import Firebase
        const { initializeApp } = await import('https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js');
        const { getFirestore, collection, getDocs } = await import('https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js');
        
        // Initialize Firebase
        const firebaseConfig = {
            apiKey: "AIzaSyCm2m3lSlh_IBgHSOLcmeCO9lZYHaxgrFw",
            authDomain: "hockey-practice-planner.firebaseapp.com",
            projectId: "hockey-practice-planner",
            storageBucket: "hockey-practice-planner.firebasestorage.app",
            messagingSenderId: "557366268618",
            appId: "1:557366268618:web:d6f5cf9e80045d966fda33",
            measurementId: "G-BSH8MT49BZ"
        };
        
        const app = initializeApp(firebaseConfig);
        const db = getFirestore(app);
        
        console.log('✅ Firebase connected');
        
        // Get all data
        const [drillsSnapshot, plansSnapshot, settingsSnapshot] = await Promise.all([
            getDocs(collection(db, 'drills')),
            getDocs(collection(db, 'practicePlans')),
            getDocs(collection(db, 'settings'))
        ]);
        
        const drills = drillsSnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
        const plans = plansSnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
        const settings = settingsSnapshot.docs.length > 0 ? settingsSnapshot.docs[0].data() : {};
        
        console.log(`📊 Found ${drills.length} drills and ${plans.length} practice plans`);
        
        // Save to localStorage
        localStorage.setItem('hockey-drills', JSON.stringify(drills));
        localStorage.setItem('hockey-practice-plans', JSON.stringify(plans));
        localStorage.setItem('hockey-settings', JSON.stringify(settings));
        localStorage.setItem('hockey-custom-categories', JSON.stringify([]));
        
        console.log('✅ Data saved to localStorage');
        
        // Show Practice 2 details
        const practice2 = plans.find(p => p.name === 'Practice 2');
        if (practice2) {
            console.log('🎯 Practice 2 details:');
            console.log(`   Created: ${new Date(practice2.createdAt).toLocaleString()}`);
            console.log(`   Updated: ${new Date(practice2.updatedAt).toLocaleString()}`);
            if (practice2.drills) {
                console.log(`   Drills: ${practice2.drills.length}`);
            }
        }
        
        console.log('🔄 Reloading page...');
        window.location.reload();
        
    } catch (error) {
        console.error('❌ Error:', error);
    }
}

// Run the restoration
restoreFromFirebase();
