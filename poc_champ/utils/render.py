import typer

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, WebDriverException

from rich import print as pprint

from poc_champ.constants import PREFIX

def wait_load(browser_instance, element):
    try:
        WebDriverWait(browser_instance, 30).until(
            ec.visibility_of_all_elements_located(element)
        )
    except WebDriverException as exc:
        browser_instance.close()
        pprint("\n[bold red]Connection failed. Exiting...[/bold red]")
        raise typer.Exit() from exc

def page_interaction(browser_instance, wait_element_load, next_btn_param, next_btn_value):
    """"""

    try:
        link = browser_instance.find_element(next_btn_param, next_btn_value)
        link.click()
        wait_load(browser_instance, wait_element_load)
    except NoSuchElementException:
        return True

    return False

def paginate(browser, load_element, interact, action, iterations=1):
    """"""

    if not interact or not action:
        missing = "button action" if not action else "button identifier"
        pprint(f"\n[bold yellow]{PREFIX}No {missing} provided =(\n{PREFIX}Exiting...[/bold yellow]")
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

def parse_javascript_page(endpoint, param, query, load_element, **kwargs):
    """Send request to DuckDuck Go search engine to retrieve Github links to repositories.

    ## Parameters:
        **query** (_str_): CVE ID string.

    ### Returns:
        _list_: 
        Available Github links to repositories.
    """

    # Configure browser instance to run on background (without GUI)
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")

    # Start Firefox browser instance
    browser = webdriver.Firefox(options=options)

    # Send request to browser to find Github repos for CVE
    request = f'{endpoint}?{param}={query} {kwargs.get("dork", "")}'
    request = request.strip()
    pprint(request)

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
            iterations=paginate_params.get("iterations", 1)
        )
    else:
        # Render all the JavaScript stuff and close browser instances
        pages = [browser.page_source]

    browser.close()

    return pages
