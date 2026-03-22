// Added by Mark: Basically just makes a hyperlink work as a form button
document.getElementById("logout-link").addEventListener("click", function (e) {
  e.preventDefault();
  document.getElementById("logout-form").submit();
});