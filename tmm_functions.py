import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction import DictVectorizer
vec=DictVectorizer()
import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials
from sklearn.svm import SVC

class Dataset:
    #classe para formatação e analise de datasets
    
    def __init__(self,df2): #df será passado como string do diretorio do csv
        if type(df2)==str:
            self.df=pd.read_csv(df2)
            self.df["loudness"]=abs(self.df["loudness"])
            self.dict=self.df.filter(items=['acousticness','danceability','instrumentalness','key','liveness','loudness','mode'
                      ,'speechiness','tempo','time_signature','valence']).to_dict('records')
        else:   
            self.df=df2
            self.df["loudness"]=abs(self.df["loudness"])
            self.dict=self.df.filter(items=['acousticness','danceability','instrumentalness','key','liveness','loudness','mode'
                      ,'speechiness','tempo','time_signature','valence']).to_dict('records')
            
        self.ans=self.df[self.df.columns[-1]].tolist()
        self.vec=DictVectorizer()
        self.train_songs=self.vec.fit_transform(self.dict).toarray()

    def save_csv(self,csv_name):
        self.df.to_csv(csv_name)
        


class User:
    #classe para facilitar o uso do spotipy
    def __init__(self,data): #a variavel client devera ser uma lista que contem o id do cliente e a senha dele
        self.credentials_manager=SpotifyClientCredentials(client_id=data[0].strip(), client_secret=data[1].strip())
        self.sp=spotipy.Spotify(client_credentials_manager=self.credentials_manager)
        self.sp.trace=False
        self.playlists={}
    
    def playlist_downloader(self,name,userid,playlist_id): 
        #name= nome que a playlist ficara salva no dicionario
        #userid = id do usuario dono da playlist
        #playlist_id = id da playlist
        #função para baixar as musicas de uma playlist do spotify
        playlist = self.sp.user_playlist(user=userid,playlist_id=playlist_id)
        songs = playlist["tracks"]["items"]
        ids = []
        artists=[]
        song_title=[]
        
        for i in range(len(songs)): 
            ids.append(songs[i]["track"]["id"])
            artists.append(songs[i]["track"]["artists"][0]["name"])
            song_title.append(songs[i]["track"]["name"])
            
        features = self.sp.audio_features(ids) 
        df_features = pd.DataFrame(features)
        df_artist = pd.DataFrame(artists)
        series_artist = pd.Series(artists, name='artist')
        series_title = pd.Series(song_title,name="song_title")
        df=pd.concat([df_features,series_title,series_artist],axis=1)
        self.playlists[name]=df
        
        return df #retornara o dataframe com as musicas


class Trainer():
    #classe para facilitar o treinamento com o NB e SVC
    def __init__(self):
        self.data={}
        self.nb={}
        self.svc={}
        self.results_nb={}
        self.results_svc={}

    def add_data(self,genre,data):
        self.data[genre]=data
    
    def train(self,name,dataset,genre="ans"):
        #name=nome da chave do dicionario que sera salvo o treinamento,
        #dataset=objeto da classe Dataset que recebera o treino
        nb=MultinomialNB()
        svc=SVC()
        if genre=="ans":
            self.nb[name]=nb.fit(dataset.train_songs,dataset.ans)
            self.svc[name]=svc.fit(dataset.train_songs,dataset.ans)
        else:
            self.nb[name]=nb.fit(dataset.train_songs,dataset.df[genre].tolist())
            self.svc[name]=svc.fit(dataset.train_songs,dataset.df[genre].tolist())
        return "The new dataset was trained and saved"
        
    def check_score(self,name,new_songs,genre="ans"):
        #metodo para checar a eficacia do machine learning
        if genre=="ans":
            print("This is the SVC score: {}".format(self.svc[name].score(new_songs.train_songs,new_songs.ans)))

            print("This is the NB score: {}".format(self.nb[name].score(new_songs.train_songs,new_songs.ans)))
        else:
            print("This is the SVC score: {}".format(self.svc[name].score(new_songs.train_songs,new_songs.df[genre].tolist())))

            print("This is the NB score: {}".format(self.nb[name].score(new_songs.train_songs,new_songs.df[genre].tolist())))

    
    
    def evaluate(self,name,new_songs):
        #metodo para salvar as musicas que a maquina classificou
        new_songs.df=new_songs.df.reset_index(drop=True)
        
        liked_nb=[]
        disliked_nb=[]
        
        liked_svc=[]
        disliked_svc=[]
        
        nb_res=self.nb[name].predict(new_songs.train_songs)
        svc_res=self.svc[name].predict(new_songs.train_songs)
        
        for i in range(len(nb_res)):
            if nb_res[i] == 0:
                
                disliked_nb.append(new_songs.df['song_title'][i]+' : '+new_songs.df['artist'][i])
            else:
                
                liked_nb.append(new_songs.df['song_title'][i]+' : '+new_songs.df['artist'][i])
            if svc_res[i] == 0:
                
                disliked_svc.append(new_songs.df['song_title'][i]+' : '+new_songs.df['artist'][i])
            else:
                liked_svc.append(new_songs.df['song_title'][i]+' : '+new_songs.df['artist'][i])
                

        self.results_nb[name]={'liked':liked_nb,'disliked':disliked_nb}
        self.results_svc[name]={'liked':liked_svc,'disliked':disliked_svc}
        

        
        return "The result of the evaluation is now saved"

def list_download(listi,listy_g,genre,datavalue):
    df_all = client.playlist_downloader(listi[0][0],listi[0][1],listi[0][2])
    print(1)
    df_list = []
    for i in range(1,len(listi)):
        df =client.playlist_downloader(listi[i][0],listi[i][1],listi[i][2])
        df_all = pd.concat([df_all,df])
        print(i+1)
    for i in range(len(listy_g)):
        df_all[listy_g[i]] = 0
    if datavalue == 1:
        df_all[genre] = datavalue
    print("SO DONE")
    return df_all

def list_download_blank(listi):
    df_all = client.playlist_downloader(listi[0][0],listi[0][1],listi[0][2])
    print(1)
    df_list = []
    for i in range(1,len(listi)):
        df =client.playlist_downloader(listi[i][0],listi[i][1],listi[i][2])
        df_all = pd.concat([df_all,df])
        print(i+1)
    print("SO DONE")
    return df_all
        
def lister(listaurl):
    liste = []
    for i in range(len(listaurl)):
        a = re.split(r"/", listaurl[0])
        temp = [a[5]+str(i+1),a[4],a[6]]
        liste.append(temp)
    return liste
