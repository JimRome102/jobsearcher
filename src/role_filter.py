"""Role filter to only include Product Manager positions."""

def is_product_manager_role(title: str) -> bool:
    """
    Check if job title is a Product Manager role.

    Accepts:
    - Product Manager
    - Senior Product Manager
    - Principal Product Manager
    - Director of Product
    - VP Product
    - Chief Product Officer
    - Group Product Manager
    - Lead Product Manager

    Rejects:
    - Engineering roles (Software Engineer, etc.)
    - Design roles (Product Designer, etc.)
    - Marketing roles (Product Marketing, etc.)
    - Data roles (Data Scientist, etc.)
    - Technical Program Manager (TPM)
    - Any non-PM roles

    Args:
        title: Job title string

    Returns:
        True if it's a Product Manager role, False otherwise
    """
    if not title:
        return False

    title_lower = title.lower()

    # REJECT: Engineering roles (most common false positives)
    engineer_keywords = [
        'software engineer', 'engineer', 'engineering manager',
        'staff engineer', 'principal engineer', 'senior engineer',
        'backend', 'frontend', 'full stack', 'fullstack',
        'devops', 'sre', 'site reliability', 'infrastructure engineer',
        'data engineer', 'ml engineer', 'machine learning engineer',
        'solutions engineer', 'sales engineer', 'security engineer'
    ]

    for keyword in engineer_keywords:
        if keyword in title_lower:
            return False

    # REJECT: Design roles
    design_keywords = [
        'product designer', 'ux designer', 'ui designer',
        'design', 'creative', 'visual designer'
    ]

    for keyword in design_keywords:
        if keyword in title_lower:
            return False

    # REJECT: Marketing roles
    marketing_keywords = [
        'product marketing', 'marketing manager', 'growth marketing',
        'marketing', 'brand manager', 'communications'
    ]

    for keyword in marketing_keywords:
        if keyword in title_lower:
            return False

    # REJECT: Data/Analytics roles
    data_keywords = [
        'data scientist', 'data analyst', 'analytics manager',
        'business intelligence', 'data manager'
    ]

    for keyword in data_keywords:
        if keyword in title_lower:
            return False

    # REJECT: Technical Program Manager (TPM)
    if 'technical program manager' in title_lower or 'tpm' in title_lower:
        return False

    # REJECT: Other non-PM roles
    other_rejects = [
        'recruiter', 'talent', 'operations', 'customer success',
        'account manager', 'project manager', 'program manager',
        'scrum master', 'agile coach', 'delivery manager'
    ]

    for keyword in other_rejects:
        if keyword in title_lower:
            return False

    # ACCEPT: Product Manager roles
    # Must contain "product" AND one of these management keywords
    if 'product' not in title_lower:
        return False

    pm_keywords = [
        'product manager',
        'product management',
        'senior product',
        'principal product',
        'staff product',
        'director of product',
        'director, product',
        'vp product',
        'vp of product',
        'vice president product',
        'head of product',
        'chief product officer',
        'cpo',
        'group product manager',
        'group pm',
        'lead product manager',
        'lead pm',
        'product lead',
        'product owner'  # Sometimes used for PM roles
    ]

    for keyword in pm_keywords:
        if keyword in title_lower:
            return True

    # If we get here, it has "product" but not clear PM keywords
    # Likely a false positive (Product Designer, Product Marketing, etc.)
    return False


def get_role_seniority_level(title: str) -> str:
    """
    Determine seniority level of a Product Manager role.

    Returns:
        One of: 'C-Suite', 'VP', 'Director', 'Principal', 'Senior', 'Mid-Level', 'Unknown'
    """
    if not title or not is_product_manager_role(title):
        return 'Unknown'

    title_lower = title.lower()

    # C-Suite
    if any(keyword in title_lower for keyword in ['chief product officer', 'cpo']):
        return 'C-Suite'

    # VP level
    if any(keyword in title_lower for keyword in ['vp product', 'vp of product', 'vice president']):
        return 'VP'

    # Director level
    if any(keyword in title_lower for keyword in ['director', 'head of product']):
        return 'Director'

    # Principal level
    if any(keyword in title_lower for keyword in ['principal', 'staff product']):
        return 'Principal'

    # Senior level
    if any(keyword in title_lower for keyword in ['senior', 'sr.', 'sr ', 'lead product']):
        return 'Senior'

    # Group PM (typically senior level)
    if 'group product manager' in title_lower or 'group pm' in title_lower:
        return 'Senior'

    # Everything else is mid-level or unclear
    return 'Mid-Level'


def meets_seniority_requirement(title: str, min_level: str = 'Senior') -> bool:
    """
    Check if job meets minimum seniority level.

    Args:
        title: Job title
        min_level: Minimum acceptable level (default: 'Senior')

    Returns:
        True if meets or exceeds minimum level
    """
    seniority_hierarchy = {
        'C-Suite': 6,
        'VP': 5,
        'Director': 4,
        'Principal': 3,
        'Senior': 2,
        'Mid-Level': 1,
        'Unknown': 0
    }

    job_level = get_role_seniority_level(title)
    min_level_score = seniority_hierarchy.get(min_level, 2)
    job_level_score = seniority_hierarchy.get(job_level, 0)

    return job_level_score >= min_level_score
