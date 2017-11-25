import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.metrics import pairwise
import pickle
import inspect
import os

class COLLOBORATIVE_FILTERING():

    # Model Build
    def fit(self, usertag_log, offertag_log, uid_min=1, mid_min=1):
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
        offertag_log = offertag_log.groupby(['ID','LABEL_ID']).size().reset_index(name='COUNT')
        offertag_log = threshold_likes(offertag_log, uid_min, mid_min)
        offertag_log = offertag_log.pivot_table(index=['ID'],columns='LABEL_ID', values ='COUNT' ).fillna(0)

        # Filter user tag data that only has offer tag
        usertag_log = usertag_log.groupby(['ID','']).size().reset_index(name='COUNT')
        usertag_log = usertag_log.loc[offertag_log.index.values]

        # Build offer mapping table
        offer_mapping, _ = mapping_table(offertag_log.columns.values.tolist())

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

        with open('offer_mapping.pickle', 'wb') as f2:
            pickle.dump(offer_mapping, f2, pickle.HIGHEST_PROTOCOL)
        print 'offer_mapping pickle Done!'

        with open('tag_mapping.pickle', 'wb') as f3:
            pickle.dump(usertag_mapping, f3, pickle.HIGHEST_PROTOCOL)
        print 'tag_mapping pickle Done!'

        return rating_table

    # Predict
    def predict(self, data):
        # load Model and Mapping Table
        with open('offerrating_table.pickle', 'rb') as f:
            rating_table = pickle.load(f)
        with open('user_sparse.pickle', 'rb') as f1:
            tag = pickle.load(f1)
        with open('offer_mapping.pickle', 'rb') as f2:
            offer_mapping = pickle.load(f2)
        with open('tag_mapping.pickle', 'rb') as f3:
            tag_mapping = pickle.load(f3)

        model_tags = tag_mapping.keys()
        user_tags = []
        for i in data['batchTag']:
            if i[u'TAG_ID'] in model_tags:
                user_tags.append(tag_mapping[i[u'TAG_ID']])

        tagging_table = np.zeros(len(model_tags))
        for i in user_tags:
                tagging_table[i] = 1

        tagging_table = tagging_table.reshape(1,-1)

        # Recommadation through user similality
        user_similarity = pairwise.cosine_similarity(tagging_table, tag)
        predict = np.sum(user_similarity.reshape(len(user_similarity[0]),1) * rating_table, axis = 0)
        sort_data = sorted(range(len(predict)), key=lambda k: predict[k])

        data = []
        for i in sort_data[-15:]:
            data.append(offer_mapping[i])

        return data


# Function That Define minimum numbers of data that use to build model
def threshold_likes(df, uid_min, mid_min):
    n_users = df.ID.unique().shape[0]
    n_items = df.LABEL_ID.unique().shape[0]
    sparsity = float(df.shape[0]) / float(n_users*n_items) * 100
    print('Starting likes info')
    print('Number of users: {}'.format(n_users))
    print('Number of models: {}'.format(n_items))
    print('Sparsity: {:4.3f}%'.format(sparsity))

    # Filter data that too less
    done = False
    while not done:
        starting_shape = df.shape[0]
        mid_counts = df.groupby('ID').LABEL_ID.count()
        df = df[~df.ID.isin(mid_counts[mid_counts < mid_min].index.tolist())]
        uid_counts = df.groupby('LABEL_ID').ID.count()
        df = df[~df.LABEL_ID.isin(uid_counts[uid_counts < uid_min].index.tolist())]

        ending_shape = df.shape[0]
        if starting_shape == ending_shape:
            done = True

    assert(df.groupby('ID').LABEL_ID.count().min() >= mid_min)
    assert(df.groupby('LABEL_ID').ID.count().min() >= uid_min)
    n_users = df.ID.unique().shape[0]
    n_items = df.LABEL_ID.unique().shape[0]

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
