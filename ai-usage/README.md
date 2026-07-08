# Part 6 — AI Usage

How I used AI tools in this assignment.

---

## 1. Which AI Tools Did I Use?

| Tool | Models | What For |
|------|--------|----------|
| [opencode](https://opencode.ai) | big-pickle (online) | Code generation, debugging, architecture suggestions, file management |
| [ollama](https://ollama.ai) | gemma4-12b, qwen3.5 (local) | Code review, drafting documentation, checking test coverage |

---

## 2. How Did They Help?

- **opencode** handled the heavy lifting — creating files, running shell commands, generating boilerplate code (Page Object classes, pytest fixtures, CI workflow files), and suggesting testing patterns.
- **Online model** helped with things I needed to verify: Selenium 4 `WebDriverWait` syntax, GitHub Actions workflow conventions, SauceDOM element selectors.
- **Local Ollama models** were useful for review passes — I'd have them read back my documentation and test case tables to catch inconsistencies (like mismatched test IDs in the traceability matrix) and suggest clearer wording.
- **Code review**: I asked AI to look at my Root Cause Analysis and API Testing Approach for logical gaps. It caught a missing step in Scenario 3 where I hadn't initially considered database connection pooling.

---

## 3. How Did I Verify AI-Generated Output?

I treated everything AI gave me as a rough draft. Nothing went in without checking:

1. **Manual review** — Read every test case, RCA step, and API contract line by line. Fixed anything that didn't match the assignment requirements.
2. **Ran the code** — Executed the Selenium tests locally (headed mode) to verify every locator, assertion, and flow step. AI-generated click handlers only passed after manual adjustments (see below).
3. **Cross-referenced** — Checked AI-suggested HTTP status codes (like 422 vs 400 for capacity edge cases) against standard REST conventions and RFC 7231.
4. **Linted** — Ran `ruff` on Python code. Checked that Markdown tables rendered properly.
5. **Tested CI** — Reviewed GitHub Actions runner logs to catch syntax errors or missing dependencies.

---

## 4. Example: Rejecting an AI Suggestion on Click Handling

### The AI's Suggestion

For the SauceDemo logout flow, the AI suggested using standard Selenium `.click()` with a `WebDriverWait`:

```python
def logout(self):
    self.wait.until(EC.element_to_be_clickable(self.burger_menu)).click()
    self.wait.until(EC.element_to_be_clickable(self.logout_link)).click()
```

### Why I Rejected It

It worked locally but failed intermittently in CI with `ElementClickInterceptedException`. The problem was a React re-render race — the sidebar menu collapses (DOM node gets replaced) between WebDriver finding the element and clicking it. The AI assumed a static DOM, which doesn't work for React SPAs.

### How I Fixed It

1. Tried `.click()` with longer `WebDriverWait` — still flaky.
2. Tried try/except retry loop — better but not reliable.
3. Final solution: used JavaScript `click()` via `executeScript` inside a retry loop that checks for page state change (URL change or element visibility). This bypasses React's DOM replacement entirely.

```python
def js_click(self, by, value, timeout=10):
    element = self.wait.until(EC.presence_of_element_located((by, value)))
    self.driver.execute_script("arguments[0].click();", element)

def logout(self):
    self.js_click(*self.burger_menu)
    self.wait.until(EC.visibility_of_element_located(self.logout_link))
    self.js_click(*self.logout_link)
    self.wait.until(EC.url_contains("https://www.saucedemo.com/"))
```

### What I Learned

The AI's suggestion was fine for a static page but didn't account for React's async DOM behavior. I generalized the fix into reusable `js_click()` and retry methods in `BasePage` so all page objects could use it. Validated against 10+ CI runs with zero flakiness.

---

## Summary

AI helped me move faster on boilerplate code, documentation outlines, and table formatting. But I reviewed, tested, and frequently rewrote everything it generated. No AI output made it into the final submission without being verified against real execution and established practices.
