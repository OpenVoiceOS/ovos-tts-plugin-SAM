# AGENTS.md — ovos-tts-plugin-SAM

OVOS TTS plugin wrapping S.A.M (Software Automatic Mouth), a tiny C speech synthesizer (C64-era, reverse-engineered from https://github.com/vidarh/SAM). English-only, fully offline, retro robotic voice presets.

## Setup
```bash
pip install .
```
At runtime the plugin needs a `sam` binary. If absent, `SAMTTS.compile_and_install_software()` git-clones vidarh/SAM into `/tmp/SAM`, runs `make`, and copies the binary to `~/.local/bin/sam`. The Dockerfile builds the binary into `/usr/bin/sam` and runs it behind `ovos-tts-server`.

## Test
No test suite exists. `build_tests.yml` only builds sdist/wheel and `pip install .`. There is no unit test command.

## Lint/Typecheck
None configured.

## Layout
- `ovos_tts_plugin_SAM/__init__.py` — the whole plugin: `SAMTTS` (TTS engine, shells out to the `sam` binary with pitch/speed/mouth/throat args), `SAMTTSValidator`, and `SAMTTSPluginConfig` (voice presets: SAM, elf, little robot, stuffy guy, little old lady, extra-terrestrial).
- `setup.py` — packaging.
- `Dockerfile` — builds the C binary and serves via `ovos-tts-server`.
- Entry-point group: `mycroft.plugin.tts` -> `SAMTTS`; config samples under `mycroft.plugin.tts.config`.

## Conventions (Org hard rules)
- Branches: work on `dev`, stable is `master`. NEVER `main`.
- Never edit version files; gh-automations bumps semver from conventional-commit prefixes (`feat:`/`fix:`/`feat!:`).
- New repos private by default.
- Commit identity: JarbasAi <jarbasai@mailfence.com>.
- Reference `OpenVoiceOS/gh-automations` reusable workflows at `@dev`.
- No Neon / `neon-*` references.
- No meta-commentary (no history, no dates) in code, docs, commits, or PRs — describe current state only.
- CI is provided by `OpenVoiceOS/gh-automations`.

## Gotchas
- `setup.py` version is `0.0.1` and `install_requires=['ovos-plugin-manager>=0.0.1a12']`, while `requirements.txt` pins `ovos-plugin-manager>=2.1.0,<2.2.0`. The two disagree — the runtime/CI uses the requirements pin.
- `from distutils.spawn import find_executable` — `distutils` is removed in Python 3.12+, yet `build_tests.yml` runs on Python 3.14. Import will fail on modern Python.
- Network + compiler side effects at construction time (git clone + `make`) make the engine non-hermetic; first run needs git, make, and a C toolchain.
- Custom Docker/dev2master workflows are bespoke, not the standard gh-automations set.
- License is intentionally unspecified (upstream SAM is abandonware); `setup.py` still declares `Apache-2.0`.
