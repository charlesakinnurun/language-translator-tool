# Security Policy

## Reporting a vulnerability

If you discover a security issue in **Language Translation Tool**, please
**do not** open a public issue. Instead, email
[charlesakinnurun@gmail.com](mailto:charlesakinnurun@gmail.com) with:

- a description of the vulnerability and where it is located,
- steps to reproduce it,
- the impact you believe it has.

You will receive a response promptly. Please allow time for a fix before
disclosing the issue publicly.

## Security posture

- **Credentials** are environment-only. Google Cloud credentials are read by
  the backend from `GOOGLE_APPLICATION_CREDENTIALS` / Application Default
  Credentials and are never committed, logged, or returned to clients.
- **Client isolation.** The frontend never knows about or receives secrets; it
  only talks to our backend over the documented API.
- **Input hardening.** Requests are validated and normalized (trimming,
  length caps, language whitelists) before any provider call.
- **Error hygiene.** Internal provider details are logged server-side for
  debugging; clients receive only generic, code-based error messages.
- **Abuse protection.** Per-client rate limiting (with a Redis-ready design)
  and CORS restrictions protect the API.

## Reporting credentials exposure

If you believe an API key or service-account file may have been exposed in
this repository (history included), treat it as a confidentiality incident:
rotate the affected credentials immediately and report it using the same
contact above.