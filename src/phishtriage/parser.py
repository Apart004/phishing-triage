from email import policy
from email.parser import BytesParser
from email.utils import parseaddr

from phishtriage.models import EmailAddress, HeaderFlag, ParsedEmail


def _to_address(value: object) -> EmailAddress | None:
    """Turn a raw header value into an EmailAddress, or None if absent/empty."""
    if not value:
        return None
    name, addr = parseaddr(str(value))
    if not addr:  # e.g. Return-Path: <> on bounce messages
        return None
    return EmailAddress(display_name=name, address=addr.lower())


def detect_mismatches(parsed: ParsedEmail) -> list[HeaderFlag]:
    """Compare identity headers and flag domain mismatches."""
    flags: list[HeaderFlag] = []
    from_ = parsed.from_addr
    if from_ is None:
        return flags

    if parsed.reply_to and parsed.reply_to.domain != from_.domain:
        flags.append(HeaderFlag(
            code="REPLY_TO_MISMATCH",
            description=f"Reply-To domain '{parsed.reply_to.domain}' differs from From domain '{from_.domain}'",
        ))
    if parsed.return_path and parsed.return_path.domain != from_.domain:
        flags.append(HeaderFlag(
            code="RETURN_PATH_MISMATCH",
            description=f"Return-Path domain '{parsed.return_path.domain}' differs from From domain '{from_.domain}'",
        ))
    return flags


def parse_eml(raw: bytes) -> ParsedEmail:
    """Parse raw .eml bytes into a ParsedEmail. No network calls."""
    msg = BytesParser(policy=policy.default).parsebytes(raw)
    parsed = ParsedEmail(
        from_addr=_to_address(msg["From"]),
        reply_to=_to_address(msg["Reply-To"]),
        return_path=_to_address(msg["Return-Path"]),
        subject=str(msg["Subject"] or ""),
        message_id=str(msg["Message-ID"] or ""),
    )
    parsed.flags = detect_mismatches(parsed)
    return parsed
