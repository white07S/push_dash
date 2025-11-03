"""Taxonomy utilities for NFR taxonomy processing."""
from typing import List, Optional, Set

def normalize_taxonomy(taxonomy_str: Optional[str]) -> str:
    """Normalize NFR taxonomy string.

    Args:
        taxonomy_str: Raw taxonomy string (pipe-delimited)

    Returns:
        Normalized taxonomy string
    """
    if not taxonomy_str:
        return ''

    # Split by pipe, trim whitespace, normalize case (title case)
    tokens = [token.strip().title() for token in taxonomy_str.split('|') if token.strip()]

    # Remove duplicates while preserving order
    seen = set()
    unique_tokens = []
    for token in tokens:
        if token not in seen:
            seen.add(token)
            unique_tokens.append(token)

    return '|'.join(unique_tokens)

def parse_taxonomy(taxonomy_str: str) -> List[str]:
    """Parse taxonomy string into list of tokens.

    Args:
        taxonomy_str: Normalized taxonomy string

    Returns:
        List of taxonomy tokens
    """
    if not taxonomy_str:
        return []

    return [token.strip() for token in taxonomy_str.split('|') if token.strip()]

def validate_taxonomy(taxonomy_str: str, valid_tokens: Optional[Set[str]] = None) -> tuple[bool, str]:
    """Validate taxonomy string.

    Args:
        taxonomy_str: Taxonomy string to validate
        valid_tokens: Optional set of valid tokens

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not taxonomy_str:
        return True, ""

    tokens = parse_taxonomy(taxonomy_str)

    if not tokens:
        return False, "Empty taxonomy after parsing"

    if valid_tokens:
        invalid = [token for token in tokens if token not in valid_tokens]
        if invalid:
            return False, f"Invalid tokens: {', '.join(invalid)}"

    return True, ""

def merge_taxonomies(*taxonomies: str) -> str:
    """Merge multiple taxonomy strings.

    Args:
        *taxonomies: Variable number of taxonomy strings

    Returns:
        Merged and normalized taxonomy string
    """
    all_tokens = []
    for taxonomy in taxonomies:
        if taxonomy:
            all_tokens.extend(parse_taxonomy(taxonomy))

    return normalize_taxonomy('|'.join(all_tokens))

def compare_taxonomies(tax1: str, tax2: str) -> dict:
    """Compare two taxonomy strings.

    Args:
        tax1: First taxonomy string
        tax2: Second taxonomy string

    Returns:
        Dictionary with comparison results
    """
    tokens1 = set(parse_taxonomy(tax1))
    tokens2 = set(parse_taxonomy(tax2))

    return {
        'common': list(tokens1 & tokens2),
        'only_in_first': list(tokens1 - tokens2),
        'only_in_second': list(tokens2 - tokens1),
        'all_unique': list(tokens1 | tokens2),
        'similarity': len(tokens1 & tokens2) / max(1, len(tokens1 | tokens2))
    }