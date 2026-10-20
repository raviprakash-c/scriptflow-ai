# Social Content Studio frontend

React, TypeScript and Vite marketing content workspace.

## Run
```bash
npm install
npm run dev
npm run build
``

Set `VITE_API_BASE_URL` locally to prepare the API client boundary. Do not expose provider secrets in browser environment variables. Campaigns and posts are stored in localStorage; initial content is labelled sample/demo content. No social account is connected and nothing is auto-published.

## Routes
/dashboard, /campaigns/new, /generate, /editor/:id, /calendar, /library, /analytics, /exports, /settings
