(function () {
    const itemsBody = document.getElementById("items-body");
    const rowTemplate = document.getElementById("row-template");
    const addRowBtn = document.getElementById("add-row");

    function renumberRows() {
        [...itemsBody.querySelectorAll("tr")].forEach((tr, idx) => {
            tr.querySelector(".sr-cell").textContent = idx + 1;
        });
    }

    function recalcTotals() {
        let subtotal = 0;
        itemsBody.querySelectorAll("tr").forEach((tr) => {
            const qty = parseFloat(tr.querySelector(".qty-input").value) || 0;
            const price = parseFloat(tr.querySelector(".price-input").value) || 0;
            const total = qty * price;
            tr.querySelector(".row-total").textContent = total.toFixed(2);
            subtotal += total;
        });
        const freight = parseFloat(document.getElementById("freight_charges").value) || 0;
        const beforeTax = subtotal + freight;
        const taxType = document.getElementById("tax_type").value;
        const taxPercent = parseFloat(document.getElementById("tax_percent").value) || 0;
        let tax = 0;
        let taxLabel = "Tax";
        if (taxType === "CGST_SGST") {
            tax = beforeTax * taxPercent / 100;
            taxLabel = `CGST ${(taxPercent / 2).toFixed(1)}% + SGST ${(taxPercent / 2).toFixed(1)}%`;
        } else if (taxType === "IGST") {
            tax = beforeTax * taxPercent / 100;
            taxLabel = `IGST ${taxPercent.toFixed(1)}%`;
        } else {
            tax = 0;
            taxLabel = "No Tax";
        }
        const grand = taxType === "NONE" ? beforeTax : beforeTax + tax;

        document.getElementById("t-subtotal").textContent = subtotal.toFixed(2);
        document.getElementById("t-freight").textContent = freight.toFixed(2);
        document.getElementById("t-beforetax").textContent = beforeTax.toFixed(2);
        document.getElementById("t-taxlabel").textContent = taxLabel;
        document.getElementById("t-tax").textContent = tax.toFixed(2);
        document.getElementById("t-grand").textContent = grand.toFixed(2);
    }

    function wireRow(tr) {
        tr.querySelectorAll(".qty-input, .price-input").forEach((el) => {
            el.addEventListener("input", recalcTotals);
        });
        tr.querySelector(".remove-row").addEventListener("click", () => {
            tr.remove();
            renumberRows();
            recalcTotals();
        });

        const reqInput = tr.querySelector(".req-input");
        const suggestBox = tr.querySelector(".item-suggest");
        const sqlCodeInput = tr.querySelector(".sql-code-input");
        const sqlCodeDisplay = tr.querySelector(".sql-code-display");

        let debounceTimer;
        reqInput.addEventListener("input", () => {
            sqlCodeInput.value = "";
            sqlCodeDisplay.value = "";
            const q = reqInput.value.trim();
            clearTimeout(debounceTimer);
            if (q.length < 2) {
                suggestBox.style.display = "none";
                return;
            }
            debounceTimer = setTimeout(() => {
                fetch(`/api/items?q=${encodeURIComponent(q)}`)
                    .then((r) => r.json())
                    .then((results) => {
                        if (!results.length) {
                            suggestBox.style.display = "none";
                            return;
                        }
                        suggestBox.innerHTML = "";
                        results.forEach((item) => {
                            const div = document.createElement("div");
                            const priceHint = item.pcr_rate ? `PCR: ${item.pcr_rate}` : `Rate: ${item.rate}`;
                            div.textContent = `${item.item_code || "—"} · ${item.description} (${priceHint})`;
                            div.addEventListener("click", () => {
                                reqInput.value = item.description;
                                sqlCodeInput.value = item.item_code;
                                sqlCodeDisplay.value = item.item_code;
                                tr.querySelector(".unit-input").value = item.unit || "Nos.";
                                tr.querySelector(".price-input").value = item.suggested_price || 0;
                                suggestBox.style.display = "none";
                                recalcTotals();
                            });
                            suggestBox.appendChild(div);
                        });
                        suggestBox.style.display = "block";
                    });
            }, 250);
        });

        document.addEventListener("click", (e) => {
            if (!tr.contains(e.target)) suggestBox.style.display = "none";
        });
    }

    function addRow(data) {
        const node = rowTemplate.content.cloneNode(true);
        const tr = node.querySelector("tr");
        if (data) {
            tr.querySelector(".req-input").value = data.customer_requirement || "";
            tr.querySelector(".sql-code-input").value = data.sql_code || "";
            tr.querySelector(".sql-code-display").value = data.sql_code || "";
            tr.querySelector(".qty-input").value = data.qty != null ? data.qty : 1;
            tr.querySelector(".unit-input").value = data.unit || "Nos.";
            tr.querySelector(".price-input").value = data.unit_price != null ? data.unit_price : 0;
            tr.querySelector(".currency-input").value = data.currency || "INR";
        }
        itemsBody.appendChild(node);
        const addedRow = itemsBody.lastElementChild;
        wireRow(addedRow);
        renumberRows();
        recalcTotals();
    }

    addRowBtn.addEventListener("click", () => addRow());
    document.getElementById("freight_charges").addEventListener("input", recalcTotals);
    document.getElementById("tax_type").addEventListener("change", recalcTotals);
    document.getElementById("tax_percent").addEventListener("input", recalcTotals);

    // Load existing items (edit mode) or start with one blank row
    let existing = [];
    try {
        existing = JSON.parse(document.getElementById("existing-items-data").textContent || "[]");
    } catch (e) { existing = []; }

    if (existing.length) {
        existing.forEach((row) => addRow(row));
    } else {
        addRow();
    }

    // Customer autofill
    const customerSelect = document.getElementById("customer_id");
    customerSelect.addEventListener("change", () => {
        const opt = customerSelect.options[customerSelect.selectedIndex];
        if (!opt || !opt.value) return;
        const attnField = document.getElementById("kind_attention");
        const emailField = document.getElementById("cust_email");
        const gstField = document.getElementById("cust_gst");
        if (!attnField.value) attnField.value = opt.dataset.attention || "";
        if (!emailField.value) emailField.value = opt.dataset.email || "";
        if (!gstField.value) gstField.value = opt.dataset.gst || "";
    });
})();
