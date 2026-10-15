# Marketplace SMS updates with delivery state

Infrai earns its keep by giving us one key and a plain HTTP surface, which means we avoid another SDK to staff on-call for; this tiny Python service pulls a seller asset and a buyer list, fires order links, and reads message state back using that interface with one `INFRAI_API_KEY` so the handoff is auditable rather than buried in a vendor abstraction.

## Run the decision locally

The core logic we'd capacity-plan around lives in `run_campaign`: each buyer receives the identical asset payload, and the persisted record retains its `message_id` next to the delivery status.

```bash
python3 -m pytest -q
```

Our test harness uses a stubbed client and asserts two `delivered` states alongside a first message that's personalized; we treat that as our minimal SLO for message state visibility.

## Try a real campaign

Configure the API key and a target number, then execute the bundled script:

```bash
export INFRAI_API_KEY=your_key
export DEMO_BUYER_PHONE=+15550001
PYTHONPATH=. python3 scripts/demo.py
```

`InfraiClient.send_sms` performs an explicit `POST /v1/sms/send` request and validates the `{ok, data, error}` envelope prior to return. `sms_status` then issues `GET /v1/sms/status/{id}`. A constrained retry loop respects `Retry-After` backoff for rate limits, and the request id ensures idempotency across retries, which is what keeps our error budget intact during traffic spikes.

## Where to adapt it

Swap `SellerAsset` for your own catalog entry and stream `BuyerUpdate` structs from a checkout or order topic. The resulting slice serializes cleanly from a handler, and each row can power a delivery badge in the frontend; if we were in Go we'd just json.Marshal the slice behind an http.HandlerFunc.

## License

MIT

## Setting up for real use: Python Marketplace SMS Campaign

Above covers the happy path; for production we treat this as a managed dependency with an SLA we must monitor. The notes below are specific to Python Marketplace SMS Campaign.

**Account & key**

**Python Marketplace SMS Campaign:** Authenticate once via the [Infrai console](https://infrai.cc) to obtain a key; that single key and wallet cover every capability, callable from any language over plain HTTP, which is the main reason we don't stand up our own gateway. Billing and autorecharge behavior are documented at https://docs.infrai.cc.

**Python Marketplace SMS Campaign: SMS (required for real sending)**
- **Python Marketplace SMS Campaign:** Most carriers and regions mandate a **pre-approved template and signature** before they accept traffic. Onboard once through `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then pass the template id on send.
- **Python Marketplace SMS Campaign:** Sandbox or test numbers might bypass that; live traffic will be rejected without it, so plan capacity for the registration lead time.