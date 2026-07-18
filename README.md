# Apotheosis.github.io

## Secure membership and payment setup

The public pages can be hosted on GitHub Pages, but membership registration,
private access-code validation, verification, and payment redirects require the
Flask application in `app.py` to run on a server.

1. Copy `.env.example` to `.env` on the server and keep `.env` private.
2. Set `MEMBERSHIP_ACCESS_CODE_SHA256` to the SHA-256 hash of the private code.
3. Create separate GoDaddy Payments Online Pay Links for Plus, Plus Plus, and
   donations. Configure the donation link to let customers choose the amount.
4. Add those HTTPS URLs to the three `GODADDY_*_CHECKOUT_URL` variables.
5. In GoDaddy Payments, connect the Wells Fargo account under Settings,
   Payments, Payouts. Banking credentials never belong in this repository.

The website does not collect or store full card numbers. Paid members and donors
are redirected to GoDaddy's hosted checkout.
