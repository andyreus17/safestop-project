// Como las imagenes se suben de forma asincronica no mostraremos nada de la tabla
// hasta que se carguen las imagenes
async function waitForImageToLoad(url, maxRetries = 50, interval = 500) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            const res = await fetch(url, { method: 'HEAD' });
            if (res.ok) {
                return true;
            }
        } catch (e) {
            // Si hay un error, continuamos con el siguiente intento solamente
        }
        await new Promise(resolve => setTimeout(resolve, interval));
    }
    return false;
}


// Ahora cargaremos asincronicamente el feed y luego se renderizara
window.addEventListener('DOMContentLoaded', async function() {
    // Obtenemos los elementos del html que cargaremos asincronicamente
    const video = this.document.getElementById('video');
    const id = window.feed_id;
    const loader = document.getElementById('loader');
    const div_video = document.getElementById('video_div');
    const table = document.getElementById('resultTable');
    const table_body = document.getElementById('resultBody');

    // Ahora haremos la peticion
    try {
        // LLamamos a la api para obtener el feed
        const respone = await fetch(`/safestop/front/api/feed${id}`);
        const data = await respone.json();

        // Si arroja un error lo mostramos
        if (data.error){
            loader.innerText = data.error;
            return;
        }

        // Ahora cargamos el video
        video.innerHTML = `<source src=/safestop/front/static/video/${data.name} type="video/mp4">`;
        video.load();
        video.play();
        // Y le añadimos el evento para que se detenga al finalizar
        video.addEventListener('ended', function() {
            video.pause();
            video.currentTime = 0;
        });

        // Y ahora cargamos la tabla
        await Promise.all(Object.values(data.frames).map(async frame => {
            // Creamos la fila
            const tr = document.createElement('tr');

            // He iremos creando las columnas
            const td_date = document.createElement('td');
            td_date.textContent = frame.date;

            const td_time = document.createElement('td');
            td_time.textContent = frame.time;
            td_time.classList.add("clickable");
            // Y si se hace click en la columna se saltara al video
            td_time.onclick = function() {
                jump(frame.time);
            };

            const td_image = document.createElement('td');
            const img = document.createElement('img');
            img.style.width = '300px';
            img.style.height = '250px';

            const td_frame = document.createElement('td');
            const img2 = document.createElement('img');
            img2.style.width = '300px';
            img2.style.height = '250px';
            
            const td_patent = document.createElement('td');
            td_patent.textContent = frame.patent;

            // Ahora revisaremos que las dos imagenes se hayan cargado
            // Esperamos a que ambas imágenes estén disponibles
            const frameURL = `/safestop${frame.frame}`;
            const plateURL = `/safestop${frame.plate_crop}`;

            await waitForImageToLoad(frameURL);
            await waitForImageToLoad(plateURL);

            // Si ya estan listas, las añadimos a las columnas
            img.src = plateURL;
            img2.src = frameURL;
            td_image.appendChild(img);
            td_frame.appendChild(img2);

            // Ahora añadimos las columnas a la fila
            tr.appendChild(td_date);
            tr.appendChild(td_time);
            tr.appendChild(td_image);
            tr.appendChild(td_frame);
            tr.appendChild(td_patent);
            // Y la fila a la tabla
            table_body.appendChild(tr);
        }));

        // Y como ya no necesitamos el loader lo ocultamos
        loader.style.display = 'none';
        // Y mostramos el video y la tabla
        div_video.style.display = 'block';
        table.style.display = 'table';
    }
    catch (error) {
        // Si hay un error lo mostramos
        loader.innerText = 'Error al cargar el feed';
        return;
    }
});

// Tendremmos una funcion para saltar desde el tiempo de la tabla al video

var myVideo = document.getElementById("video");
var s = window.start;
var liveButton = document.getElementById("liveButton");
let liveTime=0;
let lastJump=0;
let realTime=0;
let timeOffset=0;

function jump(x) {
    liveButton.style.visibility = "visible";
    if (realTime===1){
        timeOffset = timeOffset+myVideo.currentTime-lastJump;
    }
    else {
        liveTime=myVideo.currentTime;
        realTime=1;
    }
    lastJump=(60*(Number(x.substring(0, 2))-Number(s.substring(0, 2)))+(Number(x.substring(3, 5))-Number(s.substring(3, 5))))-1;
    myVideo.currentTime = (60*(Number(x.substring(0, 2))-Number(s.substring(0, 2)))+(Number(x.substring(3, 5))-Number(s.substring(3, 5))))-1;
    document.documentElement.scrollTop = 0;
    myVideo.play();
}
function live(){
    liveButton.style.visibility = "hidden";
    if (realTime===1){
        timeOffset += myVideo.currentTime-lastJump;
        liveTime += timeOffset;
        timeOffset=0
        myVideo.currentTime=liveTime;
        realTime=0;
        document.documentElement.scrollTop = 0;
        myVideo.play();
    }
}