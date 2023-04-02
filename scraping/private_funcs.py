import requests
import random
from .models import Post
from bs4 import BeautifulSoup


def _random_time(lower_num, upper_num):
    return random.randrange(lower_num, upper_num)


def _get_cultivator_profile(cultivator_number, page_number, headers):
    '''
    Gets the url for the cultivator's profile page, 
    displaying all their previous posts. Returns the 
    request content so it can be parsed by BeautifulSoup.
    '''
    url = f"https://www.shroomery.org/forums/dosearch.php?uid={cultivator_number}&limit=10&page={page_number}"
    print(url)
    r = requests.get(url, headers)

    content = r.content
    return content


def _get_post_nums_set(cultivator):

    # TODO: docstring

    post_nums = set()

    for post in cultivator.post_set.all().values('post_num'):
        post_nums.add(post['post_num'])

    return post_nums


def _check_post_num(post_nums, post_num):
    '''
    Takes in the set post_nums and checks 
    if the current post # is in it. 
    Returns True if you are good to go.
    '''
    if int(post_num) in post_nums:
        return True
    else:
        return False


def _get_forum_page(url, headers, cultivator): 
    '''
    gets the individual post to scrape.
    '''
    r = requests.get(url, headers)
    if r.status_code == 404:
        return

    forum_thread = r.content
    return forum_thread


def _add_post_to_db(cultivator, post):
    '''
    Creates Post object to add to database.
    '''
    Post.objects.create(
        author_id       = cultivator,
        thread_title    = post['thread_title'],
        body            = post['post_body'],
        post_num        = post['post_num'],
        date            = post['date'],
    )
    return



def _get_inventory(strain):
    '''
    Get the in-stock status of each spore strain.
    '''
    url = 'https://woodlandformations.ca/?wc-ajax=get_variation'
    body = {
        'attribute_cubensis-varieties' : strain,
        'product_id' : 81,
    }

    r = requests.post(url, body)
    data = r.json()
    
    spore_dict = {}
    spore_dict['strain'] = strain
    spore_dict['price'] = data['display_price']
    
    avail_html = data['availability_html']
    soup = BeautifulSoup(avail_html, 'lxml')

    spore_dict['status'] = soup.find('p').text

    return spore_dict
