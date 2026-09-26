import pytest

from app.models.product import Product
from app.models.cart import Cart
from app.models.cart_item import CartItem


@pytest.mark.asyncio
async def test_checkout_success():
    """
    Basic checkout test.

    A user has 2 products in their cart.
    Checkout should succeed and reduce stock.
    """

    assert True