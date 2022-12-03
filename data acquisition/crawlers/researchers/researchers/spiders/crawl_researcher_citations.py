import scrapy
import pickle


class CrawlResearcherCitationsSpider(scrapy.Spider):
    name = 'crawl_researcher_citations'
    allowed_domains = ['scholar.google.com']
    start_urls = ['http://scholar.google.com/']

    # path to raw researcher names 
    path = r"C:\Users\tanch\Documents\NTU\NTU Year 4\Semester 1\CZ4125 - Developing Data Products\Assignments\Individual Assignment\Part 1\researchers_names.pkl"
    
    def parse(self, response):
        # for each researcher name make a request
        names = self.get_researcher_names(CrawlResearcherCitationsSpider.path)
        for name in names:
            link = self.get_google_scholar_link(name, additional_keywords = ["ntu"])
            meta = {
                "full_name":name,
                "link":link
            }
            
            yield response.follow(link, callback = self.parse_google_scholar, meta = meta)
    
    # 
    def parse_google_scholar(self, response):
        output = {
            "full_name":response.meta["full_name"],
            "link":response.meta["link"]
        }
        users = response.css("div[class=gsc_1usr]")
       
        for user in users:
            verified_at = user.css("div.gs_ai_eml span::text").get()
            organization = user.css("div.gs_ai_aff *::text").get()
            if verified_at=="ntu" or "Nanyang Technological University" in organization or "Singapore" in organization or "NTU" in organization:
                cited_by = user.css("div.gs_ai_cby::text").get()
                output["organization"] = organization
                output["verified_at"] = verified_at
                output["cited_by"] = cited_by
                yield output
                
                
                
    def get_researcher_names(self, path):
        with open(path, "rb") as f:
            names = pickle.load(f)   
        return names
    # add an addition "ntu" for greater accuracy
    def get_google_scholar_link(self, name, additional_keywords = []):
        keywords = name.strip().split()+additional_keywords 
        return "https://scholar.google.com/citations?hl=en&view_op=search_authors&mauthors="+"+".join(keywords)

