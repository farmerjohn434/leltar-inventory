const categories = {
            Laptop: {
                Lenovo: ["ThinkPad", "Yoga", "Legion"],
                HP: ["Pavilion", "EliteBook"],
                Dell: ["Inspiron", "XPS"]
            },
            Telefon: {
                Apple: ["iPhone 13", "iPhone SE"],
                Samsung: ["Galaxy S21", "A52"],
                Huawei: ["P40", "Mate 40"]
            },
            Monitor: {
                Samsung: ["U28E590D"],
                LG: ["UltraGear"],
                ASUS: ["VG248QG"]
            }
        };

        function updateBrandAndModel() {
            const category = document.getElementById("category").value;
            const brandSelect = document.getElementById("brand");
            const modelSelect = document.getElementById("model");

            brandSelect.innerHTML = "";
            modelSelect.innerHTML = "";

            const brands = Object.keys(categories[category]);
            brands.forEach(brand => {
                const option = document.createElement("option");
                option.value = brand;
                option.textContent = brand;
                brandSelect.appendChild(option);
            });

            updateModelList();
        }

        function updateModelList() {
            const category = document.getElementById("category").value;
            const brand = document.getElementById("brand").value;
            const modelSelect = document.getElementById("model");

            modelSelect.innerHTML = "";

            const models = categories[category][brand] || [];
            models.forEach(model => {
                const option = document.createElement("option");
                option.value = model;
                option.textContent = model;
                modelSelect.appendChild(option);
            });
        }

        function toggleDarkMode() {
            const body = document.body;
            body.classList.toggle("dark-mode");
            if (body.classList.contains("dark-mode")) {
                localStorage.setItem("darkMode", "enabled");
            } else {
                localStorage.setItem("darkMode", "disabled");
            }
        }

        if (localStorage.getItem("darkMode") === "enabled") {
            document.body.classList.add("dark-mode");
        }

        updateBrandAndModel();

        // Szűrés
        function filterTable() {
            const input = document.getElementById("searchInput");
            const filter = input.value.toLowerCase();
            const rows = document.querySelectorAll("#deviceTable tbody tr");

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? "" : "none";
            });
        }

        // Rendezés + nyilak
        document.querySelectorAll("#deviceTable th").forEach((header, index) => {
            let asc = true;
            header.addEventListener("click", () => {
                const table = header.closest("table");
                const rows = Array.from(table.querySelectorAll("tbody tr"));
                table.querySelectorAll("th").forEach(th => th.classList.remove("sorted-asc", "sorted-desc"));

                rows.sort((a, b) => {
                    const aText = a.children[index].textContent.trim().toLowerCase();
                    const bText = b.children[index].textContent.trim().toLowerCase();
                    return asc ? aText.localeCompare(bText) : bText.localeCompare(aText);
                });

                rows.forEach(row => table.querySelector("tbody").appendChild(row));
                header.classList.add(asc ? "sorted-asc" : "sorted-desc");
                asc = !asc;
            });
        });