# Twilio SMS setup

The app sends SMS via Twilio's REST Messaging API using only the standard
library (ADR 0019). It reads **three environment variables** — never put the
auth token in the repo:

```
TWILIO_ACCOUNT_SID    # Account SID (live AC… or the Test AC…)
TWILIO_AUTH_TOKEN     # matching auth token
TWILIO_FROM_NUMBER    # sender: a Twilio number (+1…/+421…) OR an alphanumeric sender ID ("JOBER")
```

Unset ⇒ SMS is "not configured": sends are recorded as `failed` and nothing is
attempted (fail-closed). No code change is needed to switch sender type.

## 1. Verify the integration with Test Credentials (no number, no cost)

Use the **Test** SID/token (Console → Account → API keys & tokens → Test
credentials) with Twilio's magic numbers:

```bash
export TWILIO_ACCOUNT_SID=AC...test...
export TWILIO_AUTH_TOKEN=...test...
export TWILIO_FROM_NUMBER=+15005550006     # magic "valid sender"
scripts/dev_app.sh up
```

Then in the app: open a person, set their phone to `+15005550006`, and **Send
SMS**. Twilio validates the request and returns a fake success (the message is
recorded `sent` with a test SID) — nothing is actually delivered. Magic number
`+15005550001` simulates an invalid number if you want to see the failure path.

## 2. Send a real SMS (trial)

Use the **Live** SID/token + a sender:
- **Trial number**: Console → "Get trial phone number"; set `TWILIO_FROM_NUMBER`
  to it. Trial accounts can only send to **verified** recipient numbers.
- **Alphanumeric Sender ID** ("JOBER"): requires an **upgraded** account
  (not available on trial); for Slovakia the sender ID may need registration.
  Then just set `TWILIO_FROM_NUMBER="JOBER"` (send-only, no inbound).

## 3. Inbound replies (optional)

Point the Twilio number's "A message comes in" webhook (POST) at:

```
https://<public-host>/webhooks/twilio/inbound/
```

The endpoint verifies `X-Twilio-Signature` against `TWILIO_AUTH_TOKEN` and fails
closed (403) on a bad/missing signature. Needs a public URL (staging/prod or an
ngrok tunnel). Alphanumeric senders cannot receive replies.

## Staging / production (Dokku)

```bash
dokku config:set jober-staging \
  TWILIO_ACCOUNT_SID=… TWILIO_AUTH_TOKEN=… TWILIO_FROM_NUMBER=…
```

Real SMS to real worker numbers remains behind the legal/real-data gate.
