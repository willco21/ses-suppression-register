import os
from aws_cdk import (
    core,
    aws_cloudformation as cfn,
    aws_iam as iam,
    aws_ses as ses,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_lambda,
    aws_lambda_event_sources as lambda_event,
)
import boto3
import pprint
import uuid

class SesSuppressionRegisterStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # cfn Parameter
        manual_identity = self.node.try_get_context("identity") # you inject command cdk *** -c identity={ses identity domain}.
        param_identity_domain = core.CfnParameter(self, 'IdentityDomain',type='CommaDelimitedList', default=manual_identity)
        param_notice_bounce = core.CfnParameter(self, 'IsNoticeBounce', type='String', allowed_values=['True', 'False'], default='True')
        param_notice_complaint = core.CfnParameter(self, 'IsNoticeComplaint', type='String', allowed_values=['True', 'False'], default='False')
        param_bounce_herders = core.CfnParameter(self, 'IsBounceHeaders', type='String', allowed_values=['True', 'False'], default='False')
        param_complaint_herders = core.CfnParameter(self, 'IsComplaintHeaders', type='String', allowed_values=['True', 'False'], default='False')

        # SQS queue
        queue = sqs.Queue(
            self, "SQSQueue",
            queue_name="ses-suppression-list-queue",
            visibility_timeout=core.Duration.seconds(30), # default,
            receive_message_wait_time=core.Duration.seconds(20)
        )

        # SNS topic
        topic = sns.Topic(
            self, "SNSTopic",
            topic_name='ses-suppression-list-topic',
            display_name='ses-suppression-list-topic',
        )
        topic.add_subscription(subscriptions.SqsSubscription(queue))
        #pprint.pprint(param_notification_type.value_as_list)


        # custom resource for SES set dentity notification
        ## Configuration value that is a different based on IsNoticeBounce/IsNoticeComplaint/IsBounceHeaders/IsComplaintHeaders
        self.custom_provide_ses_set_identity_notifications(
            param_identity_domain.value_as_list, topic.topic_arn,
            param_notice_bounce, param_notice_complaint, param_bounce_herders, param_complaint_herders
        )

        # IAM policy/Role(Lambda Function)
        ses_suppressed_policy = iam.ManagedPolicy(
            self,'lambdaPolicy',
            managed_policy_name='lambdaPolicy',
            statements=[
                iam.PolicyStatement(effect=iam.Effect.ALLOW, actions=["ses:*Suppressed*"], resources=["*"])
            ]
        )
        lambda_role = iam.Role(
            self,'lambdaRole',
            role_name= 'lambdaRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaSQSQueueExecutionRole'),
                ses_suppressed_policy
            ]
        )
        
        # Lambda Function
        with open('lambda/ses_suppression_list_auto_register.py', 'r') as f:
            fn = aws_lambda.Function(
                self, "LambdaFunction",
                runtime=aws_lambda.Runtime.PYTHON_3_7,
                role= lambda_role,
                code=aws_lambda.InlineCode(f.read()),
                handler="index.lambda_handler",
                function_name='ses_suppression_list_auto_register',
                events=[lambda_event.SqsEventSource(queue,batch_size=10)],
                memory_size=128,
                timeout=core.Duration.seconds(5),
                environment={},
            )
        
    def create_param_identity_domain(self):
        ses = boto3.client("ses", region_name=self.ses_region)
        domain_list = ses.list_identities(IdentityType='Domain').get('Identities')
        test_identity = self.node.try_get_context("identity")
        allowed_values = list(set(domain_list + [test_identity])) if test_identity else domain_list
        return core.CfnParameter(self, 'IdentityDomain',
            type='String',
            default=test_identity,
            allowed_values=allowed_values
        )

    def custom_provide_ses_set_identity_notifications(self, identity_domain, topic_arn, param_notice_bounce, param_notice_complaint, param_bounce_herders, param_complaint_herders):

        # set cfn condition Fn::Equals
        is_bounce = core.CfnCondition(self, "ConditionIsBounce",
            expression=core.Fn.condition_equals(param_notice_bounce.value_as_string, "True")
        )
        is_complaint = core.CfnCondition(self, "ConditionIsComplaint",
            expression=core.Fn.condition_equals(param_notice_complaint.value_as_string, "True")
        )
        is_bounce_headers = core.CfnCondition(self, "ConditionIsBounceHeaders",
            expression=core.Fn.condition_equals(param_bounce_herders.value_as_string, "True")
        )
        is_complaint_headers = core.CfnCondition(self, "ConditionIsComplaintHeaders",
            expression=core.Fn.condition_equals(param_complaint_herders.value_as_string, "True")
        )

        # set cfn condition Fn::If
        bounce_topic_arn = core.Fn.condition_if(is_bounce.logical_id, topic_arn, '').to_string()
        complaint_topic_arn = core.Fn.condition_if(is_complaint.logical_id, topic_arn, '').to_string()

        # create custom resource provider by lambda
        with open('lambda/set_identity_notifications.py', 'r') as f:
            provider = cfn.CustomResourceProvider.from_lambda(
                aws_lambda.SingletonFunction(self, 'singleton',
                    uuid='825ec7fe-5f19-487d-87a4-7e894a9af959',
                    runtime=aws_lambda.Runtime.PYTHON_3_7,
                    initial_policy=[
                        iam.PolicyStatement(effect=iam.Effect.ALLOW, actions=["sts:*","ses:SetIdentity*"], resources=["*"])
                    ],
                    code=aws_lambda.InlineCode(f.read()),
                    handler="index.handler",
                    function_name='set_identity_notifications',
                    memory_size=128,
                    timeout=core.Duration.seconds(5),
                )
            )
        
        cfn.CustomResource(self, "ProvideSetIdentityNotifications",
            provider=provider,
            properties={
                "Identities": identity_domain,
                "BounceTopic": bounce_topic_arn,
                "ComplaintTopic": complaint_topic_arn,
                "HeadersInBounceNotificationsEnabled": core.Fn.condition_if(is_bounce_headers.logical_id, 'True', 'False').to_string(),
                "HeadersInComplaintNotificationsEnabled": core.Fn.condition_if(is_complaint_headers.logical_id, 'True', 'False').to_string()
            }
        )