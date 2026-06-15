"""Parse an American consumer/business name into components.

Primary engine: ``probablepeople`` which both tags name parts AND classifies
the string as a Person, Household, or Corporation (business). Falls back to
``nameparser`` for person names if probablepeople is unavailable.
"""
from __future__ import annotations

from ..models import ParsedName

try:
    import probablepeople as pp

    _HAS_PP = True
except Exception:  # pragma: no cover
    _HAS_PP = False

try:
    from nameparser import HumanName

    _HAS_NAMEPARSER = True
except Exception:  # pragma: no cover
    _HAS_NAMEPARSER = False


# probablepeople tag -> our person field
_PERSON_MAP = {
    "PrefixMarital": "prefix",
    "PrefixOther": "prefix",
    "GivenName": "first",
    "FirstInitial": "first",
    "MiddleName": "middle",
    "MiddleInitial": "middle",
    "Surname": "last",
    "LastInitial": "last",
    "SuffixGenerational": "suffix",
    "SuffixOther": "suffix",
    "Nickname": "nickname",
}

# Tags that indicate a corporation / business when probablepeople tags them
_CORP_TYPE = {"Corporation"}
_HOUSEHOLD_TYPE = {"Household"}

# A small keyword net to catch obvious businesses even if the classifier misses.
_BUSINESS_KEYWORDS = {
    "llc", "inc", "incorporated", "corp", "corporation", "co", "company",
    "ltd", "limited", "lp", "llp", "plc", "pllc", "group", "holdings",
    "enterprises", "industries", "services", "solutions", "associates",
    "partners", "trust", "foundation", "bank", "insurance", "realty",
    "restaurant", "plumbing", "electric", "supply", "store", "shop",
    "&", "and sons", "the",
}


def _looks_like_business(name: str) -> bool:
    tokens = {t.strip(".,").lower() for t in name.split()}
    return bool(tokens & _BUSINESS_KEYWORDS)


def _collapse(tags: dict) -> dict:
    """probablepeople returns an OrderedDict tag->value already collapsed."""
    return dict(tags)


def parse_name(raw: str) -> ParsedName:
    raw = (raw or "").strip()
    if not raw:
        return ParsedName(entity_type="unknown", is_business=False, raw=raw)

    if _HAS_PP:
        try:
            tags, label = pp.tag(raw)
            components = _collapse(tags)

            if label in _CORP_TYPE or (label != "Person" and _looks_like_business(raw)):
                return ParsedName(
                    entity_type="business",
                    is_business=True,
                    business_name=raw,
                    raw=raw,
                    confidence=0.9,
                    components=components,
                )

            if label in _HOUSEHOLD_TYPE:
                result = _person_from_pp(components, raw)
                result.entity_type = "household"
                return result

            # Person
            result = _person_from_pp(components, raw)
            # Defensive: classifier sometimes mislabels obvious businesses
            if result.first is None and result.last is None and _looks_like_business(raw):
                return ParsedName(
                    entity_type="business",
                    is_business=True,
                    business_name=raw,
                    raw=raw,
                    confidence=0.6,
                    components=components,
                )
            return result
        except Exception:
            pass  # fall through to nameparser

    # Fallback path
    if _looks_like_business(raw):
        return ParsedName(
            entity_type="business",
            is_business=True,
            business_name=raw,
            raw=raw,
            confidence=0.5,
        )
    return _person_from_nameparser(raw)


def _person_from_pp(components: dict, raw: str) -> ParsedName:
    out = {target: None for target in set(_PERSON_MAP.values())}
    for tag, value in components.items():
        field = _PERSON_MAP.get(tag)
        if field:
            out[field] = (f"{out[field]} {value}".strip() if out[field] else value)
    return ParsedName(
        entity_type="person",
        is_business=False,
        prefix=out.get("prefix"),
        first=out.get("first"),
        middle=out.get("middle"),
        last=out.get("last"),
        suffix=out.get("suffix"),
        nickname=out.get("nickname"),
        raw=raw,
        confidence=0.85,
        components=components,
    )


def _person_from_nameparser(raw: str) -> ParsedName:
    if not _HAS_NAMEPARSER:
        # Minimal whitespace split as last resort
        parts = raw.split()
        first = parts[0] if parts else None
        last = parts[-1] if len(parts) > 1 else None
        middle = " ".join(parts[1:-1]) if len(parts) > 2 else None
        return ParsedName(
            entity_type="person", is_business=False,
            first=first, middle=middle, last=last, raw=raw, confidence=0.3,
        )
    hn = HumanName(raw)
    return ParsedName(
        entity_type="person",
        is_business=False,
        prefix=hn.title or None,
        first=hn.first or None,
        middle=hn.middle or None,
        last=hn.last or None,
        suffix=hn.suffix or None,
        nickname=hn.nickname or None,
        raw=raw,
        confidence=0.6,
        components={k: v for k, v in hn.as_dict().items() if v},
    )
