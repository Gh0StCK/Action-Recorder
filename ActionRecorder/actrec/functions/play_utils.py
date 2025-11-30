# region Imports
from typing import Optional, Union, Dict, Any, List
import json
import functools
from contextlib import suppress
import traceback
import sys

# blender modules
import bpy
from bpy.types import Context, CollectionProperty, PropertyGroup

# relative imports
from .. import shared_data, constants
from ..log import logger
from .shared import loop_table, loop_iterator, loop_size
from .shared import get_preferences
# endregion


def filter_active_macros(macros: CollectionProperty) -> List:
    """Фильтрация активных макросов"""
    return [macro for macro in macros if macro.active]


def preprocess_events(
    macros: List,
    action: PropertyGroup,
    action_type: str,
    start_index: int
) -> Optional[str]:
    """
    Предварительная обработка событий (render complete, loops и т.д.)

    Returns:
        Optional[str]: ошибка или None
    """
    # non-realtime events, execute before macros get executed
    for i, macro in enumerate(macros[start_index:], start_index):
        split = macro.command.split(":")
        if split[0] != constants.EVENT_PREFIX[:-1]:
            continue

        data = json.loads(":".join(split[1:]))
        if data['Type'] == constants.EVENT_RENDER_COMPLETE:
            # Skip only render complete macro
            if len(macros) <= i + 1:
                action.is_playing = False
                return f"The '{constants.EVENT_RENDER_COMPLETE}' macro was skipped because no additional macros follow!"
            shared_data.render_complete_macros.append(
                (action_type, action.id, macros[i + 1].id))
            break
        elif data['Type'] == constants.EVENT_LOOP:
            _setup_loop(macro, data, macros, i)
    return None


def _setup_loop(start_macro: PropertyGroup, data: Dict, macros: List, start_index: int) -> None:
    """Настройка цикла"""
    # Find corresponding EndLoop
    for j, process_macro in enumerate(macros[start_index + 1:], start_index + 1):
        if not process_macro.active:
            continue

        split = process_macro.command.split(":")
        if split[0] != constants.EVENT_PREFIX[:-1]:
            continue

        process_data = json.loads(":".join(split[1:]))
        if process_data['Type'] == constants.EVENT_LOOP:
            # Nested loop - will be handled when reached
            continue
        elif process_data['Type'] == 'EndLoop':
            # Found matching EndLoop
            loop_table[process_macro.id] = start_macro.id
            loop_size[start_macro.id] = j - start_index
            loop_iterator[start_macro.id] = 0

            if data['StatementType'] == 'count':
                # DEPRECATED: support old count loop macros
                loop_iterator[start_macro.id] = data.get("Startnumber", 0)
            break


def handle_event_timer(data: Dict, context: Context, action_type: str, action_id: str, macro_index: int) -> None:
    """Обработка события таймера"""
    bpy.app.timers.register(
        functools.partial(
            run_queued_macros,
            context.copy(),
            action_type,
            action_id,
            macro_index + 1
        ),
        first_interval=data['Time']
    )


def handle_event_loop(
    data: Dict,
    macros: List,
    action: PropertyGroup,
    current_index: int,
    macro_id: str
) -> Union[int, Exception]:
    """Обработка события цикла"""
    from . import macros  # Import here to avoid circular imports

    if macro_id not in loop_iterator:
        return current_index + 1  # Skip incomplete loop

    if data['StatementType'] == 'python':
        try:
            if eval(data["PyStatement"]):
                return current_index + 1
            else:
                return current_index + loop_size[loop_table[current_index]] + 1
        except Exception as err:
            logger.error(err)
            action.alert = True
            action.is_playing = False
            return err

    elif data['StatementType'] == 'count':
        # DEPRECATED: support old count loop macros
        if loop_iterator[macro_id] < data["Endnumber"]:
            loop_iterator[macro_id] += data["Stepnumber"]
            return current_index + 1
        else:
            return current_index + loop_size[loop_table[macro_id]] + 1

    else:  # repeat
        if loop_iterator[macro_id] < data["RepeatCount"]:
            loop_iterator[macro_id] += 1
            return current_index + 1
        else:
            return current_index + loop_size[loop_table[macro_id]] + 1


def handle_event_select_object(data: Dict, context: Context, action: PropertyGroup) -> Optional[Exception]:
    """Обработка события выбора объекта"""
    selected_objects = context.selected_objects

    if not data.get('KeepSelection', False):
        for obj in selected_objects:
            obj.select_set(False)
        selected_objects.clear()

    for object_name in data.get('Objects', []):
        if obj := bpy.data.objects.get(object_name):
            obj.select_set(True)
            selected_objects.append(obj)

    if data.get('Object', "") == "":
        return None

    objects = context.view_layer.objects
    main_object = bpy.data.objects.get(data['Object'])
    if main_object is None or main_object not in objects.values():
        action.alert = True
        action.is_playing = False
        return Exception(f"{data['Object']} Object doesn't exist in the active view layer")

    objects.active = main_object
    main_object.select_set(True)
    selected_objects.append(main_object)
    return None


