
# What ses_suppression_register?

* refs [Amazon SESを利用した際のバウンス率の抑制-バウンスしたメールアドレスをSuppression Listに自動的に追加する機能](https://docs.google.com/document/d/1Ds3_3ufIdhw6g8g6e-_blD4S18MnmlWy1s-96yFXwnI/edit#heading=h.9rndut2y9t0)

# Directory

```
|--Dockerfile
|--README.md
|--app.py
|--cdk-all-synth.sh
|--cdk.context.json
|--cdk.json
|--docker-compose-run.sh
|--docker-compose.yml
|--lambda
|  |--ses_suppression_list_auto_register.py
|  |--set_identity_notifications.py
|  |--test_event
|  |  |--ses_suppression_list_auto_register.json
|  |  |--set_identity_notifications.json
|--output_template
|  |--ses-suppression-register.yml
|--requirements.txt
|--ses_suppression_register
|  |--__init__.py
|  |--ses_suppression_register_stack copy.py
|  |--ses_suppression_register_stack.py
|--setup.py
```

# prepare

you can use docker env.
please exec this shell commnad
```
./docker-compose-run.sh 
```

* **By default, the docker image created will copy `~/.aws` from your computer. Therefore, you can use the aws profile information of the host PC.**


* If you want to use specific credentials that are not in aws profile, you can specify them when you run this script and put them in the docker environment variable.
  * ```
    $ AWS_ACCESS_KEY_ID={AWS_ACCESS_KEY_ID} AWS_SECRET_ACCESS_KEY={AWS_SECRET_ACCESS_KEY} AWS_SESSION_TOKEN={AWS_SESSION_TOKEN} ./docker-compose-run.sh 
    ```
  OR 
  * ```
    $ AWS_ACCESS_KEY_ID={AWS_ACCESS_KEY_ID} AWS_SECRET_ACCESS_KEY={AWS_SECRET_ACCESS_KEY} ./docker-compose-run.sh
    ```

# For MR

* The MR must also include a CFN template created by the CDK

* At this point you can now synthesize the CloudFormation template for this code.

```
$ ./cdk-all-synth.sh
```

* If you synthesize specific stack
```
$ cdk synth {stack_name}
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

# For test

### CDK
* If you exec `cdk deploy`, you inject command for give context
* You can use the aws profile information below `~/.aws/credential`. Specify profile name as a runtime argument
  * If not specified, the AWS credentials set in the environment variable are used.

```
$ cdk deploy -c identity={ses identity domain} --profile {Your AWS Profile name}
```

* Use AWS credentials set in the environment variable

```
$ cdk deploy -c identity={ses identity domain}
```

### lambda
* you can test lambda script in local. 
* If you run script in local, script use test_event.
* you can test some event case by edit json file in test_event
* You can use the aws profile information below `~/.aws/credential`. Specify profile name as a runtime argument
  * If not specified, the AWS credentials set in the environment variable are used.

```
|--lambda
|  |--ses_suppression_list_auto_register.py
|  |--set_identity_notifications.py
|  |--test_event
|  |  |--ses_suppression_list_auto_register.json
|  |  |--set_identity_notifications.json
```


```
$ cd lambda
$ python ses_suppression_list_auto_register.py 
$ python set_identity_notifications.py
```

* Use AWS credentials set in the environment variable

````
$ cd lambda
$ python ses_suppression_list_auto_register.py {Your AWS Profile name}
$ python set_identity_notifications.py {Your AWS Profile name}
````


## CDK Useful commands 

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
