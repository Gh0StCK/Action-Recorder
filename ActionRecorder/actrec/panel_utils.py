# region Imports
from bpy.types import Panel, Context

# relative imports
from .functions.shared import get_preferences
# endregion


class BaseActionRecorderPanel(Panel):
    """Базовый класс для панелей ActionRecorder"""

    bl_region_type = 'UI'
    bl_category = UI_CATEGORY

    @classmethod
    def get_space_type(cls) -> str:
        """Получение типа пространства для панели"""
        return getattr(cls, 'bl_space_type', 'VIEW_3D')

    @classmethod
    def get_panel_id(cls) -> str:
        """Получение ID панели"""
        return getattr(cls, 'bl_idname', '')

    def draw_update_notification(self, layout):
        """Отрисовка уведомления об обновлении"""
        ActRec_pref = get_preferences(self.context)
        if ActRec_pref.update:
            box = layout.box()
            box.label(text="new Version available (%s)" % ActRec_pref.version)
            from . import update
            update.draw_update_button(box, ActRec_pref)

    def draw_action_buttons(self, layout, action_type: str, prefix: str):
        """Отрисовка кнопок управления действиями"""
        col = layout.column()
        col2 = col.column(align=True)
        col2.operator(f"{prefix}_add", text='', icon='ADD')
        col2.operator(f"{prefix}_remove", text='', icon='REMOVE')
        col2 = col.column(align=True)
        col2.operator(f"{prefix}_move_up", text='', icon='TRIA_UP')
        col2.operator(f"{prefix}_move_down", text='', icon='TRIA_DOWN')

    def draw_macro_buttons(self, layout, action, prefix: str = "ar.macro"):
        """Отрисовка кнопок управления макросами"""
        col = layout.column()
        col.active = not action.is_playing
        if not get_preferences(self.context).local_record_macros:
            col2 = col.column(align=True)
            col2.operator(f"{prefix}_add", text='', icon='ADD')
            col2.operator(f"{prefix}_add_event", text='', icon='MODIFIER')
            col2.operator(f"{prefix}_remove", text='', icon='REMOVE')
            col2 = col.column(align=True)
            col2.operator(f"{prefix}_move_up", text='', icon='TRIA_UP')
            col2.operator(f"{prefix}_move_down", text='', icon='TRIA_DOWN')


def create_panel_class(panel_name: str, space_type: str, order: int = 0):
    """Фабрика для создания панелей с общими свойствами"""

    class ActionRecorderPanel(BaseActionRecorderPanel):
        bl_space_type = space_type
        bl_idname = f"AR_PT_{panel_name}_{space_type}"
        bl_order = order

    ActionRecorderPanel.__name__ = f"AR_PT_{panel_name}_{space_type}"
    return ActionRecorderPanel


def create_local_panel(space_type: str):
    """Создание панели локальных действий"""

    class AR_PT_local(create_panel_class("local", space_type, 0)):
        bl_label = 'Local Actions'

        def draw(self, context: Context) -> None:
            ActRec_pref = get_preferences(context)
            layout = self.layout

            self.draw_update_notification(layout)

            box = layout.box()
            box_row = box.row()
            col = box_row.column()
            col.template_list('AR_UL_locals', '', ActRec_pref, 'local_actions',
                              ActRec_pref, 'active_local_action_index', rows=UI_LIST_ROWS, sort_lock=True)
            col = box_row.column()
            self.draw_action_buttons(col, "local", "ar.local")

    AR_PT_local.__name__ = f"AR_PT_local_{space_type}"
    return AR_PT_local


def create_macro_panel(space_type: str):
    """Создание панели редактора макросов"""

    class AR_PT_macro(create_panel_class("macro", space_type, 1)):
        bl_label = 'Macro Editor'

        @classmethod
        def poll(cls, context: Context) -> bool:
            ActRec_pref = get_preferences(context)
            return len(ActRec_pref.local_actions)

        def draw(self, context: Context) -> None:
            ActRec_pref = get_preferences(context)
            layout = self.layout
            box = layout.box()
            box_row = box.row()
            col = box_row.column()
            selected_action = ActRec_pref.local_actions[ActRec_pref.active_local_action_index]
            col.template_list(
                'AR_UL_macros',
                '',
                selected_action,
                'macros',
                selected_action,
                'active_macro_index',
                rows=UI_LIST_ROWS,
                sort_lock=True
            )
            col = box_row.column()
            self.draw_macro_buttons(col, selected_action)

            row = layout.row()
            row.active = not selected_action.is_playing
            if ActRec_pref.local_record_macros:
                row.scale_y = 2
                row.operator("ar.local_record", text='Stop')
            else:
                row2 = row.row(align=True)
                row2.operator("ar.local_record", text='Record', icon='REC')
                row2.operator("ar.local_clear", text='Clear')
                col = layout.column()
                row = col.row()
                row.scale_y = 2
                row.operator("ar.local_play", text="Playing..." if selected_action.is_playing else "Play")
                col.operator("ar.local_to_global", text='Local to Global')
                row = col.row(align=True)
                row.enabled = hasattr(row, 'poll') and row.operator("ar.local_to_global").poll()
                row.prop(ActRec_pref, 'local_to_global_mode', expand=True)

    AR_PT_macro.__name__ = f"AR_PT_macro_{space_type}"
    return AR_PT_macro


