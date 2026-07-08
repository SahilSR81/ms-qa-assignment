with open("automation/tests/test_saucedemo_workflow.py", "r") as f:
    content = f.read()

target = """        login_page.open()
        
        # Clear local storage to reset cart state from previous tests running on the same browser session
        self.driver.execute_script("window.localStorage.clear();")
        self.driver.refresh()
"""

replacement = """        login_page.open()
        
        # Clear local storage and reset the page completely to avoid React form restoration issues
        self.driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
        self.driver.get("about:blank")
        login_page.open()
"""

if target in content:
    content = content.replace(target, replacement)
    with open("automation/tests/test_saucedemo_workflow.py", "w") as f:
        f.write(content)
    print("Success")
else:
    print("Target not found")
