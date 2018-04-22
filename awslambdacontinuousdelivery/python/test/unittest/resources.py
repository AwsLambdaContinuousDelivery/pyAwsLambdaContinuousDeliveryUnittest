# By Janos Potecki
# University College London
# January 2018

from awslambdacontinuousdelivery.tools.iam import defaultAssumeRolePolicyDocument
from awslambdacontinuousdelivery.tools import alphanum

from troposphere import Template, Ref, Sub, Join
from troposphere.codebuild import ( Project
  , Environment, Source, Artifacts )
from troposphere.codepipeline import ( InputArtifacts
  , Actions, Stages, ActionTypeID, OutputArtifacts )
from troposphere.iam import Role, Policy

from typing import List, Tuple

import awacs.aws
from awacs.aws import Statement, Action, Allow

def getBuildRole() -> Role:
  statement = Statement( Action = [ Action("*") ]
                       , Effect = Allow
                       , Resource = ["*"]
                       )
  policy_doc = awacs.aws.Policy( Statement = [ statement ] )
  policy = Policy( PolicyName = Sub("${AWS::StackName}-UnittestPolicy")
                 , PolicyDocument = policy_doc
                 )
  assume = defaultAssumeRolePolicyDocument("codebuild.amazonaws.com")
  return Role( "UnittestRole"
             , RoleName = Sub("${AWS::StackName}-UnittestRole")
             , AssumeRolePolicyDocument = assume
             , Policies = [policy]
             )


def getDockerBuildAction( buildRef
                        , inputs: List[str]
                        , number = 1
                        ) -> Actions:
  '''
  Takes a build reference which points to the build configuration,
  input/output map with the names of the artifacts and (optimal) a number,
  if multiple build actions must be added to the same pipeline
  '''
  number = str(number)
  inputArts  = map(lambda x: InputArtifacts( Name = x ), inputs)
  actionId = ActionTypeID( Category = "Build"
                         , Owner = "AWS"
                         , Version = "1"
                         , Provider = "CodeBuild"
                         )
  return Actions( Name = Sub("${AWS::StackName}-UnittestAction" + number)
                , ActionTypeId = actionId
                , InputArtifacts = list(inputArts)
                , RunOrder = number
                , Configuration = { "ProjectName" : Ref(buildRef) }
                )


def getCodeBuild( name: str
                , serviceRole: Role
                , buildspec: List[str]
                ) -> Project:
  env = Environment( ComputeType = "BUILD_GENERAL1_SMALL"
                   , Image = "frolvlad/alpine-python3"
                   , Type = "LINUX_CONTAINER"
                   , PrivilegedMode = False
                   )
  source = Source( Type = "CODEPIPELINE"
                 , BuildSpec = Join("\n", buildspec)
                 )
  artifacts = Artifacts( Type = "CODEPIPELINE" )
  return Project( alphanum(name)
                , Name = Sub("${AWS::StackName}-" + alphanum(name))
                , Environment = env
                , Source = source
                , Artifacts = artifacts
                , ServiceRole = Ref(serviceRole)
                )


def getUnittestBuildSpec() -> List[str]:
  return [ "version: 0.2"
         , "\n"
         , "phases:"
         , "  install:"
         , "    commands:"
         , "      - apk add --no-cache curl python pkgconfig python3-dev openssl-dev libffi-dev musl-dev make gcc"
         , "      - pip3 install moto"
         , "      - pip3 install boto3"           
         , "      - pip3 install troposphere"
         , "      - pip3 install awacs"           
         , "      - pip3 install -r requirements.txt"
         , "      - pip3 install pyyaml"
         , "  pre_build:"
         , "    commands:"
         , "      - wget https://raw.githubusercontent.com/AwsLambdaContinuousDelivery/pyAwsLambdaContinuousDeliveryUnittest/master/executable/testRunner.py"         , "  build:"
         , "    commands:"
         , "      - python3 testRunner.py"
         ]

def getUnittestBuilder(role: Role) -> Actions:
  cfSpec = getUnittestBuildSpec()
  return getCodeBuild("unittestBuilder", role, cfSpec)
