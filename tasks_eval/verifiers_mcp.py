"""Ground-truth pass/fail checks for the MCP-based agent, operating on the
final `browser_snapshot` text instead of a direct Playwright Page object
(the MCP server manages its own browser process, so we don't hold a Page
reference the way the hand-rolled agent's verifiers.py does). Same
methodology, different mechanism -- text pattern matching against the
accessibility-tree snapshot rather than expect() assertions.
"""
import re


def _checked(snapshot: str, name: str) -> bool:
    # Other markers (e.g. [active]) can appear between the name and [checked]
    # on the same line, so don't require them to be adjacent.
    return re.search(rf'checkbox "{re.escape(name)}"[^\n]*\[checked\]', snapshot) is not None


def _exists(snapshot: str, name: str) -> bool:
    return f'checkbox "{name}"' in snapshot


def _absent(snapshot: str, name: str) -> bool:
    return not _exists(snapshot, name)


def _tab_selected(snapshot: str, name: str) -> bool:
    return re.search(rf'tab "{re.escape(name)}"[^\n]*\[selected\]', snapshot) is not None


def _checkbox_count(snapshot: str) -> int:
    return len(re.findall(r'checkbox "', snapshot))


def verify_t01(s: str) -> bool:
    return _exists(s, "Buy milk")


def verify_t02(s: str) -> bool:
    return _checked(s, "Read a book")


def verify_t03(s: str) -> bool:
    return _absent(s, "Pay bills")


def verify_t04(s: str) -> bool:
    return _checked(s, "Call mom")


def verify_t05(s: str) -> bool:
    return _checked(s, "Walk the dog") and _checked(s, "Read a book")


def verify_t06(s: str) -> bool:
    return _tab_selected(s, "Active")


def verify_t07(s: str) -> bool:
    return _tab_selected(s, "Completed") and _checked(s, "Walk the dog") and _absent(s, "Read a book")


def verify_t08(s: str) -> bool:
    return _checkbox_count(s) == 0


def verify_t09(s: str) -> bool:
    return _exists(s, "Task A") and _exists(s, "Task B")


def verify_t10(s: str) -> bool:
    # Impossible task by construction -- ground truth is always False.
    return False


VERIFIERS = {
    "t01": verify_t01, "t02": verify_t02, "t03": verify_t03, "t04": verify_t04, "t05": verify_t05,
    "t06": verify_t06, "t07": verify_t07, "t08": verify_t08, "t09": verify_t09, "t10": verify_t10,
}
