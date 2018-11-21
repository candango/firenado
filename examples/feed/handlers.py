import firenado.tornadoweb
from feedgen.feed import FeedGenerator
from datetime import datetime
import pytz



class IndexHandler(firenado.tornadoweb.TornadoHandler):

    def get(self):
        fg = FeedGenerator()
        fg.id("http://test.ts")
        fg.title("My Test Feed")
        fg.icon("https://avatars1.githubusercontent.com/u/715660?v=3&s=32")
        fg.author({'name': "The Author", 'email': "test@test.ts"})

        fg.link(href="http://example.org/index.atom?page=2", rel="next")

        fg.link(href="http://test.ts", rel="alternate")
        fg.logo("https://avatars1.githubusercontent.com/u/715660?v=3&s=32")
        fg.description("Este é o monstro do lago 1")
        fg.subtitle("This is an example feed!")
        fg.language("en-us")
        # Handle this:
        #< sy:updatePeriod > hourly < / sy:updatePeriod >
        #< sy:updateFrequency > 1 < / sy:updateFrequency >

        fg.lastBuildDate(datetime.now(pytz.timezone("America/Sao_Paulo")))

        fi = fg.add_item()
        fi.id("http://test.ts/id/1", )
        #fi.link(link="http://test.ts/id/1")
        fi.title("Monstro do Lago 1")
        fi.description("Este é o monstro do lago 1")
        fi.comments("http://test.ts/id/1/comments")
        fi.pubdate(datetime.now(pytz.timezone("America/Sao_Paulo")))

        fi = fg.add_item()
        fi.id("http://test.ts/id/2")
        fi.title("Monstro do Lago 2")
        fi.description("Este é o monstro do lago 2")
        fi.pubdate(datetime.now(pytz.timezone("America/Sao_Paulo")))

        #test = fg.atom_str(pretty=True)

        rss_str = fg.rss_str(pretty=True)
        self.set_header("Content-Type", 'application/xml; charset="utf-8"')
        #self.set_header("Content-Disposition",
        # "attachment; filename='test.xml'")
        self.write(rss_str)


        #if regexp.search(word) is not None:
        #    print
        #    'matched'
        if self.is_mobile():
            print("buu")
        else:
            print(self.request.headers["User-Agent"])

        #for zone in pytz.common_timezones:
        #    print(pytz.timezone(zone).localize(
        #        datetime(2002, 10, 27, 6, 0, 0)).strftime("%Z %z"), zone)
