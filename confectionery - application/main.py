import streamlit as st
import pandas as pd
import numpy as np
import requests
import datetime
import plotly.express as px


st.title('Pyladies confectionery')

st.markdown('> Shop from us')


fastapi = 'http://127.0.0.1:8000/'
get_endpoint= 'getfood/'
post_endpoint = 'postfood/'
delete_endpoint = 'deletefood/'
update_endpoint = 'updatefood/'
url1 = fastapi + get_endpoint
url2 = fastapi+ post_endpoint
url3 = fastapi + delete_endpoint
url4 = fastapi + update_endpoint


def main():

    add_selectbox = st.sidebar.selectbox(
    'what would you like to do?',
    ('HOME','ORDER', 'INVENTORY',))

    if add_selectbox == 'HOME':
        #st.subheader('HOME')
        with st.spinner('Loading...'):
            home()    

    elif add_selectbox == 'ORDER':
        st.subheader('Order')
        with st.spinner('Loading...'):
            add_order()

    elif add_selectbox == 'INVENTORY':
        with st.spinner('Loading...'):
            add_inventory()



def home():
    st.write('''Hello there, welcome to Pyladies confectionery, \
        this is what we have available in our store,\
            Kindly check what is availabe and order from us...''')
    out = get_all_db()
    #automatic delete
    for i, j in zip(out.quantity_available, out.id):
        if i <= 0:
            row_list={'row1':int(j), 'row2':0, 'row3': 0}
            del_req = requests.post(url3, json = row_list)

    out = out.drop('id', axis =1)
    if st.checkbox('Show all food items'):
        st.dataframe(out)
    if st.checkbox('Show graph'):
        fig = px.scatter(out, x='food_name', y='quantity_available',\
             hover_name= 'description', size='price')
        st.plotly_chart(fig)
    st.text('\n\n\n')

    st.text('Check what we have')
    cols =['food_name', 'description']
    st_ms = st.multiselect('By columns', out.columns.tolist(), default= cols)
    df = out[['food_name', 'description']]
    if st_ms:
        df[st_ms] = out[st_ms]
    st.dataframe(df)

    st.text('\n')
    option = st.selectbox('By food names',\
            out.food_name)
    df = out[out.food_name == option]
    st.dataframe(df)
    st.markdown('\n\n\n\nBy Dorcas')


def add_order():
    out = get_all_db()
    #number = st.number_input('How many food Items would you like to order?', )
    out_dic , name_dic = out_dict()
    order_names =['food items', 'quantity bought', 'price', 'total']
    df_order = pd.DataFrame(columns = order_names)
    receipt =['name', 'receipt_no', 'total before', 'VAT', \
        'discount', 'total', 'date of delivery', 'time of delivery']
    df_receipt = pd.DataFrame(columns = receipt)
    cost = 0
    
    if st.checkbox('Order from us'):
        qty_p = st.empty() #st.write('Total cost is{}'.format(cost))
        for i,j,d  in zip(out.food_name, out.description, out.id):
            if st.checkbox(str(i) + ' --- ' + str(j), key = str(d)):
                p_q = st.number_input('Enter Quantity of {} and press enter'.format(i))
                if p_q:
                    index = name_dic[i]
                    price = out_dic[index]['price']
                    new_price = price * p_q
                    cost += new_price
                    qty_p.text(f'Total cost is N{cost}')
                    order_entry = pd.DataFrame([[i, p_q, new_price, cost]], columns = order_names)
                    df_order = df_order.append(order_entry)
                    #update the db with data-p_q
                    old_qty = out_dic[index]['quantity_available']
                    new_qty = old_qty - p_q
                    order_dict= {'food_name': str(i), \
                        'description': str(j), \
                            'price': int(price), \
                                'quantity_available': int(new_qty)}
                     
    if cost:
        st.text('\n\n\n')
        if st.checkbox('Check to proceed with sales'):
            out_req = requests.post(url4, json = order_dict)
            f'Your total price is N{cost}'
            if 500 < cost < 1000 :
                vat = 0.05 * cost
                discount = 0
            elif cost  > 1000:
                vat = 0.05 * cost
                discount = 0.2 * cost
            else: 
                vat = 0
                discount =0

            total = cost + vat - discount
            n = st.text_input('Enter your name')
            d = st.date_input("Set your date of delivery",datetime.date(2020, 7, 20))
            t = st.time_input('Set your time of delivery', datetime.time(12,00))
            receipt_no = 'py_conf{}'.format(np.random.randint(100000))

            if st.button('Click here to view and print your receipt'):
                receipt_entry = pd.DataFrame([[n, receipt_no, cost, vat, \
                    discount, total, d, t ]], columns = receipt )
                df_receipt = df_receipt.append(receipt_entry)
                df_receipt= df_receipt.transpose()
                st.text('\n\nYour Receipt')
                st.dataframe(df_receipt)
                st.text('\n\nYour order in summary')
                blank_index = [''] * len(df_order) 
                df_order.index = blank_index
                st.dataframe(df_order)
                st.text('Refresh the page to make a new order!')    
                st.text('Refresh the page to make a new order!')


