"""The binary is resolved at the first synthesis, not in `__init__`.

`__init__` called `_find_binary`, which builds the C program from source when
no usable binary is on the system. The plugin manager constructs the class
before it calls `validator.validate()`, so on a host with no compiler the
build error replaced the validator's message: a caller that asked for a
language SAM does not speak saw `make` exit 127, not "only supports english".

Every test here runs in that state: no usable binary, and a build that fails.
"""
import subprocess
import unittest
from unittest.mock import patch

from ovos_tts_plugin_SAM import SAMTTS


def _no_toolchain():
    """Patches for a host with no SAM binary and no C compiler."""
    return [
        # no candidate on PATH or in ~/.local/bin answers the vidarh interface
        patch.object(SAMTTS, "_is_vidarh_sam", staticmethod(lambda binary: False)),
        # and the build cannot run: this is `make` missing, exit 127
        patch.object(SAMTTS, "compile_and_install_software",
                     staticmethod(lambda: (_ for _ in ()).throw(
                         subprocess.CalledProcessError(127, "make")))),
    ]


class TestLazyBinary(unittest.TestCase):
    def setUp(self):
        for p in _no_toolchain():
            p.start()
            self.addCleanup(p.stop)

    def test_init_does_not_build(self):
        tts = SAMTTS(config={"lang": "en-us", "binary": "/nonexistent/sam"})
        self.assertIsNone(tts._binary)

    def test_binary_still_builds_at_first_use(self):
        # the control: without this, the two other tests could pass because
        # the patches did nothing
        tts = SAMTTS(config={"lang": "en-us", "binary": "/nonexistent/sam"})
        with self.assertRaises(subprocess.CalledProcessError):
            _ = tts.binary

    def test_factory_reports_the_language_not_the_build(self):
        from ovos_plugin_manager.tts import OVOSTTSFactory
        with self.assertRaises(Exception) as ctx:
            OVOSTTSFactory.create({"module": "ovos-tts-plugin-SAM",
                                   "lang": "pt-PT",
                                   "ovos-tts-plugin-SAM": {
                                       "binary": "/nonexistent/sam"}})
        self.assertNotIsInstance(ctx.exception, subprocess.CalledProcessError)
        self.assertIn("english", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
