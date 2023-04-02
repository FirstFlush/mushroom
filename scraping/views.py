from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.utils.datastructures import MultiValueDictKeyError
from .soups import ShroomerySoup, ForumPage, WoodlandCubesSoup, WoodlandInventorySoup
from .models import Website, Cultivator, Post
from .forms import CultivatorForm
# from .private_funcs import _get_post_nums_set, _get_inventory, _check_post_num, _get_cultivator_profile, _get_forum_page, _add_post_to_db, _random_time

from bs4 import BeautifulSoup
import requests
import time
import random


def _random_time(lower_num, upper_num):
    '''Returns random integer'''
    return random.randrange(lower_num, upper_num)


def _get_cultivator_profile(cultivator_number, page_number, headers):
    '''
    Gets the url for the cultivator's profile page, 
    displaying all their previous posts. Returns the 
    request content so it can be parsed by BeautifulSoup.
    '''
    url = f"https://www.shroomery.org/forums/dosearch.php?uid={cultivator_number}&limit=10&page={page_number}"
    print(url)
    print(headers)
    print('------------')
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
    print(data)
    spore_dict = {}
    spore_dict['strain'] = strain
    spore_dict['price'] = data['display_price']
    
    avail_html = data['availability_html']
    soup = BeautifulSoup(avail_html, 'lxml')

    spore_dict['status'] = soup.find('p').text

    return spore_dict


def woodland_formations(request):

    website = Website.objects.get(domain='woodlandformations.ca')

    url = f"https://{website.domain}/product/cubensis-spore-solutions/"
    spore_type = 'cubes'
    # spore_type = 'gourmet'

    try:
        if request.GET['type'] == 'gourmet':
            url = f"https://{website.domain}/product/gourmet-liquid-culture/"
            spore_type = 'gourmet'
    except MultiValueDictKeyError:
        pass

    headers = settings.HEADERS
    r = requests.get(url, headers)
    if r.status_code == 404:
        return
    
    soup = WoodlandCubesSoup(r.content, 'lxml', spore_type)
    spore_list = soup.get_active_spores()

    spore_data = []

    for spore_strain in spore_list[:5]:
    # for spore_strain in spore_list:
        spore_dict = _get_inventory(spore_strain)
        spore_data.append(spore_dict)
        print(spore_dict)
        time.sleep(_random_time(2, 5))

    context = {
        'spore_list' : spore_list,
        'spore_data' : spore_data,
    }

    return render(request, 'scraping/woodland.html', context)



def scraping_home(request):

    form = CultivatorForm()

    context = {
        'form' : form,
        # 'shroomery_cultivators' : shroomery_cultivators,
    }

    return render(request, 'scraping/scraping_home.html', context)


def scrape(request):

    if request.method != 'POST':
        return redirect('scraping_home')

    form = CultivatorForm(request.POST)

    if form.is_valid():

        id = form.cleaned_data['cultivator_id']
        cultivator = get_object_or_404(Cultivator, id=id)

        headers = settings.HEADERS
        page_number = 0
        post_nums = _get_post_nums_set(cultivator)

        while True:
            # print('page number: ', page_number)

            profile_page = _get_cultivator_profile(cultivator.number, page_number, headers)
            soup = ShroomerySoup(profile_page, 'lxml', cultivator.number)

            links = soup.get_post_links()

            if len(links) == 0:
                break

            for link in links:
                if _check_post_num(post_nums, link['post_num']) == True:
                    print('ITS IN THE SET')
                    continue

                forum_thread = _get_forum_page(link['url'], headers, cultivator)
                forum_page_soup = ForumPage(forum_thread, 'lxml', link['post_num'])
                post = forum_page_soup.get_post() # returns dict
                post_nums.add(link['post_num'])

                _add_post_to_db(cultivator, post)

                time.sleep(3)

            page_number += 1


        print()
        print('[SCRAPING COMPLETE]')
        print()

    return redirect('scraping_home')