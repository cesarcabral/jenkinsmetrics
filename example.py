# -*- encoding: utf-8 -*-
from prometheus_client import start_http_server,Counter, Gauge
from conf_example import JENKINS_URL, JENKINS_USER, JENKINS_PASSWORD
from jenkins_metrics import JenkinsInfo
import time
from sys import exit 


def main():
    print("Starting Jenkins Metrics")
    jenkins = JenkinsInfo(JENKINS_URL, JENKINS_USER, JENKINS_PASSWORD)

    projects = jenkins.get_folders()
    print("Projects in Jenkins -> {}\n".format(projects))

    # The metrics we want to export
    prometheus_metrics = {}

    for p in projects:
        prometheus_metrics[p] = {'status': Gauge("Jenkins_metrics_project_{0}".format(p.replace("-","_")),
        'Metrics by project', labelnames=["status"])}
    
    print("\nEmitting metrics")
    print("Updating Jenkins Metrics")
    update_gauge(projects, jenkins, prometheus_metrics)


def update_gauge(projects, jenkins_info, g):
    for project in projects:
        success, failures, unstable = jenkins_info.get_metrics_by_project(project)
        g[project]['status'].labels(status="success").set(success)
        g[project]['status'].labels(status="failures").set(failures)
        g[project]['status'].labels(status="unstable").set(unstable)
        print("PROJECT: {} -> SUCCESS: {}, FAILURES: {}, UNSTABLE: {}\n".format(project, success, failures, unstable))

if __name__ == "__main__":
    try:
        start_http_server(8889)
        main()
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        print("[INFO] - PROCESS INTERRUPTED")
        exit(0)




