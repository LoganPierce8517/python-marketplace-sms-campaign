import os

from marketplace_sms import BuyerUpdate, InfraiClient, SellerAsset, run_campaign


def main() -> None:
    buyer_phone = os.environ.get("DEMO_BUYER_PHONE")
    if not buyer_phone:
        raise SystemExit("Set DEMO_BUYER_PHONE before running the demo")
    rows = run_campaign(
        SellerAsset("Hand-thrown mug", "$24", "https://shop.example/orders/mug"),
        [BuyerUpdate(buyer_phone, os.environ.get("DEMO_BUYER_NAME", "there"))],
        InfraiClient(),
    )
    print(rows)


if __name__ == "__main__":
    main()

