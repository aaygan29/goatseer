# Queued GitHub actions

Actions that need a human-in-the-loop decision or a MCP connector that this
session cannot reach. Everything here should either become a live issue, a PR,
or an ADR retiring it.

## Immediate (blocked on `plugin:engineering:github` connector)

The `gh` CLI is authenticated in this environment, so most of these can now
proceed. This file exists so nothing gets forgotten if a future tick loses
that access.

- [ ] Enable Issues and Projects on `aaygan29/NEW_REPO` if they are not on by
      default. `gh repo edit --enable-issues --enable-projects`.
- [ ] After merge, create labels: `lit-review`, `gate-fail`, `instrument`,
      `retirement`, `blocked-on-auth`, `synthetic-first`.
- [ ] For each portfolio project, open a tracking issue titled
      "[<slug>] first evaluation pass" linked to `portfolio/<slug>/evaluation.md`.

## Requires user action (Aayush)

- [ ] Confirm final program name (currently working title NEUROSPINE, repo
      slug NEW_REPO). If renaming the repo, use `gh repo rename` and update
      the git remote.
- [ ] Decide license: keep Unlicense (public domain, current) or switch to
      MIT per the original brief. See `decisions/ADR-001`.
- [ ] Authorize `plugin:engineering:github` in an interactive session if the
      MCP-mediated flow is preferred over `gh` CLI.
- [ ] Grant access to the private repos this program will PR against:
      `aaygan29/behavioral_decoding`, `aaygan29/decision-phenotype`,
      `aaygan29/jspace-loyalty`. Confirm each remains reachable via `gh`.
- [ ] Authorize `plugin:productivity:notion` and `plugin:productivity:linear`
      if issue mirroring or roadmap sync is desired. Not required to run.

## Nice-to-have

- [ ] Wire a GitHub Action to render the weekly report from
      `portfolio/*/evaluation.md` deltas.
- [ ] Add a CODEOWNERS file once the instrument has real code.
