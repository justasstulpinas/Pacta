import enum

# pagalbinis modelis kuris padeda isvengti typos ir padeda greicaiu ir saugiau keisti koda ateityje,
#  nes kiekvienas zpdis programoje yra saugomas kaip kintamsis o ne stringas
class TemplateStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class SubmissionStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


ContractTemplateStatus = TemplateStatus
FilledContractStatus = SubmissionStatus
