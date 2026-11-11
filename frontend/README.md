# Memory Lane frontend

The React/Vite app provides the visitor registration, returning visitor,
dashboard, and photo upload workflows.
Validated uploads are immediately available in the owner's private slideshow,
which cycles photos and refreshes its feed periodically.
The admin portal at `/admin/login` provides protected visitor, photo, and
slideshow-default management.

## Development

Install dependencies and start the API as described in the project
[README](../README.md). Then, from `frontend`, run:

```powershell
npm install
npm run dev
```

The Vite development server proxies `/api` and `/health` to
`http://localhost:8000`. Set `VITE_API_PROXY_TARGET` in a local `.env` file to
use a different backend address. For a deployed frontend, configure
`VITE_API_BASE_URL` to the API origin and configure backend CORS accordingly.

## Validation

```powershell
npm run lint
npm run build
```

Visitor access codes are held in `sessionStorage` only for the current browser
tab session. Uploaded image previews use temporary browser object URLs that are
released when removed or when leaving the upload page.
