"""Executes the small, fixed action vocabulary the agent is allowed to use.

Keeping the action space small and explicit (rather than "write arbitrary
Playwright code") is deliberate: it's what makes the agent's behavior
scoreable -- every action is one of a few known, structured types, so a
harness can log and evaluate them uniformly.
"""
from playwright.sync_api import Page


class InvalidAction(Exception):
    pass


def execute(page: Page, action: dict) -> None:
    kind = action["action"]

    if kind == "fill":
        role, name, text = action["role"], action["name"], action["text"]
        locator = page.get_by_role(role, name=name)
        if locator.count() == 0:
            raise InvalidAction(f'No {role} named "{name}" found')
        locator.fill(text)

    elif kind == "click":
        role, name = action["role"], action["name"]
        locator = page.get_by_role(role, name=name)
        if locator.count() == 0:
            raise InvalidAction(f'No {role} named "{name}" found')
        locator.click()

    elif kind == "finish":
        pass  # handled by the agent loop, not the page

    else:
        raise InvalidAction(f"Unknown action type: {kind}")
