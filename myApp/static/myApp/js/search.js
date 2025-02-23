document.addEventListener("DOMContentLoaded", function () {
    function filterRoutes() {
        let input = document.getElementById("searchBar").value.toLowerCase();
        let routes = document.querySelectorAll(".route");

        routes.forEach(route => {
            let title = route.querySelector("h2").textContent.toLowerCase();
            if (title.includes(input)) {
                route.style.display = "block"; 
            } else {
                route.style.display = "none"; 
            }
        });
    }

    
    window.filterRoutes = filterRoutes;
});
