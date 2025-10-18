Integrations — Banking (Plaid) and Apple ID

Banking via Plaid (recommended)

1) Create a Plaid account and Sandbox keys: `https://dashboard.plaid.com/`
2) Backend endpoint to create a Link Token:
   - POST `/api/plaid/create_link_token` → returns `{ link_token }`
3) Frontend uses Plaid Link JS to open the flow with `link_token`.
4) On success, frontend receives `public_token`; send to backend:
   - POST `/api/plaid/exchange_public_token` → returns `access_token` (store server-side)
5) Use `/accounts/balance/get`, `/transactions/sync` etc. from your backend.

Sign in with Apple (Web)

1) Create an Apple Developer account and enable Sign in with Apple.
2) Configure a Service ID, Redirect URI, and generate a Client Secret (JWT).
3) Frontend: Use Apple JS `https://appleid.cdn-apple.com/appleauth/static/jsapi/appleid/1/en_US/appleid.auth.js`.
4) Backend: Verify identity token, handle redirect, create session.

Apple Health Data

- iOS HealthKit is native-only; for web, import a Health app export ZIP.
- Parsing the export (XML inside ZIP) can be done client-side (Web Workers) or server-side.

Security Notes

- Never store `access_token` or Apple credentials in the browser.
- Use HTTPS, secure cookies, and a secrets manager.

Next Steps

- Add a minimal backend (Node/Express or Python/FastAPI) with Plaid token routes and Apple callback.
- Replace UI placeholders with live flows once credentials are ready.


