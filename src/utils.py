from strawberry import Info
from strawberry.types.nodes import InlineFragment
from strawberry.utils.str_converters import to_snake_case


def get_requested_fields(info: Info) -> set[str]:
    return {
        to_snake_case(s.name + ("_name" if s.selections else ""))
        for field in info.selected_fields
        for selection in field.selections
        for s in (
            selection.selections
            if isinstance(selection, InlineFragment)
            else [selection]
        )
        if not isinstance(s, InlineFragment) and s.name != "__typename"
    }
