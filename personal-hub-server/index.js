import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { Configuration, PlaidApi, PlaidEnvironments } from 'plaid';

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

const port = process.env.PORT || 4000;

const plaidConfig = new Configuration({
  basePath: PlaidEnvironments[process.env.PLAID_ENV || 'sandbox'],
  baseOptions: {
    headers: {
      'PLAID-CLIENT-ID': process.env.PLAID_CLIENT_ID,
      'PLAID-SECRET': process.env.PLAID_SECRET,
    },
  },
});

const plaid = new PlaidApi(plaidConfig);

app.get('/health', (_req, res) => res.json({ ok: true }));

app.post('/api/plaid/create_link_token', async (req, res) => {
  try {
    const userId = 'user-demo';
    const response = await plaid.linkTokenCreate({
      user: { client_user_id: userId },
      client_name: 'Personal Hub',
      products: ['transactions'],
      country_codes: ['CA'],
      language: 'en',
      redirect_uri: process.env.PLAID_REDIRECT_URI || undefined,
    });
    res.json({ link_token: response.data.link_token });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'plaid_link_token_error' });
  }
});

app.post('/api/plaid/exchange_public_token', async (req, res) => {
  try {
    const { public_token } = req.body;
    const exchange = await plaid.itemPublicTokenExchange({ public_token });
    const access_token = exchange.data.access_token;
    res.json({ access_token });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'plaid_exchange_error' });
  }
});

// Placeholder for Apple callback
app.get('/api/apple/callback', (req, res) => {
  res.send('Apple callback placeholder');
});

app.listen(port, () => {
  console.log(`Server listening on http://localhost:${port}`);
});


