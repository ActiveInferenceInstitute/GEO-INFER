"""SQL identifier validation for GEO-INFER-DATA.

Single trust boundary for every identifier that is interpolated into a
generated SQL or GraphQL statement. Values that fail the pattern are
rejected with :class:`ValueError`; they are never escaped or mangled,
because escaping identifiers is how injection bugs survive.
"""

import re
from typing import Any

# Unquoted SQL identifier: starts with a letter or underscore, then
# letters/digits/underscores, at most 63 characters (PostgreSQL's NAMEDATALEN
# budget leaves room for generated prefixes such as ``idx_..._geom``).
_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,62}$")

_MAX_IDENTIFIER_LEN = 63


def validate_sql_identifier(name: Any) -> str:
    """Validate ``name`` as a safe SQL/GraphQL identifier and return it.

    The accepted pattern is ``^[A-Za-z_][A-Za-z0-9_]{0,62}$``. Anything
    else — quotes, semicolons, whitespace, path separators, comments,
    non-string values, or names longer than 63 characters — raises
    :class:`ValueError`. Call this on every user-influenced identifier
    immediately before it is interpolated into a statement, and only
    after any internal transform (e.g. ``title -> table_name``) has run.

    Args:
        name: Candidate identifier (must be ``str``).

    Returns:
        The identifier unchanged, so callers can interpolate it directly.

    Raises:
        ValueError: If ``name`` is not a string or does not match the
            identifier pattern.
    """
    if not isinstance(name, str):
        raise ValueError(
            f"SQL identifier must be a string, got {type(name).__name__}"
        )
    if not _IDENTIFIER_RE.match(name):
        raise ValueError(
            f"Invalid SQL identifier {name!r}: must match "
            f"^[A-Za-z_][A-Za-z0-9_]{{0,{_MAX_IDENTIFIER_LEN - 1}}}$"
        )
    return name
