function ToggleDarkmode() {
  var body = document.body;
  var button = this;
  body.classList.toggle('light-mode');

  // Update button content based on the presence of 'light-mode' class on body
  if (body.classList.contains('light-mode')) {
    button.textContent = '🌜'; // Change to moon symbol for dark mode
  } else {
    button.textContent = '🌞'; // Change to sun symbol for light mode
  }
}

addEventListener("load",function(event) {
  document.getElementById('dark-toggle').addEventListener('click', function() {
    ToggleDarkmode()
  });
});


document.addEventListener('DOMContentLoaded', (event) => {
  // Get the current hour using 24-hour clock
  var currentHour = new Date().getHours();

  // If the current hour is less than 21 (9 PM), switch to light mode
  if (currentHour < 21) {
    ToggleDarkmode()
  }
});
