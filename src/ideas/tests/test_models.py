from datetime import timedelta
from django.db.models.aggregates import Sum
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from challenges.models import Challenge, Criteria
from ideas.models import Comment, CriteriaScore, Idea, Review, Tag

from users.models import User

class IdeaModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='author',
            email='testemail@example.com',
            password='secret'
        )
        cls.testuser = User.objects.create_user(
            username='testuser',
            password='secret'
        )
        cls.tag = Tag.objects.create(
            title = "tag"
        )
        cls.challenge = Challenge.objects.create(
            author=cls.author,
            title = "Challenge One",
            date_created = timezone.now() - timedelta(days=1),
            idea_submission_deadline = (timezone.now()  + timedelta(days=1)).date(),
            state = Challenge.State.ACTIVE,
            published_date = timezone.now() - timedelta(days=1)
        )
        cls.criteria1 = Criteria.objects.create(
            description = "criteria1description"
        )
        cls.criteria2 = Criteria.objects.create(
            description = "criteria2description"
        )
        cls.challenge.criterias.set([cls.criteria1,cls.criteria2])
        cls.idea1 = Idea.objects.create(
            author = cls.testuser.profile,
            title = "Idea One",
            date_posted = timezone.now(),
            approved = True,
            challenge = cls.challenge
        )
        cls.comment = Comment.objects.create(
            user = cls.testuser,
            date_posted = timezone.now(),
            content = 'test comment',
            idea = cls.idea1
        )
        cls.review = Review.objects.create(
            reviewer = cls.author,
            idea = cls.idea1
        )
        cls.cs1 = CriteriaScore.objects.create(
            review = cls.review,
            criteria = cls.criteria1,
            score = 1
        )
        cls.cs2 = CriteriaScore.objects.create(
            review = cls.review,
            criteria = cls.criteria2,
            score = 2
        )

    def test_tag_str(self):
        self.assertEqual(str(self.tag), self.tag.title)

    def test_comment_str(self):
        self.assertEqual(str(self.comment), self.comment.user.username)

    def test_review_str(self):
        self.assertEqual(str(self.review), self.review.idea.title +" review by "+ self.review.reviewer.username)

    def test_review_absolute_url(self):
        self.assertEqual(self.review.get_absolute_url(),reverse('idea-review', kwargs={'slug': self.idea1.slug}))

    def test_review_get_total(self):
        self.assertEqual(self.review.get_total, self.review.scores.aggregate(Sum('score')))

    def test_criteriascore_str(self):
        self.assertEqual(str(self.cs1), self.cs1.criteria.description)

    def test_idea_draft(self):
        draft = Idea.objects.create(
            author = self.testuser.profile,
            title = "Draft",
        )
        self.assertTrue(draft in Idea.objects.draft().all())

    def test_idea_approved(self):
        self.assertTrue(self.idea1 in Idea.objects.approved().all())

    def test_idea_str(self):
        self.assertEqual(str(self.idea1), self.idea1.title)

    def test_idea_absolute_url(self):
        self.assertEqual(self.idea1.get_absolute_url(),  reverse('idea-detail', kwargs={'pk': self.idea1.pk}))

    def test_idea_update_url(self):
        self.assertEqual(self.idea1.get_update_url(),  reverse('idea-update', kwargs={'pk': self.idea1.pk}))

    def test_idea_delete_url(self):
        self.assertEqual(self.idea1.get_delete_url(),  reverse('idea-delete', kwargs={'pk': self.idea1.pk}))

    def test_idea_save(self):
        idea = Idea( author = self.testuser.profile, title = "New Idea")
        idea.save()
        self.assertIsNotNone(idea.slug)
        self.assertEqual(len(idea.slug),len(idea.title)+7)

    def test_idea_get_comments(self):
        self.assertQuerysetEqual(self.idea1.get_comments, self.idea1.comments.all().order_by('-date_posted'),transform=lambda x:x)

    def test_idea_comment_count(self):
        self.assertEqual(self.idea1.comment_count, Comment.objects.filter(idea=self.idea1).count())

    def test_idea_get_criterias(self):
        self.assertQuerysetEqual(self.idea1.get_criterias, self.challenge.criterias.all().order_by('pk'),transform=lambda x:x)
    def test_idea_approve(self):
        idea = Idea.objects.create(
            author = self.testuser.profile,
            title = "Not Approved",
            date_posted = timezone.now(),
        )
        idea.approve()
        self.assertEqual(idea.approved , True )

