import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import re
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
                      ,'speechiness','tempo','time_signature','valence','artist']).to_dict('records')
        else:   
            self.df=df2
            self.df["loudness"]=abs(self.df["loudness"])
            self.dict=self.df.filter(items=['acousticness','danceability','instrumentalness','key','liveness','loudness','mode'
                      ,'speechiness','tempo','time_signature','valence','artist']).to_dict('records')
            
        self.ans=self.df[self.df.columns[-1]].tolist()
        self.vec=DictVectorizer()
        self.train_songs=self.vec.fit_transform(self.dict).toarray()

    def save_csv(self,csv_name):
        self.df.to_csv(csv_name)
        


class User:
    #classe para facilitar o uso do spotipy
    def __init__(self,data,token=0): #a variavel client devera ser uma lista que contem o id do cliente e a senha dele
        self.credentials_manager=SpotifyClientCredentials(client_id=data[0].strip(), client_secret=data[1].strip())
        if token!=0:
            self.sp=spotipy.Spotify(client_credentials_manager=self.credentials_manager,auth=token)
        else:
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
        def __init__(self):
            self.data={}
            self.nb={}
            self.svc={}
            self.results_nb={}
            self.results_svc={}
            self.df_results_nb = {}
            self.df_results_svc = {}
            self.vc={}
            
        def pre_format(self,genre,data,not_data):
            data.df[genre]=1
            not_data.df[genre]=0
            dada_concat=Dataset(pd.concat([data.df,not_data.df]))
            return dada_concat
    
        def train(self,name,dataset,genre="ans",threshold=[.5,.5]):
            self.vc[name]=DictVectorizer()
            dataset.train_songs=self.vc[name].fit_transform(dataset.dict).toarray()
            #name=nome da chave do dicionario que sera salvo o treinamento,
            #dataset=objeto da classe Dataset que recebera o treino
            
            nb=MultinomialNB(class_prior=threshold)
            svc=SVC()
            if genre=="ans":
                self.nb[name]=nb.fit(dataset.train_songs,dataset.ans)
                self.svc[name]=svc.fit(dataset.train_songs,dataset.ans)
            else:
                self.nb[name]=nb.fit(dataset.train_songs,dataset.df[genre].tolist())
                self.svc[name]=svc.fit(dataset.train_songs,dataset.df[genre].tolist())
            return "The new dataset was trained and saved"
        
        def evaluate(self,name,new_songs): #metodo para salvar as musicas que a maquina classificou
            #name = nome do treino que você quer usar
            #new_songs = dataset de de musicas sem genero classificado
        
            new_songs.df=new_songs.df.reset_index(drop=True)
            new_songs.train_songs=self.vc[name].transform(new_songs.dict).toarray()
    
            sim_nb=[] #Lista de Sims(1) dados pelo NaiveBayes
            nao_nb=[] #Lista de Nãos(1) dados pelo NaiveBayes

            sim_svc=[] #Lista de Sims(1) dados pelo SVC
            nao_svc=[] #Lista de Nãos(1) dados pelo SVC
            
            nb_res=self.nb[name].predict(new_songs.train_songs)
            svc_res=self.svc[name].predict(new_songs.train_songs)
            framesnb = []
            framessvc = []
            for i in range(len(nb_res)):
                if nb_res[i] == 0:
                    
                    nao_nb.append(new_songs.df['song_title'][i]+' : '+new_songs.df['artist'][i])
                else:
                    sim_nb.append(new_songs.df['song_title'][i]+' : '+new_songs.df['artist'][i])
                    framesnb.append(new_songs.df.iloc[i:i+1])
                if svc_res[i] == 0:
                    
                    nao_svc.append(new_songs.df['song_title'][i]+' : '+new_songs.df['artist'][i])
                else:
                    sim_svc.append(new_songs.df['song_title'][i]+' : '+new_songs.df['artist'][i])
                    framessvc.append(new_songs.df.iloc[i:i+1])
    
            self.results_nb[name]={'sim':sim_nb,'nao':nao_nb}
            self.results_svc[name]={'sim':sim_svc,'nao':nao_svc}
            self.df_results_nb[name] = pd.concat(framesnb)
            self.df_results_svc[name] = pd.concat(framessvc)
            
            return "The result of the evaluation is now saved!"
        def check_score(self,name,new_songs,genre="ans"):
            #metodo para checar a eficacia do machine learning
            new_songs.train_songs=self.vc[name].transform(new_songs.dict).toarray()
            if genre=="ans":
                print("This is the SVC score: {}".format(self.svc[name].score(new_songs.train_songs,new_songs.ans)))
    
                print("This is the NB score: {}".format(self.nb[name].score(new_songs.train_songs,new_songs.ans)))
        
            else:
                svcscore = self.svc[name].score(new_songs.train_songs,new_songs.df[genre].tolist())
                print("This is the SVC score: {}".format(svcscore))
                nbscore = self.nb[name].score(new_songs.train_songs,new_songs.df[genre].tolist())
                print("This is the NB score: {}".format(nbscore))
                if svcscore > nbscore:
                      print("Para {} o SVC se saiu melhor".format(name))
                else:
                      print("Para {} o NB se saiu melhor".format(name))
        def test_this(self,name,genre):
            #name=nome que sera salvo o treinamento 
            #genre=o genero que sera treinado
            
            genre_2=genre
            genre_list=['funk','rock','eletronica','metal','sertanejo','rap']

            genre_name=genre+'_df.csv'
            genre=Dataset(genre_name)
            not_genre_name='not_'+genre_name
            not_genre=Dataset(not_genre_name)
            genre_all=self.pre_format(genre,genre,not_genre)

            self.train(name,genre_all,genre)
            test_name_df='test_'+genre_name
            test_genre_df=Dataset(test_name_df)
            x=[]
            for i in range(len(genre_list)):
                if genre_list[i]!=genre_2:
                    x.append(genre_list[i])
            random_genre=np.random.choice(x)
    
            
            test_not_name_df='test_'+random_genre+'_df.csv'
            test_genre_not_df=Dataset(test_not_name_df)

            test_genre_all=self.pre_format(genre,test_genre_df,test_genre_not_df)

            self.check_score(name,test_genre_all,genre)
            self.evaluate(name,test_genre_all)
            
        def playlist_maker(self,genre,mood):
            genre_dataset =Dataset(pd.concat([pd.read_csv(genre+'_df.csv'),pd.read_csv('not_'+genre+'_df.csv')]))
            self.train(genre,genre_dataset,genre,threshold=[0.8,0.2])
            mega_dataset = Dataset(pd.read_csv("giant_df.csv"))
            self.evaluate(genre,mega_dataset)
            filtered_ds = Dataset(self.df_results_nb[genre])

            mood_dataset = Dataset(pd.concat([pd.read_csv(mood+'_df.csv'),pd.read_csv('not_'+mood+'_df.csv')]))
            self.train(mood,mood_dataset,mood)
            self.evaluate(mood,filtered_ds)
            playlist = self.df_results_nb[mood]

            playlist = playlist.drop_duplicates()
            playlist = playlist.sample(frac=1)



            return playlist

        def multidf(self,name,genre):
            #name=nome que sera salvo o treinamento 
            #genre=o genero que sera treinado
            genre_2=genre
            genre_list=['funk','rock','eletronica','metal','sertanejo','rap']

            genre_name=genre+'_df.csv'
            genre=Dataset(genre_name)
            frames = []
            for i in range(len(genre_list)):
                not_genre_name = 'not_'+ genre_list[i]
                not_genre=Dataset(not_genre_name)
                frames.append(not_genre)
            not_genre = pd.concat(frames)

            genre_all=self.pre_format(genre,genre,not_genre)

            self.multitrain(name,genre_all)
            #  self.svc[name]
            test_name_df='test_'+genre_name
            test_genre_df=Dataset(test_name_df)
            x=[]
            for i in range(len(genre_list)):
                if genre_list[i]!=genre_2:
                    x.append(genre_list[i])
            random_genre=np.random.choice(x)

            #print(random_genre)
            test_not_name_df='test_'+random_genre+'_df.csv'
            test_genre_not_df=Dataset(test_not_name_df)

            test_genre_all=self.pre_format(genre,test_genre_df,test_genre_not_df)

            self.check_score(name,test_genre_all,genre)
            self.evaluate(name,test_genre_all)





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
        a = re.split(r"/", listaurl[i])
        temp = [a[5]+str(i+1),a[4],a[6]]
        liste.append(temp)
    return liste
with open("login.txt") as f: #Abrindo o login.txt que contem na 1a linha Client_user e na segunda a Client_secre
    data = f.readlines()
client=User(data)