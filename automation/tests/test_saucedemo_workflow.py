import pytest
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage

@pytest.mark.usefixtures("setup")
class TestSauceDemoWorkflow:
    def test_end_to_end_shopping_workflow(self):
        login_page = LoginPage(self.driver)
        inventory_page = InventoryPage(self.driver)
        cart_page = CartPage(self.driver)

        # 1. Launch browser, navigate to SauceDemo
        login_page.open()
        
        # 2. Login
        login_page.login("standard_user", "secret_sauce")

        # 3. Add two products to cart
        inventory_page.add_product_to_cart("sauce-labs-backpack")
        inventory_page.add_product_to_cart("sauce-labs-bike-light")

        # 4. Verify cart badge shows 2
        badge_count = inventory_page.get_cart_badge_count()
        assert badge_count == 2, f"Expected cart badge to show 2, but got {badge_count}"

        # 5. Go to cart, verify both products present
        inventory_page.go_to_cart()
        items_count = cart_page.get_cart_items_count()
        assert items_count == 2, f"Expected 2 products in the cart, but found {items_count}"

        # 6. Remove one product
        cart_page.remove_product("sauce-labs-bike-light")

        # 7. Verify cart badge updates to 1
        # Re-using inventory_page method since the badge is in the global header
        badge_count = inventory_page.get_cart_badge_count()
        assert badge_count == 1, f"Expected cart badge to show 1 after removal, but got {badge_count}"

        # 8. Continue shopping, add another product
        cart_page.continue_shopping()
        inventory_page.add_product_to_cart("sauce-labs-bolt-t-shirt")

        # 9. Verify cart badge shows 2 again
        badge_count = inventory_page.get_cart_badge_count()
        assert badge_count == 2, f"Expected cart badge to show 2 after adding another product, but got {badge_count}"

        # 10. Logout successfully
        inventory_page.logout()
        
        # Verify login button is visible again to confirm successful logout
        assert login_page.is_visible(login_page.LOGIN_BUTTON), "Expected login button to be visible after logout"
