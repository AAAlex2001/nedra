# Production deployment

Pushes to `main` that change `frontend/**` are deployed by
`.github/workflows/deploy.yml`.

The workflow builds a Next.js standalone release, uploads it to
`/var/www/nedra/releases/<commit-sha>`, switches `/var/www/nedra/current`,
restarts `nedra-frontend`, and checks `http://127.0.0.1:3000/`. If the health
check fails, the previous release is restored. The five newest releases are
kept on the server.

## Required GitHub Actions secrets

- `DEPLOY_HOST`
- `DEPLOY_PORT`
- `DEPLOY_USER`
- `DEPLOY_SSH_KEY`
- `DEPLOY_KNOWN_HOSTS`

The production systemd service must run `/var/www/nedra/current/server.js` as
the `nedra` user. Server-only public verification files can be kept in
`/var/www/nedra/shared/public`; they are copied into every release.
