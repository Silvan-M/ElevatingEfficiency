# This is the __init__ file for the policies package.
# It is used to import all policies to the main file.
#
# Usage: from policies import {PolicyName}

from .policy import Policy, Action
from .scan_policy import SCANPolicy
from .fcfs_policy import FCFSPolicy
from .look_policy import LOOKPolicy