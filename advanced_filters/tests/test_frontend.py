from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings

class AdvancedFiltersFrontEndTestCase(StaticLiveServerTestCase):

    def setUp(self):
        super(AdvancedFiltersFrontEndTestCase, self).setUp()
        self.selenium = webdriver.Firefox()
        self.wait = WebDriverWait(self.selenium, 10)
        self.Rep = get_user_model()
        self.admin = self.Rep(is_superuser=True, is_staff=True, username='admin')
        self.admin.set_password('admin')
        self.admin.save()
        # now, login
        self.selenium.get('/'.join((self.live_server_url, 'admin')))
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys('admin')
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys('admin')
        self.selenium.find_element_by_id('login-form').submit()
        self.wait.until(EC.title_is(u'Site administration | Django site admin'))

    def tearDown(self):
        self.selenium.quit()
        self.admin.delete()
        super(AdvancedFiltersFrontEndTestCase, self).tearDown()

    def test_fail_to_create_filter(self):
        self.selenium.get('/'.join((
            self.live_server_url, 'admin', 'customers', 'client')))
        self.wait.until(EC.presence_of_element_located(
            (By.ID, 'advanced-filter-button')))
        button = self.selenium.find_element_by_id('advanced-filter-button')
        button.click()
        self.wait.until(EC.element_to_be_clickable((By.NAME, '_save_goto')))
        self.selenium.find_element_by_name('_save_goto').click()
        self.wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, 'errorlist')))

    def test_create_simple_filter(self):
        self.selenium.get('/'.join((
            self.live_server_url, 'admin', 'customers', 'client')))
        self.wait.until(EC.presence_of_element_located(
            (By.ID, 'advanced-filter-button')))
        button = self.selenium.find_element_by_id('advanced-filter-button')
        button.click()
        self.wait.until(EC.element_to_be_clickable((By.NAME, '_save_goto')))
        # create the fiter
        self.selenium.find_element_by_id('id_title').send_keys('test')
        field = Select(self.selenium.find_element_by_id('id_form-0-field'))
        field.select_by_value("language")
        operator = Select(self.selenium.find_element_by_id('id_form-0-operator'))
        operator.select_by_value("iexact")
        self.selenium.find_element_by_id('id_form-0-value').send_keys('English')
        self.selenium.find_element_by_name('_save_goto').click()
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="container"]/ul[@class="messagelist"]/li')))
        self.selenium.get_screenshot_as_file('out1.png')
        msg = self.selenium.find_element_by_xpath('//*[@id="container"]/ul[@class="messagelist"]/li')
        self.assertEqual(msg.text, "Advanced filter added successfully.")
