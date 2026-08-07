# Publishing this prepared history

This repository was prepared with four release commits and annotated tags:

- `v1.0.0`
- `v2.0.0`
- `v3.0.0`
- `v4.0.0`

The target GitHub repository was initialized with an empty README, so replacing that initial
commit requires a reviewed force-with-lease push.

```powershell
git fetch origin main
git push --force-with-lease origin main
git push origin --tags
```

Review `git log --oneline --decorate --graph --all` before pushing.
