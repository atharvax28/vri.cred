# VRI Cred

## History
VRI Cred started as a demo-first implementation of an AI-powered SME credit intelligence layer. The project combines a lightweight frontend, a Python backend API, and machine-learning scoring assets to demonstrate practical credit decision support.

## About Us
### What we do
We build credit intelligence capabilities for small and medium enterprise (SME) lending workflows. The platform brings together data ingestion, risk scoring, and report generation so teams can evaluate applicants quickly and consistently.

### Our workflow
1. **Collect and validate inputs** from applicants and internal systems.
2. **Engineer and normalize features** for model-ready scoring.
3. **Run scoring pipelines** to estimate risk and produce decision signals.
4. **Generate reports** for analysts and downstream review.
5. **Serve results through API + frontend** for operational use.

## Environment File Encryption
Environment template files in `demo/backend` were also exported to encrypted **ASCII-armored** artifacts (text-safe for PR tools):

- `demo/backend/.env.example.enc.txt`
- `demo/backend/.env.local.example.enc.txt`

You can decrypt with OpenSSL:

```bash
openssl enc -d -aes-256-cbc -pbkdf2 -a -in <file>.enc.txt -out <file> -pass pass:'VRI_CRED_CHANGE_ME'
```

> Replace the passphrase with your own secure secret in real deployments.
