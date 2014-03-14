from datetime import datetime, timedelta

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q

from Comments.models import Comment
from Evaluation.models import Evaluation
from ObjectState.models import ObjectState
from Review.models import Review
from FileUpload.models import UploadFile


class Elaboration(models.Model):
    challenge = models.ForeignKey('Challenge.Challenge')
    user = models.ForeignKey('PortfolioUser.PortfolioUser')
    creation_time = models.DateTimeField(auto_now_add=True)
    elaboration_text = models.TextField(null=True)
    submission_time = models.DateTimeField(null=True)

    def __unicode__(self):
        return str(self.id)

    def is_started(self):
        if self.elaboration_text:
            return True
        if UploadFile.objects.filter(elaboration=self):
            return True
        return False

    def is_submitted(self):
        if self.submission_time:
            return True
        return False

    def is_evaluated(self):
        evaluation = self.get_evaluation()
        if evaluation:
            if evaluation.submission_time:
                return True
        return False

    def get_evaluation(self):
        evaluation = Evaluation.objects.filter(submission=self)
        if evaluation:
            return evaluation[0]
        return None

    def is_reviewed_2times(self):
        if Review.objects.filter(elaboration=self).count() < 2:
            return False
        return True

    def is_older_3days(self):
        if not self.is_submitted():
            return False
        if self.submission_time + timedelta(3) < datetime.now():
            return False
        return True

    def get_challenge_elaborations(self):
        if Elaboration.objects.filter(challenge=self.challenge, submission_time__isnull=False):
            return Elaboration.objects.filter(challenge=self.challenge, submission_time__isnull=False)
        return False

    def get_others(self):
        elaborations = []
        for elaboration in Elaboration.objects.filter(challenge=self.challenge, submission_time__isnull=False).exclude(pk=self.id):
            if not elaboration.user.is_staff:
                elaborations.append(elaboration)
        return elaborations

    @staticmethod
    def get_sel_challenge_elaborations(challenge):
        if Elaboration.objects.filter(challenge=challenge, submission_time__isnull=False):
            return Elaboration.objects.filter(challenge=challenge, submission_time__isnull=False)
        return False

    @staticmethod
    def get_missing_reviews():
        missing_reviews = []
        for elaboration in Elaboration.objects.all():
            if not elaboration.is_reviewed_2times() and elaboration.is_older_3days() \
                and not elaboration.challenge.is_final_challenge() and not elaboration.user.is_staff and elaboration.is_submitted():
                    if not ObjectState.get_expired(elaboration):
                        missing_reviews.append(elaboration)
        return missing_reviews

    @staticmethod
    def get_top_level_challenges():
        top_level_challenges = []
        for elaboration in Elaboration.objects.all():
            if elaboration.challenge.is_final_challenge() and elaboration.is_submitted() \
                and not elaboration.is_evaluated() and not elaboration.user.is_staff:
                    if not ObjectState.get_expired(elaboration):
                        top_level_challenges.append(elaboration)
        return top_level_challenges

    @staticmethod
    def get_non_adequate_work():
        non_adequate_work = []
        for review in Review.objects.filter(appraisal=Review.NOTHING):
            if not review.elaboration.is_evaluated() and review.elaboration.is_submitted():
                    if not review.elaboration in non_adequate_work and not review.elaboration.user.is_staff:
                        if not ObjectState.get_expired(review.elaboration):
                            non_adequate_work.append(review.elaboration)
        return non_adequate_work

    @staticmethod
    def get_evaluated_non_adequate_work():
        non_adequate_work = []
        for review in Review.objects.filter(appraisal=Review.NOTHING):
            final_challenge = review.elaboration.challenge.get_final_challenge()
            final_elaboration = final_challenge.get_elaboration(review.elaboration.user)
            if final_elaboration:
                if final_elaboration.is_evaluated():
                    if not review.elaboration in non_adequate_work and not review.elaboration.user.is_staff:
                        if not ObjectState.get_expired(review.elaboration):
                            non_adequate_work.append(review.elaboration)
        return non_adequate_work

    @staticmethod
    def get_review_candidate(challenge, user):
        # get all elaborations
        candidates = Elaboration.objects.filter(challenge=challenge)
        # exclude all that are not written by the user
        candidates = candidates.exclude(user=user)
        # exclude all not submitted elaborations
        candidates = candidates.exclude(submission_time__isnull=True)
        best_candidate = None
        if not candidates:
            return best_candidate
        for candidate in candidates:
            # if there is not already a review for this elaboration reviewed by this user
            if not Review.objects.filter(elaboration=candidate, reviewer=user):
                # if there is already a valid candidate
                if best_candidate:
                    # try to get a better candidate
                    best_candidate = best_candidate.get_better_candidate(candidate)
                else:
                    # set best candidate for the first time
                    best_candidate = candidate
        return best_candidate

    def get_better_candidate(self, candidate):
        # if one of the candidates is written by staff (dummy user) and the other not
        # return the one that is not written by staff (dummy user)
        if not self.user.is_staff and candidate.user.is_staff:
            return self
        elif self.user.is_staff and not candidate.user.is_staff:
            return candidate
        stack = self.challenge.get_stack()
        blocked = stack.is_blocked(self.user)
        blocked_candidate = stack.is_blocked(candidate.user)
        if not blocked and blocked_candidate:
            return self
        elif blocked and not blocked_candidate:
            return candidate
        one_missing = Review.get_review_amount(self) == 1
        one_missing_candidate = Review.get_review_amount(candidate) == 1
        if one_missing and not one_missing_candidate:
            return self
        elif not one_missing and one_missing_candidate:
            return candidate
        if Review.get_review_amount(self) > Review.get_review_amount(candidate):
            return candidate
        return self

    def get_success_reviews(self):
        return Review.objects.filter(elaboration=self, appraisal=Review.SUCCESS)

    def get_nothing_reviews(self):
        return Review.objects.filter(elaboration=self, appraisal=Review.NOTHING)

    def get_fail_reviews(self):
        return Review.objects.filter(elaboration=self, appraisal=Review.FAIL)

    def get_awesome_reviews(self):
        return Review.objects.filter(elaboration=self, appraisal=Review.AWESOME)

    def is_passing_peer_review(self):
        nothing_reviews = Review.objects.filter(elaboration=self, appraisal=Review.NOTHING)
        return not nothing_reviews

    @staticmethod
    def get_complaints(context):
        elaborations = []
        for review in Review.objects.all():
            if Comment.query_comments_without_responses(review, context['user']):
                if not review.elaboration in elaborations:
                    if not ObjectState.get_expired(review.elaboration):
                        elaborations.append(review.elaboration)
        return elaborations

    @staticmethod
    def get_awesome():
        awesome = []
        for review in Review.objects.filter(appraisal=Review.AWESOME, submission_time__isnull=False):
            if not review.elaboration in awesome and not review.elaboration.user.is_staff:
                if not ObjectState.get_expired(review.elaboration):
                    awesome.append(review.elaboration)
        return awesome

    @staticmethod
    def get_expired():
        expired = []
        for elaboration in Elaboration.objects.filter(submission_time__isnull=False):
            if ObjectState.get_expired(elaboration):
                expired.append(elaboration)
        return expired

    @staticmethod
    def get_stack_elaborations(stack):
        elaborations = []
        for challenge in stack.get_challenges():
            for elaboration in challenge.get_elaborations():
                elaborations.append(elaboration)
        return elaborations

    @staticmethod
    def get_course_elaborations(course):
        elaborations = []
        for challenge in course.get_course_challenges():
            for elaboration in challenge.get_elaborations():
                elaborations.append(elaboration)
        return elaborations

    def get_visible_comments(self):
        comments = []
        for review in Review.objects.filter(elaboration=self.id):
            for comment in Comment.objects.filter(visibility=Comment.PUBLIC,
                                                  content_type=ContentType.objects.get_for_model(Review),
                                                  object_id=review.id):
                comments.append(comment)
        for elaboration in Elaboration.objects.filter(id=self.id):
            for comment in Comment.objects.filter(visibility=Comment.PUBLIC,
                                                  content_type=ContentType.objects.get_for_model(Elaboration),
                                                  object_id=elaboration.id):
                comments.append(comment)
        return comments

    def get_invisible_comments(self):
        comments = []
        for review in Review.objects.filter(elaboration=self.id):
            for comment in Comment.objects.filter(visibility=Comment.STAFF,
                                                  content_type=ContentType.objects.get_for_model(Review),
                                                  object_id=review.id):
                comments.append(comment)
        for elaboration in Elaboration.objects.filter(id=self.id):
            for comment in Comment.objects.filter(visibility=Comment.STAFF,
                                                  content_type=ContentType.objects.get_for_model(Elaboration),
                                                  object_id=elaboration.id):
                comments.append(comment)
        return comments