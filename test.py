import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle
import sklearn
import pandas as pd
from flask import Markup

model = pickle.load(open('model.pkl', 'rb'))
default_name = 'NA'
poc_id = 29095226
product_set = "OW_BULK_JUPILER_JUPILER PILS"
volume = 0.48

print(poc_id)
print(product_set)
print(volume)
print(type(poc_id))
print(type(product_set))
print(type(volume))
#features = [x for x in request.form.values()]

df_full_data = pd.read_excel('Data.xlsx',engine='openpyxl')

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
    print(temp.head())

    if(temp.empty):
        poc_rating = 0
        subsegment_rating = 0
        poc_tier = 0
    else:
        poc_rating = temp['Final_POC_Rating'].iloc[0]                      #POC Rating
        subsegment_rating = temp['POC_subsegement_rating'].iloc[0]         #Sub-segment Rating
        poc_tier = temp['sfdc_tier'].iloc[0]                               #Tier of POC

    temp = df_sku_ratings.loc[df_sku_ratings['Product Set']==product_set]
    temp = temp.reset_index()
    print(temp.head())
    sku_rating = temp['Final_SKU'].iloc[0]                             #SKU Rating


    oninvoice = model.predict(np.asarray([[poc_rating,sku_rating,volume,subsegment_rating]]))


temp = df_offinvoice_discount.loc[df_offinvoice_discount['Ship-to ID']==poc_id]  #OffInvoice discount perc
temp = temp.reset_index()
print(temp.head())
if(temp.empty):
    offinvoice = 0
else:
    offinvoice = temp['Final_OffInvoice_discount_perc'].iloc[0]



total_discount = oninvoice*100 + offinvoice*100

#Tier analysis
if(poc_tier == 'Tier 0'):
    total_discount+=3.5
elif(poc_tier == 'Tier 2'):
    total_discount+=2.5

if(total_discount>60):
    total_discount = 60

output = total_discount

#Retrieving POC previous record details
poc_prev_data = df_full_data.loc[df_full_data['Ship-to ID'] == poc_id]

print(poc_id)
print(poc_rating)
print(oninvoice)
print(offinvoice)
print(output)
print(sku_rating)
print(poc_tier)

poc_rating = round(poc_rating, 2)
sku_rating = round(sku_rating, 2)