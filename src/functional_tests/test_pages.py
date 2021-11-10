from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.test import TestCase, LiveServerTestCase
from allauth.account.models import EmailAddress
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from challenges.models import Challenge
from users.models import User
from ideas.models import Idea, Tag
import time


class TestHomePage(LiveServerTestCase):
    def setUp(self):
        # super(TestIdeaListPage,self).setUp()
        self.browser = webdriver.Chrome()

    def tearDown(self):
        super(TestHomePage,self).tearDown()
        self.browser.close()

    def test_home_buttons_display(self):
        self.browser.get(self.live_server_url)
        button1 = self.browser.find_element_by_name('submit')
        button2 = self.browser.find_element_by_name('view')
        self.assertEquals(
            button1.text, 'Submit an Idea'
        )
        self.assertEquals(
            button2.text, 'View Challenges'
        )

    def test_home_submit_redirect_loginpage(self):
        self.browser.get(self.live_server_url)
        redirect_url =  "%s?next=%s" % (reverse('account_login'),reverse('idea-create'))
        self.browser.find_element_by_name('submit').click()
        self.assertEquals(
            self.browser.current_url, self.live_server_url + redirect_url
        )

    def test_home_view_challenges_redirect(self):
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_name('view').click()
        self.assertEquals(
            self.browser.current_url, self.live_server_url + reverse("challenge-list")
        )

class TestLoginPage(LiveServerTestCase):
    def setUp(self):
        # super(TestIdeaListPage,self).setUp()
        self.browser = webdriver.Chrome()

    def tearDown(self):
        super(TestLoginPage,self).tearDown()
        self.browser.close()

    def test_login_successful_redirect(self):
        user = User.objects.create_user(username = 'username', email='example@example.com',password = 'password')
        user.save()
        EmailAddress.objects.create(user=user, email="example@example.com", primary=True,verified=True)
        self.assertTrue(User.objects.filter(username='username').exists())
        self.browser.get(self.live_server_url + reverse('account_login'))
        username = self.browser.find_element_by_id('id_login')
        password = self.browser.find_element_by_id('id_password')
        # #populate form
        username.send_keys('username')
        password.send_keys('password')

        self.browser.find_element_by_class_name("btn-success").click()
        self.assertEquals(
            self.browser.current_url, self.live_server_url + reverse('index')
        )
        self.assertTrue('Successfully signed in as username.' in self.browser.page_source )

    def test_sign_up_redirect(self):
        self.browser.get(self.live_server_url+ reverse('account_login'))
        self.browser.find_element_by_name('signup').click()
        self.assertEquals(
            self.browser.current_url, self.live_server_url + reverse('account_signup')
        )

