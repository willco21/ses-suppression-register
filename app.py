#!/usr/bin/env python3

from aws_cdk import core

from ses_suppression_register.ses_suppression_register_stack import SesSuppressionRegisterStack

app = core.App()

SesSuppressionRegisterStack(app, "ses-suppression-register")

app.synth()
