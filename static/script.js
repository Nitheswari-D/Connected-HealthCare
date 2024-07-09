// script.js
const navMenu = document.querySelector('nav ul');
const navToggle = document.querySelector('.nav-toggle');

navToggle.addEventListener('click', () => {
  navMenu.classList.toggle('active');
});