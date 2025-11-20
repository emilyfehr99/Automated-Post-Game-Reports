import React from 'react';

/**
 * Get NHL team logo URL
 * @param {string} teamAbbrev - Team abbreviation (e.g., 'TOR', 'BOS')
 * @returns {string} - URL to team logo
 */
export const getTeamLogo = (teamAbbrev) => {
    if (!teamAbbrev) return '';
    return `https://assets.nhle.com/logos/nhl/svg/${teamAbbrev}_light.svg`;
};

/**
 * Team Logo Component
 * @param {string} team - Team abbreviation
 * @param {string} className - Additional CSS classes
 * @param {string} alt - Alt text (defaults to team abbreviation)
 */
export const TeamLogo = ({ team, className = 'w-8 h-8', alt }) => {
    return (
        <img
            src={getTeamLogo(team)}
            alt={alt || team}
            className={`${className} drop-shadow-md`}
        />
    );
};
