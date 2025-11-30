# region Imports
import json
import uuid
from typing import TYPE_CHECKING

# blender modules
import bpy
from bpy.types import Context

# relative imports
from .. import constants
from ..functions.shared import get_preferences
if TYPE_CHECKING:
    from ..properties.shared import AR_action
# endregion


def is_event_macro(command: str) -> bool:
    """Check if command is an event macro"""
    return command.startswith(constants.EVENT_PREFIX[:-1])


def parse_event_data(command: str) -> dict:
    """Parse event data from command string"""
    split = command.split(":")
    if len(split) < 2:
        return {}
    return json.loads(":".join(split[1:]))


def create_macro_id() -> str:
    """Create unique macro ID"""
    return str(uuid.uuid1())


def validate_macro_command(command: str) -> tuple[bool, str]:
    """Validate macro command and return (is_valid, error_message)"""
    if not command:
        return False, "Command is empty"

    if command.startswith("bpy.ops.ar.local_play"):
        # Check for recursion prevention
        from ..functions.shared import extract_properties
        props = extract_properties(command.split("(")[1][:-1])
        if set(props) == {"id=\"\"", "index=-1"}:
            return False, "Don't run Local Play with default properties, this may cause recursion"

    return True, ""


def prepare_operator_command(command: str, execution_context: str) -> str:
    """Prepare operator command for execution"""
    if command.startswith(constants.OP_BPY_OPS):
        split = command.split("(")
        return "%s(\"%s\", %s" % (
            split[0],
            execution_context,
            "(".join(split[1:]))
    return command


def prepare_context_command(command: str) -> str:
    """Prepare context command for execution"""
    if command.startswith(constants.OP_BPY_CONTEXT):
        return command.replace(constants.OP_BPY_CONTEXT, "context.")
    return command


def filter_active_macros(macros) -> list:
    """Filter only active macros from collection"""
    return [macro for macro in macros if macro.active]


def save_action_to_scene(ActRec_pref, scene) -> None:
    """Save local actions to scene"""
    from ..functions.shared import property_to_python
    scene.ar.local = json.dumps(property_to_python(ActRec_pref.local_actions))


def get_macro_by_id(action, macro_id: str):
    """Get macro by ID from action"""
    for macro in action.macros:
        if macro.id == macro_id:
            return macro
    return None


def count_active_macros(macros) -> int:
    """Count active macros in collection"""
    return sum(1 for macro in macros if macro.active)


def validate_action_playback(action) -> tuple[bool, str]:
    """Validate if action can be played"""
    if action.is_playing:
        return False, constants.ERR_ALREADY_PLAYING

    active_macros = count_active_macros(action.macros)
    if active_macros == 0:
        return False, "No active macros to play"

    return True, ""
