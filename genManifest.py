import yaml
import argparse
import re
from shutil import copy

header = """
file_version: '0.1'
"""

# Template for new service

def write_config(filename, **kwargs):
    template ="""
    {component_name}:
      application:
        deployment:
          name: warehouse-app
          namespace: warehouse-ns
          replicaCount: 1
          port: 8000
          appVersion: {app_version}
          commitId: {commit_id}
          image:
            repository: lolverae/warehouse_service
            tag: {docker_tag}
          env: 
            dbHost: warehouse-db
            dbPort: 5984
        service:
          namespace: warehouse-ns
          name: warehouse-app
          type: NodePort
          port: 8000
      database:
        deployment:
          name: warehouse-app
          namespace: warehouse-ns
          replicaCount: 1
          image:
            repository: couchdb
            tag: 2:3
          port: 5984
          env: 
            dbHost: warehouse-db
            dbPort: 5984
        service:
          name: warehouse-app
          namespace: warehouse-ns
          port: 5934
          type: NodePort
          NodePort: 30001
    """
    # Adding new service for given component in given manifest file
    with open(filename, 'r+') as yml_file:
        yaml_dict = yaml.safe_load(yml_file)
        comp_yaml_dict = yaml.safe_load(template.format(**kwargs))
        yaml_dict[kwargs.get('component_name')] = comp_yaml_dict[kwargs.get('component_name')]
        yml_file.seek(0)
        yml_file.write(yaml.dump(yaml_dict))
        yml_file.truncate()


def update_valuefiles(filename, **kwargs):
    assert kwargs
    directory = 'valuefiles'
    component_name = kwargs.get('name')
    valuefile = 'manifest.yaml'

    # # reading pre-manifest file for later to be updated
    with open(valuefile, 'r') as fpm:
        y_ml = yaml.safe_load(fpm) or {}
    
    #  Version Update, after adding components data
    file_version = y_ml["file_version"]
    file_version = float(file_version) + float(0.1)
    file_version = "%.1f" % file_version
    y_ml["file_version"] = file_version
    old_valuefile= directory + '/' + 'manifest-' + file_version + '.yaml'
    with open(valuefile, 'w+') as f:
        yaml.dump(y_ml, f, default_flow_style=False)
    print("Updated Manifest File for Component %s with %s" % (component_name, kwargs.values()))
    print('-----------------------------------------------------------------------------')
    print("Added old valuefiles manifest-%s" % (file_version))
    copy(valuefile, old_valuefile)

def update_manifest(component_name, docker_tag):
    #split docker tag to get directory, version and commit_id
    separator  = len( re.findall('[-]', docker_tag) )
    #if directory is not retreived default to master
    if separator == 1:
        app_version = docker_tag.split('-')[0]
        commit_id = docker_tag.split('-')[1]

    write_config('manifest.yaml', component_name=component_name, docker_tag=docker_tag, commit_id=commit_id, app_version=app_version)
    # update pre manifest file    
    update_valuefiles('manifest.yaml', commitId=commit_id, tag=docker_tag, name=component_name)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("component_name", help="Pass Component Name that needs to be updated in manifest file")
    parser.add_argument("docker_tag", help="Pass Docker tag that needs to be updated in manifest file")
    arguments = parser.parse_args() 
    update_manifest(arguments.component_name, arguments.docker_tag)

if __name__ == "__main__":
    main()