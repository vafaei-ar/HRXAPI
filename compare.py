
import h5py as h5
import numpy as np
import os.path
from glob import glob


class MyClass():
    def __init__(self):
        self.sets = []
    def __call__(self, name, node):
        if isinstance(node, h5.Dataset):
            self.sets.append(node.name)
#        return None

def scan_hdf5(path, recursive=True, tab_step=2, verbose=False, return_file=True):
    allkeys = []
    def scan_node(g, tabs=0):
        if verbose:
            print(' ' * tabs, g.name)
        for k, v in g.items():
            if isinstance(v, h5.Dataset):
                if verbose:
                    print(' ' * tabs + ' ' * tab_step + ' -', v.name)
                allkeys.append(v.name)
            elif isinstance(v, h5.Group) and recursive:
                scan_node(v, tabs=tabs + tab_step)
    if return_file:
        f = h5.File(path, 'r')
        scan_node(f)
        return f,allkeys
    else:
        with h5.File(path, 'r') as f:
            scan_node(f)
        return allkeys

pp = '/drift_prod_hirax_survey/bt/dk_5thresh_fg_10thresh'
pp = '/maps'
pp = ''
dir1 = '1'+pp
dir2 = '0'+pp

files = glob(dir1+'/**/*.hdf5', recursive=True)+glob(dir1+'/**/*.h5', recursive=True)

for fil in files:

#    print(fil)
    fil2 = fil.replace(dir1, dir2, 1)
#    print(fil2)

#    fil2 = fil.replace(dir1)

    if not os.path.exists(fil2):
        print(fil2,'does not exist!')
        continue
        
    f1,keys1 = scan_hdf5(fil, verbose=0)
    f2,keys2 = scan_hdf5(fil2, verbose=0)
#    print(keys1)
#    print(keys2)
    
    assert keys1==keys2, 'Different scan result!'

    for key in keys1:
        x1 = f1[key][()]
        x2 = f2[key][()]
        
        mask = x1==x2
        if len(mask)==0:
            continue

        frac = np.mean(mask)
        if frac!=1 or True:
            print(fil,key)
        
            try:
                x1 = x1.view(np.float).reshape(x1.shape + (-1,))
                x2 = x2.view(np.float).reshape(x2.shape + (-1,))
            except:
                pass
        
            try:
                print(key,np.mean((x1-x2)**2))
            except:
                if np.mean(x1==x2)!=1:
                    print(fil,key)
    #        
#            exit()
        
        
#    f1 = h5.File(fil,'r')
#    M = MyClass()
#    f1.visititems(M)
#    print(M.sets)
    






























