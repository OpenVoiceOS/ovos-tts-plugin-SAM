# TODO — ovos-tts-plugin-SAM

## Open issues
- [ ] #8 Dependency Dashboard (Renovate)

## Gaps
- [ ] No test suite; `build_tests.yml` only builds + installs, runs no tests.
- [ ] Missing standard gh-automations CI: no `build-tests` reusable call, no `coverage`, `license-check`, `release_workflow`, `publish_stable`. Has bespoke `build_tests.yml`, `dev2master.yml`, `docker_tests.yml`, `publish_docker.yml` instead.
- [ ] No `opm-check` despite declaring an OPM TTS plugin entry point (`mycroft.plugin.tts`).
- [ ] Packaging uses `setup.py` (no `pyproject.toml`); version pinned at `0.0.1`.
- [ ] Dependency mismatch: `setup.py` `ovos-plugin-manager>=0.0.1a12` vs `requirements.txt` `>=2.1.0,<2.2.0`.
- [ ] `distutils.spawn.find_executable` import breaks on Python 3.12+; CI targets Python 3.14.
- [ ] `setup.py` classifiers list Python 2.7 / 3.0–3.6 — stale and inaccurate.
- [ ] Committed artifacts: `ovos_tts_plugin_SAM.egg-info/` and `sam.wav` scratch output checked into the repo.
- [ ] No mediavocab usage (not applicable to a binary-shelling TTS engine).

## Code TODOs
- [ ] `ovos_tts_plugin_SAM/__init__.py:107` — `# TODO validate voice is valid`
