from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.schemas.cart import CartItemCreate


async def get_or_create_cart(
    db: AsyncSession,
    user_id: int,
):
    result = await db.execute(
        select(Cart).where(
            Cart.user_id == user_id
        )
    )

    cart = result.scalar_one_or_none()

    if cart:
        return cart

    cart = Cart(
        user_id=user_id
    )

    db.add(cart)

    await db.commit()
    await db.refresh(cart)

    return cart


async def add_to_cart(
    db: AsyncSession,
    user_id: int,
    item_data: CartItemCreate,
):
    cart = await get_or_create_cart(
        db,
        user_id,
    )

    result = await db.execute(
        select(Product).where(
            Product.id == item_data.product_id
        )
    )

    product = result.scalar_one_or_none()

    if not product:
        raise ValueError("Product not found")

    if item_data.quantity <= 0:
        raise ValueError(
            "Quantity must be greater than 0"
        )

    if product.stock < item_data.quantity:
        raise ValueError(
            "Not enough stock"
        )

    result = await db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == item_data.product_id,
        )
    )

    cart_item = result.scalar_one_or_none()

    if cart_item:
        new_quantity = (
            cart_item.quantity +
            item_data.quantity
        )

        if new_quantity > product.stock:
            raise ValueError(
                "Not enough stock"
            )

        cart_item.quantity = new_quantity

    else:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
        )

        db.add(cart_item)

    await db.commit()
    await db.refresh(cart_item)

    return cart_item
async def get_cart(
    db: AsyncSession,
    user_id: int,
):
    result = await db.execute(
        select(Cart).where(
            Cart.user_id == user_id
        )
    )

    cart = result.scalar_one_or_none()

    if not cart:
        raise ValueError("Cart not found")

    result = await db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id
        )
    )

    items = result.scalars().all()

    return cart, items


async def update_cart_item(
    db: AsyncSession,
    user_id: int,
    item_id: int,
    quantity: int,
):
    if quantity <= 0:
        raise ValueError(
            "Quantity must be greater than 0"
        )

    result = await db.execute(
        select(Cart).where(
            Cart.user_id == user_id
        )
    )

    cart = result.scalar_one_or_none()

    if not cart:
        raise ValueError("Cart not found")

    result = await db.execute(
        select(CartItem).where(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id,
        )
    )

    cart_item = result.scalar_one_or_none()

    if not cart_item:
        raise ValueError(
            "Cart item not found"
        )

    result = await db.execute(
        select(Product).where(
            Product.id == cart_item.product_id
        )
    )

    product = result.scalar_one_or_none()

    if not product:
        raise ValueError(
            "Product not found"
        )

    if quantity > product.stock:
        raise ValueError(
            "Not enough stock"
        )

    cart_item.quantity = quantity

    await db.commit()
    await db.refresh(cart_item)

    return cart_item


async def remove_cart_item(
    db: AsyncSession,
    user_id: int,
    item_id: int,
):
    result = await db.execute(
        select(Cart).where(
            Cart.user_id == user_id
        )
    )

    cart = result.scalar_one_or_none()

    if not cart:
        raise ValueError("Cart not found")

    result = await db.execute(
        select(CartItem).where(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id,
        )
    )

    cart_item = result.scalar_one_or_none()

    if not cart_item:
        raise ValueError(
            "Cart item not found"
        )

    await db.delete(cart_item)

    await db.commit()

    return {
        "message": "Cart item removed successfully"
    }