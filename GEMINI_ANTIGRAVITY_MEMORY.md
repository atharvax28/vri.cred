# Gemini “Antigravity Memory” — Always persist context

## Directive (keep following)

If you (Gemini / Claude / any model) **run out of credits**, are **interrupted**, or must stop mid-task:

1. **Automatically create or update** `CONTINUE.md` at the repo root.
2. Ensure `CONTINUE.md` includes, at minimum:
   - What was accomplished in this session
   - Current workspace state (which component, what environment)
   - All relevant file paths changed/added
   - Any errors encountered (include exact error messages)
   - Exact next commands to run
   - Next tasks / TODOs (short, actionable)

## Canonical handoff file

- `CONTINUE.md` is the single source of truth for “what happened till now”.

