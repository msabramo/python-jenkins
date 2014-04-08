import json
import unittest

from mock import patch

from tests.helper import jenkins


class JenkinsTest(unittest.TestCase):

    def test_constructor(self):
        j = jenkins.Jenkins('http://example.com/', 'test', 'test')
        self.assertEqual(j.server, 'http://example.com/')
        self.assertEqual(j.auth, b'Basic dGVzdDp0ZXM=\n')
        self.assertEqual(j.crumb, None)

        j = jenkins.Jenkins('http://example.com', 'test', 'test')
        self.assertEqual(j.server, 'http://example.com/')
        self.assertEqual(j.auth, b'Basic dGVzdDp0ZXM=\n')
        self.assertEqual(j.crumb, None)

        j = jenkins.Jenkins('http://example.com')
        self.assertEqual(j.server, 'http://example.com/')
        self.assertEqual(j.auth, None)
        self.assertEqual(j.crumb, None)

    @patch.object(jenkins.Jenkins, 'jenkins_open')
    def test_get_job_config_encodes_job_name(self, jenkins_mock):
        """
        The job name parameter specified should be urlencoded properly.
        """
        j = jenkins.Jenkins('http://example.com/', 'test', 'test')
        j.get_job_config(u'Test Job')

        self.assertEqual(jenkins_mock.call_args[0][0].get_full_url(),
                         u'http://example.com/job/Test%20Job/config.xml')

    @patch.object(jenkins.Jenkins, 'jenkins_open')
    def test_maybe_add_crumb(self, jenkins_mock):
        jenkins_mock.return_value = False
        j = jenkins.Jenkins('http://example.com/', 'test', 'test')
        request = jenkins.Request('http://example.com/job/TestJob')

        j.maybe_add_crumb(request)

    @patch.object(jenkins.Jenkins, 'jenkins_open')
    def test_get_build_info(self, jenkins_mock):
        """
        The job name parameter specified should be urlencoded properly.
        """
        build_info_to_return = {
            u'building': False,
            u'msg': u'test',
            u'revision': 66,
            u'user': u'unknown'
        }
        jenkins_mock.return_value = json.dumps(build_info_to_return)
        j = jenkins.Jenkins('http://example.com/', 'test', 'test')

        build_info = j.get_build_info(u'TestJob', number=52)

        self.assertEqual(build_info, build_info_to_return)
        self.assertEqual(jenkins_mock.call_args[0][0].get_full_url(),
                         u'http://example.com/job/TestJob/52/api/json?depth=0')

    @patch.object(jenkins.Jenkins, 'jenkins_open')
    def test_get_job_info(self, jenkins_mock):
        """
        The job name parameter specified should be urlencoded properly.
        """
        job_info_to_return = {
            u'building': False,
            u'msg': u'test',
            u'revision': 66,
            u'user': u'unknown'
        }
        jenkins_mock.return_value = json.dumps(job_info_to_return)
        j = jenkins.Jenkins('http://example.com/', 'test', 'test')

        job_info = j.get_job_info(u'TestJob')

        self.assertEqual(job_info, job_info_to_return)
        self.assertEqual(jenkins_mock.call_args[0][0].get_full_url(),
                         u'http://example.com/job/TestJob/api/json?depth=0')

    @patch.object(jenkins.Jenkins, 'jenkins_open')
    def test_get_job_info__None(self, jenkins_mock):
        """
        The job name parameter specified should be urlencoded properly.
        """
        jenkins_mock.return_value = None
        j = jenkins.Jenkins('http://example.com/', 'test', 'test')

        # Note that if we commit to pytest, we can use pytest.raises here...
        try:
            job_info = j.get_job_info(u'TestJob')
            self.fail("This should've failed with JenkinsException")
        except jenkins.JenkinsException:
            pass

    @patch.object(jenkins.Jenkins, 'jenkins_open')
    def test_get_job_info__invalid_json(self, jenkins_mock):
        """
        The job name parameter specified should be urlencoded properly.
        """
        jenkins_mock.return_value = 'Invalid JSON'
        j = jenkins.Jenkins('http://example.com/', 'test', 'test')

        # Note that if we commit to pytest, we can use pytest.raises here...
        try:
            job_info = j.get_job_info(u'TestJob')
            self.fail("This should've failed with JenkinsException")
        except jenkins.JenkinsException as exc:
            self.assertEqual(str(exc), 'Could not parse JSON info for job[TestJob]')

    @patch.object(jenkins.Jenkins, 'jenkins_open')
    def test_get_job_info__HTTPError(self, jenkins_mock):
        """
        The job name parameter specified should be urlencoded properly.
        """
        jenkins_mock.side_effect = jenkins.HTTPError(
            'http://example.com/job/TestJob/api/json?depth=0',
            code=401,
            msg="basic auth failed",
            hdrs=[],
            fp=None)
        j = jenkins.Jenkins('http://example.com/', 'test', 'test')

        # Note that if we commit to pytest, we can use pytest.raises here...
        try:
            job_info = j.get_job_info(u'TestJob')
            self.fail("This should've failed with JenkinsException")
        except jenkins.JenkinsException as exc:
            self.assertEqual(str(exc), 'job[TestJob] does not exist')

    @patch.object(jenkins.Jenkins, 'jenkins_open')
    def test_debug_job_info(self, jenkins_mock):
        """
        The job name parameter specified should be urlencoded properly.
        """
        job_info_to_return = {
            u'building': False,
            u'msg': u'test',
            u'revision': 66,
            u'user': u'unknown'
        }
        jenkins_mock.return_value = json.dumps(job_info_to_return)
        j = jenkins.Jenkins('http://example.com/', 'test', 'test')

        j.debug_job_info(u'TestJob')

        self.assertEqual(jenkins_mock.call_args[0][0].get_full_url(),
                         u'http://example.com/job/TestJob/api/json?depth=0')

    @patch.object(jenkins.Jenkins, 'jenkins_open')
    def test_get_info(self, jenkins_mock):
        job_info_to_return = {
            u'jobs': {
                u'url': u'http://your_url_here/job/my_job/',
                u'color': u'blue',
                u'name': u'my_job',
            }
        }
        jenkins_mock.return_value = json.dumps(job_info_to_return)
        j = jenkins.Jenkins('http://example.com/', 'test', 'test')

        job_info = j.get_info()

        self.assertEqual(job_info, job_info_to_return)
        self.assertEqual(jenkins_mock.call_args[0][0].get_full_url(),
                         u'http://example.com/api/json')

    @patch.object(jenkins.Jenkins, 'jenkins_open')
    def test_get_job_name(self, jenkins_mock):
        """
        The job name parameter specified should be urlencoded properly.
        """
        job_name_to_return = {u'name': 'TestJob'}
        jenkins_mock.return_value = json.dumps(job_name_to_return)
        j = jenkins.Jenkins('http://example.com/', 'test', 'test')

        job_name = j.get_job_name(u'TestJob')

        self.assertEqual(job_name, 'TestJob')
        self.assertEqual(jenkins_mock.call_args[0][0].get_full_url(),
                         u'http://example.com/job/TestJob/api/json?tree=name')

    @patch.object(jenkins.Jenkins, 'jenkins_open')
    def test_get_job_name__None(self, jenkins_mock):
        """
        The job name parameter specified should be urlencoded properly.
        """
        jenkins_mock.return_value = None
        j = jenkins.Jenkins('http://example.com/', 'test', 'test')

        job_name = j.get_job_name(u'TestJob')

        self.assertEqual(job_name, None)
        self.assertEqual(jenkins_mock.call_args[0][0].get_full_url(),
                         u'http://example.com/job/TestJob/api/json?tree=name')

    @patch.object(jenkins.Jenkins, 'jenkins_open')
    def test_get_job_name__unexpected_job_name(self, jenkins_mock):
        """
        The job name parameter specified should be urlencoded properly.
        """
        job_name_to_return = {u'name': 'not the right name'}
        jenkins_mock.return_value = json.dumps(job_name_to_return)
        j = jenkins.Jenkins('http://example.com/', 'test', 'test')

        try:
            job_name = j.get_job_name(u'TestJob')
            self.fail("This should've failed with JenkinsException")
        except jenkins.JenkinsException as exc:
            self.assertEqual(str(exc), "Jenkins returned an unexpected job name")

    @patch.object(jenkins.Jenkins, 'jenkins_open')
    def test_cancel_queue(self, jenkins_mock):
        job_name_to_return = {u'name': 'TestJob'}
        jenkins_mock.return_value = json.dumps(job_name_to_return)
        j = jenkins.Jenkins('http://example.com/', 'test', 'test')

        j.cancel_queue(52)

        self.assertEqual(jenkins_mock.call_args[0][0].get_full_url(),
                         u'http://example.com/queue/item/52/cancelQueue')

    @patch.object(jenkins.Jenkins, 'jenkins_open')
    def test_get_queue_info(self, jenkins_mock):
        """
        The job name parameter specified should be urlencoded properly.
        """
        queue_info_to_return = {
            'items': {
                u'task': {
                    u'url': u'http://your_url/job/my_job/',
                    u'color': u'aborted_anime',
                    u'name': u'my_job'
                },
                u'stuck': False,
                u'actions': [
                    {
                        u'causes': [
                            {
                                u'shortDescription': u'Started by timer',
                            },
                        ],
                    },
                ],
                u'buildable': False,
                u'params': u'',
                u'buildableStartMilliseconds': 1315087293316,
                u'why': u'Build #2,532 is already in progress (ETA:10 min)',
                u'blocked': True,
            }
        }
        jenkins_mock.return_value = json.dumps(queue_info_to_return)
        j = jenkins.Jenkins('http://example.com/', 'test', 'test')

        queue_info = j.get_queue_info()

        self.assertEqual(queue_info, queue_info_to_return['items'])
        self.assertEqual(jenkins_mock.call_args[0][0].get_full_url(),
                         u'http://example.com/queue/api/json?depth=0')
