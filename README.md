# palmcore-cmms
One day, day one

## Deployment

Development environment:
- `docker compose -f docker/development/docker-compose.yml up --build`

Production environment:
- `docker compose -f docker/production/docker-compose.prod.yml up -d --build`

Notes:
- `docker/nginx/default.conf` includes HTTPS/Let’s Encrypt placeholders and expects valid certs under `/etc/letsencrypt`.
- Update `.env.production`, `.env.staging`, and `.env.development` with your real secrets before deploying.
- The frontend production container uses `apps/frontend/Dockerfile.prod` and serves the built SPA through Nginx.
