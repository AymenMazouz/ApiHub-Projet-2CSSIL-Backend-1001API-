# flake8: noqa


class ChargilyApi:
    def create_product(self, product_name: str, product_description: str) -> str | None:
        raise Exception("You must implement this method in a subclass.")

    def create_price(self, product_id: str, amount: int) -> str | None:
        raise Exception("You must implement this method in a subclass.")

    def create_checkout(
        self, price_id: str, redirect_url: str, metadata: dict
    ) -> str | None:
        raise Exception("You must implement this method in a subclass.")

    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        raise Exception("You must implement this method in a subclass.")
