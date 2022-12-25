import pandas as pd
import zipfile, json, glob, gc
from tqdm import tqdm

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

lines_ids = []
lines_timestamp_ms = []
lines_user = []
lines_user_name = []

lines_in_reply_to_screen_name = []
lines_in_reply_to_user_id = []
lines_country_code = []
lines_user_location = []
lines_coordinates = []
lines_text = []
lines_place_coordinates = []

for zip_path in tqdm(glob.glob('OneDrive_2_2022-11-23/*.zip')[:]):

    zip_file = zipfile.ZipFile(zip_path, 'r')

    lines = zip_file.open(zip_file.filelist[0].filename).readlines()
    lines_decode = [json.loads(x.decode().strip()) for x in lines[:]]
    lines_decode = [x for x in lines_decode if len(x) != 0 if 'id' in x]

    # lines_ids += [x['id'] for x in lines_decode if 'id' in x]
    # lines_timestamp_ms += [x['timestamp_ms'] for x in lines_decode if 'id' in x]
    # lines_user += [x['user']['id'] for x in lines_decode if 'id' in x]
    # lines_user_name += [x['user']['name'] for x in lines_decode if 'id' in x]

    # lines_in_reply_to_screen_name += [x['in_reply_to_screen_name'] for x in lines_decode if 'id' in x]
    # lines_in_reply_to_user_id += [x['in_reply_to_user_id_str'] for x in lines_decode if 'id' in x]

    for x in lines_decode:

        #     if 'id' in x:
        #         if x['place'] is not None and 'country_code' in x['place']:
        #             lines_country_code.append(x['place']['country_code'])
        #         else:
        #             lines_country_code.append(np.nan)

        # if 'user' in x and 'location' in x['user'] and x['user']['location'] is not None:
        #     lines_user_location.append(x['user']['location'])
        # else:
        #     lines_user_location.append(np.nan)
        #
        # if 'coordinates' in x and x['coordinates'] is not None and 'coordinates' in x['coordinates']:
        #     lines_coordinates.append(x['coordinates']['coordinates'])
        # else:
        #     lines_coordinates.append(np.nan)

        # if 'text' in x:
        #     lines_text.append(x['text'])
        # else:
        #     lines_text.append(np.nan)

        try:
            lines_place_coordinates.append(x['place']['bounding_box']['coordinates'])
        except:
            lines_place_coordinates.append(np.nan)

    # break
    zip_file.close()
    del lines, lines_decode

data = pd.DataFrame(
    {
        'id': lines_ids,
        'timestamp_ms': lines_timestamp_ms,
        'user': lines_user,
        'user_name': lines_user_name,
        # 'in_reply_to_user_name': lines_in_reply_to_screen_name,
        # 'in_reply_to_user_id': lines_in_reply_to_user_id,
        #
        # 'user_location': lines_user_location,
        # 'place_country_code': lines_country_code,

        # 'coordinates': lines_coordinates,

        'text': lines_text,
        # 'place_coordinates': lines_place_coordinates
    }
)

data['timestamp_ms'] = data['timestamp_ms'].astype(int) / 1000
data['timestamp_ms'] = pd.to_datetime(data['timestamp_ms'], unit='s')
data['year_month_day'] = data['timestamp_ms'].dt.strftime('%Y-%m-%d')
data['dayofweek'] = data['timestamp_ms'].dt.dayofweek
data['hour'] = data['timestamp_ms'].dt.hour


def convert_user_location(x):
    x = str(x)
    if 'england' in x.lower():
        return 'GB'
    elif 'turkey' in x.lower():
        return 'TR'
    elif 'spain' in x.lower():
        return 'ES'
    elif 'france' in x.lower():
        return 'FR'
    else:
        return np.nan


data['user_location'] = data['user_location'].map(convert_user_location)

wordcloud = WordCloud(width=1200, height=600,
                      background_color='white',
                      stopwords=STOPWORDS,
                      min_font_size=10).generate('\n'.join(
    data.loc[(data['place_country_code'] == 'GB') & (data['year_month_day'] == '2022-06-24')]['text'].sample(1000))
                                                 )
# UK

plt.figure(figsize=(8, 8), facecolor=None)
plt.imshow(wordcloud)
plt.axis("off")
plt.tight_layout(pad=0)

plt.show()


from geopy import distance  # to calculate distance on the surface

diagonals_distance = []
for x in data['place_coordinates'].sample(100000).dropna():
    x = x[0]
    diagonals_distance.append(
        distance.distance((x[0][1], x[0][0]), (x[2][1], x[2][0])).kilometers
    )

plt.figure(figsize=(10, 5))
_ = plt.hist(diagonals_distance, label='CDF', histtype='step', color='k', bins=20)
plt.xlabel('kilometers of box diagonals')
