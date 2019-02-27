# Copyright (C) iNuron - info@openvstorage.com
# This file is part of Open vStorage. For license information, see <LICENSE.txt>

import sys
import os.path
import inspect

def stop_nose():
    '''Stop nose from executing this module while looking for doctests'''

    import traceback

    stack = ''.join(traceback.format_stack())

    if 'nose/importer.py' in stack:
        import nose

        raise nose.SkipTest(
            'Nothing to test in %s' % os.path.basename(__file__))

stop_nose()
del stop_nose

import paver.setuputils
paver.setuputils.install_distutils_tasks()

from paver.easy import Bunch, needs, options, path, task

src = os.path.abspath(os.path.dirname(__file__))
if src not in sys.path:
    sys.path.insert(0, src)
del src

import pyrakoon

assert os.path.abspath(os.path.dirname(__file__)) == \
    os.path.abspath(os.path.join(os.path.dirname(
        inspect.getfile(pyrakoon)), '..'))

options(
    setup=Bunch(
        name='pyrakoon',
        version=pyrakoon.__version__,
        author=pyrakoon.__author__,
        author_email='nicolas@incubaid.com',
        description='Python Arakoon client',
        license=pyrakoon.__license__,
        url='http://www.arakoon.org',

        platforms=('Any', ),

        packages=[
            'pyrakoon',
            'pyrakoon.client',
            'pyrakoon.protocol',
        ],

        test_suite = 'nose.collector',
    ),

    sphinx=Bunch(
        docroot='doc',
        builddir='_build',
    ),

    minilib=Bunch(
        extra_files=['doctools', ],
    ),
)


@task
@needs('generate_setup', 'minilib', 'doc', 'setuptools.command.sdist')
def sdist():
    '''Build source package'''
    pass



@task
@needs('paver.doctools.html')
def sphinx():
    '''Build and move the Sphinx documentation'''
    builtdocs = path(options.sphinx.docroot) / options.sphinx.builddir / 'html'
    destdir = path('dist') / 'doc'
    destdir.rmtree()
    builtdocs.move(destdir)

@task
def epydoc():
    '''Build and move the EpyDoc API documentation'''
    from epydoc import cli

    old_argv = tuple(sys.argv)

    try:
        sys.argv[:] = ['', '--config', 'epydocrc', ]

        options, names = cli.parse_arguments()
    finally:
        sys.argv[:] = old_argv

    options.target = path('dist') / 'doc' / 'api'
    options.target.rmtree()
    options.target.makedirs()

    options.configfiles = ('epydocrc', )

    options.verbosity = options.verbosity or 1

    cli.main(options, ('pyrakoon', ))

@task
@needs('sphinx', 'epydoc')
def doc():
    '''Build all documentation'''
    pass


@task
def lint():
    '''Run pylint'''

    from pylint import lint

    args = ['--rcfile=pylintrc', 'pyrakoon', ]
    lint.Run(args)


@task
def lettuce():
    '''Run Lettuce'''

    import lettuce.lettuce_cli

    specs_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'test', 'features'))

    orig_sys_argv = tuple(sys.argv)

    sys.argv[:] = ['lettuce', specs_dir]
    try:
        lettuce.lettuce_cli.main([specs_dir])
    finally:
        sys.argv[:] = orig_sys_argv

@task
@needs('lettuce', 'paver.test')
def test():
    '''Run the test suite'''
