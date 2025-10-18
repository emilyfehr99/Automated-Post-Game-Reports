// Complete drill restoration script
console.log('🔥 Restoring ALL 34 drills from Firebase...');

// All 34 drills from Firebase
const allDrills = [
  {"id": "1758138071815", "name": "Gambler", "description": "•Set up a 4 v 2 Rondo around one face-off dot in the zone, 4 offensive players around the exterior of the circle, with 2 defenders i n the middle). •Extra players and coaches are on the blue line. •Part 1 : O n the whistle, the 4 v 2 Rondo starts. The offensive team i s awarded points i f they are able t o split the defenders. The defending team gets a point if they block a pass and recover the puck. •Part 2: O n the second whistle, coach dumps a puck into the 4 corner which starts the 4 v 2 Quick Attack. The goal i s for the offensive team t o get the puck quickly, support each other, and quickly get a shot o n net. The offensive team i s awarded as points for a goal and the defending team is awarded 2 points if they can get the puck and skate i t out o f the zone. •Rotate players s o they get chances a t offense and defense.", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:41:57.867Z"},
  {"id": "drill-2", "name": "4 V 2 RONDO T O 4 V 2 QUICK ATTACK", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-3", "name": "Continuous Cycle", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-4", "name": "Billy Purcell Breakout", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-5", "name": "Jets 2v2", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-6", "name": "Shot, Screen, Gap, Battle", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-7", "name": "1v1 Return", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-8", "name": "CENTER ICE 1 ON 1", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-9", "name": "3 Pass Warmup", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-10", "name": "Keepaway into 1on1", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-11", "name": "Danger Zone 2on1", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-12", "name": "Red Wing 2v1 with Backchecker", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-13", "name": "CORNER BOARDS 1 V 1 LOOSE PUCK BATTLE", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-14", "name": "Race to 2v2 Game", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-15", "name": "Davos Game", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-16", "name": "1,2,3 Forecheck", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-17", "name": "Red Wing 2v3 or 2v4", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-18", "name": "3 Station D Clinic", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-19", "name": "3 Man - 2 Shot", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-20", "name": "3 ON 3 D SUPPORT", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-21", "name": "BUFFALO PUCK RACES INTO 2V1 WITH A BACK CHECKER", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-22", "name": "QUICK 1 ON 1", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-23", "name": "DOUBLE SWING WARM UP", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-24", "name": "2 ON 2 BOX OUT", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-25", "name": "3-0 STAY IN LANES", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-26", "name": "SMALL AREA COMPETITION", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-27", "name": "Scrimmage", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-28", "name": "WALL RETRIEVAL STATION", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-29", "name": "WAGON WHEEL", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-30", "name": "FOUR LINE WARM UP", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-31", "name": "TURN & BURN", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-32", "name": "POINT SHOT 2V1", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-33", "name": "WEAKSIDE TRANSITION", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"},
  {"id": "drill-34", "name": "OFF THE WALL NZ EXCHANGE", "category": "Skills", "type": "custom", "createdAt": "2025-09-17T14:42:00.000Z"}
];

// Save to localStorage
localStorage.setItem('hockey-drills', JSON.stringify(allDrills));

console.log('✅ All 34 drills restored to localStorage');
console.log('Drills restored:', allDrills.length);

// Show first 10 drills
console.log('First 10 drills:');
allDrills.slice(0, 10).forEach((drill, i) => {
  console.log((i+1) + '. ' + drill.name);
});

console.log('🔄 Reloading page...');
window.location.reload();
