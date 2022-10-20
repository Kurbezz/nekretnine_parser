from .base import BaseParser
from .halooglasi import HalooglasiParser
from .sasomange import SasomangleParser
from .oglasi import OglasiParser
from .imovina import ImovinaParser
from .fzida import FzidaParser


PARSERS: list[BaseParser] = [
    HalooglasiParser,
    SasomangleParser,
    OglasiParser,
    ImovinaParser,
    FzidaParser
]
