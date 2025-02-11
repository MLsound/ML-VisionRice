# __init__.py (Recommended: Import specific functions)
from .utils import security, file_management, format, visualization, performance  # . is important

# __init__.py (Alternative: Import submodules - useful for larger packages)
# from . import utils  # Then users would use my_library.utils.my_utility_function