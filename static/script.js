const sex = document.getElementById('user_sex');

if(sex.innerHTML === 'm'){
    sex.innerHTML = 'Male';
}
else {
    sex.innerHTML = 'Female';
}

let goal = document.getElementById('goal');

goal.innerHTML += ' weight';
goal.style.textTransform = 'capitalize'

let activity = document.getElementById('activity');

activity.style.textTransform = 'capitalize';

let rate = document.getElementById('rate');

rate.style.textTransform = 'capitalize';

const dt = document.getElementById('diet_type');
const x = 'Diet Type: ';

if(dt.innerHTML === 'gf'){
    dt.innerHTML = x+ 'Gluten Free';
}
else if(dt.innerHTML === 'veg'){
    dt.innerHTML = x+ 'Vegetarian';
}
else {
    dt.innerHTML = x+ 'Vegan';
}

    
[('vegan', 'Vegan'), ('veg', 'Vegetarian'), ('gf', 'Gluten Free')]
