# Create your views here.

from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect

def main(request):
    c = Context({})
    t = loader.get_template("main/index.html")
    return HttpResponse(t.render(c))
