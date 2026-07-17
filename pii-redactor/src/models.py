from dataclasses import dataclass
from typing import Optional

@dataclass
class TextSpan:
    text: str
    source: str          # "paragraph" | "table" | "header_footer"
    paragraph_idx: int
    run_idx: int
    run_ref: object      # python-docx Run
    table_idx: int = -1
    row_idx: int = -1
    col_idx: int = -1
    forced_label: Optional[str] = None

@dataclass
class Entity:
    text: str
    label: str
    start: int
    end: int
    score: float
    source: str
    paragraph_idx: int = -1
    run_idx: int = -1
    sources: list[str] = None
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = [self.source]