def add_inventory():    
    out = get_all_db()
    data = st.dataframe(out)
    st.text('\n\n')
    st.text('Check in what you would like to do')
    if st.checkbox('Update former food items'):
        with st.spinner('Loading...'):
            update_item()

    st.text('\n\n')
    if st.checkbox('Delete former food item'):
        st.text('Delete rows from your database')
        delete_row()

    st.text('\n\n')
    if st.checkbox('Add an entire new food item'):
        st.subheader('Add to inventory')
        add_new_item()


def update_item():
    out = get_all_db()
    out_dic , name_dic = out_dict()
    st.text('Change details of listed food items by food_names')
    
    option = st.selectbox('Pick food Item here',out.food_name)
    st.text('\n')
    if option:
        index = name_dic[option]
    change_description = st.text_input('Change {} description here'.format\
        (option), out_dic[index]['description'])
    change_price = st.number_input('Change {} price here'.format\
        (option), out_dic[index]['price'])
    change_quantity = st.number_input('Change {} quantity here'.format\
        (option), out_dic[index]['quantity_available'])
    
    change_food= {}
    if option and change_price and change_quantity:
        change_food['food_name'] = option
        change_food['description'] = change_description
        change_food['price'] = change_price
        change_food['quantity_available'] = change_quantity
    if st.button('Update item in database'):
        out_req = requests.post(url4, json= change_food)
        st.write('Sucessful, resfresh page to check updated items')


def delete_row():
    st.text('\n')
    out = get_all_db()
    row_id1 = st.number_input('Enter an id to delete' )
    row_id2 = st.number_input('Enter another' )
    row_id3 = st.number_input('Enter another to delete' )
    row_list = {'row1':'', 'row2':'','row3': ''}
    if row_id1:
        row_list['row1'] = int(row_id1)
    else:
        row_list['row1'] = int(0)
    if row_id2:
        row_list['row2']= int(row_id2)
    else:
        row_list['row2']= int(0)
    if row_id3:
        row_list['row3'] = int(row_id3)
    else:
        row_list['row3'] = int(0)
    
    if st.button('Delete selected rows'):
        if row_id1 or row_id2 or row_id3:
            del_req = requests.post(url3, json = row_list) 
        elif 0 in {row_id1, row_id2, row_id3}:
            st.write('Enter rows to delete!')
        if del_req:
            st.write('The rows has been deleted succesfully! Refresh page to check')


def add_new_item():          
    food = st.text_input('Name of food, enter a unique name:', )
    description = st.text_input('Description of {}: '.format(food),)
    price = st.number_input('Price per one {}: '.format(food),)
    quantity = st.number_input('Total quantity of {} in stock: '.format(food),)
    if st.button('load to database'):
        with st.spinner('Loading...'):
            inventory = {}
            inventory['food_name'] = str(food)
            inventory['description']= str(description)
            inventory['price'] = int(price)
            inventory['quantity_available'] = int(quantity)
            #inventory = json.dumps(inventory, indent=4)
            out_req = requests.post(url2, json = inventory)
            if out_req:
                st.write('{} added to database!'.format(inventory['food_name']))
                st.write('Reload and check your table')


def get_all_db():
    time.sleep(1)
    out = requests.get(url1).json()
    out = pd.DataFrame(out)
    blank_index = [''] * len(out) 
    out.index = blank_index
    #out = out.drop('id', axis=1)
    return out


name_dict = dict()
id_name_dict = dict()
def out_dict():
    out = get_all_db()
    out_dict = out.to_dict('records')
    numb = list(range(out.shape[0]))
    for j, index in zip(out.food_name, numb):
        name_dict[j] = index
    return out_dict , name_dict


main()
