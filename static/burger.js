const bars = document.querySelector(".bars");
const burgerNav = document.querySelector(".burger-nav");
const changedNavBefore = window.getComputedStyle(
  document.querySelector(".burger-nav"),
  "::before"
);

bars.addEventListener("click", (e) => {
  burgerNav.classList.toggle("changed-nav");
  bars.classList.toggle("change");
});

document.addEventListener("click", (e) => {
  const isClickedInsideNav =
    burgerNav.contains(e.target) || bars.contains(e.target);
  if (!isClickedInsideNav) {
    burgerNav.classList.remove("changed-nav");
    bars.classList.remove("change");
  }
});
