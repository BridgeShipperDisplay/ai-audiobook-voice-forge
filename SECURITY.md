# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.6.x   | yes       |
| 0.5.x   | security fixes only |
| < 0.5   | no        |

## Reporting a vulnerability

Do not open a public issue for security problems. Email
`security@voiceforge.dev` with:

- A description of the issue and its impact.
- Reproduction steps on a clean Windows 10/11 box.
- The version string from `python -m voiceforge.bootstrap --version`.

We acknowledge within 72 hours and aim for a fix in the next patch release.

## Threat model

This tool runs local TTS models and reads user-supplied manuscript files.
The realistic attack surface is:

1. **Malicious EPUB/PDF parsing** — we sandbox document parsing in a
   subprocess with a 512 MB memory cap and a 30-second wall clock. Report
   any file that escapes that.
2. **Voice profile loading** — `embeddings.npz` is loaded with
   `allow_pickle=False`. Any profile that requires pickle is rejected.
3. **Cloud fallback API keys** — stored via Windows Credential Manager
   (`keyring`), never on disk in plaintext. If you find a code path that
   writes a key to a config file, that's a security bug.
4. **Model download** — all model fetches are HTTPS with pinned SHA-256
   hashes in `voiceforge/services/model_registry.py`. No unverified URLs.

## Out of scope

- Audio quality complaints. That's a model issue, not a security issue.
- Denial of service via a 4 GB manuscript. We cap input at 50 MB and
  document it.