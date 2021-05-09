import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle
import sklearn
import pandas as pd

model = pickle.load(open('model.pkl', 'rb'))

default_name = 'NA'
poc_id = 29000310
product_set = 'RETURNABLE_BOTTLE_JUPILER_JUPILER PILS'
volume = 0.48
#features = [x for x in request.form.values()]

df_poc_ratings = pd.read_excel('POC_Rating.xlsx',engine='openpyxl')
df_sku_ratings = pd.read_excel('SKU_Rating.xlsx',engine='openpyxl')
df_offinvoice_discount = pd.read_excel('OffInvoice_perc.xlsx',engine='openpyxl')
df_zero_poc_list = pd.read_excel('Zero_POC_list.xlsx',engine='openpyxl')

zero_poc_list = df_zero_poc_list['Zero_POC_list'].to_numpy()

if(poc_id in zero_poc_list):
    oninvoice = 0
else:
    #POC Rating and subsegment rating
    temp = df_poc_ratings.loc[df_poc_ratings['Ship-to ID']==poc_id]
    temp = temp.reset_index()
    poc_rating = temp['Final_POC_Rating'][0]
    subsegment_rating = temp['POC_subsegement_rating'][0]
    print(type(poc_rating))
    print(type(subsegment_rating))

    temp = df_sku_ratings.loc[df_sku_ratings['Product Set']==product_set]
    temp = temp.reset_index()
    sku_rating = temp['Final_SKU'][0]
    print(type(sku_rating))

    temp = df_offinvoice_discount.loc[df_offinvoice_discount['Ship-to ID']==poc_id]
    temp = temp.reset_index()
    offinvoice = temp['Final_OffInvoice_discount_perc'][0]

    oninvoice = model.predict(np.asarray([[poc_rating,sku_rating,volume,subsegment_rating]]))
    print(oninvoice)