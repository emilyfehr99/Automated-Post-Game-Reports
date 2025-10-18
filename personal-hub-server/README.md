Personal Hub Server

Quick start

1) Copy `.env.example` to `.env` and set Plaid keys
2) Start: `node index.js`
3) Endpoints:
   - POST `/api/plaid/create_link_token`
   - POST `/api/plaid/exchange_public_token`
   - GET `/health`


