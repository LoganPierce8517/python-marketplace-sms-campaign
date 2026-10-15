from marketplace_sms import BuyerUpdate, SellerAsset, run_campaign


class FakeClient:
    def __init__(self):
        self.sent = []

    def send_sms(self, to, message, request_id):
        self.sent.append((to, message, request_id))
        return {"message_id": f"m-{len(self.sent)}"}

    def sms_status(self, message_id):
        return {"state": "delivered", "message_id": message_id}


def test_campaign_hands_each_buyer_a_trackable_order_update():
    client = FakeClient()
    result = run_campaign(
        SellerAsset("Ceramic mug", "$24", "https://shop.test/orders/mug"),
        [BuyerUpdate("+15550001", "Ari"), BuyerUpdate("+15550002", "Bea")],
        client,
    )
    assert [row["status"]["state"] for row in result] == ["delivered", "delivered"]
    assert client.sent[0][1].startswith("Hi Ari, Ceramic mug")

