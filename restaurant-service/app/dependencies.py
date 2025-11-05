import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from shared.auth import get_current_user, require_role

# Re-export shared dependencies - these will be used directly in routes

