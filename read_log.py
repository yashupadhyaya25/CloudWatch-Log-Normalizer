import boto3
from configparser import ConfigParser
import os
import json
from datetime import datetime

config = ConfigParser()
config.read('config.ini')

aws_access_key_id = config.get('Dev','aws_access_key_id')
aws_secret_key = config.get('Dev','aws_secret_key')

def store_logs(log_group_name,full_load) :
    if not(full_load) :
        today_date = datetime.strftime(datetime.now(),'%Y-%m-%d').replace('-','/')+'/'
    else :
        today_date = None

    cloud_watch_client = boto3.client('logs',region_name='us-east-1')
    next_token_flag = True
    log_stream_list = []
    stream_logstreams_res = cloud_watch_client.describe_log_streams(
        logGroupName=log_group_name,
        descending = False
        )
    next_token = stream_logstreams_res.get('nextToken')
    log_stream_list.extend(stream_logstreams_res.get('logStreams'))
    if next_token is not None :
        while next_token_flag :
            stream_logstreams_res = cloud_watch_client.describe_log_streams(
            logGroupName=log_group_name,
            descending = False,
            nextToken = next_token
            )
            next_token = stream_logstreams_res.get('nextToken')
            log_stream_list.extend(stream_logstreams_res.get('logStreams'))
            if next_token is None :
                next_token_flag = False

    today_log_stream_list = []
    if today_date is not None :
        for stream in log_stream_list :
            if today_date in stream.get('logStreamName') :
                today_log_stream_list.append(stream)
    if today_log_stream_list != [] :
        log_stream_list = today_log_stream_list

    for log_stream_dic in log_stream_list :
        log_stream_next_token_flag = True
        log_events_list = []
        log_stream_name = log_stream_dic.get('logStreamName')

        folder_name = log_group_name
        date = log_stream_name.split('[$LATEST]')[0].replace('/',' ').strip().replace(' ','-')
        stream_folder = log_stream_name.split('[$LATEST]')[1]
        folder_path = 'logs'+folder_name+'/'+date+'/'+stream_folder

        next_token = None

        if os.path.exists(folder_path) :
            with open(folder_path+'/next_token.json','r') as f :
                data = f.read()
            next_token = json.loads(data).get('next_token')

        if next_token is None :
            response = cloud_watch_client.get_log_events(
                logGroupName=log_group_name,
                logStreamName = log_stream_name,
                startFromHead = True
            )
            next_token = response.get('nextForwardToken')
            log_events_list.extend(response.get('events'))

        if next_token is not None :
            while log_stream_next_token_flag :
                response = cloud_watch_client.get_log_events(
                    logGroupName=log_group_name,
                    logStreamName = log_stream_name,
                    startFromHead = True,
                    nextToken = next_token
                )
                if response.get('events') == [] :
                    log_stream_next_token_flag = False
                else : 
                    next_token = response.get('nextForwardToken')
                    log_events_list.extend(response.get('events'))

        if log_events_list != [] :
            if not os.path.exists(folder_path) :
                os.makedirs(folder_path)
            with open(folder_path+'/log.json','a') as a:
                json.dump(log_events_list, a)
            a.close()

        with open(folder_path+'/next_token.json','w') as b :
            json.dump({'next_token' : next_token}, b)
        b.close()

if __name__ == '__main__' :
    store_logs(log_group_name='log_group_name',full_load=True)