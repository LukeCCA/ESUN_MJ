import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.metrics import pairwise
import pickle
import inspect
import os

class COLLOBORATIVE_FILTERING():

    # Model Build
    def fit(self, usertag_log, offertag_log, id_min=1, offer_min=1, offer_reduce=False):
        '''
        file_path = inspect.getfile(inspect.currentframe())
        file_direction = os.path.dirname(os.path.abspath(file_path))
        offertagging = os.path.join(file_direction, offertag_log)
        usertagging = os.path.join(file_direction, usertag_log)

        # Exception Process
        offertag_log = pd.read_excel(offertagging)
        usertag_log = pd.read_excel(usertagging)
        usertag_log = usertag_log.groupby(['ID','LABEL_ID']).size().reset_index(name='COUNT')
        '''
        # Filter data that too less
        offertag_log = offertag_log.groupby(['ID','OFFER_ID','LABEL_ID']).size().reset_index(name='COUNT')
        offertag_log = threshold_likes(offertag_log, id_min, offer_min)
        if offer_reduce:
            offertag_log.COUNT = 1 

        # Build offer mapping table
        offertags = offertag_log[['OFFER_ID','LABEL_ID']].drop_duplicates().reset_index(drop=True)
        offertags['IND'] = 1
        offertags = offertags.pivot_table(index='OFFER_ID',columns='LABEL_ID',values='IND').fillna(0)
        offer_maptb, _ =  mapping_table(offertags.index.values)
        offer_sparse = sparse.coo_matrix(offertags.values, dtype = np.float64)
        offer_sparse = offer_sparse.tocsr()
        offertag_log = offertag_log.pivot_table(index=['ID'],columns='LABEL_ID', values ='COUNT' ).fillna(0)
        
        # Filter user tag data that only has offer tag
        usertag_log = usertag_log.groupby(['ID','UTID']).size().reset_index(name='COUNT')
        usertag_log = usertag_log.pivot_table(index=['ID'], columns='UTID',values ='COUNT').fillna(0)
        usertag_log = usertag_log.loc[offertag_log.index.values]

        # Build offer mapping table
        offer_mapping, reverse_offertag = mapping_table(offertag_log.columns.values.tolist())

        # Offer Sparse Matrix
        offer_likes = sparse.coo_matrix(offertag_log.values, dtype = np.float64)
        offer_likes = offer_likes.tocsr()

        # Produce user tag mapping table
        _, usertag_mapping = mapping_table(usertag_log.columns.values.tolist())

        # User Tag Sparse Matrix
        user_sparse = sparse.coo_matrix(usertag_log.values, dtype = np.float64)
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
        print 'offer_rating pickle Done!'
        with open('user_sparse.pickle', 'wb') as f1:
            pickle.dump(user_sparse, f1, pickle.HIGHEST_PROTOCOL)
        print 'user_sparse pickle Done!'
        with open('offerlabel_mapping.pickle', 'wb') as f2:
            pickle.dump(offer_mapping, f2, pickle.HIGHEST_PROTOCOL)
        print 'offerlabel_mapping pickle Done!'
        with open('tag_mapping.pickle', 'wb') as f3:
            pickle.dump(usertag_mapping, f3, pickle.HIGHEST_PROTOCOL)
        print 'tag_mapping pickle Done!'
        with open('reverse_offertag.pickle', 'wb') as f4:
            pickle.dump(reverse_offertag, f4, pickle.HIGHEST_PROTOCOL)
        print 'reverse offermapping pickle Done!'
        with open('offer_maptb.pickle', 'wb') as f5:
            pickle.dump(offer_maptb, f5, pickle.HIGHEST_PROTOCOL)
        print 'offer_mapping table pickle done!'
        with open('offer_sparse.pickle', 'wb') as f6:
            pickle.dump(offer_sparse, f6, pickle.HIGHEST_PROTOCOL)
        print 'offer map lable table pickle done!'

        return rating_table

    # Predict Offline
    def predict(self, data, online=False, 
    number=15, offer_number=6, rating_table=None, tag=None, offerlabel_mapping=None, 
    tag_mapping=None, reverse_offertag=None, offer_maptb=None, offer_sparse=None ):
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

        model_tags = tag_mapping.keys()
        user_tags = []
        for i in data['batchTag']:
            if i[u'TAG_ID'] in model_tags:
                user_tags.append(tag_mapping[i[u'TAG_ID']])

        # Create offer label table
        tagging_table = create_table(model_tags, user_tags)

        # Recommadation through user similality
        user_similarity = pairwise.cosine_similarity(tagging_table, tag)
        predict = np.sum(user_similarity.reshape(len(user_similarity[0]),1) * rating_table, axis = 0)
        sort_label = sort_output(predict)

        # Get top number offer tags
        data = []
        for i in sort_label[-number:]:
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
        for i in sort_offer[-offer_number:]:
            response.append(offer_maptb[i])

        return response



# Function That Define minimum numbers of data that use to build model
def threshold_likes(df, id_min, offer_min):

    # Filter data that too less
    done = False
    while not done:
        starting_shape = df.shape[0]
        offer_counts = df.groupby('ID').OFFER_ID.count()
        df = df[~df.ID.isin(offer_counts[offer_counts < offer_min].index.tolist())]
        id_counts = df.groupby('OFFER_ID').ID.count()
        df = df[~df.OFFER_ID.isin(id_counts[id_counts < id_min].index.tolist())]

        ending_shape = df.shape[0]
        if starting_shape == ending_shape:
            done = True

    assert(df.groupby('ID').OFFER_ID.count().min() >= offer_min)
    assert(df.groupby('OFFER_ID').ID.count().min() >= id_min)
    n_users = df.ID.unique().shape[0]
    n_items = df.OFFER_ID.unique().shape[0]

    sparsity = float(df.shape[0]) / float(n_users*n_items) * 100
    print('Ending likes info')
    print('Number of users: {}'.format(n_users))
    print('Number of models: {}'.format(n_items))
    print('Sparsity: {:4.3f}%'.format(sparsity))
    return df

# Build input Mapping table
def mapping_table(data):
    idx_to_tag = {}
    tag_to_idx = {}
    for (idx, tag) in enumerate(data):
        idx_to_tag[idx] = tag
    for (idx, tag) in enumerate(data):
        tag_to_idx[tag] = idx
    return idx_to_tag, tag_to_idx

# Sort data
def sort_output(data):
    sort_data = sorted(range(len(data)), key=lambda x: data[x])
    return sort_data

# Create Table
def create_table(data, data_ind):
    table = np.zeros(len(data))
    for i in data_ind:
        table[i] = 1
    table = table.reshape(1,-1)
