import pandas as pd

df = pd.read_hdf("file.h5", "store_data")
print(df)
