# Contributing to Language Translation Tool

We welcome contributions from everyone. By participating, you agree to abide
by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to contribute

1. **Open an issue** describing the bug, feature, or improvement you want to
   work on - or comment on an existing one so it is assigned to you.
2. **Fork** the repository and create a feature branch:

   ```bash
   git checkout -b feat/your-feature-name
   ```

3. **Implement** your change, keeping the existing architecture and
   conventions in mind:
   - Backend logic goes in `backend/app/` following the layered structure
     (config / schemas / services / providers / api).
   - New translation backends implement the `TranslationProvider` interface in
     `backend/app/services/providers/`.
   - Frontend components live in `frontend/src/components/`; hooks encapsulate
     behaviour; API calls go through `frontend/src/services/`.
4. **Add or update tests** in `backend/tests/` (pytest) and
   `frontend/src/__tests__/` (Vitest) for every change.
5. **Verify everything passes**:

   ```bash
   # Backend (from backend/)
   pytest

   # Frontend (from frontend/)
   npm run typecheck
   npm test
   npm run build
   ```

6. **Commit** with a clear, conventional message (e.g. `feat: add Azure
   provider`, `fix: reject whitespace-only input`).
7. **Open a pull request** to `main`, describing the change, the tests added,
   and any configuration or environment variables introduced.

## Rules of thumb

- **No secrets.** Never commit `.env` files, keys, or credentials. Use the
  `.env.example` templates for anything new.
- **Meaningful error handling.** New failure modes must map to the existing
  error `code` conventions in `backend/app/core/exceptions.py`.
- **Keep scope tight.** Prefer focused PRs over large rewrites.
- **Document changes.** Update the README and `.env.example` when behaviour or
  configuration changes.

## Code of conduct

Be respectful, constructive, and inclusive. Harassment of any kind is not
acceptable. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).