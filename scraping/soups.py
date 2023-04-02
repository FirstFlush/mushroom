from bs4 import BeautifulSoup
from datetime import datetime


class WoodlandInventorySoup(BeautifulSoup):

    def __init__(self, markup, parser, strain,*args, **kwargs):
        super().__init__(markup, parser, *args, **kwargs)
        self.strain = strain
        return


class WoodlandCubesSoup(BeautifulSoup):


    def __init__(self, markup, parser, spore_type, *args, **kwargs):
        super().__init__(markup, parser, *args, **kwargs)
        if spore_type == 'cubes':
            self.spore_type = 'cubensis-varieties' 
        elif spore_type == 'gourmet':
            self.spore_type = 'gourmet-medicinal-varieties'
        return


    def get_active_spores(self):

        spore_list = []

        spores_select = self.find('select', {'id':self.spore_type})

        for option in spores_select.children:
            if option['value'] == '':
                continue
            spore_list.append(option['value'])

        return spore_list     



class ShroomerySoup(BeautifulSoup):


    def __init__(self, markup, parser, cultivator):
        super().__init__(markup, parser)
        self.cultivator = cultivator
        print(self.cultivator)
        return


    def get_post_links(self):
        '''
        grabs links to all comments in user's profile. 
        Adds all post numbers to a set to check for duplicates. 
        Returns a list of dictionaries:
        [
            {
                'url'       : 'http://blahblh.com',
                'post_num   : '12345678',
            },
        ]
        '''
        link_data = []
        post_nums = set()

        table = self.find_all('table',{'class':'tableborders'})[4]
        posts = table.find_all('td', {'class':'darktable wrap'})

        for post in posts:
            a_tag = post.find('a', href=True)
            if a_tag:
                d = {}
                d['url'] = a_tag['href']
                d['post_num'] = a_tag['href'][-8:]

                if d['post_num'] not in post_nums:
                    post_nums.add(d['post_num'])
                else:
                    continue
                link_data.append(d)

        return link_data


class ForumPage(BeautifulSoup):


    def __init__(self, markup, parser, post_num):
        super().__init__(markup, parser)
        # self.cultivator = cultivator
        self.post_num = post_num

        return


    def get_post(self):
        '''
        Returns a dict with cultivator, post, and date.
        ie:
            'cultivator'  : 111534,
            'post_body'   : 'blah blah blah',
            'post_id'     : 12345678
            'date'        : 05/23/21
        '''
        post_id_span    = self.find('span', { 'id' : self.post_num })
        post_num        = post_id_span['id']
        thread_title    = post_id_span.text[:128]
        date_string     = post_id_span.parent.find_next_sibling('font', {'class':'small'}).find('a').nextSibling.text.split(' ', 3)[2]
        date            = datetime.strptime(date_string, '%m/%d/%y').date()
        try:
            post_body   = post_id_span.find_parent('td', { 'class' : 'newsubjecttable' }).parent.nextSibling.find('div', {'class':'postholder'}).text.strip()
        except AttributeError:
            post_body   = post_id_span.find_parent('td', { 'class' : 'subjecttable' }).parent.nextSibling.find('div', {'class':'postholder'}).text.strip()

        post = {
            # 'cultivator'    : self.cultivator,
            'post_body'     : post_body,
            'thread_title'  : thread_title,
            'post_num'      : post_num,
            'date'          : date,
        }

        print('post_num going into DB: ', post_num)

        return post