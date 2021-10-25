import pytz

import var
import datetime
from jenkinsapi.jenkins import Jenkins

jenkins_user = var.jenkins_user
jenkins_token = var.jenkins_token
jenkins_url = var.jenkins_url
job_name = var.job_name

builds_list_success = []
builds_list_failure = []
builds_list_aborted = []
builds_list_process = []

colection_success = {}
colection_failure = {}
colection_aborted = {}
colection_process = {}

time_start = datetime.datetime(2021, 10, 25, tzinfo=pytz.UTC)
time_end = datetime.datetime.now(tz=pytz.UTC)

artifacts = []


def get_server(url):
    try:
        jenkins = Jenkins(baseurl=url, username=jenkins_user, password=jenkins_token, timeout=100)
        print(f"Jenkins version: {jenkins.version}")
        return jenkins
    except:
        print(f"Error connect to Jenkins. Use VPN.")
        exit()


def get_builds_list(server, job_name):
    print(f"Downloading builds list.")
    job = server[job_name]
    builds = job.get_build_dict()  # {id:"url"}
    builds_list = []
    for build_id in builds.keys():
        builds_list.append(build_id)

    print(f"List builds from {job.get_full_name()} job: {builds_list}")
    print(f"Collecting data from {time_start.strftime('%d/%m/%y %H:%M')} to {time_end.strftime('%d/%m/%y %H:%M')}.")

    for build_id in builds_list:
        build_time = job.get_build(build_id).get_timestamp()
        build_status = job.get_build(build_id).get_status()

        if time_end >= build_time >= time_start:
            if build_status == None:
                builds_list_process.append(build_id)
                colection_process.update({build_id: {"time": build_time}})
            if build_status == "ABORTED":
                builds_list_aborted.append(build_id)
                colection_aborted.update({build_id: {"time": build_time}})
            if build_status == "FAILURE":
                builds_list_failure.append(build_id)
                colection_failure.update({build_id: {"time": build_time}})
            if build_status == "SUCCESS":
                builds_list_success.append(build_id)
                colection_success.update({build_id: {"time": build_time}})
        else:
            break
    print("BUILD DOWNLOAD RESULT :")
    print(f"SUCCESS: \t {builds_list_success}")
    print(f"FAILURE: \t {builds_list_failure}")
    print(f"PROCESS: \t {builds_list_process}")
    print(f"ABORTED: \t {builds_list_aborted}")


def get_artifacts(server, job_name, data):
    print(f"Downloading artifacts from {job_name}.")
    for job in server.get_jobs():
        if job[0] == job_name:
            job_instance = server.get_job(job[0])

            for build_id in data.keys():
                try:
                    print(f"Downloading artifacts from {job_name}/#{build_id}.")
                    build = job_instance.get_build(buildnumber=build_id)
                    data[build_id].update({"artifact": {}})
                    for artifact in build.get_artifacts():

                        print(f"{artifact.filename}: \t{artifact.get_data()}")

                        if len(artifact.get_data()) == 0:
                            data[build_id]["artifact"].update({artifact.filename: 0})
                        else:
                            data[build_id]["artifact"].update({artifact.filename: 1})
                    print(f"Downloading artifacts from {job_name}/#{build_id} - done")
                except:
                    print(f"Downloading artifacts from {job_name}/#{build_id} - error")
    return data


if __name__ == '__main__':
    jenkins_server = get_server(jenkins_url)
    get_builds_list(jenkins_server, job_name)
    colection_success = get_artifacts(jenkins_server, job_name, colection_success)
