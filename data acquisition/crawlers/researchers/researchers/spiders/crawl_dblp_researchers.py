import scrapy
import pickle
import time

    

class CrawlDblpResearchersSpider(scrapy.Spider):
    name = 'crawl_dblp_researchers'
    allowed_domains = ['dblp.org']
    start_urls = ["https://scholar.google.com/schhp?hl=en"]
    
    # path to raw researcher names 
    path = r"C:\Users\tanch\Documents\NTU\NTU Year 4\Semester 1\CZ4125 - Developing Data Products\Assignments\Individual Assignment\Part 1\researchers_names.pkl"
    
    
    def parse(self, response):
        # for each researcher name make a request
        names = self.get_researcher_names(CrawlDblpResearchersSpider.path)
        for name in names:
            link = self.get_dblp_link(name)
            meta = {
                "full_name":name,
                "link":link
            }
            print(meta["link"])
            yield response.follow(link, callback = self.parse_dblp, meta = meta)
            time.sleep(0.5)
            
    def parse_dblp(self, response):
        output = {
            "full_name":response.meta["full_name"],
            "link":response.meta["link"]
        }
        authors = response.css("div[id=completesearch-authors] ul.result-list")
        if len(authors)==1:
            dblp_link = authors.css("a::attr(href)").get()
            output["dblp_link"] = dblp_link
            output["multiple_results"] = False
            yield output
        else:
            for author in authors:
                description = " ".join(author.css("small::text").getall())
                if "Nanyang Technological University" in description:
                    dblp_link = author.css("a::attr(href)").get()
                    output["dblp_link"] = dblp_link
                    output["multiple_results"] = True
                    yield output
       
    def get_researcher_names(self, path):
        with open(path, "rb") as f:
            names = pickle.load(f)   
        return names
    def get_dblp_link(self, name):
        return "https://dblp.org/search?q="+"%20".join(name.strip().split())

