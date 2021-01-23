#!/usr/bin/env python

# === Start Python 2/3 compatibility
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.builtins import *  # noqa  pylint: disable=W0401, W0614
from future.builtins.disabled import *  # noqa  pylint: disable=W0401, W0614
# === End Python 2/3 compatibility

import subprocess
import yaml
from copy import deepcopy
import numpy as np
import os
import time
from sys import argv
from drift.core import manager
from caput.pipeline import Manager

class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)

def ysave(yconf,fname=None):
    if fname is None:
        idr = np.random.randint(10000000)
        fname = 'temp{}.yaml'.format(idr)
    with open(fname, 'w') as f:
        yaml.dump(yconf, f, Dumper=MyDumper, default_flow_style=False)
    return fname

def ch_mkdir(directory):
    """
    ch_mkdir : This function creates a directory if it does not exist.

    Arguments:
        directory (string): Path to the directory.

    --------
    Returns:
        null.		
    """
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except:
            print('could not make the directory!')


def savelog(configfile,dest_path):
    tt = time.strftime("%Y-%m-%d-%H:%M:%S")
    os.replace(configfile,dest_path+tt)

class SimPipline:
    def __init__(self,prefix,
                  pointing_start,pointing_stop,npointings,
                  lmax,mmax,nside,
                  ndays,grid_size,
                  freqstart,freqend,nchannels,
                  thresh_list):
                  
        fname = 'template.yaml'
        with open(fname, "r") as f:
            self.yconf = yaml.safe_load(f)
            
        self.yconforig = deepcopy(self.yconf)

        self.prefix = prefix
        self.pointing_start = pointing_start
        self.pointing_stop = pointing_stop
        self.npointings = npointings
        self.lmax = lmax
        self.mmax = mmax
        self.nside = nside
        self.ndays = ndays
        self.grid_size = grid_size
        self.freqstart = freqstart
        self.freqend = freqend
        self.nchannels = nchannels
        
        self.thresh_list = thresh_list
        
        ch_mkdir(self.prefix+'/logs/')

    def dritf_init(self,prod_dir=None):
        self.yconf = deepcopy(self.yconforig)
        
        if prod_dir is None:
            prod_dir = self.prefix+'drift_prod_hirax_survey'        
        self.prod_dir = prod_dir
        
        self.yconf['config']['output_directory'] = self.prod_dir
        self.yconf['telescope']['pointing_start'] = self.pointing_start
        self.yconf['telescope']['pointing_stop'] = self.pointing_stop
        self.yconf['telescope']['npointings'] = self.npointings
        self.yconf['telescope']['hirax_spec']['lmax'] = self.lmax
        self.yconf['telescope']['hirax_spec']['mmax'] = self.mmax
        self.yconf['telescope']['hirax_spec']['ndays'] = self.ndays
        self.yconf['telescope']['hirax_spec']['hirax_layout']['grid_size'] = self.grid_size
        self.yconf['telescope']['hirax_spec']['freq_lower'] = self.freqstart
        self.yconf['telescope']['hirax_spec']['freq_upper'] = self.freqend
        self.yconf['telescope']['hirax_spec']['num_freq'] = self.nchannels

        d1_temp = deepcopy(self.yconf['kltransform'][0])
        d2_temp = deepcopy(self.yconf['psfisher'][0])

        self.yconf['kltransform'] = []
        self.yconf['psfisher'] = []
        for kltrech,fgtrech,pstrech in self.thresh_list:

            klname = 'dk_{}thresh_fg_{}thresh'.format(kltrech,fgtrech)
            
            d1 = deepcopy(d1_temp)
            d1['name'] = klname
            d1['threshold'] = kltrech
            d1['foreground_threshold'] = fgtrech
            self.yconf['kltransform'].append(d1)
            
            d2 = deepcopy(d2_temp)
            d2['name'] = 'psmc_{}_1threshold'.format(klname,pstrech)
            d2['klname'] = klname
            d2['threshold'] = pstrech
            self.yconf['psfisher'].append(d2)


    def beamtransfers(self):
        self.dritf_init()

        self.yconf['config']['beamtransfers'] = True
        self.yconf['config']['kltransform'] = False
        self.yconf['config']['psfisher'] = False
        configfile = ysave(self.yconf)
        m = manager.ProductManager.from_config(configfile)
        m.generate()
#        os.remove(configfile)
        savelog(configfile,self.prefix+'/logs/')
        del m

    def kltransform(self):
        self.dritf_init()

        self.yconf['config']['beamtransfers'] = False
        self.yconf['config']['kltransform'] = True
        self.yconf['config']['psfisher'] = False
        configfile = ysave(self.yconf)
        m = manager.ProductManager.from_config(configfile)
        m.generate()
#        os.remove(configfile)
        savelog(configfile,self.prefix+'/logs/')
        del m

    def psfisher(self):
        self.dritf_init()

        self.yconf['config']['beamtransfers'] = False
        self.yconf['config']['kltransform'] = False
        self.yconf['config']['psfisher'] = True
        configfile = ysave(self.yconf)
        m = manager.ProductManager.from_config(configfile)
        m.generate()
