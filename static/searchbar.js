const debounce = (func, delay = 300) => {
  let timeoutId;
  return (...args) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    timeoutId = setTimeout(() => {
      func.apply(null, args);
    }, delay);
  };
};

const url = "https://api.themoviedb.org/3/search/movie";
const api_key = "eef7b2622bdba952fd2f2f4fa88395b6";
const tmdb_poster_url = "https://image.tmdb.org/t/p/w780";

const fetchData = async (query) => {
  const response = await axios.get(url, {
    params: {
      api_key,
      query,
    },
  });
  return response.data.results;
};

const input = document.querySelector("#searchbar");
const results = document.querySelector(".searchbar-results");

document.addEventListener("click", (e) => {
  if (!results.contains(e.target)) {
    results.classList.add("hide");
  }
});

const onInput = async (e) => {
  results.innerHTML = ""; // Clear previous results

  movies = await fetchData(e.target.value);
  if (movies.length > 0) {
    results.classList.remove("hide"); // Show the dropdown
  } else {
    results.classList.add("hide"); // Hide the dropdown if there are no results
  }

  for (let movie of movies) {
    const div = document.createElement("div");

    if (movie.poster_path) {
      div.innerHTML = `
      <a href="/movie/${movie.id}">
        <img loading="lazy" width="40px" height="60px" src="${tmdb_poster_url}${
        movie.poster_path
      }" />
        <p>${movie.title}
        <span class="subtitle">(${movie.release_date.substring(0, 4)})</span>
        </p>
      </a>
    `;
    } else {
      div.innerHTML = `
      <a href="/movie/${movie.id}">
        <img width="40px" height="60px" src="/static/images/poster_not_found.jpg" />
        <p>${movie.title}
        <span class="subtitle">(${movie.release_date.substring(0, 4)})</span>
        </p>
      </a>
    `;
    }

    results.appendChild(div);
  }
};

input.addEventListener("input", debounce(onInput, 300));
