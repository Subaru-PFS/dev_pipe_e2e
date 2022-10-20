#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import datetime

import pandas as pd

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

dialect = 'postgresql'
username = 'pfs'
host = '10.100.200.134'
port = '5432'
database = 'qadb'

dbinfo = f"{dialect}://{username}@{host}:{port}/{database}"


class QA(object):
    def __init__(self, res_path, res_filename, comment, sample, dataset_id):
        self.qa_version = '0.1'
        self.res_path = res_path
        self.res_filename = res_filename
        self.comment = comment
        self.sample = sample
        self.dataset_id = dataset_id
        self.status = None
        self.ver_pipe2d = None
        self.ver_pipe1d_library = None
        self.ver_pipe1d_client = None
        self.num_targets = None
        self.diff_mean = None
        self.diff_std = None
        self.frac_outlier = None

        self.engine = create_engine(dbinfo, poolclass=sqlalchemy.pool.NullPool)
        SessionClass = sessionmaker(self.engine)
        self.session = SessionClass()

    def readResults(self):
        datetime_processed = []
        with open(os.path.join(self.res_path, self.res_filename)) as file:
            for line in file:
                ''' get processing datetime '''
                if '[datetime] ' in line:
                    a = line.split()
                    datetime_processed.append(f'{a[1]} {a[2]}')
                ''' get number of targets for QA '''
                if 'Number of targets' in line:
                    a = line.split()
                    self.num_targets = int(a[3])
                ''' get redshift QA results '''
                if 'diff_mean' in line:
                    a = line.split()
                    self.diff_mean = float(a[2])
                if 'diff_std' in line:
                    a = line.split()
                    self.diff_std = float(a[2])
                if 'frac (|diff|>3sigma)' in line:
                    a = line.split()
                    self.frac_outlier = float(a[3])
                ''' get DRP versions '''
                if line[:4] == 'w.20':
                    a = line.split()
                    self.ver_pipe2d = a[0]
                    self.ver_pipe1d_library = a[1]
                    self.ver_pipe1d_client = a[2]

        if len(datetime_processed) > 1:
            self.run_datetime_start = datetime.strptime(datetime_processed[0], '%Y-%m-%d %H:%M:%S')
            self.run_datetime_end = datetime.strptime(datetime_processed[-1], '%Y-%m-%d %H:%M:%S')
            self.status = 'completed'
        return None

    def ingestTable(self):
        ''' e2e_processing '''
        df = pd.DataFrame({"run_description": [self.comment],
                           "run_sample": [self.sample],
                           "run_dataset": [self.dataset_id],
                           "run_status": [self.status],
                           "run_datetime_start": [self.run_datetime_start],
                           "run_datetime_end": [self.run_datetime_end]
                           })
        df.to_sql("e2e_processing", self.engine, if_exists='append', index=False)

        query = f'SELECT * FROM e2e_processing ORDER BY run_id DESC limit 1;'
        try:
            df = pd.read_sql(query, self.session.bind)
        except:
            self.session.rollback()
            raise
        run_id = df['run_id'][0]

        ''' e2e_drp_version '''
        df = pd.DataFrame({"run_id": [run_id],
                           "drp2d_version": [self.ver_pipe2d],
                           "drp1d_amazed_version": [self.ver_pipe1d_library],
                           "drp1d_client_version": [self.ver_pipe1d_client],
                           })
        df.to_sql("e2e_drp_version", self.engine, if_exists='append', index=False)

        ''' e2e_qa_redshift '''
        df = pd.DataFrame({"run_id": [run_id],
                           "num_targets": [self.num_targets],
                           "diff_mean": [self.diff_mean],
                           "diff_std": [self.diff_std],
                           "frac_outlier": [self.frac_outlier]
                           })
        df.to_sql("e2e_qa_redshift", self.engine, if_exists='append', index=False)

        return run_id


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(__file__)
    parser.add_argument("--res_path", required=False, default="./", help="result path")
    parser.add_argument("--res_filename", required=False, default="process.log", help="result filename")
    parser.add_argument("--comment", required=False, default=None, help="comment")
    parser.add_argument("--sample", required=False, default="weekly", help="sample (weekly/extended)")
    parser.add_argument("--dataset_id", required=False, default=1, help="dataset_id (weekly=1/extended=2)")
    parser.add_argument("--profile", required=False, action="store_true", help="Profile tests?")
    args, argv = parser.parse_known_args()

    res_path = args.res_path
    res_filename = args.res_filename
    comment = args.comment
    sample = args.sample
    dataset_id = args.dataset_id

    qa = QA(res_path, res_filename, comment, sample, dataset_id)
    qa.readResults()
    run_id = qa.ingestTable()
    print(comment, sample)
    print(run_id)
