# Collection Soleil

Custom static sunglasses catalogue and browser cart.

Build: `python build.py` (Python 3.12). Output: `dist/`.

GitHub Actions builds and checks referenced assets, then deploys successful main-branch builds to Cloudflare Pages project `glasses-website` using repository secrets `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN`.

Live demo: https://glasses-website-aj4.pages.dev/

Orders and payment are not enabled. The n8n campaign pipeline currently stages catalogue changes through a local bridge; automatic repository updates and migration of that bridge to cloud hosting are still pending.
