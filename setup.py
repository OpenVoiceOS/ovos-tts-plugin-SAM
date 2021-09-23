#!/usr/bin/env python3
import os
import subprocess

from setuptools import setup
from setuptools.command.install import install

PLUGIN_ENTRY_POINT = 'ovos-tts-plugin-SAM = ovos_tts_plugin_SAM:SAMTTS'


def compile_and_install_software():
    """Use the subprocess module to compile/install the C software."""
    dest_path = os.path.expanduser('~/.local/bin/')
    if os.path.exists(dest_path + 'sam'):
        return  # binary exists no need to build it
    elif not os.path.exists(dest_path):
        os.mkdir(dest_path)

    print("Fetching SAM")
    # Git clone
    repo = 'https://github.com/vidarh/SAM'
    src_path = '/tmp/SAM'
    subprocess.check_call('git clone {} {}'.format(repo, src_path),
                          shell=True)

    print("Building SAM")
    # compile the software
    subprocess.check_call("make", cwd=src_path, shell=True)

    # install the binary
    cmd = 'cp {}/sam {}'.format(src_path, dest_path)
    subprocess.check_call(cmd, cwd=src_path, shell=True)


class CustomInstall(install):
    """Custom handler for the 'install' command."""

    def run(self):
        compile_and_install_software()
        super().run()


setup(
    name='ovos-tts-plugin-SAM',
    version='0.0.1a1',
    description='SAM tts plugin for mycroft',
    url='https://github.com/OpenVoiceOS/ovos-tts-plugin-SAM',
    author='JarbasAi',
    author_email='jarbasai@mailfence.com',
    license='Apache-2.0',
    packages=['ovos_tts_plugin_SAM'],
    install_requires=["phoneme_guesser",
                      'ovos-plugin-manager>=0.0.1a12'],
    zip_safe=True,
    include_package_data=True,
    cmdclass={'install': CustomInstall},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Linguistic',
        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='mycroft OpenVoiceOS OVOS chatterbox plugin tts',
    entry_points={'mycroft.plugin.tts': PLUGIN_ENTRY_POINT}
)
