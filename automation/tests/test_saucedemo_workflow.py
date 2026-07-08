from __future__ import annotations
import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage

@pytest.mark.usefixtures("setup")
class TestSauceDemoWorkflow:
    @pytest.mark.smoke
    def test_end_to_end_shopping_workflow(self) -> None:
        login_page = LoginPage(self.driver)
        inventory_page = InventoryPage(self.driver)
        cart_page = CartPage(self.driver)

        login_page.open()
        login_page.login("standard_user", "secret_sauce")

        inventory_page.add_product_to_cart("sauce-labs-backpack")
        inventory_page.add_product_to_cart("sauce-labs-bike-light")

        inventory_page.wait_for_cart_badge_count(2)
        badge_count = inventory_page.get_cart_badge_count()
        assert badge_count == 2, f"Expected cart badge to show 2, but got {badge_count}"

        inventory_page.go_to_cart()
        cart_page.wait_for_cart_items_count(2)
        items_count = cart_page.get_cart_items_count()
        assert items_count == 2, f"Expected 2 products in the cart, but found {items_count}"
        
        cart_item_names = cart_page.get_cart_item_names()
        expected_names = {"Sauce Labs Backpack", "Sauce Labs Bike Light"}
        assert set(cart_item_names) == expected_names, f"Expected products {expected_names}, but got {set(cart_item_names)}"

        cart_page.remove_product("sauce-labs-bike-light")

        inventory_page.wait_for_cart_badge_count(1)
        badge_count = inventory_page.get_cart_badge_count()
        assert badge_count == 1, f"Expected cart badge to show 1 after removal, but got {badge_count}"

        cart_page.continue_shopping()
        inventory_page.add_product_to_cart("sauce-labs-bolt-t-shirt")

        inventory_page.wait_for_cart_badge_count(2)
        badge_count = inventory_page.get_cart_badge_count()
        assert badge_count == 2, f"Expected cart badge to show 2 after adding another product, but got {badge_count}"

        inventory_page.go_to_cart()
        cart_item_names = cart_page.get_cart_item_names()
        expected_names_after_update = {"Sauce Labs Backpack", "Sauce Labs Bolt T-Shirt"}
        assert set(cart_item_names) == expected_names_after_update, f"Expected products {expected_names_after_update}, but got {set(cart_item_names)}"

        inventory_page.logout()
        assert login_page.is_visible(login_page.LOGIN_BUTTON), "Expected login button to be visible after logout"

    @pytest.mark.regression
    def test_negative_login_invalid_password(self) -> None:
        login_page = LoginPage(self.driver)
        login_page.open()
        login_page.login("standard_user", "invalid_password", expect_success=False)
        error_text = login_page.get_error_message()
        assert "do not match" in error_text, f"Expected error text to contain 'do not match', but got '{error_text}'"

    @pytest.mark.regression
    def test_clear_cart(self) -> None:
        login_page = LoginPage(self.driver)
        inventory_page = InventoryPage(self.driver)
        cart_page = CartPage(self.driver)

        login_page.open()
        login_page.login("standard_user", "secret_sauce")

        inventory_page.add_product_to_cart("sauce-labs-backpack")
        inventory_page.add_product_to_cart("sauce-labs-bike-light")
        
        inventory_page.wait_for_cart_badge_count(2)
        
        inventory_page.go_to_cart()
        
        cart_page.remove_product("sauce-labs-backpack")
        cart_page.remove_product("sauce-labs-bike-light")
        
        cart_page.wait_for_cart_items_count(0)
        
        inventory_page.wait_for_cart_badge_count(0)
        assert inventory_page.get_cart_badge_count() == 0, "Cart badge should be empty"
