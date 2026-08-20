import enum

# pagalbinis modelis kuris padeda isvengti typos ir padeda greicaiu ir saugiau keisti koda ateityje,
#  nes kiekvienas zpdis programoje yra saugomas kaip kintamsis o ne stringas
class TemplateStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class SubmissionStatus(str, enum.Enum):
    # Legacy statuses (FilledContract)
    SUBMITTED = "submitted"
    CONFIRMED = "confirmed"
    # Shared statuses
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    # New secure submission statuses
    PENDING  = "pending"   # created, awaiting client signing
    SIGNED   = "signed"    # client signed, owner not yet downloaded
    DECLINED = "declined"  # client declined
    EXPIRED  = "expired"   # TTL elapsed without signing


ContractTemplateStatus = TemplateStatus
FilledContractStatus = SubmissionStatus
