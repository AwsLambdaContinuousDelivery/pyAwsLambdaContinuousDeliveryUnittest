# By Janos Potecki
# University College London
# January 2018

from awslambdacontinuousdelivery.python.test.unittest.resources import *

from troposphere import GetAtt, Template

import awacs.aws

from typing import Tuple

def getUnittest( template: Template
               , sourcecode
               ) -> Stages:
  role = template.add_resource(getBuildRole())
  unittestBuilder = getUnittestBuilder(role)
  unittestBuilderRef = template.add_resource(unittestBuilder)
  action = getDockerBuildAction(unittestBuilder, [sourcecode])
  return Stages( "UnittestStage"
               , Name = "Unittests"
               , Actions = [ action ]
               )
