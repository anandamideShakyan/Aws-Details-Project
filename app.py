from flask import Flask, jsonify
import boto3
from flask import Flask, jsonify
from flask_cors import CORS  # Import the CORS extension

app = Flask(__name__)
CORS(app)


def get_ec2_instances():
    ec2_client = boto3.client('ec2')

    # Fetch all EC2 instances
    response = ec2_client.describe_instances()
    instances = []

    for reservation in response['Reservations']:
        instances.extend(reservation['Instances'])

    return instances


def get_associated_resources(instance_id):
    ec2_client = boto3.client('ec2')
    ec2_resource = boto3.resource('ec2')

    instance = ec2_resource.Instance(instance_id)

    # Fetch associated resources
    associated_resources = {
        'security_groups': [sg['GroupId'] for sg in instance.security_groups],
        'key_name': instance.key_name,
        'volumes': [vol.id for vol in instance.volumes.all()],
        'elastic_ips': [ip['PublicIp'] for ip in ec2_client.describe_addresses()['Addresses'] if 'InstanceId' in ip and ip['InstanceId'] == instance_id],
        # Add more associated resources as needed (e.g., S3 buckets, etc.)
    }

    return associated_resources


def get_ebs_volumes():
    ec2_client = boto3.client('ec2')

    # Fetch all EBS volumes
    response = ec2_client.describe_volumes()
    volumes = response['Volumes']

    return volumes


def get_s3_buckets():
    s3_client = boto3.client('s3')

    # Fetch all S3 buckets
    response = s3_client.list_buckets()
    buckets = response['Buckets']

    return buckets


def get_elastic_ips():
    ec2_client = boto3.client('ec2')

    # Fetch all Elastic IPs
    response = ec2_client.describe_addresses()
    elastic_ips = response['Addresses']

    return elastic_ips


@app.route('/ec2-instances', methods=['GET'])
def ec2_instances():
    # Get all EC2 instances
    ec2_instances = get_ec2_instances()

    # Prepare response
    response_data = []

    # Fetch details and associated resources for each EC2 instance
    for instance in ec2_instances:
        instance_id = instance['InstanceId']
        instance_details = {
            'instance_id': instance_id,
            'instance_type': instance['InstanceType'],
            'state': instance['State']['Name'],
            'launch_time': str(instance['LaunchTime']),
            'associated_resources': get_associated_resources(instance_id)
        }
        response_data.append(instance_details)

    return jsonify(response_data)


@app.route('/ebs-volumes', methods=['GET'])
def ebs_volumes():
    # Get all EBS volumes
    ebs_volumes = get_ebs_volumes()

    # Prepare response
    response_data = {
        'ebs_volumes': ebs_volumes
    }

    return jsonify(response_data)


@app.route('/s3-buckets', methods=['GET'])
def s3_buckets():
    # Get all S3 buckets
    s3_buckets = get_s3_buckets()

    # Prepare response
    response_data = {
        's3_buckets': s3_buckets
    }

    return jsonify(response_data)


@app.route('/elastic-ips', methods=['GET'])
def elastic_ips():
    # Get all Elastic IPs
    elastic_ips = get_elastic_ips()

    # Prepare response
    response_data = {
        'elastic_ips': elastic_ips
    }

    return jsonify(response_data)


if __name__ == '__main__':
    app.run(debug=True)
