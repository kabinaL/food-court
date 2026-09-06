document.addEventListener("DOMContentLoaded", function () {

    const categoryButtons = document.querySelectorAll(".category-btn");
    const foodCards = document.querySelectorAll(".food-card");

    categoryButtons.forEach(button => {

        button.addEventListener("click", function () {

            // Remove active class from all buttons
            categoryButtons.forEach(btn => {
                btn.classList.remove("active");
            });

            // Add active class to clicked button
            this.classList.add("active");

            // Get selected category
            const selectedCategory = this.dataset.category;

            foodCards.forEach((card, index) => {

                const foodCategory = card.dataset.category;

                // First hide cards
                card.classList.remove("show-card");

                setTimeout(() => {

                    if (
                        selectedCategory === "All" ||
                        foodCategory === selectedCategory
                    ) {

                        card.style.display = "block";

                        // Small delay creates smooth entrance
                        setTimeout(() => {
                            card.classList.add("show-card");
                        }, index * 70);

                    } else {

                        card.style.display = "none";

                    }

                }, 150);

            });

        });

    });

});