import logging
import boto3
from distutils.util import strtobool
import cfnresponse
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ses = boto3.client('ses')

def set_notifications(props, identity):
    logging.info("[START] set notifications: {}".format(identity))
    responce_data = {}
    for notification_type in ["Bounce", "Complaint"]:
        topic = props.get(f"{notification_type}Topic")
        kwargs = {"Identity": identity, "NotificationType": notification_type}
        if topic:
            kwargs["SnsTopic"] = topic
        responce_data[f"Notice{notification_type}"] = ses.set_identity_notification_topic(**kwargs)

        if topic:
            kwargs.pop("SnsTopic")
            kwargs["Enabled"] = bool(strtobool(props.get(f"HeadersIn{notification_type}NotificationsEnabled")))
            responce_data[f"Headers{notification_type}"] = ses.set_identity_headers_in_notifications_enabled(**kwargs)
    logging.info("[SUCCESS] set notifications: {}".format(identity))
    return responce_data

def clear_notifications(props, identity):
    logging.info("[START] clear notifications: {}".format(identity))
    responce_data = {}
    for notification_type in ["Bounce", "Complaint"]:
        responce_data[f"Notice{notification_type}"] = ses.set_identity_notification_topic(
            Identity=identity, NotificationType=notification_type
        )
    logging.info("[SUCCESS] clear notifications: {}".format(identity))
    return responce_data

def on_create(event):
    props = event["ResourceProperties"]
    logging.info("create new resource with props {}".format(props))
    return {identity: set_notifications(props, identity) for identity in props['Identities']}

def on_update(event):
    physical_id = event["PhysicalResourceId"]
    props = event["ResourceProperties"]
    old_props = event["OldResourceProperties"]

    set_identities_list = list(set(props['Identities']) - set(old_props['Identities']))
    clear_identities_list = list(set(old_props['Identities']) - set(props['Identities']))
    logging.info("update resource {} with props {}".format(physical_id, props))
    
    set_identities_dict = {identity: set_notifications(props, identity) for identity in set_identities_list}
    clear_identities_dict = {identity: clear_notifications(props, identity) for identity in clear_identities_list}

    return {'set_identities': set_identities_dict, 'clear_identities': clear_identities_dict}

def on_delete(event):
    physical_id = event["PhysicalResourceId"]
    props = event["ResourceProperties"]
    logging.info("delete resource {}".format(physical_id))
    return {identity: clear_notifications(props, identity) for identity in props['Identities']}

def on_event(event, context):
    logging.info('cfn_event:{}'.format(event))
    logging.info('context:{}'.format(context))
    request_type = event['RequestType']

    if request_type == 'Create': return on_create(event)
    if request_type == 'Update': return on_update(event)
    if request_type == 'Delete': return on_delete(event)
    raise Exception("Invalid request type: {}".format(request_type))

def handler(event, context):
    response_data = on_event(event, context)
    cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data, event.get('PhysicalResourceId'))

def main():
    import json
    context = {}

    args = sys.argv
    if (len(args) == 2):
        aws_profile = args[1]
        session = boto3.Session(profile_name=aws_profile)
        global ses
        ses = session.client('ses')
        logger.info('Use .aws/credential info. profile name [{}]'.format(aws_profile))

    with open('test_event/set_identity_notifications.json') as f:
        event = json.load(f)
    on_event(event, context)

if __name__ == "__main__":
    main()