class TestLoggedIn(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        user = User.objects.create_user(username = 'username', email='example@example.com',password = 'password')
        user.save()
        EmailAddress.objects.create(user=user, email="example@example.com", primary=True,verified=True)
        self.client.login(username = 'username',password = 'password')
        session_key = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        self.browser.get(self.live_server_url)  # load any page
        self.browser.add_cookie({'name': settings.SESSION_COOKIE_NAME, 'value': session_key, 'path': '/'})

    def tearDown(self):
        super(TestLoggedIn,self).tearDown()
        self.browser.close()

    def test_loggedin_home_submit_redirect(self):
        self.browser.get(self.live_server_url)
        redirect_url =  reverse('idea-create')
        self.browser.find_element_by_name('submit').click()
        self.assertEquals(
            self.browser.current_url, self.live_server_url + redirect_url
        )

    def test_loggedin_nav_bar(self):
        self.browser.get(self.live_server_url)
        self.assertTrue('Log Out' in self.browser.page_source )
        self.assertFalse('Log In' in self.browser.page_source )
        self.assertFalse('Sign Up' in self.browser.page_source )

    def test_logged_in_ideas_page_submit_button(self):
        self.browser.get(self.live_server_url + reverse('idea-list'))
        self.assertTrue('create-btn' in self.browser.page_source)
        self.browser.find_element_by_class_name('create-btn').click()
        self.assertEquals(
            self.browser.current_url, self.live_server_url + reverse('idea-create')
        )
    def test_submit_idea_form(self):
        self.browser.get(self.live_server_url + reverse('idea-create'))
        title = self.browser.find_element_by_id('id_title').send_keys('Idea Test')
        overview = self.browser.find_element_by_id('id_overview').send_keys('Idea Test')
        self.browser.switch_to.frame(self.browser.find_element_by_xpath("//iframe[@class='tox-edit-area__iframe']"))
        content = self.browser.find_element_by_id('tinymce').send_keys('Idea Test')
        self.browser.switch_to.default_content()
        self.browser.find_element_by_name("final").click()
        self.assertEquals(
            self.browser.current_url, self.live_server_url + reverse('idea-detail',args=[1])
        )



class TestNotLoggedInIdea(LiveServerTestCase):
    def setUp(self):
        user1 = User.objects.create_user(username = 'username', email='example@example.com',password = 'password')
        user1.save()
        EmailAddress.objects.create(user=user1, email="example@example.com", primary=True,verified=True)
        self.browser = webdriver.Chrome()

        self.tag1 = Tag.objects.create(
            title = "tag1"
        )
        self.idea1 = Idea.objects.create(
            author = user1.profile,
            title = "Idea One",
            date_posted = timezone.now()- timedelta(days = 1),
            approved = True,
            vote_count = 1
        )
        self.idea2 = Idea.objects.create(
            author = user1.profile,
            title = "Idea Two",
            date_posted = timezone.now(),
            approved = True
        )
        self.idea_pending = Idea.objects.create(
            author = user1.profile,
            title = "Idea Pending",
            date_posted = timezone.now()- timedelta(days = 1),
            approved = False
        )
        self.idea1.tags.add(self.tag1)

    def tearDown(self):
        super(TestNotLoggedInIdea,self).tearDown()
        self.browser.close()

    def test_show_approved_ideas(self):
        self.browser.get(self.live_server_url + reverse('idea-list'))
        count = len(self.browser.find_elements_by_class_name('idea-img-1'))
        self.assertEqual(count,2)
        print(count)
        time.sleep(10)

    def test_sort_popularity(self):
        self.browser.get(self.live_server_url + reverse('idea-list'))
        self.browser.find_element_by_css_selector('#sort > option:nth-child(1)').click()
        time.sleep(2)
        first = self.browser.find_element_by_class_name('item-title-1').text
        self.assertEqual(first, 'Idea One')
        time.sleep(5)

    def test_sort_latest(self):
        self.browser.get(self.live_server_url + reverse('idea-list'))
        self.browser.find_element_by_css_selector('#sort > option:nth-child(2)').click()
        time.sleep(2)
        first = self.browser.find_element_by_class_name('item-title-1').text
        self.assertEqual(first, 'Idea Two')
        time.sleep(5)

    def test_filter_tag(self):
        self.browser.get(self.live_server_url + reverse('idea-list'))
        self.browser.find_element_by_id('filter').click()
        time.sleep(2)
        element = WebDriverWait(self.browser, 20).until(EC.element_to_be_clickable((By.XPATH, '//input[@value="tag1"]')))
        element.click()
        self.browser.find_element_by_class_name('modal-filter-btn').click()
        first = self.browser.find_element_by_class_name('item-title-1').text
        self.assertEqual(first, 'Idea One')
        time.sleep(5)

    def test_click_idea_redirect(self):
        self.browser.get(self.live_server_url + reverse('idea-list'))
        self.browser.find_element_by_css_selector('#sort > option:nth-child(1)').click()
        self.browser.find_element_by_class_name('item-title-1').click()
        redirect_url = reverse('idea-detail',args=[self.idea1.pk])
        self.assertEquals(
            self.browser.current_url, self.live_server_url + redirect_url
        )
    
    def test_not_logged_in_ideas_page_no_submit_button(self):
        self.browser.get(self.live_server_url + reverse('idea-list'))
        self.assertFalse('create-btn' in self.browser.page_source)







