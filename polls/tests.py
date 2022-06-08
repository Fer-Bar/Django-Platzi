import datetime


from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question, Choice

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

def create_question(question_text: str, days: int = 0):
    """
    Create a question with the given question text and publish the 
    given number of days offset to now (negative for questions published
    in past, positive for questions that have yet to be published.)
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
                   
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
    
    def test_future_question_and_past_questions(self):
        """
        Even if both past and future question exist, only past question are displayed.
        """
        past_question = create_question("Past question", days=-30)
        future_question = create_question("Future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["lastest_question_list"], [past_question])
        
        
    def test_two_past_questions(self):
        """
        The questions in index page may display multiple questions.
        """
        past_question_1 = create_question("Past question 1", days=-10)
        past_question_2 = create_question("Past question 2", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["lastest_question_list"], 
                                 [past_question_1, past_question_2])
    
    def test_two_future_questions(self):
        """
        The future questions in index page won't be displayed on the index page.
        """
        future_question_1 = create_question("Future question", days=40)
        future_question_2 = create_question("Future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["lastest_question_list"], [])
        
class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 Error Not Found.
        """
        future_question = create_question("Future question", days=30)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question text.
        """
        past_question = create_question("Past question", days=-30)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    
class QuestionResultViewTests(TestCase):
    # def test_question_without_choices(self):
    #     """
    #     The result view with questions without choices,
    #     returns a 404 Error Not Found.
    #     """
    #     question = create_question("Question with no one choice")
    #     question.choice_set.all().delete()
    #     response = self.client.get(reverse("polls:results", args=(question.id,)))
    #     self.assertEqual(response.status_code, 404)
        
    def test_question_with_one_choice(self):
        """
        The result view return the question with its one choice.
        """
        question = create_question("Question with one choice")
        choice = Choice(choice_text=f"Choice One", question=question)
        choice.save()
        response = self.client.get(reverse("polls:results", args=(question.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'{choice.choice_text} -- {choice.votes} votes')
        self.assertNotContains(response, None)
        
    def test_question_with_multiple_choices(self):
        """
        The result view return the question with their multiples choices.
        """
        question = create_question("Question with multiple choices")
        for i in range(1,4):
            choice = Choice(choice_text=f"Choice number: {i}", question=question)
            choice.save()
        response = self.client.get(reverse("polls:results", args=(question.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'{choice.choice_text} -- {choice.votes} votes')
        self.assertNotContains(response, None)
    