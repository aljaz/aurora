from django.shortcuts import render_to_response
from django.template import RequestContext

import json
from django.contrib.auth.decorators import login_required
from PortfolioUser.models import PortfolioUser
from Review.models import Review
from Elaboration.models import Elaboration
from Challenge.models import Challenge
from ReviewQuestion.models import ReviewQuestion
from ReviewAnswer.models import ReviewAnswer
from django.http import HttpResponse
from datetime import datetime


def create_context_review(request):
    data = {}
    if 'id' in request.GET:
        user = PortfolioUser.objects.filter(user_ptr=request.user)[0]
        challenge = Challenge.objects.get(pk=request.GET.get('id'))
        review = Review.get_open_review(challenge, user)
        if not review:
            review_candidate = Elaboration.get_review_candidate(challenge, user)
            if review_candidate:
                review = Review(elaboration=review_candidate, reviewer=user)
                review.save()
            else:
                return None
        data['review'] = review
        data['stack_id'] = challenge.get_stack().id
        review_questions = ReviewQuestion.objects.filter(challenge=challenge).order_by("order")
        data['questions'] = review_questions
    return data


@login_required()
def review(request):
    data = create_context_review(request)
    return render_to_response('review.html', data, context_instance=RequestContext(request))


@login_required()
def review_page(request):
    data = create_context_review(request)
    return render_to_response('review_page.html', data, context_instance=RequestContext(request))


@login_required()
def review_answer(request):
    if request.POST:
        data = request.body.decode(encoding='UTF-8')
        data = json.loads(data)
        review_id = data['review_id']
        answers = data['answers']
        review = Review.objects.get(pk=review_id)
        review.appraisal = data['appraisal']
        review.awesome = data['awesome']
        review.submission_time = datetime.now()
        review.save()
        for answer in answers:
            question_id = answer['question_id']
            text = answer['answer']
            review_question = ReviewQuestion.objects.get(pk=question_id)
            ReviewAnswer(review=review, review_question=review_question, text=text).save()
    return HttpResponse()


def create_context_view_review(request):
    data = {}
    if 'id' in request.GET:
        user = PortfolioUser.objects.filter(user_ptr=request.user)[0]
        challenge = Challenge.objects.get(pk=request.GET.get('id'))
        elaboration = Elaboration.objects.filter(challenge=challenge, user=user)[0]
        data['success'] = []
        for review in elaboration.get_success_reviews():
            review_data = []
            for review_question in ReviewQuestion.objects.filter(challenge=challenge).order_by("order"):
                review_answer = ReviewAnswer.objects.filter(review=review, review_question=review_question)[0]
                review_data.append(review_question.text)
                review_data.append(review_answer.text)
            data['success'].append(review_data)

        data['nothing'] = []
        for review in elaboration.get_nothing_reviews():
            review_data = []
            for review_question in ReviewQuestion.objects.filter(challenge=challenge).order_by("order"):
                review_answer = ReviewAnswer.objects.filter(review=review, review_question=review_question)[0]
                review_data.append(review_question.text)
                review_data.append(review_answer.text)
            data['nothing'].append(review_data)
        data['fail'] = []
        for review in elaboration.get_fail_reviews():
            review_data = []
            for review_question in ReviewQuestion.objects.filter(challenge=challenge).order_by("order"):
                review_answer = ReviewAnswer.objects.filter(review=review, review_question=review_question)[0]
                review_data.append(review_question.text)
                review_data.append(review_answer.text)
            data['fail'].append(review_data)
        data['awesome'] = []
        for review in elaboration.get_awesome_reviews():
            review_data = []
            for review_question in ReviewQuestion.objects.filter(challenge=challenge).order_by("order"):
                review_answer = ReviewAnswer.objects.filter(review=review, review_question=review_question)[0]
                review_data.append(review_question.text)
                review_data.append(review_answer.text)
            data['awesome'].append(review_data)


    return data


@login_required()
def received_challenge_reviews(request):
    data = create_context_view_review(request)
    return render_to_response('view_review.html', data, context_instance=RequestContext(request))

@login_required()
def received_challenge_reviews_page(request):
    data = create_context_view_review(request)
    return render_to_response('view_review_page.html', data, context_instance=RequestContext(request))

