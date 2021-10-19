from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from reporting.models import Representative
from django.contrib.auth.models import User

class RepresentativeSeleniumTest(StaticLiveServerTestCase):
    WEB_DRIVER_PATH = "./chromedriver"

    @classmethod
    def setUpClass(cls):
        super(RepresentativeSeleniumTest, cls).setUpClass()
        cls.selenium = webdriver.Chrome(cls.WEB_DRIVER_PATH)
        cls.selenium.implicitly_wait(10)

        User.objects.create_user(
            username='testUserr', email='sondaniel96@gmail.com', password='Daniel!1'
        )
        Representative.objects.create(user=self.user, title="testing")

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(RepresentativeSeleniumTest, cls).tearDownClass()

    def test_something(self):
        self.selenium.get('%s%s' % (self.live_server_url,'/submit/'))
        meeting = self.selenium.find_element_by_name('committee-id')
        meeting.selectByVisibleText("Board of Control")
