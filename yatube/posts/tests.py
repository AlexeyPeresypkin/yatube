import tempfile

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from sorl.thumbnail import get_thumbnail

from posts.models import Post, Group, Follow
from yatube import settings

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
            title='название группы',
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
        cache.clear()
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


class ImageTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alex', email='123@yandex.ru', password='12345'
        )
        self.auth_user_client = Client()
        self.auth_user_client.login(username='alex', password='12345')
        self.group = Group.objects.create(
            title='Группа картинка',
            slug='test1',
            description='description text1'
        )
        self.post = Post.objects.create(
            text='post text1', author=self.user
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        with tempfile.TemporaryDirectory() as temp_directory:
            with override_settings(MEDIA_ROOT=temp_directory):
                with open('posts/test/file.jpg', 'rb') as img:
                    self.post = self.auth_user_client.post('/new/',
                                                           {
                                                               'text': 'imagetest',
                                                               'group': self.group.id,
                                                               'image': img},
                                                           follow=True)

    def test_img_exist(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            with override_settings(MEDIA_ROOT=temp_directory):
                post = Post.objects.create(
                    text='This is a test',
                    author=self.user,
                    group=self.group,
                    image=self.uploaded
                )
                cache.clear()
                response_index = self.auth_user_client.get(reverse('index'))
                response_profile = self.auth_user_client.get(
                    reverse(
                        'profile', kwargs={'username': self.user},
                    ))
                response_post = self.auth_user_client.get(
                    reverse(
                        'post', kwargs={'post_id': 3, 'username': self.user},
                    ))
                response_group = self.auth_user_client.get(reverse(
                    'group_posts', kwargs={'slug': 'test1'}
                ))
                im = get_thumbnail(post.image, "960x339", crop="center",
                                   upscale=True)
                # print(response_index.context['page'][0].text)
                self.assertContains(response_index, im.url)
                self.assertContains(response_profile, '<img')
                self.assertContains(response_post, '<img')
                self.assertContains(response_group, '<img')

    def test_no_image(self):
        with open('posts/test/noimage.pdf', 'rb') as img:
            post = self.auth_user_client.post('/new/',
                                              {'text': 'imagetest',
                                               'group': self.group.id,
                                               'image': img},
                                              follow=True)
        cache.clear()
        response_index = self.auth_user_client.get(reverse('index'))
        self.assertNotContains(response_index, '<img')


class ChacheTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alex', email='123@yandex.ru', password='12345'
        )
        self.auth_user_client = Client()
        self.auth_user_client.login(username='alex', password='12345')
        self.guest_client = Client()
        self.group = Group.objects.create(
            title='название группы',
            slug='test1',
            description='description text1'
        )
        self.post = Post.objects.create(
            text='post text1', author=self.user
        )

    def test_cache_index(self):
        response = self.auth_user_client.get(reverse('index'))
        self.assertContains(response, 'post text1')
        new_post = Post.objects.create(
            text='cache',
            author=self.user,
            group=self.group
        )
        response = self.auth_user_client.get(reverse('index'))
        self.assertNotContains(response, 'cache')


class FollowTest(TestCase):
    def setUp(self) -> None:
        self.user1 = User.objects.create_user(
            username='user1', email='123@yandex.ru', password='12345')
        self.user2 = User.objects.create_user(
            username='user2', email='123@yandex.ru', password='12345')
        self.user3 = User.objects.create_user(
            username='user3', email='123@yandex.ru', password='12345')
        self.c0 = Client()
        self.c1 = Client()
        self.c1.force_login(self.user1)
        self.c2 = Client()
        self.c2.force_login(self.user2)
        self.c3 = Client()
        self.c3.force_login(self.user3)
        self.post1 = Post.objects.create(
            text='post text1', author=self.user1
        )
        self.post2 = Post.objects.create(
            text='post text1', author=self.user2
        )
        self.post3 = Post.objects.create(
            text='post text1', author=self.user3
        )

    def test_follow(self):
        response = self.c1.get(reverse('profile_follow', kwargs={
            'username': self.user2.username}))
        author_user2 = Follow.objects.filter(author=self.user2).count()
        follower_user1 = Follow.objects.filter(user=self.user1).count()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(author_user2, 1)
        self.assertEqual(follower_user1, 1)

    def test_unfollow(self):
        Follow.objects.create(author=self.user2, user=self.user1)
        author_user2 = Follow.objects.filter(author=self.user2).count()
        follower_user1 = Follow.objects.filter(user=self.user1).count()
        self.assertEqual(author_user2, 1)
        self.assertEqual(follower_user1, 1)
        response = self.c1.get(reverse('profile_unfollow', kwargs={
            'username': self.user2.username}))
        author_user2 = Follow.objects.filter(author=self.user2).count()
        follower_user1 = Follow.objects.filter(user=self.user1).count()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(author_user2, 0)
        self.assertEqual(follower_user1, 0)

    def test_follow_post(self):
        Post.objects.create(text='text1', author=self.user2)
        Follow.objects.create(author=self.user2, user=self.user1)
        response = self.c1.get(reverse('follow_index'))
        response_no_auth = self.c0.get(reverse('follow_index'))
        self.assertContains(response, 'text1')
        self.assertEqual(response_no_auth.status_code, 302)

    def test_comments(self):
        post = Post.objects.create(
            text='post text1', author=self.user1
        )
        response_auth_add_comment = self.c1.post(
            reverse('add_comment', kwargs={
                'username': self.user1.username,
                'post_id': post.id
            }), data={
                'text': 'text comment',
                'post': post,
                'author': self.user1
            }, follow=True)
        response_not_auth_add_comment = self.c0.get(
            reverse('add_comment', kwargs={
                'username': self.user1.username,
                'post_id': post.id
            }), follow=True)
        self.assertEqual(
            response_not_auth_add_comment.resolver_match.url_name, 'login'
        )
        self.assertContains(response_auth_add_comment, 'text comment')
