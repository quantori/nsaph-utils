from .interface import interpolate, IMPLEMENTED_METHODS

## handle log set up. the nsaph_utils.interpolation logger made here can be used to control all logging for all interpolation
import logging

logger = logging.getLogger(__name__)
del logging
