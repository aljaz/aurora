from django.http import JsonResponse
from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

from .models import Thread, Post, PostVote


@login_required
def thread(request, thread_id):
    thread_object = get_object_or_404(Thread, pk=thread_id)
    return render(request, 'diskurs/thread.html', {'thread': thread_object, 'expanded_posts': []})


@login_required
def thread_post(request, thread_id, post_id):
    post = Post.objects.get(id=post_id)
    last_post_id = post.id;
    expanded_posts = list()
    expanded_posts.append(post.id);

    while post.parent_post is not None:
        post = post.parent_post
        expanded_posts.append(post.id)

    thread_object = get_object_or_404(Thread, pk=thread_id)
    return render(request, 'diskurs/thread.html', {'thread': thread_object, 'expanded_posts': expanded_posts, 'last_post_id': last_post_id})


@login_required
def new_post(request, thread_id):
    try:
        parent_post_id = int(request.POST.get('parent_post_id', 0))
        content = request.POST.get('content', '')

        if len(content) > 0:
            if parent_post_id > 0:
                parent_post = Post.objects.get(id=parent_post_id)
                post = Post()
                post.content = request.POST.get('content', '')
                post.parent_post = parent_post
                post.user = request.user

                depth = 1

                while parent_post.parent_post is not None:
                    parent_post = parent_post.parent_post
                    depth += 1

                thread = Thread.objects.get(id=thread_id)

                if thread.first_post_id == parent_post.id:
                    post.save()

                    template = loader.get_template('diskurs/thread/post.html')
                    context = RequestContext(request, {
                        'post': post,
                        'depth': depth,
                        'thread': thread,
                    })

                    return JsonResponse({
                        'success':True,
                        'post': template.render(context),
                    })

                else:
                    return JsonResponse({
                        'error':True,
                        'message':'Invalid post ID provided!'
                    })
            else:
                return JsonResponse({
                    'error':True,
                    'message':'Invalid post ID provided!'
                })
        else:
            return JsonResponse({
                'error':True,
                'message':'No content provided!'
            })
    except ValueError:
        return JsonResponse({
                'error':True,
                'message':'Invalid post ID provided!'
            })


@login_required
def upvote_post(request, thread_id, post_id):
    try:

        if int(post_id) > 0:
            post = Post.objects.get(id=post_id)

            if not post.deleted:
                try:
                    postVote = PostVote.objects.get(post_id=post_id, user_id=request.user)

                    if postVote.value == 1:
                        postVote.value = 0
                        postVote.save()

                        return JsonResponse({
                            'removed':True,
                            'sum':Post.objects.get(id=post_id).sum_votes
                        })

                except PostVote.DoesNotExist:
                    postVote = PostVote()
                    postVote.post_id = post_id
                    postVote.user = request.user

                postVote.value = 1
                postVote.save()

                return JsonResponse({
                    'success':True,
                    'sum':Post.objects.get(id=post_id).sum_votes
                })

            else:
                return JsonResponse({
                    'error':True,
                    'message':'You cannot vote for a deleted post!'
                })

        else:
            return JsonResponse({
                'error':True,
                'message':'Invalid post ID provided!'
            })

    except ValueError:
        return JsonResponse({
                'error':True,
                'message':'Invalid post ID provided!'
            })


@login_required
def downvote_post(request, thread_id, post_id):
    try:
        if int(post_id) > 0:
            post = Post.objects.get(id=post_id)

            if not post.deleted:
                try:
                    postVote = PostVote.objects.get(post_id=post_id, user_id=request.user)

                    if postVote.value == -1:
                        postVote.value = 0
                        postVote.save()

                        return JsonResponse({
                            'removed':True,
                            'sum':Post.objects.get(id=post_id).sum_votes
                        })

                except PostVote.DoesNotExist:
                    postVote = PostVote()
                    postVote.post_id = post_id
                    postVote.user = request.user

                postVote.value = -1
                postVote.save()

                return JsonResponse({
                    'success':True,
                    'sum':Post.objects.get(id=post_id).sum_votes
                })

            else:
                return JsonResponse({
                    'error':True,
                    'message':'You cannot vote for a deleted post!'
                })

        else:
            return JsonResponse({
                'error':True,
                'message':'Invalid post ID provided!'
            })

    except ValueError:
        return JsonResponse({
                'error':True,
                'message':'Invalid post ID provided!'
            })


@login_required
def delete_post(request, thread_id, post_id):
    try:
        if int(post_id) > 0:
            post = Post.objects.get(id=post_id)

            if post.user == request.user or request.user.has_perm('delete_post'):
                if post.parent_post_id:
                    post.deleted = True
                    post.save()

                    template = loader.get_template('diskurs/thread/post/content_deleted.html')
                    context = RequestContext(request, {
                        'post': post,
                    })

                    return JsonResponse({
                        'success':True,
                        'content': template.render(context),
                    })
                else:
                    return JsonResponse({
                        'error':True,
                        'message':'You cannot delete the top post!'
                    })
            else:
                return JsonResponse({
                    'error':True,
                    'message':'You are not allowed to delete the post!'
                })
        else:
            return JsonResponse({
                'error':True,
                'message':'Invalid post ID provided!'
            })

    except ValueError:
        return JsonResponse({
                'error':True,
                'message':'Invalid post ID provided!'
            })