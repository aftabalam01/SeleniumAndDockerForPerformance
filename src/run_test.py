import subprocess
from multiprocessing import dummy as multiprocessing
from datetime import datetime
from random import choice
import boto3
import sys


def run_aws_task(env_var):
    """

    :param urls: list of users to be opened
    :return:
    """
    
    taskoverrides = {"containerOverrides": [
                        {"name": "performance-loadtest-task",
                            "command": ["python3","./src/test_script.py"],
                            "environment":[
                                {"name": "LOGIN_ID","value":env_var[1][0]}
                                , {"name": "LOGIN_PASSWD","value":env_var[1][1]}
                                , {"name": "USER_NUM","value": env_var[0]}
                                , {"name": "NUM_URLS","value":"10"}
                                ],
                         "cpu": 1024,
                         "memory": 512,
                         "memoryReservation": 512
                         }
                        ],
                    "taskRoleArn": "arn:aws:iam::<account>:role/eats-performance-ecs-task-role",
                    "executionRoleArn": "arn:aws:iam::<account>:role/eats-performance-ecs-task-role"
                    }

    networkoverrides = {"awsvpcConfiguration": {
                                    "subnets": ["subnet-636363", "subnet-36363"],
                                    "securityGroups": ["sg-13525256235"],
                                    "assignPublicIp": "DISABLED"}}
    client = boto3.client('ecs')
    start_time = datetime.now()
    response = task_arn = None
    try:
        response = client.run_task(
            cluster='performance-task',
            taskDefinition='performance-loadtest-task',
            overrides=taskoverrides,
            networkConfiguration=networkoverrides
        )
        task_arn = response['tasks'][0]['taskArn']
    
        waiter = client.get_waiter('tasks_stopped')
        waiter.wait(cluster='performance-task',
                    tasks=[task_arn],
                    WaiterConfig={
                        'Delay': 10,
                        'MaxAttempts': 600})
    except:
        print(f"error:{response}")

    end_time = datetime.now()
    print(f"{start_time},{end_time},{end_time-start_time} {env_var[0]}, {task_arn} : completed")


def run_wikitest(curr_user=10):
    user_nums = [x for x in range(1,28000,10)]  # get the list of commands
        login_cred = []
        env_vars = []
        with open("./cred/login.txt",'r') as cred_file:
            creds = cred_file.readlines()
            for line in creds:
                temp_line = line.rstrip('\n').split(',')
                login_cred.append([temp_line[0],temp_line[1]])
        for user_num in user_nums :
            env_vars.append([str(user_num),choice(login_cred)])

        pool = multiprocessing.Pool(processes=curr_user)  # create thread pool
        # pool.imap_unordered(run_docker_load, env_vars)
        pool.imap_unordered(run_aws_task, env_vars)
        pool.close()
        pool.join()


if __name__=='__main__':
    curr_user = 50
    run_wikitest(curr_user=curr_user)