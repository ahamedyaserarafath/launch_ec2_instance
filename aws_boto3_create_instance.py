#!/usr/bin/python
# Note : Above path should be changed if python package location is changes
##******************************************************************************
##
## Create AWS Instance and install the ruby application  
##   - Create a EC2 instance using boto3 
##   - Deploy the ruby application in the respective instance
##
## V 1.0 / 2 Dec 2018 / Ahamed Yaser Arafath / ahamedyaserarafath@gmail.com
##
##******************************************************************************

#Import respective package which is needed 
import boto3
import argparse
import sys
import time
import paramiko

class aws_ec2():
    """Class which launch the ec2 instance using boto3"""
    def __init__(self):
        try:
            parser=argparse.ArgumentParser(description = 'Script will be responsible for creating \
                                                                                        the aws ec2 instance using boto3')
            parser.add_argument('-k', '--aws_access_key', help = 'AWS access key of IAM user')
            parser.add_argument('-s', '--aws_secret_key', help = 'AWS secert key of IAM user')
            parser.add_argument('-r', '--aws_region', help = 'AWS region where we want to launch ec2 instance')
            parser.add_argument('-t', '--aws_instance_type', help = 'AWS instance type like t2.micro, \
                                                                                        t1.micro..Please refer AWS document')
            parser.add_argument('-i', '--aws_ami_id', help = 'AWS ami id used to launch with the same')
            parser.add_argument('-n', '--aws_instance_name', help = 'AWS instance name used to create the \
                                                                                         instance name and used the same for sg and keypair')
            arg = parser.parse_args()
            self.aws_access_key = arg.aws_access_key
            self.aws_secret_key = arg.aws_secret_key
            self.aws_region = arg.aws_region
            self.aws_instance_type = arg.aws_instance_type
            self.aws_ami_id = arg.aws_ami_id
            self.aws_instance_name = arg.aws_instance_name
            self.aws_instance_keypair = str(self.aws_instance_name) + "-keypair"
            self.aws_instance_security_group = str(self.aws_instance_name) + "-sg"
            self.aws_instance_port = [ 22, 80 ]
            if arg.aws_access_key is None or \
                arg.aws_secret_key is None or \
                arg.aws_region is None or \
                arg.aws_instance_type is None or \
                arg.aws_ami_id is None or \
                arg.aws_instance_name is None:
                print("Please have a valid input, please look for help -h")
                sys.exit(1)
        except Exception as e:
            print("Exception while paring input arguments, Exception for your reference : " + str(e))
            sys.exit(1)

    def create_client_using_boto3(self,service_string="ec2"):
        """ Create the client connection using boto3"""
        try:
            session = boto3.Session(
                                aws_access_key_id=self.aws_access_key,
                                aws_secret_access_key=self.aws_secret_key,
                                region_name=self.aws_region)
            service_client = session.client(service_string)
            return service_client
        except Exception as e:
            print("Exception while creating the session, Exception for your reference : " + str(e))
            sys.exit(1)

    def create_key_pair_using_boto3(self):
        """Create the key pair using boto3"""
        try:
            print("Initiating the key pair generation for the instance with the name : " + self.aws_instance_keypair)
            ec2_client = self.create_client_using_boto3("ec2")
            create_key_pair_response = ec2_client.create_key_pair(KeyName=self.aws_instance_keypair)
            key_pair_content = str(create_key_pair_response["KeyMaterial"])
            aws_instance_keypair_file = open(self.aws_instance_keypair + '.pem','w')
            aws_instance_keypair_file.write(key_pair_content)
            aws_instance_keypair_file.close()
            print("Successfull created the key pair with the name : ./" + self.aws_instance_keypair + ".pem")
            return self.aws_instance_keypair
        except Exception as e:
            print("Exception while creating the keypair, Exception for your reference : " + str(e))
            sys.exit(1)

    def create_security_group_using_boto3(self):
        """Create the security group using boto3"""
        try:
            print("Creating the security group for the instance with the name : "+ self.aws_instance_security_group )
            ec2_client = self.create_client_using_boto3("ec2")
            create_sg_response = ec2_client.create_security_group(GroupName=self.aws_instance_security_group, \
                                                            Description=self.aws_instance_security_group)
            for temp in self.aws_instance_port:
                ec2_client.authorize_security_group_ingress(GroupName=self.aws_instance_security_group ,\
                                                        IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=temp,ToPort=temp)
            print("Successfull created the security group with the inbound port  : "+ str(self.aws_instance_port))
        except Exception as e:
            print("Exception while creating the security group, Exception for your reference : " + str(e))
            sys.exit(1)

    def create_ec2_instance_using_boto3(self):
        """ Launch the ec2 instances using boto3 """
        try:
            print("Launching the ec2 instance")
            ec2_client = self.create_client_using_boto3("ec2")
            instances = ec2_client.run_instances(
                ImageId=self.aws_ami_id, 
                KeyName=self.aws_instance_keypair,
                MinCount=1, 
                MaxCount=1,
                InstanceType=self.aws_instance_type,
                SecurityGroups=[self.aws_instance_security_group],
                TagSpecifications = [
                        {
                            'ResourceType': "instance",
                            'Tags':[
                                {
                                    "Key":"Name",
                                    "Value" : str(self.aws_instance_name )

                                },
                            ]
                        }
                ],
                )
            InstanceId = str(instances["Instances"][0]["InstanceId"])
            print("Checking for the instance to be in running state...")
            count = 0
            while True:
                count = count +1
                time.sleep(20)
                describe_instance_status = ec2_client.describe_instance_status(InstanceIds=[InstanceId])
                if describe_instance_status["InstanceStatuses"]:
                    instance_code = describe_instance_status["InstanceStatuses"][0]["InstanceState"]["Code"]
                    InstanceStatus = describe_instance_status["InstanceStatuses"][0]["InstanceStatus"]["Status"]
                    SystemStatus = describe_instance_status["InstanceStatuses"][0]["SystemStatus"]["Status"]
                    if instance_code == 16 and InstanceStatus == "ok" and SystemStatus == "ok" :
                        print(InstanceId + " ec2 instance is up and running successfully ")
                        break
                if count == 10:
                    print("Waited for more than 200 seconds, instance " +InstanceId + " doesnt come up,\
                                 please check in AWS GUI")
                    break
            print("Successfull created the ec2 instance..")
            print("instance Id for your reference : " +InstanceId )
            describe_instance = ec2_client.describe_instances(InstanceIds=[InstanceId])
            PublicDnsName = str(describe_instance["Reservations"][0]["Instances"][0]["PublicDnsName"])
            PublicIpAddress = str(describe_instance["Reservations"][0]["Instances"][0]["PublicIpAddress"])
            print("PublicDnsName for your reference : " +PublicDnsName )
            print("PublicIpAddress for your reference : " +PublicIpAddress )
            return PublicDnsName, PublicIpAddress
        except Exception as e:
            print("Exception while creating the instance, Exception for your reference : " + str(e))
            sys.exit(1)

