import streamlit as st
import pandas as pd
import plotly.express as px

data_url = "test_data.csv"
data = pd.read_csv(data_url)

data.sort_values(by='Order Time')

data['Date'] = pd.to_datetime(data['Date'])
data['Serve Time'] = pd.to_datetime(data['Serve Time'])
data['Order Time'] = pd.to_datetime(data['Order Time'])

data['Day'] = data['Date'].dt.day
data['Week'] = data['Date'].dt.isocalendar().week
data['Month'] = data['Date'].dt.month
data['Year'] = data['Date'].dt.year

menu_order_count = data.groupby('Menu')['Menu'].count().reset_index(name='Quantity')
menu_order_count = menu_order_count.sort_values(by='Quantity', ascending=False)

monthly_sales = data.groupby('Month')['Price'].sum().reset_index(name='Total Sales')

menu_orders_by_month = data.groupby(['Month', 'Menu']).size().reset_index(name='Order Count')

category_orders_by_month = data.groupby(['Month', 'Category']).size().reset_index(name='Order Count')

pivot_data = data.pivot_table(index=['Day Of Week'], columns=['Category'], values='Menu', aggfunc='count')

food_data = data[data['Category'] == 'food']
drink_data = data[data['Category'] == 'drink']

data['Serve Hour'] = data['Serve Time'].dt.hour
data['Serve Minute'] = data['Serve Time'].dt.minute
data['Order Hour'] = data['Order Time'].dt.hour
data['Order Minute'] = data['Order Time'].dt.minute

data['Serve Time'] = data['Serve Hour'] * 60 + data['Serve Minute']
data['Order Time'] = data['Order Hour'] * 60 + data['Order Minute']

data['Serve Duration'] = data['Serve Time'] - data['Order Time']

data['Time of Day'] = pd.cut(data['Hour'], bins=[6, 12, 18, 24], labels=['Morning', 'Afternoon', 'Evening'], right=False)

data['order_id'] = range(1, len(data) + 1)

@st.cache_data 
def create_sales_chart(data, x, y, title):
    fig = px.line(data, x=x, y=y, title=title)
    return fig
def create_menu_chart():
    fig = px.bar(menu_order_count, x='Quantity', y='Menu', title='Top Ordered Menu',
    range_x=[0, 3000], text='Quantity')
    return fig
def create_line_chart(data, x, y, color, title):
    fig = px.line(data, x=x, y=y, color=color, title=title)
    return fig
def create_comparison_chart():
    
    data['Time of Day'] = pd.cut(data['Hour'], bins=[6, 12, 18, 24], labels=['Morning', 'Afternoon', 'Evening'], right=False)

    
    grouped_data = data.groupby(['Day Of Week', 'Time of Day', 'Category']).size().reset_index(name='Count')

    day_of_week_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


    fig = px.bar(grouped_data, x='Time of Day', y='Count',
             color='Category', labels={'Count': 'Number of Orders'},
             title='Average Food and Drink Orders by Time of Day',
             facet_col='Day Of Week',
             category_orders={'Time of Day': ['Morning', 'Afternoon', 'Evening'],
                              'Day Of Week': day_of_week_order},
             width=1000,
             facet_col_spacing=0.1)
    return fig
def serve_time():

    min_date = pd.to_datetime('2023-06-01').date()
    max_date = pd.to_datetime('2023-12-31').date()

    selected_date = st.date_input('Select Date', min_value=min_date, max_value=max_date, value=min_date)
   
    filtered_data = data[data['Date'].dt.date == selected_date]

    food_orders_data = filtered_data[filtered_data['Category'] == 'food']

    drink_orders_data = filtered_data[filtered_data['Category'] == 'drink']

    food_fig = px.scatter(food_orders_data, x='Hour', y='Serve Duration',color='Menu',
                       title='Serve Duration for Food Orders',
                      labels={'Serve Duration': 'Serve Duration (minutes)'})
    drink_fig = px.scatter(drink_orders_data, x='Hour', y='Serve Duration',color='Menu',
                       title='Serve Duration for Drink Orders',
                      labels={'Serve Duration': 'Serve Duration (minutes)'})
    return food_fig, drink_fig
# แสดง Dashboard
def main():
    st.title("Restaurant Management Dashboard")

    # Top Menus
    top_menu = create_menu_chart()
    st.plotly_chart(top_menu)

    # Monthly Sales
    monthly_chart = create_sales_chart(monthly_sales, x='Month', y='Total Sales', title='Total Sales by Month')
    st.plotly_chart(monthly_chart)

    # Monthly Menu Orders
    monthly_menu_chart = create_line_chart(menu_orders_by_month, x='Month', y='Order Count', color='Menu', title='Monthly Menu Orders')
    st.plotly_chart(monthly_menu_chart)

    monthly_category_chart = create_line_chart(category_orders_by_month, x='Month', y='Order Count', color='Category', title='Monthly Category Orders')
    st.plotly_chart(monthly_category_chart)

    comparison_chart = create_comparison_chart()
    st.plotly_chart(comparison_chart)

    food_fig, drink_fig = serve_time()
    st.plotly_chart(food_fig)
    st.plotly_chart(drink_fig)

if __name__ == '__main__':
    main()
