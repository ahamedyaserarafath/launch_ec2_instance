## Readme file for running the aws_boto3_create_instance.py python
## Prerequite packages 

1. Install paramiko package using the below command if not installed.

pip install paramiko

2. We need IAM user access key and secert key to run this script. Please refer AWS documents to create the same and that particular user need to have access to create the ec2 instance.

# Steps to Run the Python script 

1. Clone the repo, it has prepackaged boto3,botocore,jmespath and dateutil.

2. Execute the below command which will create the ec2 instance at the particular aws region and install the ruby application.

./aws_boto3_create_instance.py -k <AWS_ACCESS_KEY> -s <AWS_SECRET_KEY> --aws_region <AWS_REGION> -t <AWS_INSTANCE_TYPE> -i <AWS_AMI_ID> -n <AWS_TAG_NAME>

Ex: ./aws_boto3_create_instance.py -k XXXXXXXX -s XXXXX --aws_region ap-south-1 -t t2.micro -i ami-0d773a3b7bb2bb1c1 -n SampleApplication

# About the Script

1. The script contains two classes 
aws_ec2 -> Which will create the key pair, security group which opens 22 and 80 port, and launch the instance in the respective region.
install_application -> Which will connect to respective instance and execute the commands 
			sudo apt update
			sudo apt -y install ruby-bundler
			clone the git
			bundle install
			sudo bundle exec rackup --host 0.0.0.0 -p80 > application.log 2>&1 &


#Why Python?

1. Ease of changing the application incase if we want to run different.
2. Using boto3 its ease to connect to aws instance.

#Security:

1. The security group has only 80 and 22 port.
2. AWS key and secert key are not stored anywhere in the script,it taken from the command line.

# Tested Environment.

1. AWS t2.micro instances
2. Ubuntu 18.04 -> ami-0d773a3b7bb2bb1c1
3. Simple ruby application.
