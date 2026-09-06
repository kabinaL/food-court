document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("foodSearch");
    const categoryFilter = document.getElementById("categoryFilter");
    const availabilityFilter = document.getElementById("availabilityFilter");
    const foodCards = document.querySelectorAll(".food-card");
    const noFoodResults = document.getElementById("noFoodResults");


    function filterFoods() {

        const searchText = searchInput
            ? searchInput.value.toLowerCase().trim()
            : "";

        const selectedCategory = categoryFilter
            ? categoryFilter.value.toLowerCase()
            : "all";

        const selectedAvailability = availabilityFilter
            ? availabilityFilter.value.toLowerCase()
            : "all";


        let visibleCount = 0;


        foodCards.forEach(function (card) {

            const foodName = (
                card.dataset.name || ""
            ).toLowerCase();

            const foodCategory = (
                card.dataset.category || ""
            ).toLowerCase();

            const foodAvailability = (
                card.dataset.available || ""
            ).toLowerCase();


            const matchesSearch =
                foodName.includes(searchText);


            const matchesCategory =
                selectedCategory === "all" ||
                foodCategory === selectedCategory;


            const matchesAvailability =
                selectedAvailability === "all" ||
                foodAvailability === selectedAvailability;


            if (
                matchesSearch &&
                matchesCategory &&
                matchesAvailability
            ) {

                card.style.display = "";

                visibleCount++;

            } else {

                card.style.display = "none";

            }

        });


        // Show empty message when nothing matches
        if (noFoodResults) {

            if (visibleCount === 0 && foodCards.length > 0) {

                noFoodResults.style.display = "block";

            } else {

                noFoodResults.style.display = "none";

            }

        }

    }


    // Search
    if (searchInput) {

        searchInput.addEventListener(
            "input",
            filterFoods
        );

    }


    // Category filter
    if (categoryFilter) {

        categoryFilter.addEventListener(
            "change",
            filterFoods
        );

    }


    // Availability filter
    if (availabilityFilter) {

        availabilityFilter.addEventListener(
            "change",
            filterFoods
        );

    }

});