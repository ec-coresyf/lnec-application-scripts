import fnmatch
import glob
import os
import zipfile


class ProductSelector:
    def __init__(self, glob_selector):
        self.selector = glob_selector

    def isproduct(self, filepath):
        if not os.path.exists(filepath):
            raise Exception("File not found")
        if zipfile.is_zipfile(filepath):
            with zipfile.ZipFile(filepath, 'r') as z:
                namelist = [n for n in z.namelist() if fnmatch.fnmatch(n, self.selector)]
                if len(namelist) > 1:
                    raise Exception("Invalid product selector or product archive: more than one file is being selected")
                return len(namelist) == 1
        elif os.path.isfile(filepath):
            return True
        elif os.path.isdir(filepath):
            files = glob.glob(os.path.join(filepath, self.selector))
            if len(files) > 1:
                raise Exception("Invalid product selector or product archive: more than one file is being selected")
            return len(files) == 1

    def openproduct(self, filepath):
        if not os.path.exists(filepath):
            raise Exception("File not found")
        if zipfile.is_zipfile(filepath):
            with zipfile.ZipFile(filepath, 'r') as z:
                namelist = [n for n in z.namelist() if fnmatch.fnmatch(n, self.selector)]
                if not namelist:
                    raise Exception("Invalid product selector or product archive: no file is being selected")
                if len(namelist) > 1:
                    raise Exception("Invalid product selector or product archive: more than one file is being selected")
                z.extractall()
                return namelist[0]
        elif os.path.isfile(filepath):
            return filepath
        elif os.path.isdir(filepath):
            files = glob.glob(os.path.join(filepath, self.selector))
            if not files:
                raise Exception("Invalid product selector or product archive: no file is being selected")
            if len(files) > 1:
                raise Exception("Invalid product selector or product archive: more than one file is being selected")
            return files[0]
