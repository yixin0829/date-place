# DatePlace

A tool to find good places for dating.

## Goal
Create a product that helps people who are dating find a perfect place for their dating experience with interest-focused approach (criteria) instead of position-focused.

## Overview
A product (currently thinking of an app or a website) that does not have cuisine as filter. Instead, it will focuses on leverage [Google Place API](https://developers.google.com/maps/documentation/places/web-service/overview) to analyze user reviews using NLP and stats to develop interest-focused filters such as quietness, cleanness, service, intimacy, taste, lighting, price. Could also introducing feature to help couple select restaurant with data collection.

## Workflow
- [x] Tested Google Place API using Python Client
- [x] Build out basic client to fetch 10 reviews
- [x] Implement client to fetch all reviews and ratings for butcher chef and another restaurant store into two json for testing kw model and to perform t-test
    - Google Place API only return up to 5 reviews. Decided to leverage 3-rd party API called [SerpApi](https://serpapi.com/)
    - [Use SerpApi pagination token to get all the reviews](https://www.youtube.com/watch?v=HQAWQPNjw_k)
- [x] Implement kw extraction class method using mock data
    - Diversification using [Maximal Marginal Relevance algorithm](https://arxiv.org/pdf/1801.04470.pdf) (maximizing the similarity with review embeddings while ensuring different from existing extracted keywords)
- [ ] Implement REST API endpoint and testing on Mock data
	- [ ] [Deploy using Docker](https://towardsdatascience.com/deploy-apis-with-python-and-docker-4ec5e7986224), [deploy in AWS](https://medium.com/@contact.blessin/deploying-a-gpt-3-flask-application-on-aws-codepipeline-and-elastic-beanstalk-681cd2ece897)
	- [ ] quite count, loud count, review to rating ratio
- [ ] Format and document BE code and classes
- [ ] Start FE dev with mock json data
- [ ] Implement cloud storage act as cache

## General Resources
- [Youtube - Geocoding API and Place API + code](https://www.youtube.com/watch?v=ckPEY2KppHc)
- [Keywords extraction using BERT](https://towardsdatascience.com/keyword-extraction-with-bert-724efca412ea)
- [SerpApi Google Maps Reviews API](https://serpapi.com/google-maps-reviews-api)
    - [Use SerpApi pagination token to get all the reviews](https://www.youtube.com/watch?v=HQAWQPNjw_k)

