"""
Repository cloning functionality for GEO-INFER-GIT.

This module provides functionality to clone GitHub repositories
using Git commands with various options.
"""

import os
import subprocess
import logging
import shutil
from typing import Dict, Any, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import time
import psutil

from ..utils.config_loader import load_clone_config

logger = logging.getLogger(__name__) 