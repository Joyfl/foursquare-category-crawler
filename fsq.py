# -*- coding: utf-8 -*-

from foursquare import Foursquare
import json
import requests


FOURSQUARE_CLIENT_ID = ''
FOURSQUARE_CLIENT_SECRET = ''
FOURSQUARE_SEARCH_CATEGORY_IDS = [
    '4d4b7105d754a06374d81259',  # Food
    '4bf58dd8d48988d1e5931735',  # Music Venues
    '4bf58dd8d48988d1a1941735',  # College Cafeteria
    '4d4b7105d754a06376d81259',  # Nightlife Spot
]


def download():
    """Downloads all categories as `.json` file.
    """

    foursquare = Foursquare(
        client_id=FOURSQUARE_CLIENT_ID,
        client_secret=FOURSQUARE_CLIENT_SECRET
    )
    categories = foursquare.venues.categories()
    content = json.dumps(categories, indent=4)

    f = open('categories.json', 'w')
    f.write(content)
    f.close()


def get_categories():
    """Oepn downloaded `categories.json` file as `list`.
    """

    f = open('categories.json', 'r')
    categories = json.loads(f.read())['categories']
    f.close()
    return categories


def trace(categories, depth=0, indent=0, show_id=False, verbose=True,
          foreach=None, parents=[]):
    """Trace categories recursively.

    :param depth: maximum depth (0 for not limit)
    :param indent: current indent for verbose
    :param show_id: show both name and id of category when verbose
    :param verbose: log tracing
    :param foreach: called when each category traced
    :param parents: parent categories
    """

    for category in categories:
        # display log messages
        if verbose:
            line = '  ' * indent + '* ' + category['name']
            if show_id:
                line += ' (' + category['id'] + ')'
            print line.encode('utf-8')

        # call foreach callback with category, parents
        if foreach:
            foreach(category, parents)

        # if category has sub-categories
        if (depth == 0 or indent + 1 < depth) and \
           'categories' in category and len(category['categories']):
            trace(categories=category['categories'],
                  indent=indent + 1,
                  show_id=show_id,
                  verbose=verbose,
                  foreach=foreach,
                  parents=parents + [category])


def download_all_icons(size=88, bg=False):
    """Download all icons for category ids from
       `FOURSQUARE_SEARCH_CATEGORY_IDS`.

       :param size: 32, 44, 64, 88px
       :param bg: if `True`, download icons with gray background
    """

    sizes = [32, 44, 64, 88]
    if size not in sizes:
        size = 88

    # download these categories
    download_queue = []

    def append_download_queue(category):
        """Append to `download_queue` after existing check.
        """

        for download_category in download_queue:
            category_url = category['icon']['prefix']
            download_category_url = download_category['icon']['prefix']

            # if same icon already exists in queue
            if category['id'] == download_category['id'] or\
               category_url == download_category_url:
                return

        download_queue.append(category)

    def foreach(category, parents):
        """Check the icon of `category` should be downloaded.
        """

        if category['id'] in FOURSQUARE_SEARCH_CATEGORY_IDS:
            append_download_queue(category)
        else:
            for parent in parents:
                if parent['id'] in FOURSQUARE_SEARCH_CATEGORY_IDS:
                    append_download_queue(category)

    categories = get_categories()  # from `categories.json`
    trace(categories, 0, verbose=False, foreach=foreach)

    for download_category in download_queue:
        download_icon(download_category, size, bg)


def download_icon(category, size=88, bg=False):
    """Download an icon from foursquare server.
    """

    url_base = 'https://foursquare.com/img/categories_v2/'
    category_path = category['icon']['prefix'].split('categories_v2/')[1]
    url_suffix = category['icon']['suffix']

    url = url_base + category_path
    if bg:
        url += 'bg_'
    url += str(size)
    url += url_suffix

    filename = url.split('/')[-2] + '_' + url.split('/')[-1]
    path_prefix = 'icons'
    if bg:
        path_prefix += '_bg'
    download_path = '%s/%s' % (path_prefix, filename)

    print 'Downloading... %s' % download_path
    r = requests.get(url)
    with open(download_path, 'wb') as f:
        for chunk in r.iter_content():
            f.write(chunk)
    f.close()


if __name__ == '__main__':
    download_all_icons(size=32, bg=True)
