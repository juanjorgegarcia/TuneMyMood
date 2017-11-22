$(document).ready(()=>{
    console.log('ready!')

    $('#goBtn').click(() => {
        let nome = $('#name').val()
        let genre = $('#genre').val()
        let mood = $('#mood').val()
        createPlaylist(nome,genre,mood)
    })

})

function createPlaylist(nome,genero,moods){
    var params = { genero : genero, moods : moods, name : nome}
    var urlParams = new URLSearchParams(Object.entries(params))
    fetch('http://localhost:5000/playlist?' + urlParams, {
        method : 'GET'
    }).then((res)=>{
    res.json().then((data)=> {
        console.log(data)        
        $('#goBtn').after(`
        <iframe src="https://open.spotify.com/embed?uri=${data.uri}" width="300" height="380" frameborder="0" allowtransparency="true"></iframe>`)
    })})
}
