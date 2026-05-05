"""Utilities for rendering and interacting with web pages using Selenium.

This module provides functions for waiting for elements, paginating, and parsing JavaScript-rendered pages.
"""

from typing import Any
import typer

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, WebDriverException

from rich import print as pprint

from poc_champ.constants import PREFIX


def wait_load(browser_instance: webdriver.Firefox, element: tuple):
    """
    Wait for all elements located by the given selector to be visible.

    :param browser_instance: Selenium WebDriver instance.
    :type browser_instance: selenium.webdriver.Firefox
    :param element: Tuple specifying how to locate the element.
    :type element: tuple

    :raises typer.Exit: If the page fails to load.
    """
    try:
        WebDriverWait(browser_instance, 30).until(
            ec.visibility_of_all_elements_located(element)
        )
    except WebDriverException as exc:
        browser_instance.close()
        pprint("\n[bold red]Connection failed. Exiting...[/bold red]")
        raise typer.Exit() from exc


def page_interaction(
    browser_instance: webdriver.Firefox,
    wait_element_load: tuple,
    next_btn_param: str,
    next_btn_value: str,
) -> bool:
    """
    Interact with a page by clicking a button and waiting for elements to load.

    :param browser_instance: Selenium WebDriver instance.
    :type browser_instance: selenium.webdriver.Firefox
    :param wait_element_load: Tuple specifying how to locate the element to wait for.
    :type wait_element_load: tuple
    :param next_btn_param: Selenium `By` parameter for the button.
    :type next_btn_param: selenium.webdriver.common.by.By
    :param next_btn_value: Value for the button locator.
    :type next_btn_value: str

    :returns: True if the button is not found, False otherwise.
    :rtype: bool
    """
    try:
        link = browser_instance.find_element(next_btn_param, next_btn_value)
        link.click()
        wait_load(browser_instance, wait_element_load)
    except NoSuchElementException:
        return True

    return False


def paginate(
    browser: webdriver.Firefox,
    load_element: tuple,
    interact: tuple,
    action: str,
    iterations: int = 1,
) -> list[str]:
    """
    Paginate through pages by interacting with navigation buttons.

    :param browser: Selenium WebDriver instance.
    :type browser: selenium.webdriver.Firefox
    :param load_element: Tuple specifying how to locate the element to wait for.
    :type load_element: tuple
    :param interact: Tuple containing button locator parameters.
    :type interact: tuple
    :param action: Action to perform ("next" or "expand").
    :type action: str
    :param iterations: Number of pagination iterations.
    :type iterations: int

    :returns: List of page sources collected during pagination.
    :rtype: list

    :raises typer.Exit: If required pagination parameters are missing.
    """
    if not interact or not action:
        missing = "button action" if not action else "button identifier"
        pprint(
            f"\n[bold yellow]{PREFIX}No {missing} provided =(\n{PREFIX}Exiting...[/bold yellow]"
        )
        raise typer.Exit()

    pages = []
    counter = 0
    button_param, button_value = interact

    while counter < iterations:
        endpage = page_interaction(browser, load_element, button_param, button_value)

        if action == "next":
            pages.append(browser.page_source)

        if endpage:
            break

        if iterations > 1:
            counter += 1

    if action == "expand":
        pages.append(browser.page_source)

    return pages


def parse_javascript_page(
    endpoint: str, param: str, query: str, load_element: tuple, **kwargs: Any
) -> list[str]:
    """
    Send request to an endpoint and retrieve JavaScript-rendered pages.

    :param endpoint: Search engine endpoint URL.
    :type endpoint: str
    :param param: Query parameter name.
    :type param: str
    :param query: Search query string.
    :type query: str
    :param load_element: Tuple specifying how to locate the element to wait for.
    :type load_element: tuple
    :param kwargs: Additional parameters for pagination and dork.
    :type kwargs: dict

    :returns: List of page sources containing search results.
    :rtype: list

    :raises typer.Exit: If browser connection fails.
    """
    # Configure browser instance to run on background (without GUI)
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")

    # Start Firefox browser instance
    browser = webdriver.Firefox(options=options)

    # Send request to browser to find Github repos for CVE
    request = f'{endpoint}?{param}={query} {kwargs.get("dork", "")}'
    request = request.strip()

    try:
        browser.get(request)
    except WebDriverException as exc:
        browser.close()
        pprint("\n[bold red]Connection init failed. Exiting...[/bold red]")
        raise typer.Exit() from exc

    wait_load(browser, load_element)

    # Try retrieving more if search engine has more than one page result
    if "paginate" in kwargs:
        paginate_params = kwargs["paginate"]
        pages = paginate(
            browser,
            load_element,
            action=paginate_params.get("action"),
            interact=paginate_params.get("interact"),
            iterations=paginate_params.get("iterations", 1),
        )
    else:
        # Render all the JavaScript stuff and close browser instances
        pages = [browser.page_source]

    browser.close()

    return pages
