"""
Readable 6-character household join codes.

Must stay in sync with iOS `HouseholdCode` and the landing page JS alphabet.
"""

from __future__ import annotations

import secrets

# No 0/O, 1/l/I — easy to read aloud and type.
HOUSEHOLD_CODE_ALPHABET = "abcdefghjkmnpqrtuvwxyz23456789"
HOUSEHOLD_CODE_LENGTH = 6
_MAX_ATTEMPTS = 64


def normalize_household_code(raw: str) -> str:
    return raw.strip().lower()


def is_valid_household_code(code: str) -> bool:
    if len(code) != HOUSEHOLD_CODE_LENGTH:
        return False
    alphabet = frozenset(HOUSEHOLD_CODE_ALPHABET)
    return all(c in alphabet for c in code)


def generate_candidate_code() -> str:
    return "".join(
        secrets.choice(HOUSEHOLD_CODE_ALPHABET) for _ in range(HOUSEHOLD_CODE_LENGTH)
    )


def generate_unique_household_code(*, model) -> str:
    """
    model: Household model class (avoid circular import at module load).
    """
    for _ in range(_MAX_ATTEMPTS):
        candidate = generate_candidate_code()
        if not model.objects.filter(code=candidate).exists():
            return candidate
    raise RuntimeError("Could not allocate a unique household code")
