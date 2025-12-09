from dataclasses import dataclass, field
from typing import Dict, Optional, Any
import uuid

@dataclass
class CandidateRecord:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ''
    phone: str = ''
    email: str = ''
    designation: str = ''
    department: str = ''
    contact_date: str = ''  # YYYY-MM-DD
    original_data: Dict[str, Any] = field(default_factory=dict)
    source_file: str = ''
    normalized_phone: str = ''
    normalized_email: str = ''

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CandidateRecord':
        return cls(
            name=data.get('name', ''),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            designation=data.get('designation', ''),
            department=data.get('department', ''),
            contact_date=data.get('contact_date', ''),
            original_data=data,
            source_file=data.get('source_file', ''),
            normalized_phone=data.get('normalized_phone', ''),
            normalized_email=data.get('normalized_email', '')
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'designation': self.designation,
            'department': self.department,
            'contact_date': self.contact_date,
            'original_data': self.original_data,
            'source_file': self.source_file,
            'normalized_phone': self.normalized_phone,
            'normalized_email': self.normalized_email
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CandidateRecord):
            return False
        return self.to_dict() == other.to_dict()