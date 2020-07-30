import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="ses_suppression_register",
    version="0.0.1",

    description="An empty CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "ses_suppression_register"},
    packages=setuptools.find_packages(where="ses_suppression_register"),

    install_requires=[
        "aws-cdk.core",
        "aws-cdk.aws_cloudformation",
        "aws-cdk.aws-iam",
        "aws-cdk.aws-ses",
        "aws-cdk.aws-sqs",
        "aws-cdk.aws-sns",
        "aws-cdk.aws_sns_subscriptions",
        "aws-cdk.aws-lambda",
        "aws-cdk.aws-lambda-event-sources",
        "boto3",
        "cfnresponse"
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
