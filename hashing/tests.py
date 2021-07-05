import time
from django.http import response
from django.test import TestCase

from selenium import webdriver

from .forms import HashForm
from .models import Hash
import hashlib
from django.core.exceptions import ValidationError

HELLO_HASH = '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'


class FunctionalTestCase(TestCase):

    def setUp(self) -> None:
        self.browser = webdriver.Firefox()

    def tearDown(self) -> None:
        self.browser.quit()

    def test_homepage_present(self):
        self.browser.get('http://localhost:8000/')

        self.assertIn('Enter hash here:', self.browser.page_source)

    def test_hello_hash(self):
        self.browser.get('http://localhost:8000/')

        text = self.browser.find_element_by_id('id_text')
        text.send_keys('hello')

        self.browser.find_element_by_name('submit').click()

        self.assertIn(HELLO_HASH, self.browser.page_source)
        self.assertEqual(self.browser.current_url,
                         f'http://localhost:8000/hash/{HELLO_HASH}')

    def test_hash_ajax(self):
        self.browser.get('http://localhost:8000/')
        text = self.browser.find_element_by_id('id_text')
        text.send_keys('hello')
        time.sleep(5)
        self.assertIn(HELLO_HASH, self.browser.page_source)


class UnitTestCase(TestCase):
    def test_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'hashing/home.html')

    def test_hash_form(self):
        form = HashForm(data={'text': 'hello'})
        self.assertTrue(form.is_valid())

    def test_hashing(self):
        text_hash = hashlib.sha256('hello'.encode('utf-8')).hexdigest()

        self.assertEqual(HELLO_HASH, text_hash)

    def save_hash(self):
        hash = Hash()

        hash.text = 'hello'
        hash.hash = HELLO_HASH
        hash.save()
        return hash

    def test_hash_object(self):
        hash = self.save_hash()

        pulled_hash = Hash.objects.get(hash=HELLO_HASH)
        self.assertEqual(pulled_hash.text, hash.text)

    def test_viewing_hash(self):
        hash = self.save_hash()

        response = self.client.get(f'/hash/{HELLO_HASH}')
        self.assertContains(response, hash.text)

    def test_add_data(self):
        def badHash():
            hash = Hash()
            hash.hash = f'{HELLO_HASH}asentuh'
            hash.full_clean()
        self.assertRaises(ValidationError, badHash)
