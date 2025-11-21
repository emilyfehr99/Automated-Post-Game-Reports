import React, { useState } from 'react';

/**
 * ShotChart Component
 * Displays a hockey rink with shots and goals plotted
 * 
 * @param {Array} shots - Array of shot objects with {x, y, type, team, shotType, xg, period}
 * @param {String} awayTeam - Away team abbreviation
 * @param {String} homeTeam - Home team abbreviation
 */
const ShotChart = ({ shots = [], awayTeam, homeTeam }) => {
    const [tooltip, setTooltip] = useState(null);

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
            'VAN': '#00205B', 'ANA': '#F47A38', 'LAK': '#111111', 'SJS': '#006D75',
            'UTA': '#71AFE5'
        };
        return colors[team] || '#888888';
    };

    // Get team logo URL
    const getTeamLogo = (team) => {
        return `https://assets.nhle.com/logos/nhl/svg/${team}_light.svg`;
    };

    // Handle mouse enter on shot/goal
    const handleMouseEnter = (event, shot) => {
        const rect = event.currentTarget.getBoundingClientRect();
        setTooltip({
            x: rect.left + rect.width / 2,
            y: rect.top - 10,
            shooter: shot.shooter || 'Unknown',
            shotType: shot.shotType || 'Wrist',
            xg: shot.xg,
            isGoal: shot.type === 'GOAL'
        });
    };

    const handleMouseLeave = () => {
        setTooltip(null);
    };

    // Separate shots and goals by team
    const awayShots = shots.filter(s => s.team === awayTeam && s.type !== 'GOAL');
    const awayGoals = shots.filter(s => s.team === awayTeam && s.type === 'GOAL');
    const homeShots = shots.filter(s => s.team === homeTeam && s.type !== 'GOAL');
    const homeGoals = shots.filter(s => s.team === homeTeam && s.type === 'GOAL');

    const awayColor = getTeamColor(awayTeam);
    const homeColor = getTeamColor(homeTeam);

    return (
        <div className="relative w-full bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl overflow-hidden">
            {/* Rink Image Background */}
            <div className="relative w-full" style={{ paddingBottom: '42.5%' }}>
                <img
                    src="/rink.jpeg"
                    alt="Hockey Rink"
                    className="absolute inset-0 w-full h-full object-cover opacity-60 border-0"
                    style={{ border: 'none', outline: 'none' }}
                />

                {/* SVG Overlay for Shots */}
                <svg
                    viewBox={`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`}
                    className="absolute inset-0 w-full h-full"
                    preserveAspectRatio="xMidYMid meet"
                >
                    {/* Team Logos */}
                    <image
                        href={getTeamLogo(awayTeam)}
                        x="20"
                        y={SVG_HEIGHT / 2 - 50}
                        width="100"
                        height="100"
                        opacity="0.25"
                    />
                    <image
                        href={getTeamLogo(homeTeam)}
                        x={SVG_WIDTH - 120}
                        y={SVG_HEIGHT / 2 - 50}
                        width="100"
                        height="100"
                        opacity="0.25"
                    />

                    {/* Away Team Shots */}
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
                            style={{ cursor: 'pointer' }}
                            className="hover:opacity-100 hover:stroke-white transition-all"
                            onMouseEnter={(e) => handleMouseEnter(e, shot)}
                            onMouseLeave={handleMouseLeave}
                        />
                    ))}

                    {/* Away Team Goals */}
                    {awayGoals.map((goal, idx) => (
                        <g
                            key={`away-goal-${idx}`}
                            style={{ cursor: 'pointer' }}
                            className="hover:opacity-100 transition-all"
                            onMouseEnter={(e) => handleMouseEnter(e, goal)}
                            onMouseLeave={handleMouseLeave}
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

                    {/* Home Team Shots */}
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
                            style={{ cursor: 'pointer' }}
                            className="hover:opacity-100 hover:stroke-white transition-all"
                            onMouseEnter={(e) => handleMouseEnter(e, shot)}
                            onMouseLeave={handleMouseLeave}
                        />
                    ))}

                    {/* Home Team Goals */}
                    {homeGoals.map((goal, idx) => (
                        <g
                            key={`home-goal-${idx}`}
                            style={{ cursor: 'pointer' }}
                            className="hover:opacity-100 transition-all"
                            onMouseEnter={(e) => handleMouseEnter(e, goal)}
                            onMouseLeave={handleMouseLeave}
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

            {/* Custom Tooltip */}
            {tooltip && (
                <div
                    className="fixed z-50 pointer-events-none"
                    style={{
                        left: `${tooltip.x}px`,
                        top: `${tooltip.y}px`,
                        transform: 'translate(-50%, -100%)'
                    }}
                >
                    <div className="bg-black/90 backdrop-blur-sm text-white px-3 py-2 rounded-lg shadow-xl border border-white/20">
                        <div className="text-xs font-mono space-y-1">
                            {tooltip.isGoal && <div className="text-yellow-400 font-bold">🎯 GOAL</div>}
                            <div className="font-semibold">{tooltip.shooter}</div>
                            <div className="text-gray-300">{tooltip.shotType} Shot</div>
                            {tooltip.xg !== undefined && (
                                <div className="text-blue-400">
                                    xG: {(tooltip.xg * 100).toFixed(1)}%
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Legend */}
            <div className="absolute bottom-4 right-4 bg-black/60 backdrop-blur-sm p-3 rounded-lg text-xs">
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full border border-black" style={{ backgroundColor: awayColor }} />
                        <span className="text-white font-mono">{awayTeam}</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full border border-black" style={{ backgroundColor: homeColor }} />
                        <span className="text-white font-mono">{homeTeam}</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="text-white text-lg">★</span>
                        <span className="text-white font-mono">Goal</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ShotChart;
