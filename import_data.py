import requests
import datetime
import pandas as pd
from bs4 import BeautifulSoup
import tqdm


def import_data(start_date, end_date=datetime.datetime.now(),
                mta_webpage='http://web.mta.info/developers/turnstile.html'):
    """ Creates a DataFrame of Turnstile Data from MTA Website

        Args:
            start_date (datetime): The start date for retrieved data
            end_date (:obj:`datetime`, optional): The end date for retrieved data
            mta_webpage: (:obj: `str`, optional): The mta webpage from which to load data
        Returns:
            DataFrame: A Pandas DataFrame containing MTA data from the specified period.
    """
    if type(start_date) != datetime.datetime:
        raise TypeError('start_date must be a datetime object')
    if type(end_date) != datetime.datetime:
        raise TypeError('end_date must be a datetime object')
    if type(mta_webpage) != str:
        raise TypeError('mta_webpage must be a str object')
    if start_date > end_date:
        raise ValueError('the start date must occur before the end date')

    response = requests.get(mta_webpage)

    if response.status_code != 200:
        raise ValueError('the mta_webpage url could not be opened')

    soup = BeautifulSoup(response.text, 'html.parser')

    mta_hyperlinks_df = find_links(soup)

    mask = (mta_hyperlinks_df['Date'] > start_date) & (mta_hyperlinks_df['Date'] <= end_date)

    mta_hyperlinks_df = mta_hyperlinks_df.loc[mask]

    turnstile_df = pd.DataFrame()

    for link in tqdm.tqdm(mta_hyperlinks_df.Hyperlink.iteritems(), total=len(mta_hyperlinks_df)):
        try:
            turnstile_df = turnstile_df.append(pd.read_csv(link[1]))
        except HTTPError:
            print('Could not open one of the links on the web page')

    return turnstile_df


def find_links(soup):
    """ Creates a DataFrame of links to MTA csv files.

    Args:
        soup (BeautifulSoup): Parsed text from the MTA webpage.
    Returns:
        DataFrame: Dates and Links for each MTA csv file

    """
    if type(soup) != BeautifulSoup:
        assert TypeError('soup must be a BeautifulSoup Object')

    turnstile_links = []

    for link in soup.find_all('a'):
        if 'href' in link.attrs:
            if 'data/nyct/turnstile/' in link.attrs['href']:
                hyperlink = 'http://web.mta.info/developers/' + link.attrs['href']
                date = link.text

                turnstile_links.append([date, hyperlink])

    if len(turnstile_links) == 0:
        raise RunTimeError('Could not find any matching links on web-page')

    turnstile_df = pd.DataFrame(turnstile_links, columns=['Date', 'Hyperlink'])

    try:
        turnstile_df['Date'] = pd.to_datetime(turnstile_df['Date'])
    except ValueError:
        print('Could not complete DataTime conversion')

    return turnstile_df