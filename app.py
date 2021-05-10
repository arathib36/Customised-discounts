import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle
import sklearn
import pandas as pd
from flask import Markup


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
    # return render_template('my_other_template.html', 
    #                    firstname=firstname,
    #                    lastname=lastname,
    #                    cellphone=cellphone)

    return render_template('index.html',prediction_text=' OnInvoice Discount percentage : {} <br> OffInvoice perc : {} <br> Total Discount percentage : {}'.format(oninvoice*100,offinvoice*100,output))


if __name__ == "__main__":
    app.run(debug=True)