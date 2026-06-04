# Contributing to singularity-session

## Development setup

```bash
git clone https://github.com/singularityos-lab/singularity-session
cd singularity-session
meson setup build
meson install -C build
```

## Code style

- Shell: POSIX-friendly `bash`, 4-space indentation, no trailing whitespace.
- Keep the launchers prefix-relative: never hardcode an install path.

## License

By contributing you agree your code will be released under [GPL-3.0-only](LICENSE).

## Commit messages

Commits follow Conventional Commits:

```
<type>: <subject>
```

`<type>` is one of `feat`, `fix`, `chore`, `docs`, `build`, `ci`, `refactor`, `perf`, `style`, `test`, `revert`. Keep `<subject>` short, lowercase and in English. An optional scope is allowed: `<type>(<scope>): <subject>`.

When a commit closes an issue, use `<type>[closes #ID]: <issue title>`, for example:

```
fix[closes #2]: Discord doesn't open on Singularity desktop
```

Do not add co-author or attribution trailers.
