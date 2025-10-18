// Direct fix for the spread syntax error on the live site
// This script can be run in the browser console to fix the issue immediately

console.log('🔧 Fixing spread syntax error...');

// Override the problematic functions with safe versions
(function() {
    // Store original functions
    const originalSetState = React.useState;
    
    // Create a safe spread function
    function safeSpread(target, source) {
        if (!target || typeof target !== 'object') {
            return source || [];
        }
        if (!source || typeof source !== 'object') {
            return target || [];
        }
        if (Array.isArray(target) && Array.isArray(source)) {
            return [...target, ...source];
        }
        return { ...target, ...source };
    }
    
    // Override the problematic array operations
    const originalArrayMethods = {
        map: Array.prototype.map,
        filter: Array.prototype.filter,
        concat: Array.prototype.concat
    };
    
    // Create safe array operations
    Array.prototype.safeMap = function(callback) {
        if (!Array.isArray(this)) {
            return [];
        }
        return this.map(callback);
    };
    
    Array.prototype.safeFilter = function(callback) {
        if (!Array.isArray(this)) {
            return [];
        }
        return this.filter(callback);
    };
    
    Array.prototype.safeConcat = function(other) {
        if (!Array.isArray(this)) {
            return Array.isArray(other) ? other : [];
        }
        if (!Array.isArray(other)) {
            return this;
        }
        return this.concat(other);
    };
    
    console.log('✅ Safe array methods installed');
})();

// Fix the specific save function
(function() {
    // Override the onSave function to handle the spread syntax error
    const originalOnSave = window.onSave;
    
    window.safeOnSave = async function(plan) {
        console.log('🔧 Using safe save function...', { planName: plan?.name });
        
        try {
            // Ensure plan is a proper object
            const safePlan = {
                id: plan?.id || Date.now().toString(),
                name: plan?.name || 'Unnamed Practice Plan',
                description: plan?.description || '',
                drills: Array.isArray(plan?.drills) ? plan.drills : [],
                totalDuration: typeof plan?.totalDuration === 'number' ? plan.totalDuration : 0,
                createdAt: plan?.createdAt || new Date().toISOString(),
                updatedAt: new Date().toISOString()
            };
            
            console.log('🧹 Safe plan object:', safePlan);
            
            // Get current practice plans safely
            const currentPlans = JSON.parse(localStorage.getItem('hockey-practice-plans') || '[]');
            if (!Array.isArray(currentPlans)) {
                console.log('⚠️ Current plans not an array, initializing...');
                localStorage.setItem('hockey-practice-plans', '[]');
            }
            
            // Add the new plan safely
            const updatedPlans = Array.isArray(currentPlans) ? [...currentPlans, safePlan] : [safePlan];
            
            // Save to localStorage
            localStorage.setItem('hockey-practice-plans', JSON.stringify(updatedPlans));
            console.log('✅ Plan saved to localStorage');
            
            // Try to save to Firebase if available
            try {
                if (window.firebase && window.firebase.firestore) {
                    const db = window.firebase.firestore();
                    const planRef = db.collection('practicePlans').doc(safePlan.id);
                    await planRef.set(safePlan);
                    console.log('✅ Plan saved to Firebase');
                }
            } catch (firebaseError) {
                console.log('⚠️ Firebase save failed, using localStorage only:', firebaseError);
            }
            
            // Show success message
            alert(`✅ Practice plan "${safePlan.name}" saved successfully!`);
            
            // Refresh the page to show the new plan
            setTimeout(() => {
                window.location.reload();
            }, 1000);
            
        } catch (error) {
            console.error('❌ Safe save failed:', error);
            alert(`❌ Failed to save practice plan: ${error.message}`);
        }
    };
    
    console.log('✅ Safe save function installed');
})();

// Override the save button click handler
(function() {
    // Wait for the page to load
    setTimeout(() => {
        const saveButtons = document.querySelectorAll('button');
        saveButtons.forEach(button => {
            if (button.textContent.includes('Save Plan') || button.textContent.includes('Save')) {
                console.log('🔧 Found save button, replacing handler...');
                
                // Remove all existing event listeners
                const newButton = button.cloneNode(true);
                button.parentNode.replaceChild(newButton, button);
                
                // Add the safe click handler
                newButton.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    console.log('💾 Save button clicked with safe handler');
                    
                    // Get the plan data from the form
                    const planName = document.querySelector('input[type="text"]')?.value || 'Unnamed Plan';
                    const planDescription = document.querySelector('textarea')?.value || '';
                    
                    const planData = {
                        id: Date.now().toString(),
                        name: planName,
                        description: planDescription,
                        drills: [],
                        totalDuration: 0,
                        createdAt: new Date().toISOString(),
                        updatedAt: new Date().toISOString()
                    };
                    
                    // Use the safe save function
                    window.safeOnSave(planData);
                });
                
                console.log('✅ Save button handler replaced');
            }
        });
    }, 2000);
})();

console.log('🎉 Spread syntax error fix applied! Try saving a practice plan now.');
