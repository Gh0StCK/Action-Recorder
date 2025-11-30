# region Imports
from typing import Optional, Callable, Any
from bpy.types import UILayout, Context, PropertyGroup

# relative imports
from .functions.shared import get_preferences
from . import constants
# endregion


class UIHelper:
    """Хелперы для создания UI элементов"""

    @staticmethod
    def draw_action_list(
        layout: UILayout,
        actions: PropertyGroup,
        active_index_prop: str,
        rows: int = constants.UI_LIST_ROWS,
        sort_lock: bool = True
    ) -> None:
        """Отрисовка списка действий"""
        layout.template_list(
            'AR_UL_locals', '',
            actions, 'local_actions',
            actions, active_index_prop,
            rows=rows, sort_lock=sort_lock
        )

    @staticmethod
    def draw_macro_list(
        layout: UILayout,
        action: PropertyGroup,
        active_index_prop: str,
        rows: int = constants.UI_LIST_ROWS,
        sort_lock: bool = True
    ) -> None:
        """Отрисовка списка макросов"""
        layout.template_list(
            'AR_UL_macros', '',
            action, 'macros',
            action, active_index_prop,
            rows=rows, sort_lock=sort_lock
        )

    @staticmethod
    def draw_operator_buttons(
        layout: UILayout,
        operators: list,
        columns: int = 2
    ) -> None:
        """Отрисовка кнопок операторов в сетке"""
        col = layout.column()
        for i in range(0, len(operators), columns):
            row = col.row(align=True)
            for j in range(columns):
                if i + j < len(operators):
                    op_name, op_text, op_icon = operators[i + j]
                    row.operator(op_name, text=op_text, icon=op_icon)

    @staticmethod
    def draw_property_with_icon(
        layout: UILayout,
        data: PropertyGroup,
        prop_name: str,
        icon_value: int,
        **kwargs
    ) -> None:
        """Отрисовка свойства с иконкой"""
        row = layout.row(align=True)
        row.operator(
            "ar.local_icon" if "local" in prop_name else "ar.global_icon",
            text="",
            icon_value=icon_value,
            emboss=False
        )
        row.prop(data, prop_name, **kwargs)

    @staticmethod
    def draw_execution_mode(layout: UILayout, data: PropertyGroup) -> None:
        """Отрисовка режима выполнения"""
        layout.prop(data, 'execution_mode', text="", icon_only=True)

    @staticmethod
    def draw_mode_selector(
        layout: UILayout,
        ActRec_pref: PropertyGroup,
        mode_prop: str,
        expand: bool = True
    ) -> None:
        """Отрисовка селектора режима"""
        row = layout.row(align=True)
        row.enabled = UIHelper.can_convert_actions(ActRec_pref)
        row.prop(ActRec_pref, mode_prop, expand=expand)

    @staticmethod
    def draw_update_box(layout: UILayout, ActRec_pref: PropertyGroup, update_func: Callable) -> None:
        """Отрисовка блока обновлений"""
        if ActRec_pref.update:
            box = layout.box()
            box.label(text=f"new Version available ({ActRec_pref.version})")
            update_func(box, ActRec_pref)

    @staticmethod
    def draw_help_links(layout: UILayout) -> None:
        """Отрисовка ссылок помощи"""
        layout.operator(
            'wm.url_open',
            text="Manual",
            icon='ASSET_MANAGER'
        ).url = constants.manual_url
        layout.operator(
            'wm.url_open',
            text="Hint",
            icon='HELP'
        ).url = constants.hint_url
        layout.operator(
            'ar.preferences_open_explorer',
            text="Open Log"
        ).path = get_preferences(bpy.context).log_path if hasattr(get_preferences(bpy.context), 'log_path') else ""
        layout.operator(
            'wm.url_open',
            text="Bug Report",
            icon='URL'
        ).url = constants.bug_report_url
        layout.operator(
            'wm.url_open',
            text="Release Notes"
        ).url = constants.release_notes_url

    @staticmethod
    def draw_category_controls(layout: UILayout) -> None:
        """Отрисовка элементов управления категориями"""
        col = layout.column()
        col.label(text="Category", icon='GROUP')
        row = col.row(align=True)
        row.label(text='')
        row2 = row.row(align=True)
        row2.scale_x = 1.5
        row2.operator("ar.category_move_up", text='', icon='TRIA_UP')
        row2.operator("ar.category_move_down", text='', icon='TRIA_DOWN')
        row2.operator("ar.category_add", text='', icon='ADD')
        row2.operator("ar.category_delete", text='', icon='TRASH')
        row.label(text='')
        row = col.row(align=False)
        row.operator("ar.category_edit", text='Edit')

    @staticmethod
    def draw_data_management(layout: UILayout, ActRec_pref: PropertyGroup) -> None:
        """Отрисовка элементов управления данными"""
        col = layout.column()
        col.label(text="Data Management", icon='FILE_FOLDER')
        col.operator("ar.global_import", text='Import')
        col.operator("ar.global_export", text='Export')
        col.label(text="Storage File Settings", icon="FOLDER_REDIRECT")
        row = col.row()
        row.label(text="AutoSave")
        row.prop(
            ActRec_pref,
            'autosave',
            toggle=True,
            text="On" if ActRec_pref.autosave else "Off"
        )
        col.operator("ar.global_save", text='Save to File')
        col.operator("ar.global_load", text='Load from File')

    @staticmethod
    def draw_local_settings(layout: UILayout, ActRec_pref: PropertyGroup) -> None:
        """Отрисовка настроек локальных действий"""
        col = layout.column()
        col.label(text="Local Settings")
        row = col.row(align=True)
        row.operator("ar.local_load", text='Load Local Actions')
        row.prop(
            ActRec_pref,
            'hide_local_text',
            text="",
            toggle=True,
            icon="HIDE_ON" if ActRec_pref.hide_local_text else "HIDE_OFF"
        )
        col.prop(
            ActRec_pref,
            'local_create_empty',
            text="Create Empty Macro on Error"
        )

    @staticmethod
    def can_convert_actions(ActRec_pref: PropertyGroup) -> bool:
        """Проверка возможности конвертации действий"""
        return len(ActRec_pref.local_actions) and not ActRec_pref.local_record_macros

    @staticmethod
    def get_selected_action_count(ActRec_pref: PropertyGroup) -> int:
        """Получение количества выбранных глобальных действий"""
        return sum(1 for a in ActRec_pref.global_actions if getattr(a, 'selected', False))

    @staticmethod
    def is_recording(ActRec_pref: PropertyGroup) -> bool:
        """Проверка состояния записи"""
        return ActRec_pref.local_record_macros

    @staticmethod
    def is_action_playing(action: PropertyGroup) -> bool:
        """Проверка проигрывания действия"""
        return action.is_playing

    @staticmethod
    def draw_playback_controls(
        layout: UILayout,
        action: PropertyGroup,
        ActRec_pref: PropertyGroup
    ) -> None:
        """Отрисовка элементов управления воспроизведением"""
        row = layout.row()
        row.active = not UIHelper.is_action_playing(action)

        if UIHelper.is_recording(ActRec_pref):
            row.scale_y = 2
            row.operator("ar.local_record", text='Stop')
        else:
            row2 = row.row(align=True)
            row2.operator("ar.local_record", text='Record', icon='REC')
            row2.operator("ar.local_clear", text='Clear')

            col = layout.column()
            row = col.row()
            row.scale_y = 2
            row.operator(
                "ar.local_play",
                text="Playing..." if UIHelper.is_action_playing(action) else "Play"
            )
            col.operator("ar.local_to_global", text='Local to Global')

            row = col.row(align=True)
            row.enabled = UIHelper.can_convert_actions(ActRec_pref)
            row.prop(ActRec_pref, 'local_to_global_mode', expand=True)

    @staticmethod
    def draw_macro_controls(
        layout: UILayout,
        action: PropertyGroup,
        ActRec_pref: PropertyGroup
    ) -> None:
        """Отрисовка элементов управления макросами"""
        col = layout.column()
        col.active = not UIHelper.is_action_playing(action)

        if not UIHelper.is_recording(ActRec_pref):
            col2 = col.column(align=True)
            col2.operator("ar.macro_add", text='', icon='ADD')
            col2.operator("ar.macro_add_event", text='', icon='MODIFIER')
            col2.operator("ar.macro_remove", text='', icon='REMOVE')
            col2 = col.column(align=True)
            col2.operator("ar.macro_move_up", text='', icon='TRIA_UP')
            col2.operator("ar.macro_move_down", text='', icon='TRIA_DOWN')

    @staticmethod
    def draw_action_controls(
        layout: UILayout,
        actions_type: str = "local"
    ) -> None:
        """Отрисовка элементов управления действиями"""
        col = layout.column()
        col2 = col.column(align=True)
        col2.operator(f"ar.{actions_type}_add", text='', icon='ADD')
        col2.operator(f"ar.{actions_type}_remove", text='', icon='REMOVE')
        col2 = col.column(align=True)
        col2.operator(f"ar.{actions_type}_move_up", text='', icon='TRIA_UP')
        col2.operator(f"ar.{actions_type}_move_down", text='', icon='TRIA_DOWN')


# Импорт bpy для функций, использующих bpy
import bpy
