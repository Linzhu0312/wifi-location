

import altair as alt
import pandas as pd
#import json

def loadData():
    """Load reviews from ios_reviews.json and android_reviews.json
        
        Args:
        contents (iterable): an iterable of 'str' containing the review contents
        
        Return:
        dict (of DataFrame): key is platform name, value is the corresponding
        data frame containing 'name', 'rating', and 'content'.
        """
    import os 
    cur_dir = os.path.dirname(__file__) 
    df = pd.read_csv(os.path.join(cur_dir,"NYC_Free_Public_WiFi_03292017.csv"))
    df_Free  = df[df["TYPE"]=="Free"]
    df_LFree = df[df["TYPE"]=="Limited Free"]
    return {"Free":df_Free,"Limited Free":df_LFree}

def showRatingDistribution(data, name=''):
    """Create an interaactive visualization showing the distribution of ratings
        
        Args:
        data (DataFrame): the input data frame that must at least consists
        two columns 'name' and 'rating' for app names and ratings.
        name (str): the name of the platform (optional) to be displayed.
        
        Return:
        Chart: an Altair chart object that corresponds to the visualization
        """
    ## The color expression for highlighting the bar under mouse
    color_expression    = "highlight._vgsid_==datum._vgsid_"
    color_condition     = alt.ConditionalPredicateValueDef(color_expression, "SteelBlue")
    
    ## There are two types of selection in our chart:
    ## (1) A selection for highlighting a bar when the mouse is hovering over
    highlight_selection = alt.selection_single(name="highlight", empty="all", on="mouseover")
    
    ## (2) A selection for updating the rating distribution when the mouse is clicked
    ## Note the encodings=['y'] parameter is needed to specify that once a selection
    ## is triggered, it will propagate the encoding channel 'y' as a condition for
    ## any subsequent filter done on this selection. In short, it means use the data
    ## field associated with the 'y' axis as a potential filter condition.
    rating_selection    = alt.selection_single(name="PROVIDER", empty="all", encodings=['y'])
    
    ## We need to compute the max count to scale our distribution appropriately
    maxCount_BORO            = int(data['BORO'].value_counts().max())
    maxCount_SSID            = int(data['PROVIDER'].value_counts().max())
    
    ## Our visualization consists of two bar charts placed side by side. The first one
    ## sorts the apps by their average ratings as below. Note the compound selection
    ## that is constructed by adding the two selections together.
    barMean = alt.Chart() \
        .mark_bar(stroke="Black") \
        .encode(
                alt.Y('BORO:O', axis=alt.Axis(title="Location of Hotspot"),
                      sort=alt.SortField(field="BORO", op="count", order='descending'),
                      ),
                alt.X("count()", axis=alt.Axis(title="Number of Hotspot"),
                      scale = alt.Scale(domain=(0,maxCount_BORO)),
                      ),
                alt.ColorValue("LightGrey", condition=color_condition),
                ).properties(
                             selection = highlight_selection+rating_selection
                             )
    
    ## The second one uses the selected app specified by the rating_selection
    ## to filter the data, and build a histogram based on the ratings. Note
    ## the use of rating_selection.ref() as a condition for transform_filter().
    ## The scale was explicitly constructed for the X axis to fill out the
    ## the potential empty values, e.g. no one gave an app a score of 3, but
    ## we still want to show 1, 2, 3, 4, and 5 in the axis (but not in with .5).
    barRating = alt.Chart() \
        .mark_bar(stroke="Black") \
        .encode(
                alt.X("PROVIDER:O", axis=alt.Axis(title="PROVIDER"),
                      sort=alt.SortField(field="PROVIDER", op="count", order='descending'),
                      ),
                alt.Y("count()", axis=alt.Axis(title="Number of Hotspot"),
                      scale=alt.Scale(domain=(0,maxCount_SSID)),
                      ),
                alt.ColorValue("LightGrey"),
                ).properties(
                             selection = highlight_selection
                             ).transform_filter(
                                                rating_selection.ref()
                                                )

    states = "https://raw.githubusercontent.com/hvo/datasets/master/nyc_zip.geojson"
    
    # US states background
    background = alt.Chart(states
                           ).mark_geoshape(
                                   fill='lightgray',
                                   stroke='white'
                                   ).properties(
                                title='Map',
                                width=500,
                                height=500
                                ).project('albersUsa')
                                                              
    points = alt.Chart(data
                       ).mark_point(
                               filled=True, 
                               size=200
                               ).encode(
                        longitude='LON:Q',
                        latitude='LAT:Q',
                        color=alt.value('SteelBlue'),
                        size=alt.value(30)
                        ).transform_filter(
                                           rating_selection.ref())
                                                              
                                                              ## We just need to concatenate the plots horizontally, and return the result.
    return alt.hconcat(alt.vconcat(barMean,barRating,
                                   data=data,
                                   title="{} Hotspot Distribution".format(name)
                                   ),(background+points),data=data)
