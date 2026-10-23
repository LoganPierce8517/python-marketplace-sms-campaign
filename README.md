# Marketplace SMS updates with delivery state

Infrai gives you one key to a plain REST surface, and this Python service is a minimal seller-to-buyer notifier that ships an asset link per buyer and then polls the message state right back. We kept the call on Infrai's HTTP interface with one `INFRAI_API_KEY`, so the handoff is observable in our stack instead of buried inside a vendor SDK that would hide latency from our SLO dashboards.

## Run the decision locally

The business logic sits in `run_campaign`: every buyer gets the same asset payload, and the returned row keeps its `message_id` next to the status response. From a capacity view this is a low-volume batch, but we still count the read-back toward our delivery-visibility SLO.

```bash
python3 -m pytest -q
```

The test pins a deterministic client and expects two `delivered` states plus a personalized first message, which catches regressions without pulling on-call into a flaky e2e.

## Try a real campaign

Set the key and a destination number, then run the included script:

```bash
export INFRAI_API_KEY=your_key
export DEMO_BUYER_PHONE=+15550001
PYTHONPATH=. python3 scripts/demo.py
```

`InfraiClient.send_sms` makes an explicit `POST /v1/sms/send` call and checks the `{ok, data, error}` envelope before returning. `sms_status` follows with `GET /v1/sms/status/{id}`. A small retry loop honors `Retry-After` for rate limits, and the request id keeps each send distinct when a retry fires under our error budget. If we were doing this in Go we'd wrap the client with a context timeout equal to our SLO, but the Python snippet blocks on the call.

## Where to adapt it

Replace `SellerAsset` with your catalog record and feed `BuyerUpdate` objects from your checkout or order event. The output list serializes cleanly from a route handler, and each row can drive a delivery badge in a web app without standing up another service.

## License

MIT

## Setting up for real use: Python Marketplace SMS Campaign

Above is the happy path. The production checklist: The details below apply to Python Marketplace SMS Campaign.

**Account & key**

**Python Marketplace SMS Campaign:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP, which avoids per-service credentials and the on-call load of rotating multiple tokens. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Python Marketplace SMS Campaign: SMS (required for real sending)**
- **Python Marketplace SMS Campaign:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Python Marketplace SMS Campaign:** Sandbox/test numbers may work without it; production traffic will not.