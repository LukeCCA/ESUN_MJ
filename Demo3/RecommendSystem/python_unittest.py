import unittest
import pandas as pd
import function_testing
import os
import inspect
import operator
import numpy as np
from sklearn.metrics import pairwise

class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_threshold(self):
        # Load Data
        file_path = inspect.getfile(inspect.currentframe())
        file_direction = os.path.dirname(os.path.abspath(file_path))
        offertagging = os.path.join(file_direction, 'offer_testdata.csv')
        usertagging = os.path.join(file_direction, 'user_testdata.csv')
        offertagging = pd.read_csv(offertagging, sep='\t')
        usertagging = pd.read_csv(usertagging, sep='\t')

        function_test = function_testing.threshold_likes(offertagging, id_min=10, offer_min=5)
        done = False
        while not done:
            starting_shape = offertagging.shape[0]
            offer_counts = offertagging.groupby('ID').OFFER_ID.count()
            offertagging = offertagging[~offertagging.ID.isin(offer_counts[offer_counts < 5].index.tolist())]
            id_counts = offertagging.groupby('OFFER_ID').ID.count()    
            offertagging = offertagging[~offertagging.OFFER_ID.isin(id_counts[id_counts < 10].index.tolist())]
            ending_shape = offertagging.shape[0]
            if starting_shape == ending_shape:
                done = True

        self.assertEqual(function_test.values.tolist(),offertagging.values.tolist())
    
    def test_mapping(self):
        # Load Data
        file_path = inspect.getfile(inspect.currentframe())
        file_direction = os.path.dirname(os.path.abspath(file_path))
        offertagging = os.path.join(file_direction, 'offer_testdata.csv')
        usertagging = os.path.join(file_direction, 'user_testdata.csv')
        offertagging = pd.read_csv(offertagging, sep='\t')
        usertagging = pd.read_csv(usertagging, sep='\t')

        fuction_test = function_testing.mapping_table(sorted(usertagging.UTID.unique()))[0]
        mapping_table = {}
        for num, utid in enumerate(sorted(usertagging.UTID.unique())):
            mapping_table[num] = utid
        
        self.assertEqual(fuction_test[0], mapping_table[0])

    def test_sort(self):
        testing_data = [5, 3, 4, 9, 21, 10]
        output = [3, 4, 5, 9, 10, 21]
        sort_funtest = function_testing.sort_output(testing_data)
        function_test = []    
        for i in sort_funtest:
            function_test.append(testing_data[i])
        self.assertEqual(function_test, output)
    
    def test_table(self):
        testing_data = [5, 3]
        output = np.zeros(10)
        output[5] = 1
        output[3] = 1
        function_test = function_testing.create_table(range(10), testing_data)[0]
        self.assertEqual(function_test.tolist(), output.tolist())
    
    def test_cosinesimilarity(self):
        new_data = np.zeros(20)
        new_data[5] = 1
        new_data[3] = 1
        new_data[13] = 1
        new_data[17] = 1
        test_data_1 = np.zeros(20)
        test_data_1[5] = 1
        test_data_1[6] = 1
        test_data_1[9] = 1
        test_data_1[13] = 1
        test_data_1[19] = 1
        similarity_sklearn = pairwise.cosine_similarity(test_data_1.reshape(1,-1), new_data.reshape(1,-1))
        similarity_handcraft = np.dot(new_data,test_data_1)/np.dot(sum(new_data**2)**0.5,sum(test_data_1**2)**0.5)
        self.assertEqual(similarity_sklearn, similarity_handcraft)
    
    def test_similarity2(self):
        new_data = np.zeros(20)
        new_data[5] = 1
        new_data[3] = 1
        new_data[13] = 1
        new_data[17] = 1
        test_data_1 = np.zeros(20)
        test_data_1[5] = 1
        test_data_1[6] = 1
        test_data_1[9] = 1
        test_data_1[13] = 1
        test_data_1[19] = 1
        test_data_2 = np.zeros(20)
        test_data_2[0] = 1
        test_data_2[10] = 1
        test_data_2[14] = 1
        test_data_2[13] = 1
        test_data_2[17] = 1
        total_data = [new_data,test_data_1,test_data_2]
        similarity_handcraft = np.array([np.dot(new_data,new_data)/np.dot(sum(new_data**2)**0.5,sum(new_data**2)**0.5),
        np.dot(new_data,test_data_1)/np.dot(sum(new_data**2)**0.5,sum(test_data_1**2)**0.5),
        np.dot(new_data,test_data_2)/np.dot(sum(new_data**2)**0.5,sum(test_data_2**2)**0.5)]).astype('float16')
        similarity_sklearn = 1- pairwise.pairwise_distances(total_data, metric='cosine')[0].astype('float16')         
        self.assertEqual(similarity_sklearn.tolist(), similarity_handcraft.tolist())

if __name__ == "__main__":
    
    unittest.main(verbosity=2)