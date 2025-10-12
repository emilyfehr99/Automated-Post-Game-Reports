"""
Twitter API Configuration and Team Hashtags
"""

import os

# Twitter API Credentials (stored in environment variables for security)
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', 'rY7LNd3dr7Z9JJqKpdJiTWCHA')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET', '4kxhQTEBkJTfHUHFgIYMxQB11HQw8LdASJSlvIh32Y0Ats2nvE')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN', '1011358647228686336-qxTAVsHIppqf5FZ8kwxMIKflc6cn4a')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET', 'W8Uqz90Amk5NOysIsuXedqMbvQV3q6Db8RL8NhQZMqlw4')

# NHL Team Hashtags (official hashtags for all 32 teams)
TEAM_HASHTAGS = {
    'ANA': '#FlyTogether',
    'BOS': '#NHLBruins',
    'BUF': '#SabreHood',
    'CGY': '#Flames',
    'CAR': '#CarolinaCultre',
    'CHI': '#Blackhawks',
    'COL': '#GoAvsGo',
    'CBJ': '#CBJ',
    'DAL': '#TexasHockey',
    'DET': '#LGRW',
    'EDM': '#LetsGoOilers',
    'FLA': '#TimeToHunt',
    'LAK': '#GoKingsGo',
    'MIN': '#MNWild',
    'MTL': '#GoHabsGo',
    'NSH': '#Smashville',
    'NJD': '#NJDevils',
    'NYI': '#Isles',
    'NYR': '#NYR',
    'OTT': '#GoSensGo',
    'PHI': '#LetsGoFlyers',
    'PIT': '#LetsGoPens',
    'SJS': '#TheFutureIsTeal',
    'SEA': '#SeaKraken',
    'STL': '#STLBlues',
    'TBL': '#GoBolts',
    'TOR': '#LeafsForever',
    'UTA': '#TusksUp',
    'VAN': '#Canucks',
    'VGK': '#VegasBorn',
    'WSH': '#ALLCAPS',
    'WPG': '#GoJetsGo #NHLJets'
}

# NHL Season Start Date (for calculating week/day)
NHL_SEASON_START = '2025-10-08'  # Adjust this to the actual season start date

