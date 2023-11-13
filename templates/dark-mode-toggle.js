addEventListener("load",function(event) {
  document.getElementById('dark-toggle').addEventListener('click', function() {
    var body = document.body;
    var button = this;
    body.classList.toggle('light-mode');

    // Update button content based on the presence of 'light-mode' class on body
    if (body.classList.contains('light-mode')) {
      button.textContent = '🌜'; // Change to moon symbol for dark mode
    } else {
      button.textContent = '🌞'; // Change to sun symbol for light mode
    }
  });
});
