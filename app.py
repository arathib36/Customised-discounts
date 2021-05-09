import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle
import sklearn
import pandas as pd


app = Flask(__name__)
model = pickle.load(open('model.pkl', 'rb'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict',methods=['POST'])
def predict():
    '''
    For rendering results on HTML GUI
#     '''
    default_name = 'NA'
    poc_id = int(request.form.get('poc_id', default_name))
    product_set = str(request.form.get('product_set', default_name))
    volume = float(request.form.get('volume', default_name))
    print(poc_id)
    print(product_set)
    print(volume)
    print(type(poc_id))
    print(type(product_set))
    print(type(volume))
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
        print(temp.head())
        poc_rating = temp['Final_POC_Rating'].iloc[0]
        subsegment_rating = temp['POC_subsegement_rating'].iloc[0]

        temp = df_sku_ratings.loc[df_sku_ratings['Product Set']==product_set]
        temp = temp.reset_index()
        print(temp.head())
        sku_rating = temp['Final_SKU'].iloc[0]

        temp = df_offinvoice_discount.loc[df_offinvoice_discount['Ship-to ID']==poc_id]
        temp = temp.reset_index()
        print(temp.head())
        offinvoice = temp['Final_OffInvoice_discount_perc'].iloc[0]
        
        oninvoice = model.predict(np.asarray([[poc_rating,sku_rating,volume,subsegment_rating]]))

    
    temp = df_offinvoice_discount.loc[df_offinvoice_discount['Ship-to ID']==poc_id]
    temp = temp.reset_index()
    print(temp.head())
    offinvoice = temp['Final_OffInvoice_discount_perc'].iloc[0]
    total_discount = oninvoice*100 + offinvoice*100

    #Tier analysis

    output = total_discount

    return render_template('index.html', prediction_text='Total Discount percentage {}'.format(output))


if __name__ == "__main__":
    app.run(debug=True)