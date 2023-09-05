
// Function to populate the select with unique Beneficiaries from the table
function populateBeneficiarySelect() {
    var beneficiarySelect = document.getElementById('beneficiarySelect');
    var tableRows = document.querySelectorAll('.table-bordered tbody tr');
    var beneficiaries = new Set();

    // Get the unique Beneficiaries from the table
    tableRows.forEach(function (row) {
        var beneficiary = row.cells[2].textContent.trim(); // Assuming the Beneficiary is in the third column (index 2)
        beneficiaries.add(beneficiary);
    });

    // Sort the Beneficiaries in ascending order
    var sortedBeneficiaries = Array.from(beneficiaries).sort();

    // Populate the select with the unique Beneficiary options
    beneficiarySelect.innerHTML = '<option value="">Todos os Beneficiários</option>'; // Reset the select options
    sortedBeneficiaries.forEach(function (beneficiary) {
        var option = document.createElement("option");
        option.value = beneficiary;
        option.textContent = beneficiary;
        beneficiarySelect.appendChild(option);
    });
}

// Function to handle the Beneficiary filter
function handleBeneficiaryFilter() {
    filterTable();
}

// Function to populate the select with unique Codes from the table
function populateCodeSelect() {
    var codeSelect = document.getElementById('codeSelect');
    var tableRows = document.querySelectorAll('.table-bordered tbody tr');
    var codes = new Set();

    // Get the unique Codes from the table (excluding the last row)
    for (var i = 0; i < tableRows.length - 1; i++) {
        var row = tableRows[i];
        var code = row.cells[1].textContent.trim(); // Assuming the Code is in the second column (index 1)
        codes.add(code);
    }

    // Sort the Codes in ascending order
    var sortedCodes = Array.from(codes).sort();

    // Populate the select with the unique Code options
    codeSelect.innerHTML = '<option value="">Todos os Códigos</option>'; // Reset the select options
    sortedCodes.forEach(function (code) {
        var option = document.createElement("option");
        option.value = code;
        option.textContent = code;
        codeSelect.appendChild(option);
    });
}

// Function to handle the Code filter
function handleCodeFilter() {
    filterTable();
}

// Function to filter the table rows based on both Beneficiary and Code selections
function filterTable() {
    var selectedBeneficiary = document.getElementById('beneficiarySelect').value;
    var selectedCode = document.getElementById('codeSelect').value;
    var tableRows = document.querySelectorAll('.table-bordered tbody tr');
    var noDataMessageRow = document.getElementById('noDataMessageRow');

    var hasMatchingRows = false;

    tableRows.forEach(function (row) {
        var beneficiaryCell = row.cells[2].textContent.trim(); // Assuming the Beneficiary is in the third column (index 2)
        var codeCell = row.cells[1].textContent.trim(); // Assuming the Code is in the second column (index 1)
        var displayRow = true;


        if (selectedBeneficiary !== '' && beneficiaryCell !== selectedBeneficiary) {
            displayRow = false;
        }

        if (selectedCode !== '' && codeCell !== selectedCode) {
            displayRow = false;
        }

        row.style.display = displayRow ? 'table-row' : 'none';

        if (displayRow) {
            hasMatchingRows = true;
        }
    });

    // updateTotal();

    // Show or hide the "Nenhum dado encontrado" message row
    if (hasMatchingRows) {
        noDataMessageRow.style.display = 'none';
    } else {
        noDataMessageRow.style.display = 'block';
    }
}

// function updateTotal() {
//     var totalQtdPaga = 0;
//     var totalValor = 0;

//     var tableRows = document.querySelectorAll('.table-bordered tbody tr');

//     tableRows.forEach(function (row) {
//         if (row.style.display !== 'none') {
//             var qtdPagaCell = row.cells[3];
//             var valorCell = row.cells[4];

//             totalQtdPaga += parseFloat(qtdPagaCell.textContent);
//             totalValor += parseFloat(valorCell.textContent.replace('R$ ', '').replace(',', ''));
//         }
//     });

//     // Atualiza os valores na linha de Total
//     var totalQtdPagaCell = document.getElementById('totalQtdPaga');
//     var totalValorCell = document.getElementById('totalValor');

//     totalQtdPagaCell.textContent = totalQtdPaga.toFixed(0); // Mostra apenas o valor inteiro
//     totalValorCell.textContent = 'R$ ' + totalValor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });


//     // Mostra a linha de Total somente se houver linhas visíveis após o filtro
//     var totalRow = document.getElementById('totalRow');
//     totalRow.style.display = (totalQtdPaga > 0 || totalValor > 0) ? 'table-row' : 'none';
// }


document.addEventListener("DOMContentLoaded", function () {
    var beneficiarySelect = document.getElementById('beneficiarySelect');
    var codeSelect = document.getElementById('codeSelect');

    // Populate the Beneficiary and Code selects
    populateBeneficiarySelect();
    populateCodeSelect();

    // updateTotal();

    // Event listeners for both filters
    beneficiarySelect.addEventListener('change', function () {
        handleBeneficiaryFilter();
    });

    codeSelect.addEventListener('change', function () {
        handleCodeFilter();
    });
});

document.addEventListener("DOMContentLoaded", function () {
    var beneficiarySelect = document.getElementById('beneficiarySelect');
    var codeSelect = document.getElementById('codeSelect');

    // Populate the Beneficiary and Code selects
    populateBeneficiarySelect();
    populateCodeSelect();
    // updateTotal();

    // Set default value for the code select to "5000510"
    codeSelect.value = "5000510";

    // Event listeners for both filters
    beneficiarySelect.addEventListener('change', function () {
        handleBeneficiaryFilter();
    });

    codeSelect.addEventListener('change', function () {
        handleCodeFilter();
    });

    // Initial filtering to hide the "Nenhum dado encontrado" message row
    filterTable();
});
