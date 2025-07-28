import base64
import json
from dataclasses import asdict, dataclass
from uuid import UUID


@dataclass
class Cursor:
	last_id: UUID

	def to_b64(self) -> str:
		cursor_dict = asdict(self)
		cursor_json = json.dumps(cursor_dict)
		return base64.urlsafe_b64encode(cursor_json.encode()).decode()

	@classmethod
	def from_b64(cls, cursor_str: str) -> "Cursor":
		cursor_json = base64.urlsafe_b64decode(cursor_str.encode()).decode()
		cursor_dict = json.loads(cursor_json)
		return cls(**cursor_dict)
