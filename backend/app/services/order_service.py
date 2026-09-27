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

        # Get user's cart
        result = await db.execute(
            select(Cart).where(
                Cart.user_id == user_id
            )
        )

        cart = result.scalar_one_or_none()

        if not cart:
            raise ValueError("Cart not found")

        # Get cart items in a consistent order
        result = await db.execute(
            select(CartItem)
            .where(
                CartItem.cart_id == cart.id
            )
            .order_by(CartItem.product_id)
        )

        cart_items = result.scalars().all()

        if not cart_items:
            raise ValueError("Cart is empty")

        total_amount = Decimal("0")
        order_items_data = []

        # Lock products while checking and updating stock
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

            # Check stock while the product row is locked
            if product.stock < cart_item.quantity:
                raise ValueError(
                    f"Not enough stock for {product.name}"
                )

            # Reserve stock
            product.stock -= cart_item.quantity

            item_total = (
                product.price * cart_item.quantity
            )

            total_amount += item_total

            order_items_data.append(
                {
                    "product_id": product.id,
                    "quantity": cart_item.quantity,
                    "price": product.price,
                }
            )

        # Create order
        order = Order(
            user_id=user_id,
            status="pending",
            total_amount=total_amount,
        )

        db.add(order)

        await db.flush()

        # Create order items
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

        # Clear cart
        for cart_item in cart_items:
            await db.delete(cart_item)

    return {
        "id": order.id,
        "user_id": order.user_id,
        "status": order.status,
        "total_amount": order.total_amount,
        "items": response_items,
    }


async def get_order(
    db: AsyncSession,
    order_id: int,
):
    result = await db.execute(
        select(Order).where(
            Order.id == order_id
        )
    )

    order = result.scalar_one_or_none()

    if not order:
        raise ValueError("Order not found")

    result = await db.execute(
        select(OrderItem)
        .where(
            OrderItem.order_id == order.id
        )
        .order_by(OrderItem.id)
    )

    order_items = result.scalars().all()

    return {
        "id": order.id,
        "user_id": order.user_id,
        "status": order.status,
        "total_amount": order.total_amount,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": item.price,
            }
            for item in order_items
        ],
    }

async def get_user_orders(
    db: AsyncSession,
    user_id: int,
):
    result = await db.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .order_by(Order.id.desc())
    )

    orders = result.scalars().all()

    response = []

    for order in orders:

        result = await db.execute(
            select(OrderItem)
            .where(
                OrderItem.order_id == order.id
            )
            .order_by(OrderItem.id)
        )

        order_items = result.scalars().all()

        response.append(
            {
                "id": order.id,
                "user_id": order.user_id,
                "status": order.status,
                "total_amount": order.total_amount,
                "items": [
                    {
                        "id": item.id,
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "price": item.price,
                    }
                    for item in order_items
                ],
            }
        )

    return response