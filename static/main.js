// without jQuery (doesn't work in older IEs)
document.addEventListener('DOMContentLoaded', function(){ 
    console.log("ready!")
      
    fetch('http://localhost:5000/token',{
        method: 'GET',
        
    }).then((res) => {
        console.log(res)
        res.text().then((token) => {
            $('#playlists').append(`Token : ${token}`)            
        })
    }).catch((err) => console.log(err))


    const params = { generos : 'rock,gospel' ,moods:'gym,focus'}
    const urlParams = new URLSearchParams(Object.entries(params));

    fetch('http://localhost:5000/playlist?' + urlParams).then((res) => {

        res.json().then((data) => {
            console.log(data)
        })
    })

    // $()

}, false);

var requestPlaylist = function(){
    const params = { generos : 'rock' ,moods:'gym'}
    const urlParams = new URLSearchParams(Object.entries(params));
    fetch('http://localhost:5000/playlist?' + urlParams).then((res) => {
        res.json().then((data) => {
            console.log(data)
        })
        })

    }
