from django.views import generic
from .models import Chapter
from bible_search_engine.pipeline import create_bible_search_engine
import os
from django.db.models import Case, When
from django.core.cache import cache

bible_search_engine = create_bible_search_engine()

# Create your views here.
class ChapterView(generic.DetailView):
    model = Chapter
    template_name = "search/chapter.html"

class SearchView(generic.ListView):
    model = Chapter
    template_name = 'search/main.html'
    context_object_name = 'results'
    paginate_by = 10  # Number of results per page

    def get_queryset(self):
        query = self.request.GET.get('query_text', '')

        results = cache.get(query)

        if results is None:
            if query:
                result_ids = [raw_result["chapterid"] for raw_result in bible_search_engine.search(query)]
                results = self.model.objects.all().order_by(Case(*[When(id=id, then=pos)
                                                                   for pos, id in enumerate(result_ids)]))
                cache.set(query, results, timeout=600)
            else:
                results = self.model.objects.none()

        return results
