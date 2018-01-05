import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.metrics import pairwise
import pickle
import inspect
import os

class COLLOBORATIVE_FILTERING():

    # Model Build
    def fit(self, usertag, offertag, update_model=False):
        '''
        usertag: user's tag info
        offertag: user's offertag info
        update_model: rebuild model or update exist model
        
        '''

        if update_model:
            with open('user_sparse.pickle', 'rb') as f1:
                user_sparse = pickle.load(f1)
            with open('offer_likes.pickle', 'rb') as f2:
                offer_likes = pickle.load(f2)
            with open('tag_mapping.pickle', 'rb') as f3:
                tag_mapping = pickle.load(f3)  

            usertag = create_table(tag_mapping, usertag)
            usertag = np.concatenate((user_sparse.toarray(), usertag.reshape(1,-1)),axis=0)
            offertag = np.concatenate((offer_likes.toarray(), np.array(offertag).reshape(1,-1)),axis=0)

        # Offer Sparse Matrix
        offer_likes = sparse.coo_matrix(offertag, dtype = np.float64)
        offer_likes = offer_likes.tocsr()

        # User Tag Sparse Matrix
        user_sparse = sparse.coo_matrix(usertag, dtype = np.float64)
        user_sparse = user_sparse.tocsr()

        # Similarity Calculation
        user_similarity = 1 - pairwise.pairwise_distances(offer_likes, metric='cosine')
        item_similarity = 1 - pairwise.pairwise_distances(offer_likes.T, metric='cosine')

        # UserBase Rating
        user_mean = offer_likes.mean(axis = 1)
        user_diff = offer_likes - user_mean
        user_rating = np.asarray(user_mean + user_similarity.dot(user_diff) / np.array([np.abs(user_similarity).sum(axis=1)]).T)

        # ItemBase Rating
        item_rating = offer_likes.dot(item_similarity) / np.array([np.abs(item_similarity).sum(axis=1)])

        # Total Rating
        rating_table = user_rating * item_rating

        # Save User and Offer Model, Offer Mapping Table, UserTag Mapping Table
        with open('offerrating_table.pickle', 'wb') as f:
            pickle.dump(rating_table, f, pickle.HIGHEST_PROTOCOL)
        with open('user_sparse.pickle', 'wb') as f1:
            pickle.dump(user_sparse, f1, pickle.HIGHEST_PROTOCOL)
        with open('offer_likes.pickle', 'wb') as f2:
            pickle.dump(offer_likes, f2, pickle.HIGHEST_PROTOCOL)

        return rating_table

    # Predict Offline
    def predict(self, data, online=True, similar_num=10,
    offertag_num=15, offer_number=6, rating_table=None, tag=None, offerlabel_mapping=None, 
    tag_mapping=None, reverse_offertag=None, offer_maptb=None, offer_sparse=None ):

        '''
        data: the customer you want to recommand's tag
        online: count offline or online
        similar_num: how many similar customer preference take into count
        offertag_num: how many recommand offer tag should use to count offer
        offer_number: how many recommand offer you want
        others: model reference data 
        
        '''

        # load Model and Mapping Table
        if not online:
            with open('offerrating_table.pickle', 'rb') as f:
                rating_table = pickle.load(f)
            with open('user_sparse.pickle', 'rb') as f1:
                tag = pickle.load(f1)
            with open('offerlabel_mapping.pickle', 'rb') as f2:
                offerlabel_mapping = pickle.load(f2)
            with open('tag_mapping.pickle', 'rb') as f3:
                tag_mapping = pickle.load(f3)
            with open('reverse_offertag.pickle', 'rb') as f4:
                reverse_offertag = pickle.load(f4)   
            with open('offer_maptb.pickle', 'rb') as f5:
                offer_maptb = pickle.load(f5)
            with open('offer_sparse.pickle', 'rb') as f6:
                offer_sparse = pickle.load(f6)
            user_tags = data
            model_tags = tag_mapping.keys()

        else:
            model_tags = tag_mapping.keys()
            user_tags = []
            for i in data['batchTag']:
                if i[u'TAG_ID'] in model_tags:
                    user_tags.append(tag_mapping[i[u'TAG_ID']])

        # Create offer label table
        tagging_table = create_table(model_tags, user_tags)

        # Recommadation through user similality
        user_similarity = pairwise.cosine_similarity(tagging_table, tag)

        # Pick first n numbers elements
        sort_usersim = sort_output(user_similarity[0])[:similar_num]
        user_similarity = user_similarity[0][sort_usersim]
        rating_table = rating_table[sort_usersim]

        predict = np.sum(user_similarity.reshape(len(user_similarity),1) * rating_table, axis = 0)
        sort_label = sort_output(predict)

        # Get first n number offer tags
        data = []
        for i in sort_label[:offertag_num]:
            data.append(offerlabel_mapping[i])
            
        # Offer tag mapping index
        offer = []
        for i in data:
            offer.append(reverse_offertag[i])

        # Create offer table
        offer_table = create_table(reverse_offertag, offer)
        
        # Calculate Offer similarity
        offer_similarity = pairwise.cosine_similarity(offer_table, offer_sparse)
        sort_offer = sort_output(offer_similarity[0])
        response = []
        for i in sort_offer[:offer_number]:
            response.append(offer_maptb[i])

        return response

# Sort data
def sort_output(data):
    sort_data = sorted(range(len(data)), key=lambda x: data[x],reverse=True)
    return sort_data

# Create Table
def create_table(data, data_ind):
    table = np.zeros(len(data))
    for i in data_ind:
        table[i] = 1
    table = table.reshape(1,-1)
    return table