#        os.remove(configfile)
        savelog(configfile,self.prefix+'/logs/')
        del m
        
    def telescope_init(self):
        self.dritf_init()

        self.yconf['config']['beamtransfers'] = True
        self.yconf['config']['kltransform'] = True
        self.yconf['config']['psfisher'] = True
        configfile = ysave(self.yconf) 
        m = manager.ProductManager.from_config(configfile)
        m.generate()
#        os.remove(configfile)
        savelog(configfile,self.prefix+'/logs/')
        del m

    def make_maps(self,mode='21cm',output_root=None):
    
        if output_root is None:
            ch_mkdir(self.prefix+'/maps/')
            output_root = self.prefix+'/maps/'+mode+'.h5'
        else:
            output_root = output_root+'/'+mode+'.h5'

    #'cora-makesky --nside {} --freq {} {} {} --freq-mode edge --pol full --filename {} {}'.format(nside,freqstart,freqend,nchannels,fname,mode)
        
        subprocess.run(['cora-makesky',
                        '--nside',
                        str(self.nside),
                        '--freq',
                        str(self.freqstart),
                        str(self.freqend),
                        str(self.nchannels),
                        '--freq-mode',
                        'edge',
                        '--pol',
                        'full',
                        '--filename',
                        str(output_root),
                        str(mode)])

    def gen_vis(self,files,output_root):
        
#        files = [self.prefix+'21cm.h5']
#        output_root = self.prefix+'draco/sstream_signal_'
    
        self.dritf_init()

        self.yconf['pipeline'] = deepcopy(self.yconf['pipeline_vis'])
        self.yconf['pipeline']['tasks'][1]['params']['product_directory'] = self.prod_dir
        self.yconf['pipeline']['tasks'][2]['params']['type'] = 'draco.core.io.LoadMaps'
        self.yconf['pipeline']['tasks'][2]['params']['type'] = 'map'
        self.yconf['pipeline']['tasks'][2]['params']['maps'] = [{'files': files}]
        self.yconf['pipeline']['tasks'][3]['params']['type'] = 'draco.synthesis.stream.SimulateSidereal'
        self.yconf['pipeline']['tasks'][3]['params']['requires'] = 'pm'
        self.yconf['pipeline']['tasks'][3]['params']['in'] = 'map'
        self.yconf['pipeline']['tasks'][3]['params']['out'] = 'sstream'
        self.yconf['pipeline']['tasks'][3]['params']['ndays'] = self.ndays
        self.yconf['pipeline']['tasks'][3]['params']['save'] = True
        self.yconf['pipeline']['tasks'][3]['params']['output_root'] = output_root
        configfile = ysave(self.yconf)

        #subprocess.run(['caput-pipeline','run',configfile])
        P = Manager.from_yaml_file(configfile)
        P.run()
#        os.remove(configfile)
        savelog(configfile,self.prefix+'/logs/')
        del P


    def ps_extract(self,files,pstypes=['unwindowed'],output_format=None):
    
#        files = [self.prefix+'draco/sstream_fg_group_0.h5']
        pstypes = ['unwindowed','minimum_variance']
        if output_format is None:
            output_format = self.prefix+'/draco/psmc_{}_wnoise_{}_'
    
        self.dritf_init()

        self.yconf['pipeline'] = deepcopy(self.yconf['pipeline_ps'])
        self.yconf['pipeline']['tasks'][1]['params']['product_directory'] = self.prod_dir
        self.yconf['pipeline']['tasks'][2]['params']['files'] = files

        d1_temp = deepcopy(self.yconf['pipeline']['tasks'][5])
        d2_temp = deepcopy(self.yconf['pipeline']['tasks'][6])
        self.yconf['pipeline']['tasks'] = self.yconf['pipeline']['tasks'][:5]

        for kltrech,fgtrech,pstrech in self.thresh_list:

            klname = 'dk_{}thresh_fg_{}thresh'.format(kltrech,fgtrech)
            
            d1 = deepcopy(d1_temp)
            d1['out'] = 'klmodes_{}'.format(klname)
            d1['params']['klname'] = klname
            d1['params']['threshold'] = pstrech
            
            self.yconf['pipeline']['tasks'].append(d1)    

            for pstype in pstypes: #'uncorrelated'
            
                output_root = output_format.format(pstype,klname)
                d2 = deepcopy(d2_temp)
            
                d2['in'] = 'klmodes_{}'.format(klname)
                d2['out'] = 'psmc_uw_{}'.format(klname)
                d2['params']['psname'] = 'psmc_{}_{}threshold'.format(klname,pstrech)
                d2['params']['pstype'] = pstype
                d2['params']['save'] = True
                d2['params']['output_root'] = output_root
                self.yconf['pipeline']['tasks'].append(d2) 
                    
        configfile = ysave(self.yconf)

        #subprocess.run(['caput-pipeline','run',configfile])
        P = Manager.from_yaml_file(configfile)
        P.run()
#        os.remove(configfile)
        savelog(configfile,self.prefix+'/logs/')
        del P



def checkres():

    pass
    











