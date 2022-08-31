from clients import GoogleMapsClient, SerpApiClient
import json
import numpy as np
from turtle import distance
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class KwExtraction(object):
    """
    Keywords extraction class to process the data get from SerpAPI and does keywords extraction
    """

    def __init__(self, res:dict=None, custom_kws:list=None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.reviews = []
        self.ratings = []
        self.custom_kws = custom_kws # cutom kws can be passed from FE in the future
        self.model = SentenceTransformer('distilbert-base-nli-mean-tokens')

        # Read reviews and rating from the response returned by API client (use mock data here)
        with open('./json/butcher-reviews.json') as f:
            for review in json.load(f):
                self.reviews.append(review['snippet'])
                self.ratings.append(review['rating'])
        
    # Max Marginal Relevance Diversification of returned KWs result
    def mmr(self, doc_embeddingss:np.ndarray, word_embeddings:np.ndarray, words:list, top_n:int, diversity:float) -> list:
        '''Higher diversity (0 - 1) = more diverse'''

        # Extract similarity within words, and between words and the reviews
        word_doc_similarity = cosine_similarity(word_embeddings, doc_embeddingss)
        word_doc_similarity_mean = np.mean(word_doc_similarity, axis=1).reshape(-1, 1)
        word_similarity = cosine_similarity(word_embeddings)

        # Initialize candidates and already chosen best keyword/keyphras
        keywords_idx = [np.argmax(word_doc_similarity_mean)]
        candidates_idx = [i for i in range(len(words)) if i != keywords_idx[0]]

        for _ in range(top_n - 1):
            # Extract similarities within candidates and
            # between candidates and selected keywords/phrases
            candidate_similarities = word_doc_similarity_mean[candidates_idx, :]
            target_similarities = np.max(word_similarity[candidates_idx][:, keywords_idx], axis=1)

            # Calculate MMR
            mmr = (1-diversity) * candidate_similarities - diversity * target_similarities.reshape(-1, 1)
            mmr_idx = candidates_idx[np.argmax(mmr)]

            # Update keywords & candidates
            keywords_idx.append(mmr_idx)
            candidates_idx.remove(mmr_idx)

        return [words[idx] for idx in keywords_idx]

    def extract_kw(self, n_gram_range:tuple=(1,1), stop_words:str='english', top_n:int=10, diversity:float=0.5) -> dict:
        # Extract candidate words/phrases
        count = CountVectorizer(ngram_range=n_gram_range, stop_words=stop_words).fit(self.reviews)
        candidates = count.get_feature_names_out()

        # Next, we convert both the reviews as well as the candidate keywords/keyphrases to numerical data using pre-trained BERT
        review_embeddings = self.model.encode(self.reviews)
        candidate_embeddings = self.model.encode(candidates)

        kws= self.mmr(doc_embeddingss=review_embeddings, word_embeddings=candidate_embeddings, words=candidates, top_n=top_n, diversity=diversity)

        # Adding custom keywords from FE user input to the final extracted KWs list
        for kw in self.custom_kws:
            if kw not in kws: kws.append(kw)

        # Check concated reviews to get keywords count and store in a dict
        concat_reviews = ' '.join(self.reviews).lower()
        kws_cnt = {}
        for kw in kws:
            # count() returns the number of occurrences of a substring in a give string
            cnt = concat_reviews.count(kw)
            kws_cnt[kw] = cnt

        return kws_cnt
    
    def find_similar_kw(self, kw:str, doc_embeddings:np.ndarray, word_embeddings:np.ndarray, words:list[str], top_n:int=100) -> list:
        '''
        Take a string keywords as input and find the closest meaning kw in the top top_N keyword candidates
        '''

        # Extract similarity within words, and between words and the reviews
        word_doc_similarity = cosine_similarity(word_embeddings, doc_embeddings)
        word_doc_similarity_mean = np.mean(word_doc_similarity, axis=1)

        # Get top_n keywords representive to doc embeddings
        keywords = [words[index] for index in word_doc_similarity_mean.argsort()[-top_n:]]

        # Compute input kw embedding and compute its similarity with extracted top_n keywords
        kw_emb = self.model.encode([kw])
        kw_similarity = cosine_similarity(self.model.encode(keywords), kw_emb).reshape(-1,)

        # Take the top 10 most similar keywords
        similar_kw = [keywords[index] for index in kw_similarity.argsort()[-10:]]
        
        return similar_kw


if __name__=='__main__':
    custom_kws = ['quite', 'intimate', 'dim', 'waygu'] 
    kw_extraction = KwExtraction(custom_kws=custom_kws)
    print(kw_extraction.extract_kw(n_gram_range=(1,1), top_n=10, diversity=0.5))
    # output: {'tasty': 4, 'steakhouses': 3, 'nyc': 2, 'thanksgiving': 1, 'waitresses': 1, 'cheesecake': 11, 'boyfriend': 2, 'diningroom': 1, '300': 2, 'sauvignon': 1, 'quite': 4, 'intimate': 7, 'dim': 0, 'waygu': 2}