import time
import requests
import json
import csv

#事前に取得したYouTube API key
YT_API_KEY = '****************'

#csvファイルの名前
filename='Livecomment.csv'

def get_chat_id(yt_url):
    '''
    https://developers.google.com/youtube/v3/docs/videos/list?hl=ja
    '''
    video_id = yt_url.replace('https://www.youtube.com/watch?v=', '')
    #print('video_id : ', video_id)

    url    = 'https://www.googleapis.com/youtube/v3/videos'
    params = {'key': YT_API_KEY, 'id': video_id, 'part': 'liveStreamingDetails'}
    data   = requests.get(url, params=params).json()

    liveStreamingDetails = data['items'][0]['liveStreamingDetails']
    if 'activeLiveChatId' in liveStreamingDetails.keys():
        chat_id = liveStreamingDetails['activeLiveChatId']
        print('get_chat_id done!')
    else:
        chat_id = None
        print('NOT live')

    return chat_id

def get_chat(chat_id, pageToken):
    '''
    https://developers.google.com/youtube/v3/live/docs/liveChatMessages/list
    '''
    url    = 'https://www.googleapis.com/youtube/v3/liveChat/messages'
    params = {'key': YT_API_KEY, 'liveChatId': chat_id, 'part': 'id,snippet,authorDetails'}
    if type(pageToken) == str:
        params['pageToken'] = pageToken

    data   = requests.get(url, params=params).json()

    try:
        for item in data['items']:
            channelId = item['snippet']['authorChannelId']
            msg       = item['snippet']['displayMessage']
            date      = item['snippet']['publishedAt']
            usr       = item['authorDetails']['displayName']
            #supChat   = item['snippet']['superChatDetails']
            #supStic   = item['snippet']['superStickerDetails']
            log_text  = 'name: {} comment: {}'.format(usr, msg) #ユーザー名とコメントの出力
            with open(filename,'a',encoding='utf_8') as f:
                print(log_text)
                if len(msg)>0 and msg.isalnum():#コメントの長さが0のものと英語以外の言語の除外
                    csv.writer(f, lineterminator='\n').writerow([usr,msg])#csvファイルへの出力

    except:
        pass

    return data['nextPageToken']


def main(yt_url):
    slp_time        = 25 #sec
    iter_times      = 120 #回
    take_time       = slp_time / 60 * iter_times
    print('{}分後　終了予定'.format(take_time))
    print('work on {}'.format(yt_url))

    chat_id  = get_chat_id(yt_url)

    nextPageToken = None
    for ii in range(iter_times):
        #for jj in [0]:
        try:
            nextPageToken = get_chat(chat_id, nextPageToken)
            time.sleep(slp_time)
        except:
            break


if __name__ == '__main__':
    yt_url = input('Input YouTube URL > ')
    with open(filename,'a',encoding='utf_8') as f:
        csv.writer(f, lineterminator='\n').writerow(['AUTHOR','COMMENT'])#出力の名称
    main(yt_url)