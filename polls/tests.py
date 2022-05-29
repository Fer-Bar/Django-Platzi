import datetime


from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

class QuestionModelTests(TestCase):
    
    def setUp(self):
        self.question = Question(
            question_text='¿Quién es el mejor Course Director de Platzi')
    
    def test_was_published_with_future_questions(self):
        """
        was_published_recently returns False for questions whose 
        pub_date is in the future.   
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = self.question
        future_question.pub_date = time 
        self.assertEqual(future_question.was_published_recently(), False)
    
    def test_was_published_with_past_questions(self):
        """
        was_published_recently returns False for questions whose 
        pub_date is in the past(2 days before).   
        """
        time = timezone.now() - datetime.timedelta(days=2)
        past_question = self.question
        past_question.pub_date = time 
        self.assertEqual(past_question.was_published_recently(), False)
    
    def test_was_published_with_today_date(self):
        """
        was_published_recently returns True for questions whose 
        pub_date is in today date.   
        """
        time = timezone.now()
        present_question = self.question
        present_question.pub_date = time
        self.assertEqual(present_question.was_published_recently(), True)

def create_question(question_text: str, days: int):
    """
    Create a question with the given question text and publish the 
    given number of days offset to now (negative for questions published
    in past, positive for questions that have yet to be published.)
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)
class QuestionIndexView(TestCase):
                   
    def test_no_question(self):
        """ 
        If no question exists, an appropiate message is displayed.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["lastest_question_list"], [])
    
    def test_future_questions(self):
        """
        Question with a pub_date in the future aren't displayed on the index page.
        """
        create_question("Future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["lastest_question_list"], [])
    
    def test_past_questions(self):
        """
        Question with a pub_date in the past are displayed on the index page.
        """
        question = create_question("Past question", days=-10)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["lastest_question_list"], [question])
        