from dataclasses import dataclass, field
from typing import List, Optional
from .candidate_record import CandidateRecord

@dataclass
class DuplicateGroup:
    group_id: str
    matching_key: str
    key_type: str  # "phone", "email", or "both"
    records: List[CandidateRecord] = field(default_factory=list)
    merged_record: Optional[CandidateRecord] = None
    merge_status: str = 'unreviewed'

    def add_record(self, record: CandidateRecord) -> None:
        self.records.append(record)

    def get_conflicting_fields(self) -> List[str]:
        if not self.records:
            return []
        fields = ['name', 'phone', 'email', 'designation', 'department', 'contact_date']
        conflicts = []
        for field_name in fields:
            values = {getattr(r, field_name) for r in self.records}
            if len(values) > 1:
                conflicts.append(field_name)
        return conflicts

    def is_identical(self) -> bool:
        if not self.records:
            return True
        first = self.records[0]
        return all(r == first for r in self.records)