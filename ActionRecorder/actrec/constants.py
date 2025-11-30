# region Constants
# Icon constants
ICON_BLANK1 = 101  # Global NONE icon
ICON_MESH_PLANE = 286  # Local NONE icon
ICON_NONE = "NONE"

# Event types
EVENT_PREFIX = "ar.event:"
EVENT_TIMER = "Timer"
EVENT_RENDER_COMPLETE = "Render Complete"
EVENT_LOOP = "Loop"
EVENT_END_LOOP = "EndLoop"
EVENT_SELECT_OBJECT = "Select Object"
EVENT_RUN_SCRIPT = "Run Script"
EVENT_CLIPBOARD = "Clipboard"

# Operation prefixes
OP_BPY_OPS = "bpy.ops."
OP_BPY_CONTEXT = "bpy.context."

# UI strings
UI_CATEGORY = "Action Recorder"
UI_LOCAL_ACTIONS = "Local Actions"
UI_MACRO_EDITOR = "Macro Editor"
UI_GLOBAL_ACTIONS = "Global Actions"
UI_ADVANCED = "Advanced"
UI_HELP = "Help"

# File extensions and paths
FILE_JSON = ".json"
FILE_ZIP = ".zip"
STORAGE_FILE = "Storage.json"
ICONS_DIR = "Icons"

# Execution contexts
EXEC_DEFAULT = "EXEC_DEFAULT"
EXEC_INVOKE = "INVOKE_DEFAULT"

# Loop statement types
LOOP_STATEMENT_REPEAT = "repeat"
LOOP_STATEMENT_PYTHON = "python"

# Default values
DEFAULT_ICON = 0
DEFAULT_TIMEOUT = 1.0
DEFAULT_REPEAT_COUNT = 1
DEFAULT_WIDTH = 500

# UI layout constants
UI_UNITS_X = 0.5
UI_ORDER_OFFSET = 1
UI_LIST_ROWS = 4

# Blender API constants
BL_OPTIONS_REGISTER = 'REGISTER'
BL_OPTIONS_UNDO = 'UNDO'
BL_OPTIONS_INTERNAL = 'INTERNAL'

# Error messages
ERR_NO_ACTION_FOUND = "No action found"
ERR_MACRO_NOT_FOUND = "Macro not found"
ERR_INVALID_COMMAND = "Invalid command"
ERR_ALREADY_PLAYING = "Action is already playing"

# endregion
