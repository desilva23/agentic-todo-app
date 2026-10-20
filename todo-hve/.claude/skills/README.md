# Skills for Claude Code

These folders are **byte-identical copies** of `.github/skills/rpi/*` (the HVE Core originals). Claude Code only discovers skills
under `.claude/skills/` and does not follow symlinks, so they are copied. `.github/skills/rpi/` stays the canonical HVE layout
(what GitHub Copilot reads). To re-sync after changing an original: `cp -R .github/skills/rpi/<name> .claude/skills/`, and check with
`diff -r .claude/skills .github/skills/rpi` (this README is the only expected difference).
