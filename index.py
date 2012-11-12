import web
from django.utils import simplejson
urls = ("/resource","resource")

resources  = {
        "1.00":"resource-full.zip",
        "1.01":"resource-part.zip",
        "2.00":"resource-2.0.zip",
        }

class resource:
    def GET(self):
        max_version = max(resources.keys())
        result = []
        for key in sorted(resources.keys()):
            if self.is_same_main_version(key,max_version):
                result.append({"version":key,"name":resources[key]})
        return simplejson.dumps(result)

    def is_same_main_version(self,version1,version2):
        return version1.split('.')[0] == version2.split('.')[0]

app = web.application(urls,globals())
application = app.wsgifunc()
