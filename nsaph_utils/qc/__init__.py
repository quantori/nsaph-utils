from .tester import Tester

## handle log set up. the nsaph_utils.qc logger made here can be used to control all logging for all qc
import logging

logger = logging.getLogger(__name__)
del logging