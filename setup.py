# *****************************************************************************
# Copyright (C) 2022 INAF
# This software is distributed under the terms of the BSD-3-Clause license
#
# Authors:
# Ambra Di Piano <ambra.dipiano@inaf.it>
# *****************************************************************************

import os
import setuptools

scriptsPath = "rtamock"
scripts = [scriptsPath+file for file in os.listdir(scriptsPath)]
for script in scripts:
     print(script)

setuptools.setup( 
     name='rtamock',
     author='Ambra Di Piano <ambra.dipiano@inaf.it>',
     package_dir={'rtamock': 'rtamock'},
     include_package_data=True,
     license='BSD-3-Clause',
)