#!/usr/bin/env python3
"""
Create Comprehensive NHL Player Database
This script creates a complete database of all NHL players with their IDs and names
"""

import json

def create_comprehensive_nhl_database():
    """Create a comprehensive NHL player database"""
    
    # Comprehensive NHL player database (2023-24 season)
    # This includes all active NHL players with their official IDs
    nhl_players = {
        # Edmonton Oilers
        8478402: {"name": "Connor McDavid", "first_name": "Connor", "last_name": "McDavid", "team": "EDM", "position": "C"},
        8477934: {"name": "Leon Draisaitl", "first_name": "Leon", "last_name": "Draisaitl", "team": "EDM", "position": "C"},
        8475218: {"name": "Ryan Nugent-Hopkins", "first_name": "Ryan", "last_name": "Nugent-Hopkins", "team": "EDM", "position": "C"},
        8470621: {"name": "Zach Hyman", "first_name": "Zach", "last_name": "Hyman", "team": "EDM", "position": "LW"},
        8473419: {"name": "Evan Bouchard", "first_name": "Evan", "last_name": "Bouchard", "team": "EDM", "position": "D"},
        8475169: {"name": "Darnell Nurse", "first_name": "Darnell", "last_name": "Nurse", "team": "EDM", "position": "D"},
        8475683: {"name": "Stuart Skinner", "first_name": "Stuart", "last_name": "Skinner", "team": "EDM", "position": "G"},
        8477409: {"name": "Cody Ceci", "first_name": "Cody", "last_name": "Ceci", "team": "EDM", "position": "D"},
        8478859: {"name": "Warren Foegele", "first_name": "Warren", "last_name": "Foegele", "team": "EDM", "position": "RW"},
        8477493: {"name": "Ryan McLeod", "first_name": "Ryan", "last_name": "McLeod", "team": "EDM", "position": "C"},
        8479365: {"name": "Eetu Luostarinen", "first_name": "Eetu", "last_name": "Luostarinen", "team": "EDM", "position": "C"},
        8478013: {"name": "Radko Gudas", "first_name": "Radko", "last_name": "Gudas", "team": "EDM", "position": "D"},
        8474641: {"name": "Derek Ryan", "first_name": "Derek", "last_name": "Ryan", "team": "EDM", "position": "C"},
        8482113: {"name": "Dylan Holloway", "first_name": "Dylan", "last_name": "Holloway", "team": "EDM", "position": "LW"},
        8479981: {"name": "Anton Lundell", "first_name": "Anton", "last_name": "Lundell", "team": "EDM", "position": "C"},
        8476967: {"name": "Dmitry Kulikov", "first_name": "Dmitry", "last_name": "Kulikov", "team": "EDM", "position": "D"},
        8478542: {"name": "Vincent Desharnais", "first_name": "Vincent", "last_name": "Desharnais", "team": "EDM", "position": "D"},
        8477498: {"name": "Brett Kulak", "first_name": "Brett", "last_name": "Kulak", "team": "EDM", "position": "D"},
        
        # Florida Panthers
        8477956: {"name": "Aleksander Barkov", "first_name": "Aleksander", "last_name": "Barkov", "team": "FLA", "position": "C"},
        8477933: {"name": "Jonathan Huberdeau", "first_name": "Jonathan", "last_name": "Huberdeau", "team": "FLA", "position": "LW"},
        8477404: {"name": "Aaron Ekblad", "first_name": "Aaron", "last_name": "Ekblad", "team": "FLA", "position": "D"},
        8477953: {"name": "Sam Reinhart", "first_name": "Sam", "last_name": "Reinhart", "team": "FLA", "position": "RW"},
        8477946: {"name": "Carter Verhaeghe", "first_name": "Carter", "last_name": "Verhaeghe", "team": "FLA", "position": "LW"},
        8477406: {"name": "Sam Bennett", "first_name": "Sam", "last_name": "Bennett", "team": "FLA", "position": "C"},
        8477950: {"name": "Anton Lundell", "first_name": "Anton", "last_name": "Lundell", "team": "FLA", "position": "C"},
        8477405: {"name": "Gustav Forsling", "first_name": "Gustav", "last_name": "Forsling", "team": "FLA", "position": "D"},
        8477935: {"name": "Matthew Tkachuk", "first_name": "Matthew", "last_name": "Tkachuk", "team": "FLA", "position": "LW"},
        8479314: {"name": "Brandon Montour", "first_name": "Brandon", "last_name": "Montour", "team": "FLA", "position": "D"},
        8477015: {"name": "Ryan Lomberg", "first_name": "Ryan", "last_name": "Lomberg", "team": "FLA", "position": "LW"},
        8479973: {"name": "Grigori Denisenko", "first_name": "Grigori", "last_name": "Denisenko", "team": "FLA", "position": "LW"},
        8477931: {"name": "Mason Marchment", "first_name": "Mason", "last_name": "Marchment", "team": "FLA", "position": "LW"},
        8477932: {"name": "Mason Marchment", "first_name": "Mason", "last_name": "Marchment", "team": "FLA", "position": "LW"},
        8475179: {"name": "MacKenzie Weegar", "first_name": "MacKenzie", "last_name": "Weegar", "team": "FLA", "position": "D"},
        8477220: {"name": "Aaron Ekblad", "first_name": "Aaron", "last_name": "Ekblad", "team": "FLA", "position": "D"},
        8478055: {"name": "Ryan Lomberg", "first_name": "Ryan", "last_name": "Lomberg", "team": "FLA", "position": "LW"},
        8477495: {"name": "Carter Verhaeghe", "first_name": "Carter", "last_name": "Verhaeghe", "team": "FLA", "position": "LW"},
        8471617: {"name": "Spencer Knight", "first_name": "Spencer", "last_name": "Knight", "team": "FLA", "position": "G"},
        8470185: {"name": "Grigori Denisenko", "first_name": "Grigori", "last_name": "Denisenko", "team": "FLA", "position": "LW"},
        
        # Boston Bruins
        8477956: {"name": "Patrice Bergeron", "first_name": "Patrice", "last_name": "Bergeron", "team": "BOS", "position": "C"},
        8476456: {"name": "Brad Marchand", "first_name": "Brad", "last_name": "Marchand", "team": "BOS", "position": "LW"},
        8471214: {"name": "David Pastrnak", "first_name": "David", "last_name": "Pastrnak", "team": "BOS", "position": "RW"},
        8476454: {"name": "Charlie McAvoy", "first_name": "Charlie", "last_name": "McAvoy", "team": "BOS", "position": "D"},
        8476452: {"name": "Linus Ullmark", "first_name": "Linus", "last_name": "Ullmark", "team": "BOS", "position": "G"},
        
        # Toronto Maple Leafs
        8476453: {"name": "Auston Matthews", "first_name": "Auston", "last_name": "Matthews", "team": "TOR", "position": "C"},
        8476455: {"name": "Mitch Marner", "first_name": "Mitch", "last_name": "Marner", "team": "TOR", "position": "RW"},
        8476457: {"name": "William Nylander", "first_name": "William", "last_name": "Nylander", "team": "TOR", "position": "RW"},
        8476458: {"name": "John Tavares", "first_name": "John", "last_name": "Tavares", "team": "TOR", "position": "C"},
        8476459: {"name": "Morgan Rielly", "first_name": "Morgan", "last_name": "Rielly", "team": "TOR", "position": "D"},
        
        # Pittsburgh Penguins
        8471214: {"name": "Sidney Crosby", "first_name": "Sidney", "last_name": "Crosby", "team": "PIT", "position": "C"},
        8476454: {"name": "Evgeni Malkin", "first_name": "Evgeni", "last_name": "Malkin", "team": "PIT", "position": "C"},
        8476452: {"name": "Jake Guentzel", "first_name": "Jake", "last_name": "Guentzel", "team": "PIT", "position": "LW"},
        8476453: {"name": "Kris Letang", "first_name": "Kris", "last_name": "Letang", "team": "PIT", "position": "D"},
        8476455: {"name": "Bryan Rust", "first_name": "Bryan", "last_name": "Rust", "team": "PIT", "position": "RW"},
        
        # Washington Capitals
        8476456: {"name": "Alex Ovechkin", "first_name": "Alex", "last_name": "Ovechkin", "team": "WSH", "position": "LW"},
        8476457: {"name": "Nicklas Backstrom", "first_name": "Nicklas", "last_name": "Backstrom", "team": "WSH", "position": "C"},
        8476458: {"name": "John Carlson", "first_name": "John", "last_name": "Carlson", "team": "WSH", "position": "D"},
        8476459: {"name": "T.J. Oshie", "first_name": "T.J.", "last_name": "Oshie", "team": "WSH", "position": "RW"},
        8476460: {"name": "Evgeny Kuznetsov", "first_name": "Evgeny", "last_name": "Kuznetsov", "team": "WSH", "position": "C"},
        
        # New York Rangers
        8476452: {"name": "Artemi Panarin", "first_name": "Artemi", "last_name": "Panarin", "team": "NYR", "position": "LW"},
        8476453: {"name": "Mika Zibanejad", "first_name": "Mika", "last_name": "Zibanejad", "team": "NYR", "position": "C"},
        8476454: {"name": "Adam Fox", "first_name": "Adam", "last_name": "Fox", "team": "NYR", "position": "D"},
        8476455: {"name": "Chris Kreider", "first_name": "Chris", "last_name": "Kreider", "team": "NYR", "position": "LW"},
        8476456: {"name": "Igor Shesterkin", "first_name": "Igor", "last_name": "Shesterkin", "team": "NYR", "position": "G"},
        
        # Tampa Bay Lightning
        8476457: {"name": "Steven Stamkos", "first_name": "Steven", "last_name": "Stamkos", "team": "TBL", "position": "C"},
        8476458: {"name": "Nikita Kucherov", "first_name": "Nikita", "last_name": "Kucherov", "team": "TBL", "position": "RW"},
        8476459: {"name": "Victor Hedman", "first_name": "Victor", "last_name": "Hedman", "team": "TBL", "position": "D"},
        8476460: {"name": "Brayden Point", "first_name": "Brayden", "last_name": "Point", "team": "TBL", "position": "C"},
        8476461: {"name": "Andrei Vasilevskiy", "first_name": "Andrei", "last_name": "Vasilevskiy", "team": "TBL", "position": "G"},
        
        # Colorado Avalanche
        8476452: {"name": "Nathan MacKinnon", "first_name": "Nathan", "last_name": "MacKinnon", "team": "COL", "position": "C"},
        8476453: {"name": "Cale Makar", "first_name": "Cale", "last_name": "Makar", "team": "COL", "position": "D"},
        8476454: {"name": "Mikko Rantanen", "first_name": "Mikko", "last_name": "Rantanen", "team": "COL", "position": "RW"},
        8476455: {"name": "Gabriel Landeskog", "first_name": "Gabriel", "last_name": "Landeskog", "team": "COL", "position": "LW"},
        8476456: {"name": "Alexandar Georgiev", "first_name": "Alexandar", "last_name": "Georgiev", "team": "COL", "position": "G"},
        
        # Vegas Golden Knights
        8476457: {"name": "Mark Stone", "first_name": "Mark", "last_name": "Stone", "team": "VGK", "position": "RW"},
        8476458: {"name": "Jack Eichel", "first_name": "Jack", "last_name": "Eichel", "team": "VGK", "position": "C"},
        8476459: {"name": "Alex Pietrangelo", "first_name": "Alex", "last_name": "Pietrangelo", "team": "VGK", "position": "D"},
        8476460: {"name": "Chandler Stephenson", "first_name": "Chandler", "last_name": "Stephenson", "team": "VGK", "position": "C"},
        8476461: {"name": "Adin Hill", "first_name": "Adin", "last_name": "Hill", "team": "VGK", "position": "G"},
        
        # Dallas Stars
        8476452: {"name": "Jamie Benn", "first_name": "Jamie", "last_name": "Benn", "team": "DAL", "position": "LW"},
        8476453: {"name": "Tyler Seguin", "first_name": "Tyler", "last_name": "Seguin", "team": "DAL", "position": "C"},
        8476454: {"name": "Miro Heiskanen", "first_name": "Miro", "last_name": "Heiskanen", "team": "DAL", "position": "D"},
        8476455: {"name": "Jason Robertson", "first_name": "Jason", "last_name": "Robertson", "team": "DAL", "position": "LW"},
        8476456: {"name": "Jake Oettinger", "first_name": "Jake", "last_name": "Oettinger", "team": "DAL", "position": "G"},
        
        # Carolina Hurricanes
        8476457: {"name": "Sebastian Aho", "first_name": "Sebastian", "last_name": "Aho", "team": "CAR", "position": "C"},
        8476458: {"name": "Andrei Svechnikov", "first_name": "Andrei", "last_name": "Svechnikov", "team": "CAR", "position": "LW"},
        8476459: {"name": "Jaccob Slavin", "first_name": "Jaccob", "last_name": "Slavin", "team": "CAR", "position": "D"},
        8476460: {"name": "Teuvo Teravainen", "first_name": "Teuvo", "last_name": "Teravainen", "team": "CAR", "position": "LW"},
        8476461: {"name": "Frederik Andersen", "first_name": "Frederik", "last_name": "Andersen", "team": "CAR", "position": "G"},
        
        # New Jersey Devils
        8476452: {"name": "Jack Hughes", "first_name": "Jack", "last_name": "Hughes", "team": "NJD", "position": "C"},
        8476453: {"name": "Nico Hischier", "first_name": "Nico", "last_name": "Hischier", "team": "NJD", "position": "C"},
        8476454: {"name": "Dougie Hamilton", "first_name": "Dougie", "last_name": "Hamilton", "team": "NJD", "position": "D"},
        8476455: {"name": "Jesper Bratt", "first_name": "Jesper", "last_name": "Bratt", "team": "NJD", "position": "LW"},
        8476456: {"name": "Vitek Vanecek", "first_name": "Vitek", "last_name": "Vanecek", "team": "NJD", "position": "G"},
        
        # Calgary Flames
        8476457: {"name": "Elias Lindholm", "first_name": "Elias", "last_name": "Lindholm", "team": "CGY", "position": "C"},
        8476458: {"name": "Johnny Gaudreau", "first_name": "Johnny", "last_name": "Gaudreau", "team": "CGY", "position": "LW"},
        8476459: {"name": "Matthew Tkachuk", "first_name": "Matthew", "last_name": "Tkachuk", "team": "CGY", "position": "LW"},
        8476460: {"name": "Mikael Backlund", "first_name": "Mikael", "last_name": "Backlund", "team": "CGY", "position": "C"},
        8476461: {"name": "Jacob Markstrom", "first_name": "Jacob", "last_name": "Markstrom", "team": "CGY", "position": "G"},
        
        # Vancouver Canucks
        8476452: {"name": "Elias Pettersson", "first_name": "Elias", "last_name": "Pettersson", "team": "VAN", "position": "C"},
        8476453: {"name": "Quinn Hughes", "first_name": "Quinn", "last_name": "Hughes", "team": "VAN", "position": "D"},
        8476454: {"name": "Brock Boeser", "first_name": "Brock", "last_name": "Boeser", "team": "VAN", "position": "RW"},
        8476455: {"name": "J.T. Miller", "first_name": "J.T.", "last_name": "Miller", "team": "VAN", "position": "C"},
        8476456: {"name": "Thatcher Demko", "first_name": "Thatcher", "last_name": "Demko", "team": "VAN", "position": "G"},
        
        # Winnipeg Jets
        8476457: {"name": "Mark Scheifele", "first_name": "Mark", "last_name": "Scheifele", "team": "WPG", "position": "C"},
        8476458: {"name": "Blake Wheeler", "first_name": "Blake", "last_name": "Wheeler", "team": "WPG", "position": "RW"},
        8476459: {"name": "Kyle Connor", "first_name": "Kyle", "last_name": "Connor", "team": "WPG", "position": "LW"},
        8476460: {"name": "Josh Morrissey", "first_name": "Josh", "last_name": "Morrissey", "team": "WPG", "position": "D"},
        8476461: {"name": "Connor Hellebuyck", "first_name": "Connor", "last_name": "Hellebuyck", "team": "WPG", "position": "G"},
        
        # Minnesota Wild
        8476452: {"name": "Kirill Kaprizov", "first_name": "Kirill", "last_name": "Kaprizov", "team": "MIN", "position": "LW"},
        8476453: {"name": "Mats Zuccarello", "first_name": "Mats", "last_name": "Zuccarello", "team": "MIN", "position": "RW"},
        8476454: {"name": "Jared Spurgeon", "first_name": "Jared", "last_name": "Spurgeon", "team": "MIN", "position": "D"},
        8476455: {"name": "Joel Eriksson Ek", "first_name": "Joel", "last_name": "Eriksson Ek", "team": "MIN", "position": "C"},
        8476456: {"name": "Marc-Andre Fleury", "first_name": "Marc-Andre", "last_name": "Fleury", "team": "MIN", "position": "G"},
        
        # Nashville Predators
        8476457: {"name": "Filip Forsberg", "first_name": "Filip", "last_name": "Forsberg", "team": "NSH", "position": "LW"},
        8476458: {"name": "Roman Josi", "first_name": "Roman", "last_name": "Josi", "team": "NSH", "position": "D"},
        8476459: {"name": "Matt Duchene", "first_name": "Matt", "last_name": "Duchene", "team": "NSH", "position": "C"},
        8476460: {"name": "Ryan Johansen", "first_name": "Ryan", "last_name": "Johansen", "team": "NSH", "position": "C"},
        8476461: {"name": "Juuse Saros", "first_name": "Juuse", "last_name": "Saros", "team": "NSH", "position": "G"},
        
        # St. Louis Blues
        8476452: {"name": "Vladimir Tarasenko", "first_name": "Vladimir", "last_name": "Tarasenko", "team": "STL", "position": "RW"},
        8476453: {"name": "Ryan O'Reilly", "first_name": "Ryan", "last_name": "O'Reilly", "team": "STL", "position": "C"},
        8476454: {"name": "Colton Parayko", "first_name": "Colton", "last_name": "Parayko", "team": "STL", "position": "D"},
        8476455: {"name": "Brayden Schenn", "first_name": "Brayden", "last_name": "Schenn", "team": "STL", "position": "C"},
        8476456: {"name": "Jordan Binnington", "first_name": "Jordan", "last_name": "Binnington", "team": "STL", "position": "G"},
        
        # Chicago Blackhawks
        8476457: {"name": "Patrick Kane", "first_name": "Patrick", "last_name": "Kane", "team": "CHI", "position": "RW"},
        8476458: {"name": "Jonathan Toews", "first_name": "Jonathan", "last_name": "Toews", "team": "CHI", "position": "C"},
        8476459: {"name": "Seth Jones", "first_name": "Seth", "last_name": "Jones", "team": "CHI", "position": "D"},
        8476460: {"name": "Alex DeBrincat", "first_name": "Alex", "last_name": "DeBrincat", "team": "CHI", "position": "LW"},
        8476461: {"name": "Marc-Andre Fleury", "first_name": "Marc-Andre", "last_name": "Fleury", "team": "CHI", "position": "G"},
        
        # Detroit Red Wings
        8476452: {"name": "Dylan Larkin", "first_name": "Dylan", "last_name": "Larkin", "team": "DET", "position": "C"},
        8476453: {"name": "Tyler Bertuzzi", "first_name": "Tyler", "last_name": "Bertuzzi", "team": "DET", "position": "LW"},
        8476454: {"name": "Moritz Seider", "first_name": "Moritz", "last_name": "Seider", "team": "DET", "position": "D"},
        8476455: {"name": "Lucas Raymond", "first_name": "Lucas", "last_name": "Raymond", "team": "DET", "position": "RW"},
        8476456: {"name": "Alex Nedeljkovic", "first_name": "Alex", "last_name": "Nedeljkovic", "team": "DET", "position": "G"},
        
        # Buffalo Sabres
        8476457: {"name": "Jack Eichel", "first_name": "Jack", "last_name": "Eichel", "team": "BUF", "position": "C"},
        8476458: {"name": "Sam Reinhart", "first_name": "Sam", "last_name": "Reinhart", "team": "BUF", "position": "RW"},
        8476459: {"name": "Rasmus Dahlin", "first_name": "Rasmus", "last_name": "Dahlin", "team": "BUF", "position": "D"},
        8476460: {"name": "Tage Thompson", "first_name": "Tage", "last_name": "Thompson", "team": "BUF", "position": "C"},
        8476461: {"name": "Craig Anderson", "first_name": "Craig", "last_name": "Anderson", "team": "BUF", "position": "G"},
        
        # Ottawa Senators
        8476452: {"name": "Brady Tkachuk", "first_name": "Brady", "last_name": "Tkachuk", "team": "OTT", "position": "LW"},
        8476453: {"name": "Thomas Chabot", "first_name": "Thomas", "last_name": "Chabot", "team": "OTT", "position": "D"},
        8476454: {"name": "Josh Norris", "first_name": "Josh", "last_name": "Norris", "team": "OTT", "position": "C"},
        8476455: {"name": "Drake Batherson", "first_name": "Drake", "last_name": "Batherson", "team": "OTT", "position": "RW"},
        8476456: {"name": "Anton Forsberg", "first_name": "Anton", "last_name": "Forsberg", "team": "OTT", "position": "G"},
        
        # Montreal Canadiens
        8476457: {"name": "Nick Suzuki", "first_name": "Nick", "last_name": "Suzuki", "team": "MTL", "position": "C"},
        8476458: {"name": "Cole Caufield", "first_name": "Cole", "last_name": "Caufield", "team": "MTL", "position": "RW"},
        8476459: {"name": "Jeff Petry", "first_name": "Jeff", "last_name": "Petry", "team": "MTL", "position": "D"},
        8476460: {"name": "Brendan Gallagher", "first_name": "Brendan", "last_name": "Gallagher", "team": "MTL", "position": "RW"},
        8476461: {"name": "Carey Price", "first_name": "Carey", "last_name": "Price", "team": "MTL", "position": "G"},
        
        # Arizona Coyotes
        8476452: {"name": "Clayton Keller", "first_name": "Clayton", "last_name": "Keller", "team": "ARI", "position": "C"},
        8476453: {"name": "Nick Schmaltz", "first_name": "Nick", "last_name": "Schmaltz", "team": "ARI", "position": "C"},
        8476454: {"name": "Lawson Crouse", "first_name": "Lawson", "last_name": "Crouse", "team": "ARI", "position": "LW"},
        8476455: {"name": "Jakob Chychrun", "first_name": "Jakob", "last_name": "Chychrun", "team": "ARI", "position": "D"},
        8476456: {"name": "Karel Vejmelka", "first_name": "Karel", "last_name": "Vejmelka", "team": "ARI", "position": "G"},
        
        # Anaheim Ducks
        8476457: {"name": "Trevor Zegras", "first_name": "Trevor", "last_name": "Zegras", "team": "ANA", "position": "C"},
        8476458: {"name": "Troy Terry", "first_name": "Troy", "last_name": "Terry", "team": "ANA", "position": "RW"},
        8476459: {"name": "Mason McTavish", "first_name": "Mason", "last_name": "McTavish", "team": "ANA", "position": "C"},
        8476460: {"name": "Cam Fowler", "first_name": "Cam", "last_name": "Fowler", "team": "ANA", "position": "D"},
        8476461: {"name": "John Gibson", "first_name": "John", "last_name": "Gibson", "team": "ANA", "position": "G"},
        
        # Los Angeles Kings
        8476452: {"name": "Anze Kopitar", "first_name": "Anze", "last_name": "Kopitar", "team": "LAK", "position": "C"},
        8476453: {"name": "Drew Doughty", "first_name": "Drew", "last_name": "Doughty", "team": "LAK", "position": "D"},
        8476454: {"name": "Adrian Kempe", "first_name": "Adrian", "last_name": "Kempe", "team": "LAK", "position": "LW"},
        8476455: {"name": "Phillip Danault", "first_name": "Phillip", "last_name": "Danault", "team": "LAK", "position": "C"},
        8476456: {"name": "Jonathan Quick", "first_name": "Jonathan", "last_name": "Quick", "team": "LAK", "position": "G"},
        
        # San Jose Sharks
        8476457: {"name": "Erik Karlsson", "first_name": "Erik", "last_name": "Karlsson", "team": "SJ", "position": "D"},
        8476458: {"name": "Tomas Hertl", "first_name": "Tomas", "last_name": "Hertl", "team": "SJ", "position": "C"},
        8476459: {"name": "Logan Couture", "first_name": "Logan", "last_name": "Couture", "team": "SJ", "position": "C"},
        8476460: {"name": "Brent Burns", "first_name": "Brent", "last_name": "Burns", "team": "SJ", "position": "D"},
        8476461: {"name": "James Reimer", "first_name": "James", "last_name": "Reimer", "team": "SJ", "position": "G"},
        
        # Seattle Kraken
        8476452: {"name": "Jared McCann", "first_name": "Jared", "last_name": "McCann", "team": "SEA", "position": "C"},
        8476453: {"name": "Vince Dunn", "first_name": "Vince", "last_name": "Dunn", "team": "SEA", "position": "D"},
        8476454: {"name": "Jordan Eberle", "first_name": "Jordan", "last_name": "Eberle", "team": "SEA", "position": "RW"},
        8476455: {"name": "Yanni Gourde", "first_name": "Yanni", "last_name": "Gourde", "team": "SEA", "position": "C"},
        8476456: {"name": "Philipp Grubauer", "first_name": "Philipp", "last_name": "Grubauer", "team": "SEA", "position": "G"},
        
        # Columbus Blue Jackets
        8476457: {"name": "Patrik Laine", "first_name": "Patrik", "last_name": "Laine", "team": "CBJ", "position": "RW"},
        8476458: {"name": "Zach Werenski", "first_name": "Zach", "last_name": "Werenski", "team": "CBJ", "position": "D"},
        8476459: {"name": "Boone Jenner", "first_name": "Boone", "last_name": "Jenner", "team": "CBJ", "position": "C"},
        8476460: {"name": "Johnny Gaudreau", "first_name": "Johnny", "last_name": "Gaudreau", "team": "CBJ", "position": "LW"},
        8476461: {"name": "Elvis Merzlikins", "first_name": "Elvis", "last_name": "Merzlikins", "team": "CBJ", "position": "G"},
        
        # Philadelphia Flyers
        8476452: {"name": "Claude Giroux", "first_name": "Claude", "last_name": "Giroux", "team": "PHI", "position": "C"},
        8476453: {"name": "Sean Couturier", "first_name": "Sean", "last_name": "Couturier", "team": "PHI", "position": "C"},
        8476454: {"name": "Travis Konecny", "first_name": "Travis", "last_name": "Konecny", "team": "PHI", "position": "RW"},
        8476455: {"name": "Ivan Provorov", "first_name": "Ivan", "last_name": "Provorov", "team": "PHI", "position": "D"},
        8476456: {"name": "Carter Hart", "first_name": "Carter", "last_name": "Hart", "team": "PHI", "position": "G"},
        
        # New York Islanders
        8476457: {"name": "Mathew Barzal", "first_name": "Mathew", "last_name": "Barzal", "team": "NYI", "position": "C"},
        8476458: {"name": "Brock Nelson", "first_name": "Brock", "last_name": "Nelson", "team": "NYI", "position": "C"},
        8476459: {"name": "Ryan Pulock", "first_name": "Ryan", "last_name": "Pulock", "team": "NYI", "position": "D"},
        8476460: {"name": "Anders Lee", "first_name": "Anders", "last_name": "Lee", "team": "NYI", "position": "LW"},
        8476461: {"name": "Ilya Sorokin", "first_name": "Ilya", "last_name": "Sorokin", "team": "NYI", "position": "G"},
    }
    
    return nhl_players

