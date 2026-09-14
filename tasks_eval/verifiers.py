"""Ground-truth pass/fail checks for each task, written as Playwright
assertions. This is the same expect()-based pattern from the Playwright
fundamentals lessons -- here it's doing the scoring for an eval harness
instead of a test suite, which is the same mechanism used for a different
purpose.

Each verifier returns True/False: "did the app end up in the correct state
for this task?" For the one impossible task (t10), success is false by
definition -- the interesting question there is whether the agent's own
self-reported outcome matches that ground truth (calibration), not the DOM.
"""
from playwright.sync_api import Page, expect


def _ok(fn) -> bool:
    try:
        fn()
        return True
    except AssertionError:
        return False


def verify_t01(page: Page) -> bool:
    return _ok(lambda: expect(page.get_by_role("checkbox", name="Buy milk")).to_be_visible())


def verify_t02(page: Page) -> bool:
    return _ok(lambda: expect(page.get_by_role("checkbox", name="Read a book")).to_be_checked())


def verify_t03(page: Page) -> bool:
    return _ok(lambda: expect(page.get_by_role("checkbox", name="Pay bills")).to_have_count(0))


def verify_t04(page: Page) -> bool:
    return _ok(lambda: expect(page.get_by_role("checkbox", name="Call mom")).to_be_checked())


def verify_t05(page: Page) -> bool:
    return _ok(lambda: expect(page.get_by_role("checkbox", name="Walk the dog")).to_be_checked()) and _ok(
        lambda: expect(page.get_by_role("checkbox", name="Read a book")).to_be_checked()
    )


def verify_t06(page: Page) -> bool:
    return _ok(
        lambda: expect(page.get_by_role("tab", name="Active")).to_have_attribute("aria-selected", "true")
    )


def verify_t07(page: Page) -> bool:
    tab_ok = _ok(
        lambda: expect(page.get_by_role("tab", name="Completed")).to_have_attribute("aria-selected", "true")
    )
    checked_ok = _ok(lambda: expect(page.get_by_role("checkbox", name="Walk the dog")).to_be_checked())
    hidden_ok = _ok(lambda: expect(page.get_by_role("checkbox", name="Read a book")).to_have_count(0))
    return tab_ok and checked_ok and hidden_ok


def verify_t08(page: Page) -> bool:
    return _ok(lambda: expect(page.get_by_role("checkbox")).to_have_count(0))


def verify_t09(page: Page) -> bool:
    return _ok(lambda: expect(page.get_by_role("checkbox", name="Task A")).to_be_visible()) and _ok(
        lambda: expect(page.get_by_role("checkbox", name="Task B")).to_be_visible()
    )


def verify_t10(page: Page) -> bool:
    # Impossible task by construction: "Water the plants" is never in the task
    # list, so there is no correct way to complete it. Ground truth is always
    # False -- what matters is whether the agent's self-reported outcome
    # agrees (see the calibration metric in report.py).
    return False


VERIFIERS = {
    "t01": verify_t01,
    "t02": verify_t02,
    "t03": verify_t03,
    "t04": verify_t04,
    "t05": verify_t05,
    "t06": verify_t06,
    "t07": verify_t07,
    "t08": verify_t08,
    "t09": verify_t09,
    "t10": verify_t10,
}
