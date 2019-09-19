## Launch EC2 instance using boto3 with sample application
- [Introduction](#Introduction)
- [Pre-requisites](#pre-requisites)
- [Steps to run script](#Steps-to-run-script)
- [Result](#Result)

# Introduction
In this repo, we are lanuch ec2 instance using native boto3.

# Pre-requisites 
* Ensure you install the latest version of python and requests package.
```
pip install paramiko
```
* We need IAM user access key and secert key to run this script. Please refer AWS documents to create the same.


# Steps to run script

* Clone the repo, it has prepackaged boto3,botocore,jmespath and dateutil.

* Execute the below command which will create the ec2 instance at the particular aws region and install the ruby application.
```
./aws_boto3_create_instance.py -k <AWS_ACCESS_KEY> -s <AWS_SECRET_KEY> --aws_region <AWS_REGION> -t <AWS_INSTANCE_TYPE> -i <AWS_AMI_ID> -n <AWS_TAG_NAME>
```
Example:
```
./aws_boto3_create_instance.py -k XXXXXXXX -s XXXXX --aws_region ap-south-1 -t t2.micro -i ami-0d773a3b7bb2bb1c1 -n SampleApplication
```

Notes:
* The script contains two classes 

aws_ec2 -> Which will create the key pair, security group which opens 22 and 80 port, and launch the instance in the respective region.
install_application -> Which will connect to respective instance and execute the commands 
			sudo apt update
			sudo apt -y install ruby-bundler
			git clone https://github.com/iproperty/simple-sinatra-app.gitt
			cd simple-sinatra-app/ ; bundle install"
			cd simple-sinatra-app/ ; sudo bundle exec rackup --host 0.0.0.0 -p80 > application.log 2>&1 &


# Why Python?

* Ease of changing the application incase if we want to run different.
* Using boto3 its ease to connect to aws instance.

# Security:

* The security group has only 80 and 22 port.
* AWS key and secert key are not stored anywhere in the script,it taken from the command line.

# Tested Environment.

* AWS t2.micro instances
* Ubuntu 18.04 -> ami-0d773a3b7bb2bb1c1
* Simple ruby application.
