# Copyright (c) Charl P. Botha, TU Delft.
# All rights reserved.
# See COPYRIGHT for details.

import config
from install_package import InstallPackage
import os
import shutil
import sys
import utils

# NB: for this module to build successfully, ITK has to be built with
#     ITK_USE_REVIEW=ON (until the itkFlatStructuringElement moves OUT of the
#     review directory, that is)

BASENAME = "itktudoss"
SVN_REPO = "http://itktudoss.googlecode.com/svn/trunk/"
SVN_REL = 9

dependencies = ['CMake', 'ITK', 'WrapITK', 'SWIG']

class ITKTUDOSS(InstallPackage):
    
    def __init__(self):
        self.source_dir = os.path.join(config.archive_dir, BASENAME)
        self.build_dir = os.path.join(config.build_dir, '%s-build' %
                                      (BASENAME,))

    def get(self):
        if os.path.exists(self.source_dir):
            utils.output("itktudoss already checked out, skipping step.")

        else:
            os.chdir(config.archive_dir)
            ret = os.system("%s co %s %s -r%s" % (config.SVN,
                SVN_REPO, BASENAME, SVN_REL))
            if ret != 0:
                utils.error("Could not SVN checkout.  Fix and try again.")

    def unpack(self):
        # no unpack step
        pass

    def configure(self):
        if os.path.exists(
            os.path.join(self.build_dir, 'CMakeFiles/cmake.check_cache')):
            utils.output("itktudoss build already configured.")
            return
        
        if not os.path.exists(self.build_dir):
            os.mkdir(self.build_dir)

        # we need the PATH types for VTK_DIR and for WrapITK_DIR, else
        # these variables are NOT stored.  That's just weird.
        # we also need to pass the same instal prefix as for WrapITK, so
        # that the external module can be put in the right place.
        cmake_params = "-DBUILD_WRAPPERS=ON " \
                       "-DCMAKE_BUILD_TYPE=RelWithDebInfo " \
                       "-DCMAKE_INSTALL_PREFIX=%s " \
                       "-DITK_DIR=%s " \
                       "-DITK_TEST_DRIVER=%s " \
                       "-DWrapITK_DIR:PATH=%s " \
                       "-DSWIG_DIR=%s " \
                       "-DSWIG_EXECUTABLE=%s " \
                       "-DPYTHON_EXECUTABLE=%s " \
                       "-DPYTHON_LIBRARY=%s " \
                       "-DPYTHON_INCLUDE_PATH=%s " \
                        % \
                       (config.WRAPITK_TOPLEVEL,
                        config.ITK_DIR, config.ITK_TEST_DRIVER,
                        config.WRAPITK_DIR,
                        config.SWIG_DIR, config.SWIG_EXECUTABLE,
                        config.PYTHON_EXECUTABLE,
                        config.PYTHON_LIBRARY,
                        config.PYTHON_INCLUDE_PATH)

        ret = utils.cmake_command(self.build_dir, self.source_dir,
                cmake_params)

        if ret != 0:
            utils.error(
                "Could not configure itktudoss.  Fix and try again.")


    def build(self):
        posix_file = os.path.join(self.build_dir, 
                'lib/_itktudossPython.so')
        nt_file = os.path.join(self.build_dir, 'lib',
                config.BUILD_TARGET, 
                '_itktudossPython' + config.PYE_EXT)

        if utils.file_exists(posix_file, nt_file):    
            utils.output("itktudoss already built.  Skipping build step.")

        else:
            os.chdir(self.build_dir)
            ret = utils.make_command('ITKTUDOSS.sln')

            if ret != 0:
                utils.error("Could not build itktudoss.  Fix and try again.")
        

    def install(self):
        if os.path.exists(
            os.path.join(config.WRAPITK_LIB, 
                '_itktudossPython' + config.PYE_EXT)):
            utils.output("itktudoss already installed.  Skipping step.")

        else:
            os.chdir(self.build_dir)
            ret = utils.make_command('itktudoss.sln', install=True)

            if ret != 0:
                utils.error(
                    "Could not install itktudoss.  Fix and try again.")

 
    def clean_build(self):
        # nuke the build dir, the source dir is pristine and there is
        # no installation
        utils.output("Removing build dir.")
        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)

        inst_so = os.path.join(config.WRAPITK_LIB, '_itktudossPython.so')
        if os.path.exists(inst_so):
            os.remove(inst_so)


    def get_installed_version(self):
        return "NA"

