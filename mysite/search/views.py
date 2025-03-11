from django.views import generic
from .models import Chapter
from search import bible_search_engine
from django.db.models import Case, When
from django.core.cache import cache
import re
from django.shortcuts import redirect

# Create your views here.
class ChapterView(generic.DetailView):
    model = Chapter
    template_name = "search/chapter.html"

class SearchView(generic.ListView):
    model = Chapter
    template_name = 'search/main.html'
    context_object_name = 'results'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        if 'page' not in request.GET and 'query_text' in request.GET:
            url = f"{request.path}?query_text={request.GET['query_text']}&page=1"
            return redirect(url)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        query = self.request.GET.get('query_text', '').strip()
        cache_key = re.sub(r'[^a-zA-Z0-9]','', query)
        results = cache.get(cache_key)

        if results is None:
            if query:
                result_ids = [raw_result["chapterid"] for raw_result in bible_search_engine.search(query)[:50]]
                results = self.model.objects.filter(id__in=result_ids).order_by(
                    Case(*[When(id=id, then=pos) for pos, id in enumerate(result_ids)])
                )
                cache.set(cache_key, results, timeout=600)
            else:
                results = self.model.objects.none()

        return results
