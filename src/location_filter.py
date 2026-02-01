"""Location filter to only include NYC, Westchester, or Remote jobs."""

def matches_location_preference(location: str) -> bool:
    """
    Check if a job location matches NYC, Westchester County, or Remote.

    Args:
        location: Job location string

    Returns:
        True if location matches preferences, False otherwise
    """
    if not location:
        return False

    location_lower = location.lower()

    # Remote keywords
    remote_keywords = ['remote', 'work from home', 'wfh', 'anywhere']
    if any(keyword in location_lower for keyword in remote_keywords):
        return True

    # NYC keywords
    nyc_keywords = [
        'new york', 'nyc', 'new york city', 'manhattan', 'brooklyn',
        'queens', 'bronx', 'staten island', 'ny, ny'
    ]
    if any(keyword in location_lower for keyword in nyc_keywords):
        return True

    # Westchester County keywords
    westchester_keywords = [
        'westchester', 'white plains', 'yonkers', 'new rochelle',
        'mount vernon', 'scarsdale', 'rye', 'port chester', 'harrison',
        'mamaroneck', 'larchmont', 'pelham', 'tarrytown', 'dobbs ferry'
    ]
    if any(keyword in location_lower for keyword in westchester_keywords):
        return True

    return False
