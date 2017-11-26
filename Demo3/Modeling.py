import Collobrative_Filtering as CF
import pandas as pd
import numpy as np
import inspect
import os

# Load Data
file_path = inspect.getfile(inspect.currentframe())
file_direction = os.path.dirname(os.path.abspath(file_path))
offertagging = os.path.join(file_direction, 'MJ_OFFER.xlsx')
usertagging = os.path.join(file_direction, 'MJ_TAG.xlsx')
offertagging = pd.read_excel(offertagging)
usertagging = pd.read_excel(usertagging)

# Build Model
model = CF.COLLOBORATIVE_FILTERING()
rating_table = model.fit(usertagging,offertagging)
print "Finish Model Building!"