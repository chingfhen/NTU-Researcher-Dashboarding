import scrapy
import re


class CrawlResearchersSpider(scrapy.Spider):
    name = 'crawl_researchers'
    allowed_domains = ['dr.ntu.edu.sg']
    
    # start_urls = ["https://dr.ntu.edu.sg/simple-search?query=&location=researcherprofiles&crisID=&relationName=&sort_by=score&order=desc&rpp=50&etal=0&start=0"]
    start_urls = ["https://dr.ntu.edu.sg/simple-search?location=researcherprofiles"]
    
    def parse(self, response):
    
        # parse the all names and emails, then go to each profile
        domain = "https://dr.ntu.edu.sg"
        researcher_rows = response.css("table.table.table-hover td")
        names = researcher_rows.css("td[headers=t1] a::text").getall()
        emails = researcher_rows.css("td[headers=t3]::text").getall()
        endpoints = researcher_rows.css("td a::attr(href)").getall()
        for i, endpoint in enumerate(endpoints):
            dr_ntu_profile_url = domain+endpoint
            meta = {
                "full_name":names[i],
                "email":emails[i],
                "dr_ntu_url": dr_ntu_profile_url
            }
            yield response.follow(dr_ntu_profile_url, callback = self.parse_profile, meta = meta)
            
        # check if there's next page then go to next page
        pagination = response.css("ul.pagination.pull-right")
        has_next = "next" in pagination.css("li a[href] ::text").getall()
        if has_next:
            next_endpoint = pagination.css("li a::attr(href)").getall()[-1]
            next_link = domain+next_endpoint
            yield response.follow(next_link, callback=self.parse)
        
    # parse the schools and personal sites, then save following data: full_name, email, dr_ntu_url, schools, personal_site
    def parse_profile(self, response):
        output = {
            "full_name": response.meta["full_name"],
            "email":response.meta["email"],
            "dr_ntu_url": response.meta["dr_ntu_url"]
        }
        info = response.css("div[id=researcherInfo]")
        schools = [self.clean_school(string) for string in info.css("div::text").getall() if re.search('[a-zA-Z]', string)]
        output["schools"] = schools
        output["personal_site"] = info.css("div[id=personalsiteDiv] a::attr(href)").get()
        yield output
        
        
    # remove extra spaces, \n and \t
    def clean_school(self, string):
        string = re.sub(r"[\n\t]*", "", string)
        string = re.sub(' +', ' ', string)
        return string.strip()
            
        
    
        
