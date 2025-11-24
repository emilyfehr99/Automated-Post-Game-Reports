import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { getTeamLogo } from '../utils/teamLogos';

/**
 * ShotChart Component
 * Displays a hockey rink with shots and goals plotted
 * 
 * @param {Array} shotsData - Array of shot objects with {x, y, type, team, period, time}
 * @param {String} awayTeam - Away team abbreviation
 * @param {String} homeTeam - Home team abbreviation
 * @param {Object} awayHeatmap - Pre-game heatmap data for away team
 * @param {Object} homeHeatmap - Pre-game heatmap data for home team
 * @param {String} gameState - Current game state (FUT, LIVE, FINAL)
 */
const ShotChart = ({ shotsData = [], awayTeam, homeTeam, awayHeatmap = null, homeHeatmap = null, gameState = 'FUT' }) => {
    const [tooltip, setTooltip] = useState(null);
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
        return () => setMounted(false);
    }, []);

    // Rink dimensions (NHL standard in feet)
    const RINK_WIDTH = 200; // -100 to 100
    const RINK_HEIGHT = 85; // -42.5 to 42.5

    // SVG viewBox dimensions
    const SVG_WIDTH = 800;
    const SVG_HEIGHT = 340;

    // Convert rink coordinates to SVG coordinates
    const toSVGX = (x) => ((x + 100) / RINK_WIDTH) * SVG_WIDTH;
    const toSVGY = (y) => ((42.5 - y) / RINK_HEIGHT) * SVG_HEIGHT; // Flip Y axis

    // Team colors (simplified - you can expand this)
    const getTeamColor = (team) => {
        const colors = {
            'BOS': '#FFB81C', 'TOR': '#00205B', 'MTL': '#AF1E2D', 'OTT': '#C52032',
            'TBL': '#002868', 'FLA': '#041E42', 'DET': '#CE1126', 'BUF': '#002654',
            'NYR': '#0038A8', 'NYI': '#00539B', 'NJD': '#CE1126', 'PHI': '#F74902',
            'PIT': '#000000', 'WSH': '#041E42', 'CAR': '#CE1126', 'CBJ': '#002654',
            'CHI': '#CF0A2C', 'STL': '#002F87', 'MIN': '#154734', 'WPG': '#041E42',
            'NSH': '#FFB81C', 'COL': '#6F263D', 'DAL': '#006847', 'ARI': '#8C2633',
            'VGK': '#B4975A', 'SEA': '#001628', 'CGY': '#C8102E', 'EDM': '#041E42',
            'VAN': '#00205B', 'ANA': '#F47A38', 'LAK': '#111111', 'SJS': '#006D75'
        };
        return colors[team] || '#888888';
    };

    // Handle mouse enter on shot/goal
    const handleMouseEnter = (event, shot) => {
        event.preventDefault();
        event.stopPropagation();

        const elementRect = event.currentTarget.getBoundingClientRect();

        // Calculate position relative to viewport (center of the element)
        let x = elementRect.left + (elementRect.width / 2);
        let y = elementRect.top;

        // Constrain to viewport bounds to prevent horizontal scrolling
        // Use a safe approach that works even if window is not available
        if (typeof window !== 'undefined') {
            const tooltipWidth = 250; // Approximate tooltip width
            const tooltipHeight = 100; // Approximate tooltip height
            const padding = 10;
            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;

            // Ensure tooltip doesn't go off the left or right edge
            if (x < tooltipWidth / 2 + padding) {
                x = tooltipWidth / 2 + padding;
            } else if (x > viewportWidth - tooltipWidth / 2 - padding) {
                x = viewportWidth - tooltipWidth / 2 - padding;
            }

            // Ensure tooltip doesn't go off the top edge
            if (y < tooltipHeight + padding) {
                y = tooltipHeight + padding;
            }
        }

        // Get shooter name - prioritize 'shooter' field from backend (has proper names)
        // Backend should provide 'shooter' with player name, not ID
        let shooterName = shot.shooter || shot.shooterName || shot.player || 'Unknown';

        // Only use player_id as fallback if shooter is not available
        if ((!shooterName || shooterName === 'Unknown') && shot.player_id) {
            shooterName = `Player #${shot.player_id}`;
        }

        // If it's still a numeric ID (shouldn't happen if backend is working), format it
        if (typeof shooterName === 'number' || (typeof shooterName === 'string' && /^\d+$/.test(shooterName))) {
            shooterName = `Player #${shooterName}`;
        }

        console.log('Shot data:', { shooter: shot.shooter, shooterName: shot.shooterName, player_id: shot.player_id, finalName: shooterName });

        // Get shot type - normalize to title case
        const shotType = shot.shotType ? shot.shotType.charAt(0).toUpperCase() + shot.shotType.slice(1).toLowerCase() : 'Wrist';

        // Get xG - handle different formats
        let xgValue = shot.xg;
        if (xgValue === undefined || xgValue === null) {
            xgValue = null;
        } else if (typeof xgValue === 'string') {
            xgValue = parseFloat(xgValue);
            if (isNaN(xgValue) || xgValue === 0) {
                xgValue = null; // Will trigger fallback calculation
            }
        }

        // If xG is 0, null, or NaN, calculate a simple distance-based xG as fallback
        // IMPORTANT: Coordinates are normalized (each team shoots from their own side)
        // Away team shoots from right (positive x), Home team shoots from left (negative x)
        // Goals are at x=89 (right) and x=-89 (left) in NHL coordinates
        // But after normalization, we need to calculate from the appropriate goal
        if (xgValue === null || xgValue === undefined || isNaN(xgValue) || xgValue === 0) {
            const shotX = shot.x || 0;
            const shotY = shot.y || 0;

            // Determine which goal based on normalized x coordinate
            // Positive x = shooting toward right goal (x=89 in raw coords)
            // Negative x = shooting toward left goal (x=-89 in raw coords)
            // After normalization, goal is at x=89 for positive shots, x=-89 for negative shots
            const goalX = shotX >= 0 ? 89 : -89;

            // Calculate distance from the appropriate goal (not from center!)
            const distanceFromGoal = Math.sqrt((goalX - shotX) ** 2 + shotY ** 2);

            // Simple xG model based on distance from goal
            // Closer shots have higher xG
            if (distanceFromGoal < 20) {
                xgValue = 0.15;
            } else if (distanceFromGoal < 35) {
                xgValue = 0.08;
            } else if (distanceFromGoal < 50) {
                xgValue = 0.04;
            } else {
                xgValue = 0.02;
            }

            // Apply angle adjustment (shots from wider angles have lower xG)
            const angleRatio = Math.abs(shotY) / Math.max(distanceFromGoal, 1);
            if (angleRatio > 0.6) {
                xgValue *= 0.8; // Wide angle
            } else if (angleRatio < 0.3) {
                xgValue *= 1.2; // Good angle (slot)
            }

            xgValue = Math.max(0.01, Math.min(xgValue, 0.95));
        }

        const tooltipData = {
            x: x,
            y: y,
            shooter: shooterName,
            shotType: shotType,
            xg: xgValue,
            isGoal: shot.type === 'GOAL' || shot.type === 'goal' || shot.isGoal
        };

        console.log('Setting tooltip:', tooltipData, 'Element rect:', elementRect);
        setTooltip(tooltipData);
    };

    const handleMouseLeave = (event) => {
        event.preventDefault();
        event.stopPropagation();
        setTooltip(null);
    };

    // Determine if we're showing pre-game (last 5 games) or in-game/post-game data
    const isPreGame = gameState === 'FUT' || gameState === 'PREVIEW';
    const hasLiveData = shotsData.length > 0;

    // Debug logging
    console.log('ShotChart Debug:', {
        gameState,
        isPreGame,
        hasLiveData,
        shotsDataLength: shotsData.length,
        shotsDataSample: shotsData.slice(0, 2),
        awayTeam,
        homeTeam,
        hasAwayHeatmap: !!awayHeatmap,
        hasHomeHeatmap: !!homeHeatmap
    });

    // For pre-game, use heatmap data (last 5 games)
    // For in-game/post-game, use live shots data
    let awayShots = [];
    let awayGoals = [];
    let homeShots = [];
    let homeGoals = [];

    if (isPreGame && (awayHeatmap || homeHeatmap)) {
        // Pre-game: Use heatmap data from last 5 games
        // Backend already normalizes so teams shoot from right (positive x)
        // Away team shoots right, Home team shoots left
        if (awayHeatmap) {
            awayShots = (awayHeatmap.shots_for || []).map(shot => ({
                ...shot,
                x: Math.abs(shot.x || 0), // Ensure positive (right side)
                y: shot.y || 0,
                team: awayTeam,
                shooter: shot.shooter,
                shotType: shot.shotType,
                xg: shot.xg
            }));
            awayGoals = (awayHeatmap.goals_for || []).map(goal => ({
                ...goal,
                x: Math.abs(goal.x || 0), // Ensure positive (right side)
                y: goal.y || 0,
                team: awayTeam,
                type: 'GOAL',
                shooter: goal.shooter,
                shotType: goal.shotType,
                xg: goal.xg
            }));
        }
        if (homeHeatmap) {
            homeShots = (homeHeatmap.shots_for || []).map(shot => ({
                ...shot,
                x: -Math.abs(shot.x || 0), // Ensure negative (left side)
                y: shot.y || 0,
                team: homeTeam,
                shooter: shot.shooter,
                shotType: shot.shotType,
                xg: shot.xg
            }));
            homeGoals = (homeHeatmap.goals_for || []).map(goal => ({
                ...goal,
                x: -Math.abs(goal.x || 0), // Ensure negative (left side)
                y: goal.y || 0,
                team: homeTeam,
                type: 'GOAL',
                shooter: goal.shooter,
                shotType: goal.shotType,
                xg: goal.xg
            }));
        }
    } else if (hasLiveData) {
        // In-game/Post-game: Use live shots data
        // Normalize coordinates so each team has their own side regardless of period
        shotsData.forEach(shot => {
            const isAway = shot.team === awayTeam;
            // Normalize: Away team always shoots from right (positive x), Home from left (negative x)
            const normalizedShot = {
                ...shot,
                x: isAway ? Math.abs(shot.x || 0) : -Math.abs(shot.x || 0),
                y: shot.y || 0
            };

            if (shot.type === 'GOAL' || shot.type === 'goal') {
                if (isAway) awayGoals.push(normalizedShot);
                else homeGoals.push(normalizedShot);
            } else {
                if (isAway) awayShots.push(normalizedShot);
                else homeShots.push(normalizedShot);
            }
        });
    }

    const awayColor = getTeamColor(awayTeam);
    const homeColor = getTeamColor(homeTeam);

    // Debug: Log final shot counts
    console.log('ShotChart Final Counts:', {
        awayShots: awayShots.length,
        awayGoals: awayGoals.length,
        homeShots: homeShots.length,
        homeGoals: homeGoals.length,
        totalShots: awayShots.length + homeShots.length + awayGoals.length + homeGoals.length
    });

    return (
        <div className="relative w-full rounded-xl overflow-visible">
            {/* Rink Image Background */}
            <div className="relative w-full" style={{ paddingBottom: '42.5%' }}>
                <img
                    src="/rink.jpeg"
                    alt="Hockey Rink"
                    className="absolute inset-0 w-full h-full object-cover opacity-60"
                />

                {/* SVG Overlay for Shots */}
                <svg
                    viewBox={`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`}
                    className="absolute inset-0 w-full h-full"
                    preserveAspectRatio="xMidYMid meet"
                    style={{ pointerEvents: 'all' }}
                >
                    {/* Team Logos - Always show */}
                    <>
                        {/* Away Team Logo (Right side - they shoot right) */}
                        <g transform={`translate(${SVG_WIDTH * 0.85}, ${SVG_HEIGHT * 0.5})`}>
                            <image
                                href={getTeamLogo(awayTeam)}
                                x="-40"
                                y="-40"
                                width="80"
                                height="80"
                                opacity="0.7"
                            />
                            <text
                                x="0"
                                y="60"
                                textAnchor="middle"
                                fill="white"
                                fontSize="16"
                                fontWeight="bold"
                                className="drop-shadow-lg"
                            >
                                {awayTeam}
                            </text>
                        </g>
                        {/* Home Team Logo (Left side - they shoot left) */}
                        <g transform={`translate(${SVG_WIDTH * 0.15}, ${SVG_HEIGHT * 0.5})`}>
                            <image
                                href={getTeamLogo(homeTeam)}
                                x="-40"
                                y="-40"
                                width="80"
                                height="80"
                                opacity="0.7"
                            />
                            <text
                                x="0"
                                y="60"
                                textAnchor="middle"
                                fill="white"
                                fontSize="16"
                                fontWeight="bold"
                                className="drop-shadow-lg"
                            >
                                {homeTeam}
                            </text>
                        </g>
                    </>

                    {/* Away Team Shots (Right side) */}
                    {awayShots.map((shot, idx) => (
                        <circle
                            key={`away-shot-${idx}`}
                            cx={toSVGX(shot.x)}
                            cy={toSVGY(shot.y)}
                            r="4"
                            fill={awayColor}
                            stroke="black"
                            strokeWidth="0.8"
                            opacity="0.85"
                            style={{ cursor: 'pointer', pointerEvents: 'all' }}
                            className="hover:opacity-100 hover:stroke-white transition-all"
                            onMouseEnter={(e) => handleMouseEnter(e, shot)}
                            onMouseLeave={(e) => handleMouseLeave(e)}
                        />
                    ))}

                    {/* Away Team Goals (Right side) */}
                    {awayGoals.map((goal, idx) => (
                        <g
                            key={`away-goal-${idx}`}
                            style={{ cursor: 'pointer', pointerEvents: 'all' }}
                            className="hover:opacity-100 transition-all"
                            onMouseEnter={(e) => handleMouseEnter(e, goal)}
                            onMouseLeave={(e) => handleMouseLeave(e)}
                        >
                            <circle
                                cx={toSVGX(goal.x)}
                                cy={toSVGY(goal.y)}
                                r="7"
                                fill={awayColor}
                                stroke="black"
                                strokeWidth="1.5"
                                opacity="1"
                                className="hover:stroke-white"
                            />
                            {/* Star marker for goals */}
                            <text
                                x={toSVGX(goal.x)}
                                y={toSVGY(goal.y)}
                                textAnchor="middle"
                                dominantBaseline="central"
                                fill="white"
                                fontSize="10"
                                fontWeight="bold"
                                pointerEvents="none"
                            >
                                ★
                            </text>
                        </g>
                    ))}

                    {/* Home Team Shots (Left side) */}
                    {homeShots.map((shot, idx) => (
                        <circle
                            key={`home-shot-${idx}`}
                            cx={toSVGX(shot.x)}
                            cy={toSVGY(shot.y)}
                            r="4"
                            fill={homeColor}
                            stroke="black"
                            strokeWidth="0.8"
                            opacity="0.85"
                            style={{ cursor: 'pointer', pointerEvents: 'all' }}
                            className="hover:opacity-100 hover:stroke-white transition-all"
                            onMouseEnter={(e) => handleMouseEnter(e, shot)}
                            onMouseLeave={(e) => handleMouseLeave(e)}
                        />
                    ))}

                    {/* Home Team Goals (Left side) */}
                    {homeGoals.map((goal, idx) => (
                        <g
                            key={`home-goal-${idx}`}
                            style={{ cursor: 'pointer', pointerEvents: 'all' }}
                            className="hover:opacity-100 transition-all"
                            onMouseEnter={(e) => handleMouseEnter(e, goal)}
                            onMouseLeave={(e) => handleMouseLeave(e)}
                        >
                            <circle
                                cx={toSVGX(goal.x)}
                                cy={toSVGY(goal.y)}
                                r="7"
                                fill={homeColor}
                                stroke="black"
                                strokeWidth="1.5"
                                opacity="1"
                                className="hover:stroke-white"
                            />
                            {/* Star marker for goals */}
                            <text
                                x={toSVGX(goal.x)}
                                y={toSVGY(goal.y)}
                                textAnchor="middle"
                                dominantBaseline="central"
                                fill="white"
                                fontSize="10"
                                fontWeight="bold"
                                pointerEvents="none"
                            >
                                ★
                            </text>
                        </g>
                    ))}
                </svg>
            </div>

            {/* Custom Tooltip - Render via Portal to avoid overflow issues */}
            {tooltip && mounted && typeof document !== 'undefined' && document.body && createPortal(
                <div
                    className="fixed pointer-events-none"
                    style={{
                        left: `${tooltip.x}px`,
                        top: `${tooltip.y}px`,
                        transform: 'translate(-50%, calc(-100% - 12px))',
                        zIndex: 10000,
                        maxWidth: '250px',
                        width: 'max-content'
                    }}
                >
                    <div className="bg-black/95 backdrop-blur-sm text-white px-3 py-2 rounded-lg shadow-2xl border border-white/30">
                        <div className="text-xs font-mono space-y-1">
                            {tooltip.isGoal && <div className="text-yellow-400 font-bold">🎯 GOAL</div>}
                            <div className="font-semibold text-white whitespace-nowrap">{tooltip.shooter}</div>
                            <div className="text-gray-300 whitespace-nowrap">{tooltip.shotType} Shot</div>
                            {tooltip.xg !== undefined && tooltip.xg !== null && (
                                <div className="text-blue-400 whitespace-nowrap">
                                    xG: {typeof tooltip.xg === 'number' ? (tooltip.xg * 100).toFixed(1) + '%' : tooltip.xg}
                                </div>
                            )}
                        </div>
                    </div>
                </div>,
                document.body
            )}

        </div>
    );
};

export default ShotChart;
