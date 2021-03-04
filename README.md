[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Web API

A simple RESTful API that allows you to get data about free e-books in the form of JSON object.

## Functionalities:
5 types of request that the API supports are GET, POST, PUT, PATCH, DELETE.
```
GET:    \
GET:    \books
GET:    \books\<bookid>
POST:   \books
PUT:    \books\<bookid>
PATCH:  \books\<bookid>
DELETE: \books\<bookid>
```

Sample response:
```js
GET: \books\<bookid>
{
    "author": "Morse, Katharine Duncan",
    "id": "1006",
    "link": "https://www.gutenberg.org/ebooks/51495",
    "title": "The Uncensored Letters of a Canteen Girl",
    "year": "19-Mar-16"
}
```

## Deployed app: 

The app is available online at: [Web API](https://ebooks-web-api.herokuapp.com/). However, note that the app is a bit flaky on Heroku, but works perfectly locally.

## Future direction

I am planning to assign user IP address to limit usage as well as to prevent DOS/DDOS attack.