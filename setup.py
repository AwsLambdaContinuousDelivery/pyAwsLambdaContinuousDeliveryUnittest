#!/usr/bin/env python

from distutils.core import setup

setup( name='pyAwsLambdaContinuousDeliveryUnittest'
     , version = '0.0.2'
     , description = 'pyAwsLambdaContinuousDeliveryUnittest'
     , author = 'Janos Potecki'
     , url = 'https://github.com/AwsLambdaContinuousDelivery/pyAwsLambdaContinuousDeliveryUnittest'
     , packages = ['awslambdacontinuousdelivery.python.test.unittest']
     , license='MIT'
     , install_requires = [ 
          'troposphere'
        , 'awacs'
        ]
     )
