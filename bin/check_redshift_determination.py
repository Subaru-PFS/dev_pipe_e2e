#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import pathlib

pipe2d_res_dir = '/arch1/ipmu/pipe_e2e_test/pipe2d_results/rerun/'
pipe1d_res_dir = '/arch1/ipmu/pipe_e2e_test/pipe1d_results/output/data/'
weekly_spec_in_dir = '/arch1/princeton/simulator/pfsSimObjects/lowz_COSMOS_2020_12_14/'
science_spec_in_dir = '/arch1/princeton/simulator/pfsSimObjects/GE_combined_2021_08_05/'
weekly_brn_pfsobject_dir = os.path.join(pipe2d_res_dir,
                                        'weekly/pipeline/brn/pipeline/pfsObject',
                                        '00001/00000/0,0/')
weekly_bmn_pfsobject_dir = os.path.join(pipe2d_res_dir,
                                        'weekly/pipeline/bmn/pipeline/pfsObject',
                                        '00001/00000/0,0/')
science_pfsobject_dir = os.path.join(pipe2d_res_dir,
                                     'science/pipeline/pfsObject',
                                     '00006/00000/0,0/')

weeklyVisitHashLR = '0x7ace412dc05971ff'
weeklyVisitHashMR = '0x47af676df42df175'
scienceVisitHashLR = '0x11fcdfd13c364618'
scienceVisitHashMR = '0x5ee4f7af5a556820'

# pfsZcandidates-00001-00000-0,0-00000000000005a1-006-0x47af676df42df175.fits
# pfsZcandidates-00001-00000-0,0-00000000000005a1-006-0x7ace412dc05971ff.fits


def get_redshift_pipe1d(pfsobject_dir, spec_in_dir, cat_id, visit_hash):
    """
    Description
    -----------
        check the redshift determination results of DRP1D

    Parameters
    ----------
        pfsobject_dir : `string`
            Directory of pfsObject- fits
        spec_in_dir : `string`
            Directory of pfsZcandidates- fits
        cat_id : `string`
            cadId
        visit_hash : `string`
            pfsVisithash

    Returns
    -------
        filename_out : `ndarray`
            Filenames of output
        objId_out : `ndarray`
            objId of input/output sources
        redshift_in : `ndarray`
            Redshift of input spectra
        redshift_out : `ndarray`
            Redshift of output spectra
        l3727_in : `ndarray`
            L([OII]3727) of input sources
        l3729_in : `ndarray`
            L([OII]3729) of input sources
        ver_pipe2d : `string`
            Version of PIPE2D
        ver_pipe1d_library : `string`
            Version of PIPE1D (library)
        ver_pipe1d_client : `string`
            Version of PIPE1D (client)
    """

    filename_out = []
    objId_out = []
    redshift_in = []
    redshift_out = []
    l3727_in = []
    l3729_in = []

    ''' get PIPE2D version '''
    ''' weekly (brn) '''
    pfsObjects = pathlib.Path(pfsobject_dir).glob('pfsObject-*.fits')
    for i, p in enumerate(pfsObjects):
        if i == 0:
            with fits.open(pfsobject_dir + p.name) as hdul:
                hdr = hdul[1].header
                ver_pipe2d = hdr['HIERARCH VERSION_drp_stella']
    ''' get PIPE1D version '''
    pfsZcandidates = pathlib.Path(pipe1d_res_dir).glob('pfsZcandidates*.fits')
    for i, p in enumerate(pfsZcandidates):
        if i == 0:
            with fits.open(pipe1d_res_dir + p.name) as hdul:
                hdr = hdul[0].header
                ver_pipe1d_library = hdr['D1D_VER']
                ver_pipe1d_client = hdr['D1DP_VER']
    print(ver_pipe2d, ver_pipe1d_library, ver_pipe1d_client)

    ''' get redshift information '''
    pfsZcandidates = pathlib.Path(pipe1d_res_dir).glob('pfsZcandidates*.fits')
    for p in pfsZcandidates:
        ''' parse filename '''
        v = p.name.split('-')
        catId = v[1]
        tract = v[2]
        patch = v[3]
        objId = v[4]
        pfsVisitHash = v[6].split('.')[0]
        ''' get redshift determination of PIPE1D '''
        if catId == cat_id and pfsVisitHash == visit_hash:
            # print(p.name)
            with fits.open(pipe1d_res_dir + p.name) as hdul:
                data = hdul['GALAXY_CANDIDATES'].data
                Z = data['Z'][0]
            ''' get redshift of the input spectrum '''
            filename = spec_in_dir + f'pfsSimObject-{catId}-{tract}-{patch}-{objId}.fits'
            with fits.open(filename) as hdul:
                try:
                    data = hdul[3].data
                    lambda_r = data['lambda_r']
                    lambda_o = data['lambda_o']
                    Z_in = np.median(lambda_o / lambda_r - 1)
                    l3729 = data['Lline'][13]
                    l3727 = data['Lline'][14]
                except IndexError:
                    # print('exception: %s' % (objId))
                    Z_in = np.nan
                    l3729 = np.nan
                    l3727 = np.nan

            filename_out.append(p.name)
            objId_out.append(objId)
            redshift_in.append(Z_in)
            redshift_out.append(Z)
            l3727_in.append(l3727)
            l3729_in.append(l3729)

    objId_out = np.array(objId_out)
    redshift_in = np.array(redshift_in)
    redshift_out = np.array(redshift_out)
    l3727_in = np.array(l3727_in)
    l3729_in = np.array(l3729_in)

    return filename_out, objId_out, redshift_in, redshift_out, l3727_in, l3729_in, \
        ver_pipe2d, ver_pipe1d_library, ver_pipe1d_client


