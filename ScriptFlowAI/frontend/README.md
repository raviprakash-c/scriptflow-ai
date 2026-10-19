# ScriptFlow AI frontend

React + TypeScript + Vite workspace for the PS3 video engine.

## Run
```bash
npm install
npm run dev
npm run build
``

Optional API base URL: set `VITE_API_BASE_URL` in a local `.env` file. Do not put provider secrets in frontend variables. The current typed local-demo adapter persists project drafts in browser localStorage. Sample visuals are not verified commercial footage; the interface distinguishes local demo status from actual backend rendering.

## Main routes
/dashboard, /create, /editor/:id, /footage/:id, /render/:id, /exports/:id, /history, /settings
