from pydantic import BaseModel, Field


class EmailAddress(BaseModel):
    display_name: str = ""
    address: str = ""

    @property
    def domain(self) -> str:
        return self.address.rpartition("@")[2].lower()


class HeaderFlag(BaseModel):
    code: str          # machine-readable, e.g. "REPLY_TO_MISMATCH"
    description: str   # human-readable, goes into the report


class ParsedEmail(BaseModel):
    from_addr: EmailAddress | None = None
    reply_to: EmailAddress | None = None
    return_path: EmailAddress | None = None
    subject: str = ""
    message_id: str = ""
    flags: list[HeaderFlag] = Field(default_factory=list)
