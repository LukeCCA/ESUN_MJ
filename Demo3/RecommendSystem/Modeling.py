import pandas as pd
import numpy as np
import inspect
import os
from scipy import sparse 
import Collobrative_Filtering as CF
import pickle


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






# Load Data
file_path = inspect.getfile(inspect.currentframe())
file_direction = os.path.dirname(os.path.abspath(file_path))
offertagging = os.path.join(file_direction, './Data/Train_Data.csv')
usertagging = os.path.join(file_direction, './Data/MJ_TAG.xlsx')
offertagging = pd.read_csv(offertagging)
usertagging = pd.read_excel(usertagging)


# Filter data that too less
offertag_log = offertagging.groupby(['ID','OFFER_ID','LABEL_ID']).size().reset_index(name='COUNT')
offertag_log = threshold_likes(offertag_log, 1, 1)
offertag_log.COUNT = 1 # Optional, reduce the count into 1 or 0

# Build offer mapping table
offertags = offertag_log[['OFFER_ID','LABEL_ID']].drop_duplicates().reset_index(drop=True)
offertags['IND'] = 1
offertags = offertags.pivot_table(index='OFFER_ID',columns='LABEL_ID',values='IND').fillna(0)

# offer tag mapping offer label
offer_maptb, _ =  mapping_table(offertags.index.values)

offer_sparse = sparse.coo_matrix(offertags.values, dtype = np.float64)
offer_sparse = offer_sparse.tocsr()

offertag_log = offertag_log.pivot_table(index=['ID'],columns='LABEL_ID', values ='COUNT' ).fillna(0)


usertag_log = usertagging.groupby(['ID','UTID']).size().reset_index(name='COUNT')
usertag_log = usertag_log.pivot_table(index=['ID'], columns='UTID',values ='COUNT').fillna(0)
# left people with offers
usertag_log = usertag_log.loc[offertag_log.index.tolist()]

# offer mapping tables
offer_mapping, reverse_offertag = mapping_table(offertag_log.columns.values.tolist())

 # Produce user tag mapping table
_, usertag_mapping = mapping_table(usertag_log.columns.values.tolist())

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


# Build Model
model = CF.COLLOBORATIVE_FILTERING()
rating_table = model.fit(usertag_log,offertag_log)
print 'Finsh Model Building!!'