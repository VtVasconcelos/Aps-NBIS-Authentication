import os
import subprocess, sys
import re
import tempfile
import shutil
import attr
import os.path

def identify(fileName):
    cmd = "./library/bozorth3 -g " + fileName + " ./banco/*.xyt"
    result = os.popen(cmd).read()

    for temp in result.splitlines():
        if(int(temp)>40):
            return True

    return False

def mindtct_from_image(image,path):
    tempdir = tempfile.mkdtemp()
    oroot = os.path.join(tempdir, 'result')
    callMindtct = "./library/mindtct "+ image +" "+ oroot
    try:
        os.popen(callMindtct).read()
        result = ""
        with open(oroot + '.xyt') as fd:
            result = fd.read()
        with open(path+"result.xyt","w") as fd:
            fd.write(result)
            return "result.xyt"
        return "Sucess"

    finally:
        shutil.rmtree(tempdir)