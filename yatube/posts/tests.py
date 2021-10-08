from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group

User = get_user_model()


class PostsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alex', email='123@yandex.ru', password='12345'
        )
        self.auth_user_client = Client()
        self.auth_user_client.login(username='alex', password='12345')
        self.guest_client = Client()
        self.group = Group.objects.create(
            title='название',
            slug='test1',
            description='description text1'
        )
        self.post = Post.objects.create(
            text='post text1', author=self.user
        )
        self.edit_text = 'edit text'

    def test_profile_view(self):
        response = self.auth_user_client.get(
            reverse('profile', kwargs={'username': self.user}))
        self.assertEqual(response.status_code, 200)

    def test_new_post_exist(self):
        new_post = Post.objects.create(
            text='text',
            author=self.user,
            group=self.group
        )
        response = self.auth_user_client.get(
            reverse(
                'post',
                kwargs={'post_id': new_post.pk, 'username': self.user},
            ))
        self.assertEqual(response.status_code, 200)

    def test_new_post_non_auth(self):
        response = self.guest_client.get(reverse('new_post'))
        self.assertEqual(response.status_code, 302)

    def test_new_post_auth_user(self):
        response = self.auth_user_client.get(reverse('new_post'))
        self.assertEqual(response.status_code, 200)

    def test_new_post_appear_index_profile_post(self):
        new_post = Post.objects.create(
            text='text',
            author=self.user,
            group=self.group
        )
        response_post = self.auth_user_client.get(
            reverse(
                'post',
                kwargs={'post_id': new_post.pk, 'username': self.user},
            ))
        self.assertContains(response_post, 'text')
        response_profile = self.auth_user_client.get(
            reverse(
                'profile',
                kwargs={'username': self.user},
            ))
        self.assertContains(response_profile, 'text')
        response_index = self.auth_user_client.get(reverse('index'))
        self.assertContains(response_index, 'text')

    def test_edit_post_all_views(self):
        response = self.auth_user_client.post(reverse('post_edit', kwargs={
            'username': self.user,
            'post_id': self.post.pk
        }), {"text": self.edit_text}, follow=True)
        # print(response.context['post'])
        response_index = self.auth_user_client.get(reverse('index'))
        response_profile = self.auth_user_client.get(
            reverse(
                'profile',
                kwargs={'username': self.user},
            ))
        response_post = self.auth_user_client.get(
            reverse(
                'post',
                kwargs={'post_id': self.post.pk, 'username': self.user},
            ))
        self.assertContains(response_index, 'edit text')
        self.assertContains(response_post, 'edit text')
        self.assertContains(response_profile, 'edit text')

    def test_404(self):
        response = self.auth_user_client.get('/fsdfsdf/')
        self.assertEqual(response.status_code, 404)
