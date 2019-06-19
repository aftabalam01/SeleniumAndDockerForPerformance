from awsapi import AwsAPI
from logger import Logger
from config import CONFIG
import inspect
import json
import os
import sys

__author__ = 'aftabalam01'

PERF_ENABLE_ENV = os.getenv("PERFORMANCE_ENABLE", CONFIG.get('performance_enable'))
ENV = os.getenv("ENV", CONFIG.get('default_env'))
Logger = Logger()
class BrowserPerformance(object):
    """
    input Browser windows driver. this util will execute java script to capture performance 
    navigation API timing as json and then post it to aws sqs
    """
    def __init__(self,
                 webdriver, env=ENV,application="Enterprise Applications", inputlogger=Logger.getLogger(name=__name__,level=CONFIG.get('logging').get('level') )):
        self.awsapi = AwsAPI(environment=ENV)
        self.logger = inputlogger
        self.application_name=application
        self.webdriver = webdriver
        self.testenv = env
        self.config = CONFIG.get('aws').get(ENV)
        self.perf_metric_sqs_url = self.config.get('perf_metric_sqs_url')
        self.perf_metric_s3 = self.config.get('perf_metric_s3')


    def _get_caller_details(self,skip=2):
        """
        Get a name of a caller in the format module.class.method

        `skip` specifies how many levels of stack to skip while getting caller
        name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.

        An empty string is returned if skipped levels exceed stack height
        """

        def stack_(frame):
            framelist = []
            while frame:
                framelist.append(frame)
                frame = frame.f_back
            return framelist

        stack = stack_(sys._getframe(1))
        start = 0 + skip
        if len(stack) < start + 1:
            return ''
        parentframe = stack[start]

        name = []
        module = inspect.getmodule(parentframe)

        if module:
            name.append(module.__name__)
        # detect classname
        if 'self' in parentframe.f_locals:
            name.append(parentframe.f_locals['self'].__class__.__name__)
        codename = parentframe.f_code.co_name
        if codename != '<module>':  # top level usually
            name.append(codename)  # function or a method
        del parentframe
        self.logger.info("calling method is {}".format(".".join(name)))
        return ".".join(name)

    def _enable_navigation_timing(self):
        """
        This method enables or disables browser navigation timing capture
        if PERFORMANCE_ENABLE is set to 1 and application is set to capture navigation timing in CONFIG .
        if application is not set in CONFIG, global default value is considered
        :return:
        """

        if PERF_ENABLE_ENV and self.config.get('navigation_timing',True):
            enable_nav_timing = True
        else:
            enable_nav_timing = False
        return enable_nav_timing

    def _enable_profiler_log(self):
        """
        This method enables or disables browser profiler log capture
        if PERFORMANCE_ENABLE is set to 1 and application is set to  profiler log in CONFIG .
        if application is not set in CONFIG, global default value is considered

        :return:
        """

        if PERF_ENABLE_ENV  and self.config.get('profiler_log',False):
            enable_profiler_log = True
        else:
            enable_profiler_log = False
        return enable_profiler_log

    def set_page_context(self, action, testname=None,  pageContext=None,):
        """

        :param action: required
        :param testname:
        :param pageContext:
        :return:
        """
        caller_details = self._get_caller_details().split(".")
        # TODO: need to check or handle len of caller_details is <2
        if not testname :
            testname = caller_details[-2]
        if not pageContext:
            pageContext = caller_details[-1]

        self.testname = testname
        self.pageContext = pageContext
        self.action = action

    def message_sqs_send(self,message):
        """
        message : json message that needed to be send to SQS
        updates messages with test context
        uses awsapi.send_sqs_message method to post json message to SQS
        :return:
        """
        if message :
            # add context in message
            message_json = {}
            message_json['metrics'] = message
            message_json['msgtype'] = "navigationtiming"
            message_json['testcontext']={"testname":self.testname,"env":self.testenv,"pageContext":self.pageContext,"action":self.action,"applicationname":self.application_name}
            self.awsapi.send_sqs_message(self.perf_metric_sqs_url,message_json=message_json)

    def message_s3_upload(self,message):
        """
        message : json log contents
        creates filepath using test context
        uses awsapi.upload_s3_json_file method to save logs in S3 for furthure analysis
        :return:
        """

        if message:
            # create filepath with test context in message
            filename = self.testenv+"/"+self.testname+"/"+self.pageContext+"_"+self.action + ".json"
            self.awsapi.upload_s3_json_file(s3_bucket=self.perf_metric_s3,message_json=message,filename=filename)

    def capture_navigation_timing(self):
        """
        capture browser navigating time as json
        call message_sqs_send with navigation timing json object
        :return:
        """

        if self._enable_navigation_timing():
            self.logger.info("to get Performance Navigation Timings")
            try:
                perf_json = self.webdriver.execute_script("return window.performance.timing")
                self.logger.info("Performance Navigation Timings{}".format(perf_json))
                if perf_json:
                    self.message_sqs_send(message=perf_json)

            except Exception as e:
                self.logger.error("Unable to get Performance Navigation Timings {}".format(e))

    def capture_profiler_log(self):
        """
        driver should have
        caps = DesiredCapabilities.CHROME
        caps['loggingPrefs'] = {'performance': 'ALL'}
        driver = webdriver.Chrome(desired_capabilities=caps)

        capture browser performance log as json
        call message_s3_upload with log as json object

        :return:
        """
        if self._enable_profiler_log():
            try:
                logs = [json.loads(log['message'])['message'] for log in self.webdriver.get_log('performance')]

                if logs :
                    self.message_s3_upload(message=logs)
            except (Exception):
                self.logger.error("Unable to get Performance profiler log")

