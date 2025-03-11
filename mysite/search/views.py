from django.views import generic
from .models import Chapter
from search import bible_search_engine
from django.db.models import Case, When
from django.core.cache import cache
from django.core.paginator import Paginator

# Create your views here.
class ChapterView(generic.DetailView):
    model = Chapter
    template_name = "search/chapter.html"

class SearchView(generic.ListView):
    model = Chapter
    template_name = 'search/main.html'
    context_object_name = 'results'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('query_text', '').strip()
        cache_key = f"search_results_{query}"
        results = cache.get(cache_key)

        if results is None:
            if query:
                result_ids = [raw_result["chapterid"] for raw_result in bible_search_engine.search(query)]
                queryset = self.model.objects.all().order_by(
                    Case(*[When(id=id, then=pos) for pos, id in enumerate(result_ids)])
                )
                results = list(queryset)
                cache.set(cache_key, results, timeout=600)
            else:
                results = []

        return results

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query_text', '').strip()
        results = self.get_queryset()

        paginator = Paginator(results, self.paginate_by)
        page = self.request.GET.get('page')

        context['results'] = paginator.get_page(page)
        context['query_text'] = query

        return context
