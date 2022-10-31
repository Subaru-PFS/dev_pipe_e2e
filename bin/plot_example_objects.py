#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

base_dir = '/arch1/ipmu/pipe_e2e/'
res_2d_dir = os.path.join(base_dir,
                          'pipe2d_results/rerun',
                          'weekly/pipeline/brn/pipeline/pfsObject',
                          '00001/00000/0,0/'
                          )
res_1d_dir = os.path.join(base_dir,
                          'pipe1d_results/output/data/'
                          )
spec_in_dir = '/arch1/princeton/simulator/pfsSimObjects/lowz_COSMOS_2020_12_14/'

redshift_filename = 'check_redshift_determination.csv'

catId = '00001'
tract = '00000'
patch = '0,0'
nVisit = '006'
pfsVisitHash = '0x7ace412dc05971ff'


def get_top5_objects():
    info = {}
    with open(os.path.join(base_dir, redshift_filename), 'r') as f:
        for line in f:
            a = line.split(',')
            if a[0] != "filename":
                if pfsVisitHash in a[1]:
                    name = a[0] + ',' + a[1] + ':' + a[2] + ':' + a[3]
                    f1 = float(a[4])
                    f2 = float(a[5])
                    f12 = f1 + f2
                    info[name] = f12
    info_sorted = sorted(info.items(), key=lambda x: x[1], reverse=True)
    for i in range(5):
        print(info_sorted[i])


def get_object(objId):
    ''' get pfsObject '''
    filename = f'pfsObject-{catId}-{tract}-{patch}-{objId}-{nVisit}-{pfsVisitHash}.fits'
    with fits.open(os.path.join(res_2d_dir, filename)) as hdul:
        hdr = hdul[1].header
        naxis1 = hdr['NAXIS1']
        crpix1 = hdr['CRPIX1']
        cdelt1 = hdr['CDELT1']
        crval1 = hdr['CRVAL1']
        wav_pipe2d = (((np.arange(naxis1) + 1) - crpix1) * cdelt1 + crval1) * 1e9
        flx_pipe2d = hdul[1].data
    ''' get pfsSimObject '''
    filename = f'pfsSimObject-{catId}-{tract}-{patch}-{objId}.fits'
    with fits.open(os.path.join(spec_in_dir, filename)) as hdul:
        wav_sim2d = hdul[2].data
        flx_sim2d = hdul[1].data
    return wav_sim2d, flx_sim2d, wav_pipe2d, flx_pipe2d


def plot_example(objIds, redshifts_in, redshifts_out):

    ymin = +0.
    ymax = +50000.
    fig = plt.figure(figsize=(10, 6))

    ax1 = fig.add_subplot(511)
    wav_sim2d, flx_sim2d, wav_pipe2d, flx_pipe2d = get_object(objIds[0])
    xmin = (1 + redshifts_in[0]) * 400.
    xmax = (1 + redshifts_in[0]) * 520.
    ax1.set_xlim(xmin, xmax)
    ax1.set_ylim(ymin, ymax)
    ax1.plot(wav_sim2d, flx_sim2d, ls='solid', lw=1, color='C1', alpha=1.0, zorder=1)
    ax1.plot(wav_pipe2d, flx_pipe2d, ls='solid', lw=1, color='C2', alpha=0.5, zorder=2)
    ax1.text(xmin + 5, ymax * 0.8, f'z_in={redshifts_in[0]}, z_out={redshifts_out[0]}')

    ax2 = fig.add_subplot(512)
    wav_sim2d, flx_sim2d, wav_pipe2d, flx_pipe2d = get_object(objIds[1])
    xmin = (1 + redshifts_in[1]) * 400.
    xmax = (1 + redshifts_in[1]) * 520.
    ax2.set_xlim(xmin, xmax)
    ax2.set_ylim(ymin, ymax)
    ax2.plot(wav_sim2d, flx_sim2d, ls='solid', lw=1, color='C1', alpha=1.0, zorder=1)
    ax2.plot(wav_pipe2d, flx_pipe2d, ls='solid', lw=1, color='C2', alpha=0.5, zorder=2)
    ax2.text(xmin + 5, ymax * 0.8, f'z_in={redshifts_in[1]}, z_out={redshifts_out[1]}')

    ax3 = fig.add_subplot(513)
    ax3.set_ylabel('flux density (nJy)')
    wav_sim2d, flx_sim2d, wav_pipe2d, flx_pipe2d = get_object(objIds[2])
    xmin = (1 + redshifts_in[2]) * 400.
    xmax = (1 + redshifts_in[2]) * 520.
    ax3.set_xlim(xmin, xmax)
    ax3.set_ylim(ymin, ymax)
    ax3.plot(wav_sim2d, flx_sim2d, ls='solid', lw=1, color='C1', alpha=1.0, zorder=1)
    ax3.plot(wav_pipe2d, flx_pipe2d, ls='solid', lw=1, color='C2', alpha=0.5, zorder=2)
    ax3.text(xmin + 5, ymax * 0.8, f'z_in={redshifts_in[2]}, z_out={redshifts_out[2]}')

    ax4 = fig.add_subplot(514)
    wav_sim2d, flx_sim2d, wav_pipe2d, flx_pipe2d = get_object(objIds[3])
    xmin = (1 + redshifts_in[3]) * 400.
    xmax = (1 + redshifts_in[3]) * 520.
    ax4.set_xlim(xmin, xmax)
    ax4.set_ylim(ymin, ymax)
    ax4.plot(wav_sim2d, flx_sim2d, ls='solid', lw=1, color='C1', alpha=1.0, zorder=1)
    ax4.plot(wav_pipe2d, flx_pipe2d, ls='solid', lw=1, color='C2', alpha=0.5, zorder=2)
    ax4.text(xmin + 5, ymax * 0.8, f'z_in={redshifts_in[3]}, z_out={redshifts_out[3]}')

    ax5 = fig.add_subplot(515)
    ax5.set_xlabel('wavelength (nm)')
    wav_sim2d, flx_sim2d, wav_pipe2d, flx_pipe2d = get_object(objIds[4])
    xmin = (1 + redshifts_in[4]) * 400.
    xmax = (1 + redshifts_in[4]) * 520.
    ax5.set_xlim(xmin, xmax)
    ax5.set_ylim(ymin, ymax)
    ax5.plot(wav_sim2d, flx_sim2d, ls='solid', lw=1, color='C1', alpha=1.0, zorder=1)
    ax5.plot(wav_pipe2d, flx_pipe2d, ls='solid', lw=1, color='C2', alpha=0.5, zorder=2)
    ax5.text(xmin + 5, ymax * 0.8, f'z_in={redshifts_in[4]}, z_out={redshifts_out[4]}')

    plt.subplots_adjust(wspace=0.4, hspace=0.4)
    plt.savefig('example.pdf', bbox_inches='tight')


if __name__ == '__main__':

    get_top5_objects()
    objIds = ['00000000000003c1',
              '000000000000067b',
              '0000000000000597',
              '000000000000054a',
              '00000000000004b7'
              ]
    redshifts_in = [1.4765,
                    1.2729,
                    1.2618,
                    0.9956,
                    1.5688
                    ]
    redshifts_out = [5.3107,
                     1.2729,
                     3.4200,
                     1.6806,
                     1.5691
                     ]
    plot_example(objIds=objIds, redshifts_in=redshifts_in, redshifts_out=redshifts_out)
