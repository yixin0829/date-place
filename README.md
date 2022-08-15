# DatePlace

A tool to find good places for dating.

## Goal
Create a product that helps people who are dating find a perfect place for their dating experience with interest-focused approach (criteria) instead of position-focused.

## Overview
A product (currently thinking of an app or a website) that does not have cuisine as filter. Instead, it will focuses on leverage [Google Place API](https://developers.google.com/maps/documentation/places/web-service/overview) to analyze user reviews using NLP and stats to develop interest-focused filters such as quietness, cleanness, service, intimacy, taste, lighting, price. Could also introducing feature to help couple select restaurant with data collection.

## Produce Vision Board
- Product Vision
	- Immerse every relationships on this planet with experience that sparks love. Makes love grow, like a tree.
- 1st User
	- Couples who are dating and want to find a place to eat
- Themes: what the products need to solve
	- Be able to analyze and quantify interest-focused criteria of a restaurant.
	- Be able to suggest favourable locations based on the input from users
- Features for MVP
	- "criteria-based restaurant search"
        - input: restaurant name + array of keywords (be able to select default kw or add their own to pass to BE API)
	- Insights dashboard analyzing searched restaurant using NLP keywords extraction
	- similar restaurant recommendation by leveraging SerpAPI Google Maps API

## Workflow
- [x] Tested Google Place API using Python Client
- [x] Build out basic client to fetch 10 reviews
- [ ] Implement client to fetch all reviews for butcher chef and store into a json for testing kw model
    - Google Place API only return up to 5 reviews. Decided to leverage 3-rd party API called [Serpapi](https://serpapi.com/)
    - [Use SerpApi pagination token to get all the reviews](https://www.youtube.com/watch?v=HQAWQPNjw_k)
- [ ] Implement kw extraction class method using mock data
- [ ] Implement REST API endpoint and testing on Mock data
	- [ ] quite count, loud count, review to rating ratio
- [ ] Start FE dev with mock json data
- [ ] Implement GCP cloud storage act as cache

## General Resources
- [Youtube - Geocoding API and Place API + code](https://www.youtube.com/watch?v=ckPEY2KppHc)
- [Keywords extraction using BERT](https://towardsdatascience.com/keyword-extraction-with-bert-724efca412ea)
- [SerpApi Google Maps Reviews API](https://serpapi.com/google-maps-reviews-api)
    - [Use SerpApi pagination token to get all the reviews](https://www.youtube.com/watch?v=HQAWQPNjw_k)