class install_application():
    """Class which install ruby application"""

    def __init__(self, PublicDnsName,PublicIpAddress,key_pair_file_name):
        self.username = "ubuntu"
        self.PublicDnsName = PublicDnsName
        self.PublicIpAddress = PublicIpAddress
        self.key_pair_file_name = key_pair_file_name

    def connect_to_aws_instanace(self):
        """ Connect to aws instance using paramiko """
        try:
            private_key = paramiko.RSAKey.from_private_key_file(key_pair_file_name + ".pem")
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            print("connecting to ..." + str(self.PublicIpAddress))
            ssh_client.connect( hostname = self.PublicIpAddress,username = "ubuntu", pkey = private_key )
            print("Successfull connected to " + str(self.PublicIpAddress))
            return ssh_client
        except Exception as e:
            print("Exception while connecting to the instance, Exception for your reference : " + str(e))
            sys.exit(1)

    def execute_command(self):
        """ Execute command in the aws instances"""
        try:
            ssh_client = self.connect_to_aws_instanace()
            commands = [ "sudo apt update", \
                                    "sudo apt -y install ruby-bundler",\
                                    "git clone https://github.com/iproperty/simple-sinatra-app.git",\
                                    "cd simple-sinatra-app/ ; bundle install", \
                                    "cd simple-sinatra-app/ ; sudo bundle exec rackup --host 0.0.0.0 -p80 > application.log 2>&1 &"]
            for command in commands:
                stdin , stdout, stderr = ssh_client.exec_command(command)
                stdout.read()
                stderr.read()
                print("Successfully executed the command : " + str(command) )
            print("Application should be up and running, please check http://"+ str(self.PublicIpAddress))
            ssh_client.close()
        except Exception as e:
            print("Exception while connecting to the instance, Exception for your reference : " + str(e))
            sys.exit(1)

        

if __name__ == '__main__':
    # Launching the aws ec2 instance
    aws_ec2_instance = aws_ec2()
    # Creating the key pair file name
    key_pair_file_name= aws_ec2_instance.create_key_pair_using_boto3()
    # Creating the security group 
    aws_ec2_instance.create_security_group_using_boto3()
    # Launching the ec2 instance
    PublicDnsName,PublicIpAddress = aws_ec2_instance.create_ec2_instance_using_boto3()
    # Connecting to instance to install the application
    aws_ec2_instance = install_application(PublicDnsName,PublicIpAddress,key_pair_file_name)
    # Executing the list of commands in the instance
    aws_ec2_instance.execute_command()
    

