# region Imports
from typing import Optional
from bpy.types import Operator, Context
from bpy.props import StringProperty, IntProperty

# relative imports
from .functions.shared import get_preferences
from . import functions
# endregion


class BaseOperator(Operator):
    """Базовый класс для всех операторов ActionRecorder"""

    @classmethod
    def poll(cls, context: Context) -> bool:
        """Базовая проверка доступности"""
        return context is not None


class IdBasedOperator(BaseOperator):
    """Базовый класс для операторов, работающих с объектами по id/index"""

    id: StringProperty(name="id", description="UUID объекта")
    index: IntProperty(name="index", description="Индекс объекта", default=-1)

    def clear(self) -> None:
        """Очистка параметров"""
        self.id = ""
        self.index = -1


class ActionBasedOperator(IdBasedOperator):
    """Базовый класс для операторов, работающих с действиями"""

    action_index: IntProperty(default=-1, options={'HIDDEN'})
    ignore_selection: bool = False

    def get_action_index(self, context: Context) -> int:
        """Получение индекса действия"""
        ActRec_pref = get_preferences(context)
        return functions.get_local_action_index(ActRec_pref, self.id, self.index)

    def get_action(self, context: Context):
        """Получение объекта действия"""
        ActRec_pref = get_preferences(context)
        index = self.get_action_index(context)
        if 0 <= index < len(ActRec_pref.local_actions):
            return ActRec_pref.local_actions[index]
        return None

    def clear(self) -> None:
        """Очистка параметров"""
        self.action_index = -1
        super().clear()


class MacroBasedOperator(ActionBasedOperator):
    """Базовый класс для операторов, работающих с макросами"""

    macro_index: IntProperty(default=-1, options={'HIDDEN'})

    def get_macro_index(self, action) -> int:
        """Получение индекса макроса"""
        return functions.get_local_macro_index(action, self.id, self.index)

    def get_macro(self, context: Context):
        """Получение объекта макроса"""
        action = self.get_action(context)
        if action is None:
            return None
        index = self.get_macro_index(action)
        if 0 <= index < len(action.macros):
            return action.macros[index]
        return None

    def clear(self) -> None:
        """Очистка параметров"""
        self.macro_index = -1
        super().clear()


class CategoryBasedOperator(IdBasedOperator):
    """Базовый класс для операторов, работающих с категориями"""

    def get_category_index(self, context: Context) -> int:
        """Получение индекса категории"""
        ActRec_pref = get_preferences(context)
        return functions.get_category_id(ActRec_pref, self.id, self.index)

    def get_category(self, context: Context):
        """Получение объекта категории"""
        ActRec_pref = get_preferences(context)
        id = functions.get_category_id(ActRec_pref, self.id, self.index)
        return ActRec_pref.categories.get(id)


class GlobalActionBasedOperator(IdBasedOperator):
    """Базовый класс для операторов, работающих с глобальными действиями"""

    def get_global_action_ids(self, context: Context) -> list:
        """Получение списка ID глобальных действий"""
        ActRec_pref = get_preferences(context)
        return functions.get_global_action_ids(ActRec_pref, self.id, self.index)

    def get_global_action(self, context: Context, id: str = None):
        """Получение объекта глобального действия"""
        ActRec_pref = get_preferences(context)
        action_id = id or functions.get_global_action_id(ActRec_pref, self.id, self.index)
        return ActRec_pref.global_actions.get(action_id) if action_id else None
