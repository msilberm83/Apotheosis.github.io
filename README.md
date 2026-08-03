# Apotheosis.github.io

## Secure membership and payment setup

The public pages can be hosted on GitHub Pages, but free Basic membership
registration and email/phone verification require the Flask application in
`app.py` to run on a server.

1. Copy `.env.example` to `.env` on the server and keep `.env` private.
2. Set `MEMBERSHIP_ACCESS_CODE_SHA256` to the SHA-256 hash of the private
   complimentary-access code (waives the fee for the free Basic tier only).
3. Configure the `SMTP_*` variables so verification emails can be sent.

Plus and Plus Plus subscriptions are sold through Stripe Payment Links
(`buy.stripe.com/...`) linked directly from members.html, and donations go
through a Stripe donation link on support.html. Both bypass `app.py`
entirely, so no payment-provider configuration is needed in this repo for
them. The website does not collect or store full card numbers; Stripe hosts
checkout and the customer portal.
