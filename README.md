# Catalog of articles categorized by groups
In this version adds reviews for articles and comments for reviews, subscriptions to authors, cache, images for articles.
Templates refactored.


This is the fourth stage in the Bloggers Social Network project series.


Сloned from: https://github.com/web2cap/hw03_forms
Final repo: https://github.com/web2cap/hw05_final

### Includes applications

 - posts: articles by authors and categories of articles, reviews and comments
 - about: static pages
 - core: context processors 
 - users: reimplemented authorization and registration forms, user subscriptions

## Technology:

Python and Django
Bootstrap
Pytest

## Installation
Clone the repository and change into it on the command line:
```
git clone https://github.com/web2cap/hw02_community.git
```

```
cd hw02_community
```

Create and activate virtual environment:

```
python3 -m venv venv
```

```
source venv/bin/activate
```

```
python3 -m pip install --upgrade pip
```

Install dependencies from requirements.txt file:

```
pip install -r requirements.txt
```

Run migrations:

```
python3 manage.py migrate
```

You can create a super user:

```
python3 manage.py createsuperuser
```

Run project:

```
python3 manage.py runserver
```

## Author

Pavel Koshelev