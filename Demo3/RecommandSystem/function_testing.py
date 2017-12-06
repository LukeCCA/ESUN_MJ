import numpy as np
import pandas as pd
import inspect
import os


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
    return table