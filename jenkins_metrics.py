# -*- encoding: utf-8 -*-

import requests
from basicauth import encode
from pprint import pprint
import json


class JenkinsInfo(object):

    defaultHeader = {
        'Accept': 'application/json, */*',
	'content-type': 'application/json',
	'Authorization': ''
    }

    def __init__(self, url, user, password, ssl_verify=True):
        self.jenkins_url = url.rstrip("/")
        self.jenkins_user = user
        self.jenkins_password = password
        self.s = requests.Session()
        self.ssl_verify = ssl_verify
        self.defaultHeader['Authorization'] = encode(user, password)

    def get_folders(self, folder=None):
        folders = []
        if folder:
            print("Getting sub-folder list ......")
            path = "{}/job/{}/api/json".format(self.jenkins_url, folder)
        else:
            print("Getting folder list ......")
            path = "{}/api/json".format(self.jenkins_url)

        response = requests.get(path)
        #pprint(response.text)
        if response.status_code != 201 and response.status_code != 200:
            print("[ERROR] Could not get folder list.")
            print("Status code is: "+ str(response.status_code))
        else:
            result = response.json()
            # pprint(result)
            for job in result['jobs']:
                # pprint(job)
                if job['_class'] == 'com.cloudbees.hudson.plugins.folder.Folder':
                    folders.append(job['name'])
        return folders

    def get_jobs_by_folder(self, folder, sub_folder):
        jobs = []
        path = "{}/job/{}/job/{}/api/json".format(self.jenkins_url, folder, sub_folder)

        response = requests.get(path)
        if response.status_code != 201 and response.status_code != 200:
            print("[ERROR] Could not get job list.")
        else:
            result = response.json()
            for job in result['jobs']:
                if job['_class'] == 'org.jenkinsci.plugins.workflow.job.WorkflowJob':
                    jobs.append(job['name'])
        return jobs

    def get_metrics_by_project(self, project):
        success = failures = unstable = 0
        applications = self.get_folders(project)
        for app in applications:
            jobs = self.get_jobs_by_folder(project, app)
            for job in jobs:
                s, f, u = self.get_metrics_by_job(project, app, job)
                success += s
                failures += f
                unstable += u
        return success, failures, unstable

    def get_metrics_by_job(self, folder, sub_folder, job_name):
        path = "{}/job/{}/job/{}/job/{}/api/json?tree=builds[number,status,timestamp,id,result,estimatedDuration]".format(self.jenkins_url, folder, sub_folder, job_name)
        s = f = u = 0

        response = requests.get(path)
        if response.status_code != 201 and response.status_code != 200:
            print("[ERROR] Could not get build info metrics.")
        else:
            result = response.json()
            builds = result['builds']
            for build in builds:
                if build['result'] == 'SUCCESS':
                    s += 1
                elif build['result'] == 'FAILURE':
                    f += 1
                else:
                    u += 1
            # print("SUCCESS: {}, FAILURE: {}, UNSTABLE: {}".format(s, f, u))
            return s, f, u















