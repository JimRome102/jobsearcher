"""Location filter for Manhattan, Bronx, or Remote jobs with Midtown preference."""

def is_midtown_manhattan(location: str) -> bool:
    """
    Check if location is in Midtown Manhattan (near Grand Central).

    Midtown defined as roughly 15-minute walk from Grand Central Terminal:
    - East-West: 3rd Ave to 8th Ave
    - North-South: 34th St to 59th St

    Args:
        location: Job location string

    Returns:
        True if location appears to be in Midtown Manhattan
    """
    if not location:
        return False

    location_lower = location.lower()

    # Midtown neighborhood keywords
    midtown_keywords = [
        'midtown', 'grand central', 'times square', 'bryant park',
        'rockefeller', 'radio city', 'madison avenue', 'fifth avenue',
        'park avenue', 'lexington avenue', 'vanderbilt', 'murray hill',
        'turtle bay', 'herald square', 'penn station', 'garment district'
    ]

    # Midtown street ranges (rough approximation)
    midtown_streets = [
        '34th', '35th', '36th', '37th', '38th', '39th', '40th',
        '41st', '42nd', '43rd', '44th', '45th', '46th', '47th',
        '48th', '49th', '50th', '51st', '52nd', '53rd', '54th',
        '55th', '56th', '57th', '58th', '59th'
    ]

    # Check for Midtown keywords
    if any(keyword in location_lower for keyword in midtown_keywords):
        return True

    # Check for street numbers in Midtown range
    if any(street in location_lower for street in midtown_streets):
        # Make sure it also mentions Manhattan/NYC to avoid false positives
        if any(word in location_lower for word in ['manhattan', 'nyc', 'new york']):
            return True

    return False


def matches_location_preference(location: str) -> bool:
    """
    Check if a job location matches Manhattan, Bronx, or Remote.

    Allowed locations:
    - Manhattan (all neighborhoods)
    - Bronx
    - Remote/WFH

    NOT allowed:
    - Brooklyn
    - Queens
    - Staten Island
    - Other boroughs

    Args:
        location: Job location string

    Returns:
        True if location matches preferences, False otherwise
    """
    if not location:
        return False

    location_lower = location.lower()

    # Remote keywords (always accepted)
    remote_keywords = ['remote', 'work from home', 'wfh', 'anywhere', 'distributed']
    if any(keyword in location_lower for keyword in remote_keywords):
        return True

    # Manhattan keywords
    manhattan_keywords = [
        'manhattan', 'midtown', 'downtown', 'uptown',
        'lower manhattan', 'upper east side', 'upper west side',
        'east village', 'west village', 'soho', 'tribeca', 'financial district',
        'chelsea', 'gramercy', 'murray hill', 'kips bay', 'flatiron',
        'union square', 'madison square', 'times square', 'grand central',
        'columbus circle', 'lincoln center', 'herald square'
    ]
    if any(keyword in location_lower for keyword in manhattan_keywords):
        return True

    # Bronx keywords
    bronx_keywords = ['bronx', 'fordham', 'riverdale', 'mott haven']
    if any(keyword in location_lower for keyword in bronx_keywords):
        return True

    # Generic "New York, NY" or "NYC" - need to check it's NOT other boroughs
    if 'new york' in location_lower or 'nyc' in location_lower or 'ny, ny' in location_lower:
        # Exclude if it mentions other boroughs
        excluded_boroughs = ['brooklyn', 'queens', 'staten island']
        if not any(borough in location_lower for borough in excluded_boroughs):
            # It's probably Manhattan (most "NYC" jobs are in Manhattan)
            return True

    return False


def get_location_score(location: str) -> int:
    """
    Score a location for sorting preference.

    Higher score = better location preference
    - Midtown Manhattan: 100
    - Other Manhattan: 80
    - Bronx: 60
    - Remote: 50

    Args:
        location: Job location string

    Returns:
        Score from 0-100
    """
    if not location or not matches_location_preference(location):
        return 0

    location_lower = location.lower()

    # Check for Midtown first (highest preference)
    if is_midtown_manhattan(location):
        return 100

    # Other Manhattan locations
    manhattan_keywords = ['manhattan', 'downtown', 'uptown', 'lower manhattan',
                         'upper east', 'upper west', 'village', 'soho', 'tribeca']
    if any(keyword in location_lower for keyword in manhattan_keywords):
        return 80

    # Bronx
    if 'bronx' in location_lower:
        return 60

    # Remote
    if any(keyword in location_lower for keyword in ['remote', 'work from home', 'wfh']):
        return 50

    # Generic NYC (assume Manhattan)
    if 'new york' in location_lower or 'nyc' in location_lower:
        return 75

    return 0
