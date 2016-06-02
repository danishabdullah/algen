from __future__ import print_function, unicode_literals
import logging

__author__ = "danishabdullah"

LOG = logging.getLogger("algen")
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
LOG.addHandler(ch)
LOG.setLevel(logging.ERROR)

