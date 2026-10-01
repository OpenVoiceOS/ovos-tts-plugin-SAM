"""The module imports with no `distutils`.

`distutils` is removed from the standard library in Python 3.12. The module
imported `find_executable` from it at module level, so on 3.12 and later the
plugin did not import at all unless `setuptools`, which ships a copy of
`distutils`, happened to be installed. `shutil.which` is the standard-library
replacement and needs no such luck.
"""
import shutil
import subprocess
import sys
import unittest
from os.path import expanduser


class TestNoDistutils(unittest.TestCase):
    """The real build never runs from this file.

    `compile_and_install_software` runs `git clone` and `make` against a fixed
    shared path, `/tmp/SAM`, and installs into `~/.local/bin`. A unit test must
    not do that: it needs the network, it races every other run on the host,
    and it writes the home directory of whoever runs the suite. The class
    method is replaced for every test here by one that fails instead of
    building, so an edit that reaches the build is a red test and not a silent
    clone. A test that means to reach the lookup's end puts its own recorder on
    the instance, which shadows this one.
    """

    def setUp(self):
        from ovos_tts_plugin_SAM import SAMTTS

        def refuse():
            raise AssertionError(
                "compile_and_install_software ran for real in a unit test")

        # The class attribute is read and written through `__dict__`, not
        # through the class. `compile_and_install_software` is a staticmethod,
        # and `SAMTTS.compile_and_install_software` hands back the plain
        # function the descriptor wraps; writing that back on tearDown would
        # leave a plain function on the class, which then takes `self` as its
        # first argument and raises TypeError for every later test that builds
        # an instance. `__dict__` carries the descriptor itself.
        self._real_build = SAMTTS.__dict__["compile_and_install_software"]
        SAMTTS.compile_and_install_software = staticmethod(refuse)

    def tearDown(self):
        from ovos_tts_plugin_SAM import SAMTTS
        SAMTTS.compile_and_install_software = self._real_build

    def test_module_does_not_import_distutils(self):
        # `distutils` must not reach the module by any path, not even an
        # indirect one. The check runs in its own interpreter, which imports
        # the module and nothing else, because `sys.modules` in this process
        # says what the whole test session imported: `import setuptools` alone
        # puts `distutils` there, so asserting on this process would go red for
        # a conftest or a pytest plugin that never touched the module.
        code = ("import ovos_tts_plugin_SAM, sys\n"
                "print('distutils' in sys.modules)\n")
        proc = subprocess.run([sys.executable, "-c", code],
                              capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "False", proc.stdout)

    def test_the_check_above_reads_a_clean_interpreter(self):
        # The control for the control. If `python -c` already carried
        # `distutils`, through a .pth file or a site hook, the test above would
        # be a false red and this one says so first.
        code = "import sys; print('distutils' in sys.modules)"
        proc = subprocess.run([sys.executable, "-c", code],
                              capture_output=True, text=True, check=False)
        self.assertEqual(proc.stdout.strip(), "False", proc.stdout)

    def test_import_without_distutils_in_a_subprocess(self):
        # `distutils` is blocked by name, which is the state of a Python 3.12
        # or later interpreter with no `setuptools` installed
        code = (
            "import sys\n"
            "class Block:\n"
            "    def find_spec(self, name, path=None, target=None):\n"
            "        if name == 'distutils' or name.startswith('distutils.'):\n"
            "            raise ImportError('no distutils')\n"
            "        return None\n"
            "sys.meta_path.insert(0, Block())\n"
            "import ovos_tts_plugin_SAM\n"
            "print('ok')\n"
        )
        proc = subprocess.run([sys.executable, "-c", code],
                              capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("ok", proc.stdout)

    def test_which_is_the_lookup(self):
        """`_find_binary` asks `shutil.which`, and the test stays offline.

        The lookup ends in `compile_and_install_software`, which runs
        `git clone https://github.com/vidarh/SAM /tmp/SAM` and then `make`. So
        the build is replaced by a recorder on the instance: nothing reaches
        the network, nothing writes `/tmp/SAM`, and nothing installs a binary
        into the home directory of whoever runs the suite. No exception is
        swallowed either, so a real error inside the lookup fails the test.
        """
        from ovos_tts_plugin_SAM import SAMTTS
        seen = []
        built = []

        def fake_which(name):
            # shutil.which answers None when the binary is absent, and an
            # implicit None is that same answer.
            seen.append(name)

        # The candidate list is [configured, shutil.which("sam"),
        # expanduser("~/.local/bin/sam")]. Neutralising only the second leaves
        # the THIRD answering from the real home directory: any machine that has
        # run this plugin once has ~/.local/bin/sam, because
        # compile_and_install_software writes exactly there, and the lookup then
        # returns it instead of asking for the build. Reproduced: with such a
        # file present this test failed, "Lists differ: [] != [True]", and
        # passed on a clean home. With isfile held to False all three candidates
        # decline, so the test measures the lookup and not the host.
        import ovos_tts_plugin_SAM as sam_module
        original = shutil.which
        original_isfile = sam_module.isfile
        shutil.which = fake_which
        sam_module.isfile = lambda path: False
        try:
            tts = SAMTTS.__new__(SAMTTS)
            tts.config = {"binary": None}
            tts.compile_and_install_software = lambda: built.append(True)
            found = tts._find_binary()
        finally:
            shutil.which = original
            sam_module.isfile = original_isfile

        self.assertEqual(seen, ["sam"])
        # no candidate answered, so the lookup asked for the build and then
        # returned the path the build installs to
        self.assertEqual(built, [True])
        self.assertEqual(found, expanduser("~/.local/bin/sam"))



if __name__ == "__main__":
    unittest.main()
