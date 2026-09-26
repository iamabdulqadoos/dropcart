from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product


async def checkout_cart(
    db: AsyncSession,
    user_id: int,
):
    async with db.begin():

        # --------------------------------
        # 1. Get user's cart
        # --------------------------------

        result = await db.execute(
            select(Cart).where(
                Cart.user_id == user_id
            )
        )

        cart = result.scalar_one_or_none()

        if not cart:
            raise ValueError(
                "Cart not found"
            )

        # --------------------------------
        # 2. Get cart items
        # --------------------------------

        result = await db.execute(
            select(CartItem)
            .where(
                CartItem.cart_id == cart.id
            )
            .order_by(
                CartItem.product_id
            )
        )

        cart_items = result.scalars().all()

        if not cart_items:
            raise ValueError(
                "Cart is empty"
            )

        # --------------------------------
        # 3. Prepare order calculation
        # --------------------------------

        total_amount = Decimal("0")

        order_items_data = []

        # --------------------------------
        # 4. Lock products
        # --------------------------------

        for cart_item in cart_items:

            result = await db.execute(
                select(Product)
                .where(
                    Product.id == cart_item.product_id
                )
                .with_for_update()
            )

            product = result.scalar_one_or_none()

            if not product:
                raise ValueError(
                    f"Product {cart_item.product_id} not found"
                )

            # --------------------------------
            # 5. Check stock
            # --------------------------------

            if product.stock < cart_item.quantity:
                raise ValueError(
                    f"Not enough stock for "
                    f"{product.name}"
                )

            # --------------------------------
            # 6. Reduce stock
            # --------------------------------

            product.stock -= cart_item.quantity

            # --------------------------------
            # 7. Calculate price
            # --------------------------------

            item_total = (
                product.price *
                cart_item.quantity
            )

            total_amount += item_total

            order_items_data.append(
                {
                    "product_id": product.id,
                    "quantity": cart_item.quantity,
                    "price": product.price,
                }
            )

        # --------------------------------
        # 8. Create order
        # --------------------------------

        order = Order(
            user_id=user_id,
            status="pending",
            total_amount=total_amount,
        )

        db.add(order)

        # Generate order ID
        await db.flush()

        # --------------------------------
        # 9. Create order items
        # --------------------------------

        response_items = []

        for item_data in order_items_data:

            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data["product_id"],
                quantity=item_data["quantity"],
                price=item_data["price"],
            )

            db.add(order_item)

            await db.flush()

            response_items.append(
                {
                    "id": order_item.id,
                    "product_id": order_item.product_id,
                    "quantity": order_item.quantity,
                    "price": order_item.price,
                }
            )

        # --------------------------------
        # 10. Clear cart
        # --------------------------------

        for cart_item in cart_items:
            await db.delete(cart_item)

        # --------------------------------
        # 11. Transaction commits
        # --------------------------------
        #
        # If everything succeeds:
        #
        #   stock reduced
        #   order created
        #   order items created
        #   cart cleared
        #
        # If anything fails:
        #
        #   EVERYTHING rolls back
        #
        # --------------------------------

    return {
        "id": order.id,
        "user_id": order.user_id,
        "status": order.status,
        "total_amount": order.total_amount,
        "items": response_items,
    }