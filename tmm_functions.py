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

with open('login.txt') as f: 
    data = f.readlines()
class Dataset:
    #classe para formatação e analise de datasets
    
    def __init__(self,df2): #df será passado como string do diretorio do csv
        if type(df2)==str:
            self.df=pd.read_csv(df2)
            self.df["loudness"]=abs(self.df["loudness"])
            self.dict=self.df.iloc[:,1:14].to_dict('records')
        else:   
            self.df=df2
            self.df["loudness"]=abs(self.df["loudness"])
            self.dict=self.df.iloc[:,[0,2,3,4,6,7,8,9,10,11,12,13]].to_dict('records')
            
        self.ans=self.df[self.df.columns[-1]].tolist()
        self.vec=DictVectorizer()
        self.nb=MultinomialNB()
        self.train_songs=self.vec.fit_transform(self.dict).toarray()
        self.svc=SVC()
        
    def train(self):
        self.svc.fit(self.train_songs,self.ans)
        self.nb.fit(self.train_songs,self.ans)
        return "<R2D2>AS THE TIME PASSES BY, THE MORE I LEARN <R2D2>"
        
    def check_score(self,new_songs,clf="nb"):
        if clf=="svc":
            return self.svc.score(new_songs.train_songs,new_songs.ans)
        else:
            return self.nb.score(new_songs.train_songs,new_songs.ans)
    
    
    def evaluate(self,new_songs,clf="nb"): #cat_number= numero de categorias (ex: muito ruim,ruim,medio,bom,otimo (5) )
        if clf=="svc":
            return self.svc.predict(new_songs.train_songs)
        else:
            return self.nb.predict(new_songs.train_songs)
    def savecsv(self,csv_name):
        self.df.to_csv(csv_name)
        if not df['study']:
            print("Aviso: Dataframe sem classificação de /Study/ salvo")
        
            

class User():
    #classe para facilitar o uso do spotipy
    def __init__(self,client): #a variavel client devera ser uma lista que contem o id do cliente e a senha dele
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
