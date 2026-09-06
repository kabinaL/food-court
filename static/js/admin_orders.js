document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("orderSearch");
    const statusFilter = document.getElementById("statusFilter");
    const orderRows = document.querySelectorAll(".order-row");
    const noOrderResults = document.getElementById("noOrderResults");


    function filterOrders() {

        const searchText = searchInput
            ? searchInput.value.toLowerCase().trim()
            : "";

        const selectedStatus = statusFilter
            ? statusFilter.value.toLowerCase()
            : "all";


        let visibleCount = 0;


        orderRows.forEach(function (row) {

            const orderId = (
                row.dataset.orderId || ""
            ).toLowerCase();

            const customerName = (
                row.dataset.customer || ""
            ).toLowerCase();

            const orderStatus = (
                row.dataset.status || ""
            ).toLowerCase();


            const matchesSearch =
                orderId.includes(searchText) ||
                customerName.includes(searchText);


            const matchesStatus =
                selectedStatus === "all" ||
                orderStatus === selectedStatus;


            if (matchesSearch && matchesStatus) {

                row.style.display = "";

                visibleCount++;

            } else {

                row.style.display = "none";

            }

        });


        if (noOrderResults) {

            if (
                visibleCount === 0 &&
                orderRows.length > 0
            ) {

                noOrderResults.style.display = "block";

            } else {

                noOrderResults.style.display = "none";

            }

        }

    }


    if (searchInput) {

        searchInput.addEventListener(
            "input",
            filterOrders
        );

    }


    if (statusFilter) {

        statusFilter.addEventListener(
            "change",
            filterOrders
        );

    }

});