// Direct data restoration script
// Run this in your browser console at http://localhost:3000

console.log('🔥 Starting data restoration...');

// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyCm2m3lSlh_IBgHSOLcmeCO9lZYHaxgrFw",
    authDomain: "hockey-practice-planner.firebaseapp.com",
    projectId: "hockey-practice-planner",
    storageBucket: "hockey-practice-planner.firebasestorage.app",
    messagingSenderId: "557366268618",
    appId: "1:557366268618:web:d6f5cf9e80045d966fda33",
    measurementId: "G-BSH8MT49BZ"
};

// Import Firebase modules
import('https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js').then(firebaseApp => {
    import('https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js').then(firebaseFirestore => {
        
        const { initializeApp } = firebaseApp;
        const { getFirestore, collection, getDocs } = firebaseFirestore;
        
        // Initialize Firebase
        const app = initializeApp(firebaseConfig);
        const db = getFirestore(app);
        
        console.log('✅ Firebase initialized');
        
        // Get all data from Firebase
        Promise.all([
            getDocs(collection(db, 'drills')),
            getDocs(collection(db, 'practicePlans')),
            getDocs(collection(db, 'settings'))
        ]).then(([drillsSnapshot, plansSnapshot, settingsSnapshot]) => {
            
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
            
            console.log('🔄 Reloading page to show restored data...');
            window.location.reload();
            
        }).catch(error => {
            console.error('❌ Error fetching data:', error);
        });
        
    }).catch(error => {
        console.error('❌ Error importing Firestore:', error);
    });
}).catch(error => {
    console.error('❌ Error importing Firebase:', error);
});
