# Django imports
from django.shortcuts import render, render_to_response
from django.utils.translation import ugettext as _
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.template.context import RequestContext

# pluggable apps
from haystack.query import SearchQuerySet
from haystack.inputs import Exact
from haystack.views import basic_search
from entities.models import Entity
# our apps
from qa.models import Answer, Question
from user.models import Profile

def place_search(request):
    """ A view to search in a specific place """
    entity_slug = request.GET.get('entity_slug', None)
    if entity_slug:
        searchqs = SearchQuerySet().filter(place=Exact(entity_slug))
        return basic_search(request, searchqueryset=searchqs)
    return basic_search(request)



@login_required
def entity_stats(request):

    if not request.user.is_superuser:
        return HttpResponseForbidden(_('Only superusers have access to this page.'))

    entities = Entity.objects.filter(division__index=3).\
                annotate(profile_count=Count('profile')).\
                filter(profile_count__gt=0)
    editor_count = Profile.objects.filter(is_editor=True).\
                    values('locality').\
                    annotate(Count('locality'))
    answer_count = Answer.objects.values('question__entity').\
                    annotate(Count('question__entity'))
    return render(request, 'user/entity_stats.html',
                            {'entities': entities, 
                            'editor_count': editor_count,
                            'answer_count': answer_count,
                            })

def home_page(request):
    context = RequestContext(request, {
        'questions': Question.objects.count(),
        'answers': Answer.objects.count(),
        })
    return render_to_response('home_page.html', context)