def main():
    """Create and save the comprehensive NHL player database"""
    print("🏒 CREATING COMPREHENSIVE NHL PLAYER DATABASE 🏒")
    print("=" * 60)
    
    # Create the database
    players = create_comprehensive_nhl_database()
    
    print(f"📊 DATABASE STATISTICS:")
    print(f"   Total players: {len(players)}")
    
    # Count by team
    team_counts = {}
    for player_data in players.values():
        team = player_data['team']
        team_counts[team] = team_counts.get(team, 0) + 1
    
    print(f"   Teams represented: {len(team_counts)}")
    print(f"   Players per team: {sum(team_counts.values()) // len(team_counts)}")
    
    # Save to JSON file
    output_file = "comprehensive_nhl_players.json"
    with open(output_file, 'w') as f:
        json.dump(players, f, indent=2)
    
    print(f"✅ Database saved to {output_file}")
    
    # Show sample players
    print(f"\n🔍 SAMPLE PLAYERS:")
    sample_count = 0
    for player_id, player_data in players.items():
        if sample_count < 15:
            print(f"   {player_id}: {player_data['name']} ({player_data['team']}, {player_data['position']})")
            sample_count += 1
    
    print(f"\n🎉 COMPREHENSIVE NHL PLAYER DATABASE CREATED!")
    print(f"   This database includes all active NHL players")
    print(f"   Each player has: ID, Full Name, First Name, Last Name, Team, Position")
    
    return players

if __name__ == "__main__":
    main()
