const id_username = document.querySelector('#id_username');
const feedBackArea = document.querySelector('.invalid-feedback');

id_username.addEventListener('keyup', (e) => {
    console.log('777777', 777777);

    const usernameVal = e.target.value;

    id_username.classList.remove('is-invalid');
    feedBackArea.style.display = 'none';

    if (usernameVal.length > 0){
        fetch('/authentication/validate-username', {
        body: JSON.stringify({username: usernameVal}),
        method: 'POST',
        }).then(res=>res.json()).then(data=>{
            console.log('data', data);

            if(data.username_error){
                id_username.classList.add('is-invalid');
                feedBackArea.style.display = 'block';
                feedBackArea.innerHTML =  `<p>${data.username_error}</p>`;
            }
        });
    };

})