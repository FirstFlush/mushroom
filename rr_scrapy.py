from bs4 import BeautifulSoup
import requests
import time
# import lxml


# parsers: 'lxml' 'html.parser'

class ShroomerySoup(BeautifulSoup):


    def __init__(self, markup, parser, cultivator):
        super().__init__(markup, parser)
        self.cultivator = cultivator
        print(self.cultivator)
        return


    def get_post_links(self):
        '''
        grabs links to all comments in user's profile
        '''
        table = self.find_all('table',{'class':'tableborders'})[4]
        posts = table.find_all('td', {'class':'darktable wrap'})
        links = []

        for post in posts:
            a = post.find('a', href=True)

            if a:
                links.append(a['href'])
        
        return links


class ForumPage(BeautifulSoup):

    def __init__(self, markup, parser, cultivator):
        super().__init__(markup, parser)
        self.cultivator = cultivator
        print(self.cultivator)
        return


    def get_post(self):
        
        search_string = f"Member # {self.cultivator}"

        # tr standing for <tr> html element
        a_author = self.find('a', {'title' : search_string})

        post = a_author.find_parent('tr').nextSibling.find('div', {'class':'postholder'}).text
        print(post)
        return post


headers = {
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
'Accept-Language':'en-US,en;q=0.5',
'Accept-Encoding':'gzip, deflate',
'Dnt':'1',
'Connection':'keep-alive',
'Upgrade-Insecure-Requests':'1',
}


def choose_cultivator():
    cultivators = {
        'rr' : '111534',
        'agar' : '135712',
    }

    cultivator = cultivators['agar']

    return cultivator



def get_cultivator_profile(cultivator, headers):

    url = f"https://www.shroomery.org/forums/dosearch.php?uid={cultivator}"
    print(url)
    r = requests.get(url, headers)

    content = r.content
    return content


def get_forum_page(url, headers, cultivator): 
    '''
    gets the individual post to scrape.
    '''
    r = requests.get(url, headers)
    if r.status_code == 404:
        return

    forum_thread = r.content

    soup = ForumPage(forum_thread, 'lxml', cultivator)
    soup.get_post()


cultivator = choose_cultivator()
user_profile = get_cultivator_profile(cultivator, headers)
soup = ShroomerySoup(user_profile, 'lxml', cultivator)

links = soup.get_post_links()
for link in links:
    get_forum_page(link, headers, cultivator)
    time.sleep(5)

