# region Imports
# external modules
from typing import Optional, Union, Any, Dict, List
from contextlib import suppress

# blender modules
import bpy
from bpy.types import Property, PropertyGroup, CollectionProperty

# relative imports
from .constants import *
# endregion


class PropertyUtils:
    """Утилиты для работы с Blender Property"""

    @staticmethod
    def get_pointer_property_as_dict(
        property: Property,
        exclude: List[str],
        depth: int
    ) -> Dict[str, Any]:
        """
        Конвертирует PointerProperty в dict
        """
        if depth <= 0:
            return {"max_depth": True}

        data = {}
        main_exclude = set()
        sub_exclude = {}

        for x in exclude:
            prop = x.split(".", 1)
            if len(prop) > 1:
                sub_exclude.setdefault(prop[0], []).append(prop[1])
            else:
                main_exclude.add(prop[0])

        for attr in property.bl_rna.properties[1:]:  # exclude rna_type
            identifier = attr.identifier
            if identifier in main_exclude:
                continue
            data[identifier] = PropertyUtils.property_to_python(
                getattr(property, identifier),
                sub_exclude.get(identifier, []),
                depth - 1
            )
        return data

    @staticmethod
    def property_to_python(
        property: Property,
        exclude: List[str] = [],
        depth: int = 5
    ) -> Union[List, Dict, str, Any]:
        """
        Конвертирует Blender Property в Python объект
        """
        if depth <= 0:
            return "max depth"

        if isinstance(property, set):  # EnumProperty с EnumFlag
            return list(property)
        if not hasattr(property, 'id_data'):
            return property

        id_object = property.id_data
        if property == id_object:
            return property

        class_name = property.__class__.__name__

        if class_name == 'bpy_prop_collection_idprop':
            return [PropertyUtils.property_to_python(item, exclude, depth) for item in property]
        if class_name == 'bpy_prop_collection':
            if hasattr(property, "bl_rna"):
                data = PropertyUtils.get_pointer_property_as_dict(property, exclude, depth)
                data["items"] = [
                    PropertyUtils.property_to_python(item, exclude, depth) for item in property
                ]
                return data
            else:
                return [PropertyUtils.property_to_python(item, exclude, depth) for item in property]
        if class_name == 'bpy_prop_array':
            return [PropertyUtils.property_to_python(item, exclude, depth) for item in property]

        return PropertyUtils.get_pointer_property_as_dict(property, exclude, depth)

    @staticmethod
    def apply_data_to_item(property: Property, data: Any, key: str = "") -> None:
        """
        Применяет данные к Property
        """
        if isinstance(data, list):
            item = getattr(property, key) if key else property
            if isinstance(item, set):  # EnumProperty с EnumFlag
                setattr(property, key, set(data))
                return
            if isinstance(item, bpy.types.bpy_prop_array):
                setattr(property, key, data)
                return
            if not isinstance(item, (set, bpy.types.bpy_prop_array)):
                for element in data:
                    PropertyUtils.apply_data_to_item(item.add(), element)
        elif isinstance(data, dict):
            target = getattr(property, key) if key else property
            for k, v in data.items():
                PropertyUtils.apply_data_to_item(target, v, k)
        elif hasattr(property, key):
            with suppress(AttributeError):  # игнорируем read-only свойства
                setattr(property, key, data)

    @staticmethod
    def add_data_to_collection(collection: CollectionProperty, data: Dict) -> None:
        """Добавляет данные в коллекцию"""
        new_item = collection.add()
        PropertyUtils.apply_data_to_item(new_item, data)

    @staticmethod
    def insert_to_collection(
        collection: CollectionProperty,
        index: int,
        data: Dict
    ) -> None:
        """Вставляет данные в коллекцию по индексу"""
        PropertyUtils.add_data_to_collection(collection, data)
        if index < len(collection):
            collection.move(len(collection) - 1, index)

    @staticmethod
    def swap_collection_items(
        collection: CollectionProperty,
        index_1: int,
        index_2: int
    ) -> None:
        """Меняет местами элементы коллекции"""
        collection_length = len(collection)
        if index_1 >= collection_length:
            index_1 = collection_length - 1
        if index_2 >= collection_length:
            index_2 = collection_length - 1
        if index_1 == index_2:
            return
        if index_1 < index_2:
            index_1, index_2 = index_2, index_1
        collection.move(index_1, index_2)
        collection.move(index_2 + 1, index_1)


class CollectionUtils:
    """Утилиты для работы с коллекциями"""

    @staticmethod
    def check_for_duplicates(check_list: List, name: str, num: int = 1) -> str:
        """Проверяет дубликаты имен и добавляет .001, .002 и т.д."""
        split = name.split(".")
        base_name = name
        if split[-1].isnumeric():
            base_name = ".".join(split[:-1])
        while name in check_list:
            name = f"{base_name}.{num:03d}"
            num += 1
        return name


class UIUtils:
    """Утилиты для работы с UI"""

    @staticmethod
    def enum_list_id_to_name_dict(enum_list: List) -> Dict[str, str]:
        """Конвертирует enum список в dict identifier->name"""
        return {identifier: name for identifier, name, *_ in enum_list}

    @staticmethod
    def enum_items_to_enum_prop_list(
        items: CollectionProperty,
        value_offset: int = 0
    ) -> List[tuple]:
        """Конвертирует enum items в список для EnumProperty"""
        return [
            (item.identifier, item.name, item.description, item.icon, item.value + value_offset)
            for item in items
        ]

    @staticmethod
    def get_categorized_view_3d_modes(
        items: CollectionProperty,
        value_offset: int = 0
    ) -> List[tuple]:
        """Получает категоризированные режимы 3D Viewport"""
        general = [("", "General", "")]
        grease_pencil = [("", "Grease Pencil", "")]
        curves = [("", "Curves", "")]

        modes = UIUtils.enum_items_to_enum_prop_list(items, value_offset)
        for mode in modes:
            if "GPENCIL" in mode[0]:
                grease_pencil.append(mode)
            elif "CURVES" in mode[0]:
                curves.append(mode)
            else:
                general.append(mode)
        return general + grease_pencil + curves


# Константы
class Constants:
    """Магические числа и строки"""

    # Максимальная глубина рекурсии
    MAX_DEPTH = 5

    # Таймеры и интервалы
    TIMER_INTERVAL = 0.1
    TIMER_FIRST_INTERVAL = 0.05

    # Строки
    EMPTY_JSON = "{}"
    MAX_DEPTH_MSG = "max depth"
