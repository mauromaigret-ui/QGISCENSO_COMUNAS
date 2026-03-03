document.addEventListener('DOMContentLoaded', () => {
    const regionSelect = document.getElementById('regionSelect');
    const comunaSelect = document.getElementById('comunaSelect');
    const resultadosContainer = document.getElementById('resultadosContainer');
    const headerTitle = document.getElementById('headerTitle');
    const dataStatus = document.getElementById('dataStatus');
    const exportActions = document.getElementById('exportActions');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const btnExportExcel = document.getElementById('btnExportExcel');
    const btnExportWord = document.getElementById('btnExportWord');

    let currentComunaData = null;
    let exportPaths = null;
    const variablesContainer = document.getElementById('variablesContainer');

    // Helper: Formatear número con separador de miles
    const formatStr = (num) => {
        if (num === null || num === undefined) return '-';
        return Number(num).toLocaleString('de-DE'); // Formato de miles con punto
    };

    // Función para obtener variables seleccionadas
    const getSelectedVariables = () => {
        const checkboxes = variablesContainer.querySelectorAll('input[type="checkbox"]:checked');
        const selected = Array.from(checkboxes).map(cb => cb.value);
        return selected;
    };

    // Inicializar: Cargar Regiones y Variables
    Promise.all([
        fetch('/api/regiones').then(res => res.json()),
        fetch('/api/variables').then(res => res.json())
    ])
        .then(([regionesData, variablesData]) => {
            // Llenar Regiones
            regionSelect.innerHTML = '<option value="">-- Seleccionar Región --</option>';
            regionesData.regiones.forEach(r => {
                const opt = document.createElement('option');
                opt.value = r.id;
                opt.textContent = r.nombre;
                regionSelect.appendChild(opt);
            });

            // Llenar Variables
            variablesContainer.innerHTML = '';
            variablesData.variables.forEach(v => {
                const label = document.createElement('label');
                label.className = 'modern-checkbox';
                label.innerHTML = `<input type="checkbox" value="${v}" checked> <span>${v}</span>`;
                variablesContainer.appendChild(label);
            });

            // Agregar evento de cambio a los checkboxes para actualizar si hay comuna seleccionada
            variablesContainer.addEventListener('change', () => {
                if (comunaSelect.value) {
                    // Trigger comuna change to reload data
                    comunaSelect.dispatchEvent(new Event('change'));
                }
            });

        })
        .catch(err => console.error("Error inicializando:", err));

    // Evento: Al cambiar Región
    regionSelect.addEventListener('change', (e) => {
        const regionId = e.target.value;
        comunaSelect.innerHTML = '<option value="">-- Seleccionar Comuna --</option>';
        comunaSelect.disabled = true;

        exportActions.style.display = 'none';
        resetDashboard();

        if (regionId) {
            comunaSelect.innerHTML = '<option value="">Cargando comunas...</option>';
            fetch(`/api/comunas/${regionId}`)
                .then(res => res.json())
                .then(data => {
                    comunaSelect.innerHTML = '<option value="">-- Seleccionar Comuna --</option>';
                    data.comunas.forEach(c => {
                        const opt = document.createElement('option');
                        opt.value = c.id;
                        opt.textContent = c.nombre;
                        comunaSelect.appendChild(opt);
                    });
                    comunaSelect.disabled = false;
                })
                .catch(err => {
                    console.error("Error cargando comunas:", err);
                    comunaSelect.innerHTML = '<option value="">Error al cargar</option>';
                });
        }
    });

    // Evento: Al cambiar Comuna (Cargar datos principales)
    comunaSelect.addEventListener('change', async (e) => {
        const comunaId = e.target.value;
        if (!comunaId) {
            resetDashboard();
            exportActions.style.display = 'none';
            return;
        }

        const comunaName = comunaSelect.options[comunaSelect.selectedIndex].text;
        headerTitle.textContent = `Resultados Censo: ${comunaName}`;
        dataStatus.textContent = 'Calculando...';
        resultadosContainer.innerHTML = '<div class="empty-state"><div class="spinner"></div><p>Procesando reglas sobre bases de microdatos...</p></div>';
        exportActions.style.display = 'none';
        exportPaths = null;

        try {
            const payload_body = {
                variables_seleccionadas: getSelectedVariables()
            };

            const res = await fetch(`/api/datos_censo/${comunaId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload_body)
            });
            if (!res.ok) throw new Error('Error en API');
            const payload = await res.json();

            dataStatus.textContent = `Procesado instantáneo (${comunaName})`;
            renderTablas(payload.data);

            // Generate reports silently in background immediately after showing data 
            // This makes the "Download" buttons perfectly snappy later
            generateReportsBackground(comunaId, payload_body);
            exportActions.style.display = 'block';

        } catch (err) {
            console.error(err);
            dataStatus.textContent = 'Error fallido';
            resultadosContainer.innerHTML = `<div class="empty-state"><i class="uil uil-exclamation-triangle"></i><h3>Error cargando datos</h3><p>${err.message}</p></div>`;
        }
    });

    const resetDashboard = () => {
        headerTitle.textContent = 'Explorador del Censo';
        dataStatus.textContent = 'Esperando selección';
        resultadosContainer.innerHTML = `
            <div class="empty-state">
                <i class="uil uil-search-alt"></i>
                <h3>Selecciona un territorio</h3>
                <p>Utiliza el panel lateral para elegir una Región y Comuna y visualizar instantáneamente todos los resultados tabulados del Censo 2024.</p>
            </div>`;
    };

    const renderTablas = (data) => {
        resultadosContainer.innerHTML = '';

        let delay = 0;
        for (const [titulo, detalles] of Object.entries(data)) {
            const card = document.createElement('div');
            card.className = 'data-card';
            card.style.animationDelay = `${delay}s`;
            delay += 0.1;

            const header = document.createElement('div');
            header.className = 'data-card-header';
            header.innerHTML = `<h3>${titulo} <span style="font-weight:400;font-size:0.9rem;color:var(--text-muted)">(${formatStr(detalles.Denominador)} ${detalles.Unidad})</span></h3>`;
            card.appendChild(header);

            const tableWrap = document.createElement('div');
            tableWrap.className = 'table-responsive';

            // Build Table
            const table = document.createElement('table');
            const CategoriasDict = detalles.Categorias || {};

            // Extract columns from the first object
            const firstCatKey = Object.keys(CategoriasDict)[0];
            if (!firstCatKey) continue;
            const columns = ["Categoría", ...Object.keys(CategoriasDict[firstCatKey])];

            // Thead
            const thead = document.createElement('thead');
            const trHead = document.createElement('tr');
            columns.forEach(col => {
                const th = document.createElement('th');
                th.textContent = col;
                if (col !== 'Categoría') th.className = 'numeric';
                trHead.appendChild(th);
            });
            thead.appendChild(trHead);
            table.appendChild(thead);

            // Tbody
            const tbody = document.createElement('tbody');
            // Sort to ensure Total is at the bottom, and others are logically placed
            const keys = Object.keys(CategoriasDict).sort((a, b) => {
                if (a === "Total") return 1;
                if (b === "Total") return -1;
                return a.localeCompare(b);
            });

            keys.forEach(catName => {
                const tr = document.createElement('tr');
                if (catName === 'Total') tr.style.backgroundColor = 'rgba(255,255,255,0.03)';
                if (catName === 'Total') tr.style.fontWeight = 'bold';

                const tdCat = document.createElement('td');
                tdCat.textContent = catName;
                tr.appendChild(tdCat);

                const rowData = CategoriasDict[catName];
                columns.slice(1).forEach(col => {
                    const td = document.createElement('td');
                    td.className = 'numeric';
                    let val = rowData[col];

                    if (col === 'Porcentaje') {
                        const pctStr = val !== null ? `${val.toFixed(1)}%` : '-';
                        td.innerHTML = `${pctStr} <div class="percent-bar-container"><div class="percent-bar" style="width: ${val || 0}%"></div></div>`;
                    } else {
                        td.textContent = formatStr(val);
                    }
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });

            table.appendChild(tbody);
            tableWrap.appendChild(table);
            card.appendChild(tableWrap);
            resultadosContainer.appendChild(card);
        }
    };

    // Pre-generar reportes en background para ganar tiempo
    const generateReportsBackground = async (comunaId, payload_body) => {
        const statusBox = document.getElementById('exportStatus');
        statusBox.textContent = 'Preparando Archivos Exportables...';
        btnExportExcel.disabled = true;
        btnExportWord.disabled = true;

        try {
            const res = await fetch(`/api/exportar/${comunaId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload_body)
            });
            if (!res.ok) throw new Error("Error generando reportes");
            const payload = await res.json();
            exportPaths = payload; // save the paths
            statusBox.textContent = '¡Reportes listos para descargar!';
            statusBox.dataset.ready = 'true';
            btnExportExcel.disabled = false;
            btnExportWord.disabled = false;
        } catch (err) {
            console.error(err);
            statusBox.textContent = 'Ocurrió un error preparando exportaciones.';
        }
    };

    // Export Buttons Logic
    const triggerDownload = (url) => {
        if (!url) return;
        const a = document.createElement('a');
        a.href = url;
        a.download = url.split('/').pop();
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    };

    btnExportExcel.addEventListener('click', () => {
        if (exportPaths && exportPaths.excel_url) {
            triggerDownload(exportPaths.excel_url);
        }
    });

    btnExportWord.addEventListener('click', () => {
        if (exportPaths && exportPaths.word_url) {
            triggerDownload(exportPaths.word_url);
        }
    });
});