def handle_event_run_script(data: Dict, macro: PropertyGroup, action: PropertyGroup) -> Optional[Exception]:
    """Обработка события выполнения скрипта"""
    text = bpy.data.texts.new(macro.id)
    text.clear()
    text.write(data['ScriptText'])

    try:
        text.as_module()
    except Exception:
        error = traceback.format_exception(*sys.exc_info())
        # Correct filename in exception
        error_split = error[3].replace('"<string>"', '').split(',')
        error[3] = f'{error_split[0]} "{text.name}",{error_split[1]}'
        # Remove exec(self.as_string(), mod.__dict__) in bpy_types.py
        error.pop(2)
        error.pop(1)  # Remove text.as_module()
        error = "".join(error)
        logger.error(f"{error}; command: {data}")
        action.alert = macro.alert = True
        return Exception(error)
    finally:
        bpy.data.texts.remove(text)

    return None


def handle_event_end_loop(current_index: int, macro_id: str) -> int:
    """Обработка события окончания цикла"""
    from . import macros  # Import here to avoid circular imports

    start_id = loop_table.get(macro_id)
    if start_id:
        return current_index - loop_size[start_id]
    return current_index + 1  # Skip if no matching loop


def execute_macro_command(
    macro: PropertyGroup,
    context: Context,
    action: PropertyGroup
) -> Optional[Exception]:
    """Выполнение команды макроса"""
    command = macro.command

    # Handle recursion prevention
    if (command.startswith("bpy.ops.ar.local_play")
            and set(extract_properties(command.split("(")[1][:-1])) == {"id=\"\"", "index=-1"}):
        err = "Don't run Local Play with default properties, this may cause recursion"
        logger.error(err)
        action.alert = macro.alert = True
        action.is_playing = False
        return Exception(err)

    # Prepare command execution
    if command.startswith("bpy.ops."):
        split = command.split("(")
        command = f"{split[0]}('{macro.operator_execution_context}', {''.join(split[1:])}"
    elif command.startswith("bpy.context."):
        command = command.replace("bpy.context.", "context.")

    # Setup area override if needed
    temp_window = context.window
    temp_screen = context.screen
    temp_area = context.area
    temp_region = context.region
    area_type = None

    if temp_area and macro.ui_type and temp_area.ui_type != macro.ui_type:
        windows = list(context.window_manager.windows)
        windows.reverse()
        for window in windows:
            if window.screen.areas[0].ui_type == macro.ui_type:
                temp_window = window
                temp_screen = temp_window.screen
                temp_area = temp_screen.areas[0]
                break
        else:
            area_type = temp_area.ui_type
            temp_area.ui_type = macro.ui_type

    if temp_area:
        # Find WINDOW region
        for region in reversed(temp_area.regions):
            if region.type != "WINDOW":
                continue
            temp_region = region

    # Execute with context override
    try:
        with context.temp_override(
                window=temp_window,
                screen=temp_screen,
                area=temp_area,
                region=temp_region):
            if action.execution_mode == "GROUP":
                exec(command)
            else:
                execute_individually(context, command)

        if temp_area and area_type:
            temp_area.ui_type = area_type

        if bpy.context and bpy.context.area:
            bpy.context.area.tag_redraw()

    except Exception as err:
        logger.error(f"{err}; command: {command}")
        action.alert = macro.alert = True
        if hasattr(context, 'area') and context.area and area_type:
            context.area.ui_type = area_type
        action.is_playing = False
        return err

    return None


def execute_individually(context: Context, command: str) -> None:
    """Выполнение команды индивидуально для каждого выделенного объекта"""
    old_selected_objects = context.selected_objects[:]
    for obj in old_selected_objects:
        obj.select_set(False)

    for obj in old_selected_objects:
        obj.select_set(True)
        context.view_layer.objects.active = obj
        exec(command)
        with suppress(ReferenceError):
            obj.select_set(False)

    for obj in old_selected_objects:
        with suppress(ReferenceError):
            obj.select_set(True)


def run_queued_macros(context_copy: Dict, action_type: str, action_id: str, start: int) -> None:
    """Запуск макросов из очереди"""
    context = bpy.context
    if context_copy is None:
        temp_override = context.temp_override()
    else:
        temp_override = context.temp_override(**context_copy)
    with temp_override:
        ActRec_pref = context.preferences.addons[__package__.split(".")[0]].preferences
        action = getattr(ActRec_pref, action_type)[action_id]
        from .shared import play
        play(context, action.macros, action, action_type, start)


def extract_properties(properties: str) -> List[str]:
    """Извлечение свойств из строки формата 'prop1, prop2, ...'"""
    properties = properties.split(",")
    new_props = []
    prop_str = ''
    for prop in properties:
        prop = prop.split('=')
        if prop[0].strip().isidentifier() and len(prop) > 1:
            new_props.append(prop_str.strip())
            prop_str = ''
            prop_str += "=".join(prop)
        else:
            prop_str += ",%s" % prop[0]
    new_props.append(prop_str.strip())
    return new_props[1:]


# Import here to avoid circular imports
import sys
