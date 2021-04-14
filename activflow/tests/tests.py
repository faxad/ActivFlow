"""Tests for Core app"""
from django.contrib.auth.models import User, Group
from django.urls import reverse

from django.test import TestCase
from django.test import Client

from activflow.core.models import Request
from activflow.tests.models import Foo, Corge


class CoreTests(TestCase):
    """Core workflow engine tests"""
    def setUp(self):
        """Test Setup"""
        self.client = Client()
        self.submitter = Group.objects.create(name='Submitter')
        self.reviewer = Group.objects.create(name='Reviewer')

        self.john_doe = User.objects.create_user(
            'john_doe',
            'john@company.com',
            '12345')

        self.jane_smith = User.objects.create_user(
            'jane_smith',
            'jane@company.com',
            '12345')

        self.client.login(username='john_doe', password='12345')

    def test_available_workflows(self):
        """Tests view that lists workflows"""
        response = self.client.get(reverse('workflows'))
        self.assertEqual(response.status_code, 200,
                         'Response did not result in success')

    def test_workflow_detail_view(self):
        """Test to get requests for a workflow"""
        response = self.client.get(reverse(
            'workflow-detail',
            kwargs={'app_name': 'tests'}))

        self.assertEqual(response.status_code, 200,
                         'Response did not result in success')
        self.assertQuerysetEqual(
            response.context['requests'], [],
            'Response did not result in the expected '
            'instances of the workflow')

    def test_workflow_init_to_finish(self):
        """Tests the entire workflow cycle"""
        request_args = {
            'app_name': 'tests',
            'model_name': 'Foo',
            'pk': 'Initial'
        }

        for verb in ('get', 'post'):
            response = getattr(self.client, verb)(
                reverse(
                    'create',
                    kwargs=request_args
                ),
                {
                    'FooLineItemForm-0-plugh': '',
                    'FooLineItemForm-0-thud': '',
                    'FooLineItemForm-TOTAL_FORMS': 1,
                    'FooLineItemForm-INITIAL_FORMS': 0,
                    'FooLineItemForm-MIN_NUM_FORMS': 0,
                    'FooLineItemForm-MAX_NUM_FORMS': 1000,
                    'FooMoreLineItemForm-0-plughmore': '',
                    'FooMoreLineItemForm-0-thudmore': '',
                    'FooMoreLineItemForm-TOTAL_FORMS': 1,
                    'FooMoreLineItemForm-INITIAL_FORMS': 0,
                    'FooMoreLineItemForm-MIN_NUM_FORMS': 0,
                    'FooMoreLineItemForm-MAX_NUM_FORMS': 1000
                }
            )

            if verb == 'get':
                # Access Denied
                self.assertFalse('form' in response.context,
                                 'User has no access to initiate workflow, '
                                 'still the system did not limit')
                # Adds user to the group with permission
                self.submitter.user_set.add(self.john_doe)

            response = getattr(self.client, verb)(
                reverse(
                    'create',
                    kwargs=request_args),
                {
                    'FooLineItemForm-0-plugh': '',
                    'FooLineItemForm-0-thud': '',
                    'FooLineItemForm-TOTAL_FORMS': 1,
                    'FooLineItemForm-INITIAL_FORMS': 0,
                    'FooLineItemForm-MIN_NUM_FORMS': 0,
                    'FooLineItemForm-MAX_NUM_FORMS': 1000,
                    'FooMoreLineItemForm-0-plughmore': '',
                    'FooMoreLineItemForm-0-thudmore': '',
                    'FooMoreLineItemForm-TOTAL_FORMS': 1,
                    'FooMoreLineItemForm-INITIAL_FORMS': 0,
                    'FooMoreLineItemForm-MIN_NUM_FORMS': 0,
                    'FooMoreLineItemForm-MAX_NUM_FORMS': 1000
                }
            )

            self.assertEqual(response.context['form']._meta.model, Foo,
                             'User has access to initiate workflow, '
                             'still the context does not contain the '
                             'required form instance')

        # Post the form with validation failure
        response = self.client.post(
            reverse(
                'create',
                kwargs=request_args
            ),
            {
                'subject': 'test',
                'bar': 'example - small e',
                'baz': 'WL',
                'qux': 'Nothing',
                'FooLineItemForm-0-plugh': '',
                'FooLineItemForm-0-thud': '',
                'FooLineItemForm-TOTAL_FORMS': 1,
                'FooLineItemForm-INITIAL_FORMS': 0,
                'FooLineItemForm-MIN_NUM_FORMS': 0,
                'FooLineItemForm-MAX_NUM_FORMS': 1000,
                'FooMoreLineItemForm-0-plughmore': '',
                'FooMoreLineItemForm-0-thudmore': '',
                'FooMoreLineItemForm-TOTAL_FORMS': 1,
                'FooMoreLineItemForm-INITIAL_FORMS': 0,
                'FooMoreLineItemForm-MIN_NUM_FORMS': 0,
                'FooMoreLineItemForm-MAX_NUM_FORMS': 1000
            }
        )

        self.assertEqual(response.status_code, 200,
                         'Form post did not result in success')
        # No instance gets created because form is invalid
        self.assertEqual(Foo.objects.count(), 0,
                         'Validation errors still result in creation '
                         'of initial activity instance')

        # Post the form for adding related instance
        response = self.client.post(
            reverse(
                'create',
                kwargs=request_args
            ),
            {
                'subject': 'test',
                'bar': 'Example - small e',
                'baz': 'WL',
                'qux': 'Nothing',
                'add-FooLineItem': 'Add',
                'FooLineItemForm-0-plugh': '',
                'FooLineItemForm-0-thud': '',
                'FooLineItemForm-TOTAL_FORMS': 1,
                'FooLineItemForm-INITIAL_FORMS': 0,
                'FooLineItemForm-MIN_NUM_FORMS': 0,
                'FooLineItemForm-MAX_NUM_FORMS': 1000,
                'FooMoreLineItemForm-0-plughmore': '',
                'FooMoreLineItemForm-0-thudmore': '',
                'FooMoreLineItemForm-TOTAL_FORMS': 1,
                'FooMoreLineItemForm-INITIAL_FORMS': 0,
                'FooMoreLineItemForm-MIN_NUM_FORMS': 0,
                'FooMoreLineItemForm-MAX_NUM_FORMS': 1000
            }
        )

        response = self.client.post(
            reverse(
                'create',
                kwargs=request_args
            ),
            {
                'subject': 'test',
                'bar': 'Example - small e',
                'baz': 'WL',
                'qux': 'Nothing',
                'add-FooLineItem': 'Add',
                'FooLineItemForm-0-plugh': 'Abc',
                'FooLineItemForm-0-thud': 'GR',
                'FooLineItemForm-TOTAL_FORMS': 1,
                'FooLineItemForm-INITIAL_FORMS': 0,
                'FooLineItemForm-MIN_NUM_FORMS': 0,
                'FooLineItemForm-MAX_NUM_FORMS': 1000,
                'FooMoreLineItemForm-0-plughmore': 'Abc',
                'FooMoreLineItemForm-0-thudmore': 'GR',
                'FooMoreLineItemForm-TOTAL_FORMS': 1,
                'FooMoreLineItemForm-INITIAL_FORMS': 0,
                'FooMoreLineItemForm-MIN_NUM_FORMS': 0,
                'FooMoreLineItemForm-MAX_NUM_FORMS': 1000
            }
        )

        self.assertEqual(response.status_code, 200,
                         'Form post did not result in success')

        # Post the form again without any validation failure
        response = self.client.post(
            reverse(
                'create',
                kwargs=request_args
            ),
            {
                'subject': 'test',
                'bar': 'Example - small e',
                'baz': 'WL',
                'qux': 'Nothing',
                'FooLineItemForm-0-plugh': 'Abc',
                'FooLineItemForm-0-thud': 'GR',
                'FooLineItemForm-1-plugh': 'Abc',
                'FooLineItemForm-1-thud': 'GR',
                'FooLineItemForm-TOTAL_FORMS': 2,
                'FooLineItemForm-INITIAL_FORMS': 0,
                'FooLineItemForm-MIN_NUM_FORMS': 0,
                'FooLineItemForm-MAX_NUM_FORMS': 1000,
                'FooMoreLineItemForm-0-plughmore': 'Abc',
                'FooMoreLineItemForm-0-thudmore': 'GR',
                'FooMoreLineItemForm-TOTAL_FORMS': 1,
                'FooMoreLineItemForm-INITIAL_FORMS': 0,
                'FooMoreLineItemForm-MIN_NUM_FORMS': 0,
                'FooMoreLineItemForm-MAX_NUM_FORMS': 1000
            }
        )

        instances = Foo.objects.all()
        instance = instances.first()

        # Instance gets saved successfully against form submit
        self.assertEqual(instances.count(), 1,
                         'No validation errors, still initial activity '
                         'instance did not get created')

        # Redirects the control to update form
        request_args = {
            'app_name': 'tests',
            'model_name': 'Foo',
            'pk': instance.id
        }

        self.assertRedirects(
            response,
            reverse('update', kwargs=request_args),
            status_code=302,
            target_status_code=200)

        # Update activity
        for verb in ('get', 'post'):
            response = getattr(self.client, verb)(
                reverse(
                    'update',
                    kwargs=request_args),
                {
                    'FooLineItemForm-0-plugh': '',
                    'FooLineItemForm-0-thud': '',
                    'FooLineItemForm-TOTAL_FORMS': 1,
                    'FooLineItemForm-INITIAL_FORMS': 0,
                    'FooLineItemForm-MIN_NUM_FORMS': 0,
                    'FooLineItemForm-MAX_NUM_FORMS': 1000,
                    'FooMoreLineItemForm-0-plughmore': '',
                    'FooMoreLineItemForm-0-thudmore': '',
                    'FooMoreLineItemForm-TOTAL_FORMS': 1,
                    'FooMoreLineItemForm-INITIAL_FORMS': 0,
                    'FooMoreLineItemForm-MIN_NUM_FORMS': 0,
                    'FooMoreLineItemForm-MAX_NUM_FORMS': 1000
                }
            )

        # Post the form with SAVE action
        response = self.client.post(
            reverse(
                'update',
                kwargs=request_args
            ),
            {
                'subject': 'test',
                'bar': 'Example - small e',
                'baz': 'WL',
                'qux': 'Nothing',
                'save': 'Save',
                'FooLineItemForm-0-plugh': 'Abc',
                'FooLineItemForm-0-thud': 'GR',
                'FooLineItemForm-1-plugh': 'Abc',
                'FooLineItemForm-1-thud': 'GR',
                'FooLineItemForm-TOTAL_FORMS': 2,
                'FooLineItemForm-INITIAL_FORMS': 0,
                'FooLineItemForm-MIN_NUM_FORMS': 0,
                'FooLineItemForm-MAX_NUM_FORMS': 1000,
                'FooMoreLineItemForm-0-plughmore': 'Abc',
                'FooMoreLineItemForm-0-thudmore': 'GR',
                'FooMoreLineItemForm-TOTAL_FORMS': 1,
                'FooMoreLineItemForm-INITIAL_FORMS': 0,
                'FooMoreLineItemForm-MIN_NUM_FORMS': 0,
                'FooMoreLineItemForm-MAX_NUM_FORMS': 1000
            }
        )

        # Control redirects to update after save
        self.assertRedirects(
            response,
            reverse(
                'update',
                kwargs=request_args))

        # Post the form with SUBMIT action (to next activity)
        response = self.client.post(
            reverse(
                'update',
                kwargs=request_args
            ),
            {
                'subject': 'test',
                'bar': 'Example',
                'baz': 'WL',
                'qux': 'Nothing',
                'submit': 'corge_activity',
                'FooLineItemForm-0-plugh': 'Abc',
                'FooLineItemForm-0-thud': 'GR',
                'FooLineItemForm-1-plugh': 'Abc',
                'FooLineItemForm-1-thud': 'GR',
                'FooLineItemForm-TOTAL_FORMS': 2,
                'FooLineItemForm-INITIAL_FORMS': 0,
                'FooLineItemForm-MIN_NUM_FORMS': 0,
                'FooLineItemForm-MAX_NUM_FORMS': 1000,
                'FooMoreLineItemForm-0-plughmore': 'Abc',
                'FooMoreLineItemForm-0-thudmore': 'GR',
                'FooMoreLineItemForm-TOTAL_FORMS': 1,
                'FooMoreLineItemForm-INITIAL_FORMS': 0,
                'FooMoreLineItemForm-MIN_NUM_FORMS': 0,
                'FooMoreLineItemForm-MAX_NUM_FORMS': 1000
            }
        )

        # Control redirects to workflow detail
        # self.assertRedirects(
        #     response,
        #     reverse(
        #         'workflow-detail',
        #         kwargs={
        #             'app_name': 'tests'}))

        # Initiate task for next (last) activity
        final_task = instance.task.request.tasks.latest('id')

        # Posts the form for last (final) activity
        response = self.client.post(
            reverse(
                'create',
                kwargs={
                    'app_name': 'tests',
                    'model_name': 'Corge',
                    'pk': final_task.id
                }
            ),
            {
                'grault': 'Example - big E',
                'thud': 23,
                'FooLineItemForm-0-plugh': 'Abc',
                'FooLineItemForm-0-thud': 'GR',
                'FooLineItemForm-1-plugh': 'Abc',
                'FooLineItemForm-1-thud': 'GR',
                'FooLineItemForm-TOTAL_FORMS': 2,
                'FooLineItemForm-INITIAL_FORMS': 0,
                'FooLineItemForm-MIN_NUM_FORMS': 0,
                'FooLineItemForm-MAX_NUM_FORMS': 1000,
                'FooMoreLineItemForm-0-plughmore': 'Abc',
                'FooMoreLineItemForm-0-thudmore': 'GR',
                'FooMoreLineItemForm-TOTAL_FORMS': 1,
                'FooMoreLineItemForm-INITIAL_FORMS': 0,
                'FooMoreLineItemForm-MIN_NUM_FORMS': 0,
                'FooMoreLineItemForm-MAX_NUM_FORMS': 1000
            }
        )

        instances = Corge.objects.all()
        instance = instances.first()

        # New instance for last activity gets created
        self.assertEqual(instances.count(), 1,
                         'Instance of final activity did not get '
                         'created even after a successfull post')

        request_args = {
            'app_name': 'tests',
            'model_name': 'Corge',
            'pk': instance.id
        }

        # Control redirects to update after save
        self.assertRedirects(
            response,
            reverse('update', kwargs=request_args),
            status_code=302,
            target_status_code=200)

        # Finish the workflow cycle
        response = self.client.post(
            reverse(
                'update',
                kwargs=request_args
            ),
            {'grault': 'Example - big E', 'thud': 23, 'finish': 'Finish'})

        response = self.client.get(reverse(
            'view',
            kwargs=request_args))

        self.assertEqual(response.status_code, 200,
                         'Response did not result in success')

        response = self.client.post(reverse(
            'delete',
            kwargs=request_args))

        self.assertEqual(Corge.objects.all().count(), 0,
                         'Delete operation did not end up removing '
                         'the instance')

    def test_rollback_feature(self):
        """Tests rollback feature"""
        request_args = {
            'app_name': 'tests',
            'model_name': 'Foo',
            'pk': 'Initial'
        }

        # Post the form  without any validation failure
        response = self.client.post(
            reverse(
                'create',
                kwargs=request_args
            ),
            {
                'subject': 'test',
                'bar': 'Example',
                'baz': 'WL',
                'qux': 'Nothing',
                'FooLineItemForm-0-plugh': 'Abc',
                'FooLineItemForm-0-thud': 'GR',
                'FooLineItemForm-TOTAL_FORMS': 1,
                'FooLineItemForm-INITIAL_FORMS': 0,
                'FooLineItemForm-MIN_NUM_FORMS': 0,
                'FooLineItemForm-MAX_NUM_FORMS': 1000,
                'FooMoreLineItemForm-0-plughmore': 'Abc',
                'FooMoreLineItemForm-0-thudmore': 'GR',
                'FooMoreLineItemForm-TOTAL_FORMS': 1,
                'FooMoreLineItemForm-INITIAL_FORMS': 0,
                'FooMoreLineItemForm-MIN_NUM_FORMS': 0,
                'FooMoreLineItemForm-MAX_NUM_FORMS': 1000
            }
        )

        instances = Foo.objects.all()
        instance = instances.first()

        # Redirects the control to update form
        request_args = {
            'app_name': 'tests',
            'model_name': 'Foo',
            'pk': instance.id
        }

        self.assertRedirects(
            response,
            reverse('update', kwargs=request_args),
            status_code=302,
            target_status_code=200)

        # Post the form with SAVE action
        response = self.client.post(
            reverse(
                'update',
                kwargs=request_args
            ),
            {
                'subject': 'test',
                'bar': 'Example',
                'baz': 'WL',
                'qux': 'Nothing',
                'save': 'Save',
                'FooLineItemForm-0-plugh': 'Abc',
                'FooLineItemForm-0-thud': 'GR',
                'FooLineItemForm-TOTAL_FORMS': 1,
                'FooLineItemForm-INITIAL_FORMS': 0,
                'FooLineItemForm-MIN_NUM_FORMS': 0,
                'FooLineItemForm-MAX_NUM_FORMS': 1000,
                'FooMoreLineItemForm-0-plughmore': 'Abc',
                'FooMoreLineItemForm-0-thudmore': 'GR',
                'FooMoreLineItemForm-TOTAL_FORMS': 1,
                'FooMoreLineItemForm-INITIAL_FORMS': 0,
                'FooMoreLineItemForm-MIN_NUM_FORMS': 0,
                'FooMoreLineItemForm-MAX_NUM_FORMS': 1000
            }
        )

        # Control redirects to update after save
        self.assertRedirects(
            response,
            reverse(
                'update',
                kwargs=request_args))

        # Post the form with SUBMIT action (to next activity)
        response = self.client.post(
            reverse(
                'update',
                kwargs=request_args
            ),
            {
                'subject': 'test',
                'bar': 'Example',
                'baz': 'WL',
                'qux': 'Nothing',
                'submit': 'corge_activity',
                'FooLineItemForm-0-plugh': 'Abc',
                'FooLineItemForm-0-thud': 'GR',
                'FooLineItemForm-TOTAL_FORMS': 1,
                'FooLineItemForm-INITIAL_FORMS': 0,
                'FooLineItemForm-MIN_NUM_FORMS': 0,
                'FooLineItemForm-MAX_NUM_FORMS': 1000,
                'FooMoreLineItemForm-0-plughmore': 'Abc',
                'FooMoreLineItemForm-0-thudmore': 'GR',
                'FooMoreLineItemForm-TOTAL_FORMS': 1,
                'FooMoreLineItemForm-INITIAL_FORMS': 0,
                'FooMoreLineItemForm-MIN_NUM_FORMS': 0,
                'FooMoreLineItemForm-MAX_NUM_FORMS': 1000
            }
        )

        # Control redirects to workflow detail
        # self.assertRedirects(
        #     response,
        #     reverse(
        #         'workflow-detail',
        #         kwargs={
        #             'app_name': 'tests'}))

        # Initiate task for next (last) activity
        final_task = instance.task.request.tasks.latest('id')

        # Posts the form for last (final) activity
        response = self.client.post(
            reverse(
                'create',
                kwargs={
                    'app_name': 'tests',
                    'model_name': 'Corge',
                    'pk': final_task.id
                }
            ),
            {'grault': 'Example - big E', 'thud': 23})

        instances = Corge.objects.all()
        instance = instances.latest('id')

        request_args = {
            'app_name': 'tests',
            'model_name': 'Corge',
            'pk': instance.id
        }

        # Control redirects to update after save
        self.assertRedirects(
            response,
            reverse('update', kwargs=request_args),
            status_code=302,
            target_status_code=200)

        self.client.post(reverse(
            'rollback',
            kwargs={
                'app_name': 'tests',
                'pk': instance.task.id
            }))

        request = Request.objects.all().latest('id')
        final_task = request.tasks.latest('id')

        # Rollback result in task creation for previous activity
        self.assertEqual(final_task.activity_ref, 'foo_activity',
                         'Rollback did not create the required task '
                         'for previous activity')
