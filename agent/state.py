"""Turn a live page into a compact text description the LLM agent can read.

This is a simplified stand-in for what a real browser-agent system does with
a page's accessibility tree: reduce a messy DOM down to "here are the
interactive things you can act on, and their current state."
"""
from playwright.sync_api import Page


def describe_page(page: Page) -> str:
    lines = []

    textbox = page.get_by_role("textbox", name="New task")
    lines.append(f'[textbox] name="New task" value="{textbox.input_value()}"')

    lines.append('[button] name="Add"')

    for cb in page.get_by_role("checkbox").all():
        name = cb.get_attribute("aria-label")
        checked = cb.is_checked()
        lines.append(f'[checkbox] name="{name}" checked={checked}')

    for btn in page.get_by_role("button").all():
        label = btn.get_attribute("aria-label") or btn.text_content()
        if label and label.startswith("Delete "):
            lines.append(f'[button] name="{label}"')

    for tab in page.get_by_role("tab").all():
        name = tab.text_content()
        selected = tab.get_attribute("aria-selected") == "true"
        lines.append(f'[tab] name="{name}" selected={selected}')

    return "\n".join(lines)
