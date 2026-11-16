from pathlib import Path

from phishtriage.parser import parse_eml

SAMPLES = Path(__file__).parent.parent / "samples"


def test_credential_harvest_headers_and_flags():
    parsed = parse_eml((SAMPLES / "credential_harvest.eml").read_bytes())

    assert parsed.from_addr.address == "helpdesk@victim-corp.example"
    assert parsed.from_addr.display_name == "IT Helpdesk"
    assert parsed.subject == "Action required: password expires today"
    assert parsed.message_id == "<20261109091402.9F3A1@mailer.example.net>"

    codes = {f.code for f in parsed.flags}
    assert codes == {"REPLY_TO_MISMATCH", "RETURN_PATH_MISMATCH"}


def test_no_flags_when_domains_match():
    raw = (
        b"From: a@corp.example\r\nReply-To: b@corp.example\r\n"
        b"Return-Path: <a@corp.example>\r\nSubject: hi\r\n\r\nbody"
    )
    assert parse_eml(raw).flags == []