def main():
    filename_out1, objId_out1, redshift_in1, redshift_out1, l3727_in1, l3729_in1, \
        ver_pipe2d, ver_pipe1d_library, ver_pipe1d_client = get_redshift_pipe1d(weekly_brn_pfsobject_dir,
                                                                                weekly_spec_in_dir,
                                                                                '00001',
                                                                                weeklyVisitHashLR,
                                                                                )
    info1 = np.array(['weekly_lr' for _ in range(len(filename_out1))])
    filename_out2, objId_out2, redshift_in2, redshift_out2, l3727_in2, l3729_in2, \
        ver_pipe2d, ver_pipe1d_library, ver_pipe1d_client = get_redshift_pipe1d(weekly_bmn_pfsobject_dir,
                                                                                weekly_spec_in_dir,
                                                                                '00001',
                                                                                weeklyVisitHashMR,
                                                                                )
    info2 = np.array(['weekly_mr' for _ in range(len(filename_out2))])
    filename_out3, objId_out3, redshift_in3, redshift_out3, l3727_in3, l3729_in3, \
        ver_pipe2d, ver_pipe1d_library, ver_pipe1d_client = get_redshift_pipe1d(science_pfsobject_dir,
                                                                                science_spec_in_dir,
                                                                                '00006',
                                                                                scienceVisitHashLR,
                                                                                )
    info3 = np.array(['science_lr' for _ in range(len(filename_out3))])
    filename_out4, objId_out4, redshift_in4, redshift_out4, l3727_in4, l3729_in4, \
        ver_pipe2d, ver_pipe1d_library, ver_pipe1d_client = get_redshift_pipe1d(science_pfsobject_dir,
                                                                                science_spec_in_dir,
                                                                                '00006',
                                                                                scienceVisitHashMR,
                                                                                )
    info4 = np.array(['science_mr' for _ in range(len(filename_out4))])
    filename_out = np.append(np.append(np.append(filename_out1, filename_out2), filename_out3), filename_out4)
    redshift_out = np.append(np.append(np.append(redshift_out1, redshift_out2), redshift_out3), redshift_out4)
    redshift_in = np.append(np.append(np.append(redshift_in1, redshift_in2), redshift_in3), redshift_in4)
    objId_out = np.append(np.append(np.append(objId_out1, objId_out2), objId_out3), objId_out4)
    l3727_in = np.append(np.append(np.append(l3727_in1, l3727_in2), l3727_in3), l3727_in4)
    l3729_in = np.append(np.append(np.append(l3729_in1, l3729_in2), l3729_in3), l3729_in4)
    info = np.append(np.append(np.append(info1, info2), info3), info4)

    ''' get statistics '''
    diff = redshift_out - redshift_in
    diff_mean = np.nanmean(diff)
    diff_std = np.nanstd(diff)
    msk = (diff - diff_mean)**2 > (3 * diff_std)**2
    diff_outlier = diff[msk]
    frac_outlier = len(diff_outlier) / len(diff)
    print('Number of targets:', len(redshift_out))
    print('  diff_mean = %.3f' % (diff_mean))
    print('  diff_std = %.3f' % (diff_std))
    print('  frac (|diff|>3sigma) = %.3f' % (frac_outlier))

    filename_res = 'check_redshift_determination.csv'
    with open(filename_res, 'w') as f:
        f.write('filename,z_in,z_out,L3727,L3729,info\n')
        for i in range(len(objId_out)):
            f.write('%s,%.4f,%.4f,%.4e,%.4e,%s\n' % (filename_out[i], redshift_in[i], redshift_out[i], l3727_in[i], l3729_in[i], info[i]))

    ''' plot comparison '''
    xmin = 0.0
    xmax = 6.0
    ymin = 0.0
    ymax = 6.0

    fig = plt.figure(figsize=(6, 6))
    axe = fig.add_subplot(111)
    axe.set_xlabel('Redshift (input)', fontsize=12)
    axe.set_ylabel('Redshift (PIPE1D)', fontsize=12)
    axe.set_title('drp_stella=%s,drp_1d=%s,drp_1dpipe=%s' % (ver_pipe2d, ver_pipe1d_library, ver_pipe1d_client), fontsize=12)
    axe.set_xlim(xmin, xmax)
    axe.set_ylim(ymin, ymax)

    axe.plot([xmin, xmax], [ymin, ymax], ls='dashed', lw=1, color='k')
    # msk1 = resolution == 'LR'
    # msk2 = resolution == 'MR'
    # axe.scatter(redshift_in[msk1], redshift_out[msk1], marker='o', s=50, facecolor='red', edgecolor='k', label='LR')
    # axe.scatter(redshift_in[msk2], redshift_out[msk2], marker='^', s=50, facecolor='red', edgecolor='k', label='MR')

    axe.scatter(redshift_in1, redshift_out1, marker='o', s=50, facecolor='red', edgecolor='k', alpha=0.8, label='weekly (LR)')
    axe.scatter(redshift_in2, redshift_out2, marker='^', s=50, facecolor='red', edgecolor='k', alpha=0.8, label='weekly (MR)')
    axe.scatter(redshift_in3, redshift_out3, marker='o', s=50, facecolor='blue', edgecolor='k', alpha=0.8, label='science (LR)')
    axe.scatter(redshift_in4, redshift_out4, marker='^', s=50, facecolor='blue', edgecolor='k', alpha=0.8, label='science (MR)')

    axe.text(2.8, 1.00, 'diff_mean = %.3f' % (diff_mean))
    axe.text(2.8, 0.75, 'diff_std = %.3f' % (diff_std))
    axe.text(2.8, 0.50, 'frac (|diff|>3sigma) = %.3f' % (frac_outlier))

    axe.legend(loc='upper left', ncol=2, fontsize=12)
    plt.savefig('check_redshift_determination.pdf', bbox_inches='tight')

    filename1 = 'check_redshift_determination_%s_%s_%s.pdf' % (ver_pipe2d, ver_pipe1d_library, ver_pipe1d_client)
    filename2 = 'check_redshift_determination_%s_%s_%s.csv' % (ver_pipe2d, ver_pipe1d_library, ver_pipe1d_client)
    os.system('cp check_redshift_determination.pdf ./check_results/%s' % (filename1))
    os.system('cp check_redshift_determination.csv ./check_results/%s' % (filename2))

    return 0


if __name__ == '__main__':
    main()
