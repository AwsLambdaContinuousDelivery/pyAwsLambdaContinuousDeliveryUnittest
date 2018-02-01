# awslambdacontinuousdelivery.python.test.unittest
## Overview

### Purpose
This packages creates a stage running unittests defined by the user.
It is advised to have this stage straight after the `Source` stage.

### Packages
- `awslambdacontinuousdelivery.test.unittest`

### License
- see `LICENSE` file

### Requirements
- `troposphere`
- `awacs`

## Quick Start
### Pipeline Template
```python
from troposphere import Template, Sub
from troposphere.codepipeline import Pipeline
from awslambdacontinuousdelivery.source.codecommit import getCodeCommit
from awslambdacontinuousdelivery.python.test.unittest import getUnittest
from awslambdacontinuousdelivery.tools.iam import \
     defaultAssumeRolePolicyDocument, oneClickCodePipeServicePolicy

# Create the necessary Role for the Pipeline
assume = defaultAssumeRolePolicyDocument("codepipeline.amazonaws.com")
policy = oneClickCodePipeServicePolicy()
pipeline_role = Role( "AwsLambdaPipelineRole"
                    , RoleName = Sub("${AWS::StackName}PipelineRole")
		    , AssumeRolePolicyDocument = assume
             	    , Policies = [policy]
             	    )

# create an S3 Bucket for the artifact storage
artifactStorage = Bucket( "ArtifactStoreS3Location"
    		        , AccessControl = "Private"
    			)

pipeline = "examplePipelineName"
template = Template()

sourceArtifactName = "SourceCode"

pipeline_stages = []
pipeline_stages.append(getCodeCommit(template, sourceArtifactName))
pipeline_stages.append(getUnittest(template, sourcceArtifactName))

pipeline = Pipeline( "AwsLambdaPipeline"
	           , Name = Sub("${AWS::StackName}-Pipeline")
		   , RoleArn = GetAtt(pipelineRole, "Arn")
		   , Stages = pipeline_stages
		   , ArtifactStore = artifactStorage
		   )
template.add_resource(pipeline)
print(template.to_json())
```

### config/config.yaml
In order to run the `unittests` you need to add the location of the unittests
to your `config/config.yaml` inside the `config` folder.
The fieldname is `Unittests`, which must have the subfield `Folder` pointing to the folder, and can optionally have a list of files in the subfield `Files`.

Assume the following folder structure:
```
|MyExampleFunction
||config
 || Alpha
 || PROD
 |-config.yaml
||test
 ||unittests
  |-test1.py
  |-test2.py
  |-test3.py
  |-requirements.txt
||src
 |-function.py
|-requirements.txt
```

Example for the config/config.yaml file for just executing `test1.py` and
`test2.py`:
```yaml
Name: MyExampleFunction
Handler: function.handler
Unittests:
  Folder: test/unittests
  Files:
    - test1.py
    - test2.py
```

Example for running all files in the folder:
```yaml
Name: MyExampleFunction
Handler: function.handler
Unittests:
  Folder: test/unittests
```

### test1.py
Every testfile suppost to be executed will need to be executed without any commandline arguments.

Example:
```python
import unittest
import hypothesis.strategies as st
from hypothesis import given, example, infer

import os, sys
# import the function files located at /src in order to call them from here
rootdir = os.path.join(os.path.dirname(__file__), "../../")
srcdir =  os.path.join(os.path.join(rootdir, "src"))
sys.path.insert(0, os.path.abspath(srcdir))

from function import handler
from typing import List
import logging

```


### (Optional) requirements.txt
If you want to use any non standard libraries for your unittests, you can
add a `requirements.txt` file to your unittest folder (as
shown in the example folder structure).
Every library specified in there will be installed before running the
unittests.