def create_global_panel(space_type: str):
    """Создание панели глобальных действий"""

    class AR_PT_global(create_panel_class("global", space_type, 2)):
        bl_label = 'Global Actions'

        def draw_header(self, context: Context) -> None:
            ActRec_pref = get_preferences(context)
            layout = self.layout
            row = layout.row(align=True)
            row.prop(
                ActRec_pref,
                'global_hide_menu',
                icon='COLLAPSEMENU',
                text="",
                emboss=True
            )

        def draw(self, context: Context) -> None:
            ActRec_pref = get_preferences(context)
            if not ActRec_pref.is_loaded:
                ActRec_pref.is_loaded = True
            layout = self.layout
            if not ActRec_pref.global_hide_menu:
                col = layout.column()
                row = col.row()
                row.scale_y = 2
                row.operator("ar.global_to_local", text='Global to Local')
                row = col.row(align=True)
                row.enabled = hasattr(row, 'poll') and row.operator("ar.global_to_local").poll()
                row.prop(ActRec_pref, 'global_to_local_mode', expand=True)
                row = layout.row().split(factor=0.4)
                row.label(text='Buttons')
                row2 = row.row(align=True)
                row2.operator("ar.global_move_up", text='', icon='TRIA_UP')
                row2.operator("ar.global_move_down", text='', icon='TRIA_DOWN')
                row2.operator(
                    "ar.global_recategorize_action",
                    text='',
                    icon='PRESET'
                )
                row2.operator("ar.global_remove", text='', icon='TRASH')

    AR_PT_global.__name__ = f"AR_PT_global_{space_type}"
    return AR_PT_global


def create_help_panel(space_type: str):
    """Создание панели помощи"""

    class AR_PT_help(create_panel_class("help", space_type, 3)):
        bl_label = 'Help'
        bl_options = {'DEFAULT_CLOSED'}

        def draw_header(self, context: Context) -> None:
            layout = self.layout
            layout.label(icon='INFO')

        def draw(self, context: Context) -> None:
            from . import config, update
            layout = self.layout
            ActRec_pref = get_preferences(context)
            layout.operator(
                'wm.url_open',
                text="Manual",
                icon='ASSET_MANAGER'
            ).url = config.manual_url
            layout.operator(
                'wm.url_open',
                text="Hint",
                icon='HELP'
            ).url = config.hint_url
            layout.operator(
                'ar.preferences_open_explorer',
                text="Open Log"
            ).path = get_preferences(context).log_path if hasattr(get_preferences(context), 'log_path') else ""
            layout.operator(
                'wm.url_open',
                text="Bug Report",
                icon='URL'
            ).url = config.bug_report_url
            layout.operator(
                'wm.url_open',
                text="Release Notes"
            ).url = config.release_notes_url
            row = layout.row()
            if ActRec_pref.update:
                update.draw_update_button(row, ActRec_pref)
            else:
                row.operator('ar.update_check', text="Check For Updates")
                if ActRec_pref.restart:
                    row.operator(
                        'ar.show_restart_menu',
                        text="Restart to Finish"
                    )
            if ActRec_pref.version != '':
                if ActRec_pref.update:
                    layout.label(
                        text="new Version available (%s)" % ActRec_pref.version
                    )
                else:
                    layout.label(text="latest Version (%s)" % ActRec_pref.version)

    AR_PT_help.__name__ = f"AR_PT_help_{space_type}"
    return AR_PT_help


def create_advanced_panel(space_type: str):
    """Создание панели дополнительных настроек"""

    class AR_PT_advanced(create_panel_class("advanced", space_type, 4)):
        bl_label = 'Advanced'
        bl_options = {'DEFAULT_CLOSED'}

        def draw(self, context: Context) -> None:
            ActRec_pref = get_preferences(context)
            layout = self.layout
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
            row.prop(
                ActRec_pref,
                'show_all_categories',
                text="",
                toggle=True,
                icon='RESTRICT_VIEW_OFF' if ActRec_pref.show_all_categories else 'RESTRICT_VIEW_ON'
            )
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

    AR_PT_advanced.__name__ = f"AR_PT_advanced_{space_type}"
    return AR_PT_advanced
