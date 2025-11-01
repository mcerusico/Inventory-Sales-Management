import reflex as rx
from sqlmodel import select, and_
from app.db_models import Product, Stock, Branch, ProductDict, StockDict
import sqlalchemy as sa
import logging


class ProductState(rx.State):
    products: list[ProductDict] = []
    stocks: list[StockDict] = []
    new_product_name: str = ""
    new_product_description: str = ""
    new_product_category: str = ""
    new_product_price: str = ""
    selected_product_id: str = ""
    selected_branch_id: str = ""
    stock_quantity: int = 0
    transfer_from_branch_id: str = ""
    transfer_to_branch_id: str = ""
    transfer_product_id: str = ""
    transfer_quantity: int = 1

    @rx.event
    async def load_products_and_stock(self):
        with rx.session() as session:
            all_products = session.exec(select(Product)).all()
            self.products = [p.dict() for p in all_products]
            stock_query = select(Stock).options(
                sa.orm.selectinload(Stock.product), sa.orm.selectinload(Stock.branch)
            )
            all_stocks = session.exec(stock_query).all()
            self.stocks = [
                {
                    **s.dict(),
                    "product_name": s.product.name if s.product else "N/A",
                    "branch_name": s.branch.name if s.branch else "N/A",
                }
                for s in all_stocks
            ]

    @rx.event(background=True)
    async def add_product(self):
        async with self:
            if not self.new_product_name or not self.new_product_price:
                yield rx.toast.error("Product name and price are required.")
                return
            try:
                price = float(self.new_product_price)
                if price <= 0:
                    raise ValueError("Price must be positive")
            except ValueError as e:
                logging.exception(f"Error: {e}")
                yield rx.toast.error("Invalid price.")
                return
            with rx.session() as session:
                new_product = Product(
                    name=self.new_product_name,
                    description=self.new_product_description,
                    category=self.new_product_category,
                    price=price,
                )
                session.add(new_product)
                session.commit()
                self.new_product_name = ""
                self.new_product_description = ""
                self.new_product_category = ""
                self.new_product_price = ""
        yield ProductState.load_products_and_stock
        yield rx.toast.success("Product added successfully!")

    @rx.event(background=True)
    async def delete_product(self, product_id: int):
        async with self:
            with rx.session() as session:
                existing_stock = session.exec(
                    select(Stock).where(Stock.product_id == product_id)
                ).first()
                if existing_stock:
                    yield rx.toast.error(
                        "Cannot delete product with existing stock records. Please clear stock first."
                    )
                    return
                product = session.get(Product, product_id)
                if product:
                    session.delete(product)
                    session.commit()
        yield ProductState.load_products_and_stock
        yield rx.toast.info("Product deleted.")

    @rx.event(background=True)
    async def update_stock(self):
        async with self:
            if not self.selected_product_id or not self.selected_branch_id:
                yield rx.toast.error("Please select a product and a branch.")
                return
            product_id = int(self.selected_product_id)
            branch_id = int(self.selected_branch_id)
            quantity = int(self.stock_quantity)
            with rx.session() as session:
                stock_record = session.exec(
                    select(Stock).where(
                        and_(
                            Stock.product_id == product_id, Stock.branch_id == branch_id
                        )
                    )
                ).first()
                if stock_record:
                    stock_record.quantity = quantity
                else:
                    stock_record = Stock(
                        product_id=product_id, branch_id=branch_id, quantity=quantity
                    )
                session.add(stock_record)
                session.commit()
        yield ProductState.load_products_and_stock
        yield rx.toast.success("Stock updated.")

    @rx.event(background=True)
    async def perform_stock_transfer(self):
        async with self:
            from_branch_id = int(self.transfer_from_branch_id)
            to_branch_id = int(self.transfer_to_branch_id)
            product_id = int(self.transfer_product_id)
            quantity_to_transfer = self.transfer_quantity
            if from_branch_id == to_branch_id:
                yield rx.toast.error(
                    "Source and destination branches cannot be the same."
                )
                return
            if quantity_to_transfer <= 0:
                yield rx.toast.error("Transfer quantity must be positive.")
                return
            with rx.session() as session:
                from_stock = session.exec(
                    select(Stock).where(
                        and_(
                            Stock.branch_id == from_branch_id,
                            Stock.product_id == product_id,
                        )
                    )
                ).first()
                if not from_stock or from_stock.quantity < quantity_to_transfer:
                    yield rx.toast.error("Insufficient stock in the source branch.")
                    return
                to_stock = session.exec(
                    select(Stock).where(
                        and_(
                            Stock.branch_id == to_branch_id,
                            Stock.product_id == product_id,
                        )
                    )
                ).first()
                if not to_stock:
                    to_stock = Stock(
                        branch_id=to_branch_id, product_id=product_id, quantity=0
                    )
                    session.add(to_stock)
                from_stock.quantity -= quantity_to_transfer
                to_stock.quantity += quantity_to_transfer
                session.commit()
        yield ProductState.load_products_and_stock
        yield rx.toast.success("Stock transfer completed!")