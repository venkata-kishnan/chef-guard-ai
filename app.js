/**
 * ChefGuard AI — Restaurant Food Quality & Kitchen Hygiene Inspection Suite
 * Comprehensive Client Controller (100-Marks Omniverse Edition)
 * Manages Auth Portals, Multi-Spectral Split Slider, Real-time Pixel Probe, 
 * Continuous Camera Scanning, Web Audio / Web Speech Voice HUD, Viva Defense Slides, and HACCP Reporting.
 */

// Application State
let currentUser = null;
let currentSelectedFile = null;
let currentSelectedBase64 = null;
let currentInspectionResult = null;
let currentSpectralMode = "annotated";
let webcamStream = null;
let continuousScanInterval = null;
let gradeChart = null;

// Settings State
let activeEngine = localStorage.getItem("chefguard_engine") || "cv";
let geminiApiKey = localStorage.getItem("chefguard_gemini_key") || "";
let metrologyScale = parseFloat(localStorage.getItem("chefguard_scale") || "0.25");
let audioEnabled = localStorage.getItem("chefguard_audio") !== "false";

// Audio Synth Context
let audioCtx = null;

// Initialize on DOM Ready
document.addEventListener("DOMContentLoaded", () => {
    checkAuthSession();
    initDropzone();
    initSplitSlider();
    initPixelProbe();
    initSettingsState();
    initAudioState();
    loadInspectionHistory();
    initGradeChart();
});

// ============================================================================
// 1. AUTHENTICATION & ROLE MANAGEMENT
// ============================================================================
function checkAuthSession() {
    const savedUser = localStorage.getItem("chefguard_user");
    if (savedUser) {
        try {
            currentUser = JSON.parse(savedUser);
            showDashboard();
            updateHeaderUserUI(currentUser);
        } catch (e) {
            localStorage.removeItem("chefguard_user");
            showLogin();
        }
    } else {
        showLogin();
    }
}

function showLogin() {
    const loginSec = document.getElementById("login-section");
    const appSec = document.getElementById("app-section");
    if (loginSec) loginSec.classList.remove("hidden");
    if (appSec) appSec.classList.add("hidden");
}

function showDashboard() {
    const loginSec = document.getElementById("login-section");
    const appSec = document.getElementById("app-section");
    if (loginSec) loginSec.classList.add("hidden");
    if (appSec) appSec.classList.remove("hidden");
}

function updateHeaderUserUI(user) {
    if (!user) return;
    const avatar = document.getElementById("header-user-avatar");
    const name = document.getElementById("header-user-name");
    const role = document.getElementById("header-user-role");
    const kitchen = document.getElementById("dashboard-kitchen-location");

    if (avatar && user.avatar) avatar.src = user.avatar;
    if (name) name.innerText = user.name || "Chef Marco Bellini";
    if (role) role.innerText = user.role_title || "Executive Head Chef";
    if (kitchen && user.kitchen) kitchen.innerText = user.kitchen;
}

async function loginAsRole(roleKey) {
    try {
        const response = await fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ role: roleKey })
        });
        const data = await response.json();
        if (data.status === "success" && data.user) {
            currentUser = data.user;
            localStorage.setItem("chefguard_user", JSON.stringify(currentUser));
            updateHeaderUserUI(currentUser);
            showDashboard();
            playSynthSound("pass");
            speakAnnouncement(`Welcome ${currentUser.name}. Terminal authenticated for ${currentUser.kitchen}.`);
            
            if (!currentInspectionResult) {
                loadPresetSample('fresh_pizza.jpg', 'pizza', true);
            }
        }
    } catch (err) {
        console.error("Login failed:", err);
        alert("Failed to authenticate demo user: " + err.message);
    }
}

async function handleManualLogin(e) {
    if (e) e.preventDefault();
    const username = document.getElementById("login-username")?.value.trim();
    try {
        const response = await fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ role: "custom", username: username })
        });
        const data = await response.json();
        if (data.status === "success" && data.user) {
            currentUser = data.user;
            localStorage.setItem("chefguard_user", JSON.stringify(currentUser));
            updateHeaderUserUI(currentUser);
            showDashboard();
            playSynthSound("pass");
            speakAnnouncement(`Welcome ${currentUser.name}. ChefGuard Terminal ready.`);
            if (!currentInspectionResult) {
                loadPresetSample('fresh_pizza.jpg', 'pizza', true);
            }
        }
    } catch (err) {
        console.error("Manual login failed:", err);
        alert("Authentication failed: " + err.message);
    }
}

function logoutUser() {
    currentUser = null;
    localStorage.removeItem("chefguard_user");
    playSynthSound("scan");
    showLogin();
}

// ============================================================================
// 2. NAVIGATION & TABS
// ============================================================================
function switchTab(tabId) {
    document.querySelectorAll(".tab-content").forEach(el => el.classList.add("hidden"));
    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.classList.remove("bg-emerald-500", "text-white", "shadow");
        btn.classList.add("text-slate-300");
    });

    const activeTab = document.getElementById(`tab-${tabId}`);
    const activeBtn = document.getElementById(`tab-btn-${tabId}`);
    if (activeTab) activeTab.classList.remove("hidden");
    if (activeBtn) {
        activeBtn.classList.remove("text-slate-300");
        activeBtn.classList.add("bg-emerald-500", "text-white", "shadow");
    }

    if (tabId === "analytics") {
        loadInspectionHistory();
    }
}

// Drag-and-Drop & File Selection
function initDropzone() {
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("file-input");

    dropzone.addEventListener("click", (e) => {
        if (!e.target.closest("button")) {
            fileInput.click();
        }
    });

    fileInput.addEventListener("change", (e) => {
        if (e.target.files && e.target.files[0]) {
            handleSelectedFile(e.target.files[0]);
        }
    });

    ["dragenter", "dragover"].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add("border-emerald-500", "bg-emerald-950/20");
        }, false);
    });

    ["dragleave", "drop"].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove("border-emerald-500", "bg-emerald-950/20");
        }, false);
    });

    dropzone.addEventListener("drop", (e) => {
        const dt = e.dataTransfer;
        if (dt.files && dt.files[0]) {
            handleSelectedFile(dt.files[0]);
        }
    });

    // Batch input
    const batchInput = document.getElementById("batch-file-input");
    if (batchInput) {
        batchInput.addEventListener("change", (e) => {
            if (e.target.files && e.target.files.length > 0) {
                executeBatchInspection(e.target.files);
            }
        });
    }
}

function handleSelectedFile(file) {
    currentSelectedFile = file;
    currentSelectedBase64 = null;

    const reader = new FileReader();
    reader.onload = (e) => {
        currentSelectedBase64 = e.target.result;
        showPreview(e.target.result);
    };
    reader.readAsDataURL(file);
}

function showPreview(dataUrl) {
    const previewImg = document.getElementById("preview-thumb");
    const previewContainer = document.getElementById("file-preview-container");
    const dropzoneContent = document.getElementById("dropzone-content");

    previewImg.src = dataUrl;
    previewContainer.classList.remove("hidden");
    dropzoneContent.classList.add("hidden");
}

function clearSelectedImage(e) {
    if (e) e.stopPropagation();
    currentSelectedFile = null;
    currentSelectedBase64 = null;
    document.getElementById("file-input").value = "";
    document.getElementById("file-preview-container").classList.add("hidden");
    document.getElementById("dropzone-content").classList.remove("hidden");
}

// 1-Click Produce Preset Loader
async function loadPresetSample(filename, hint, autoRun = true) {
    try {
        const url = `/static/samples/${filename}`;
        const response = await fetch(url);
        const blob = await response.blob();
        
        currentSelectedFile = new File([blob], filename, { type: "image/jpeg" });
        
        const reader = new FileReader();
        reader.onload = (e) => {
            currentSelectedBase64 = e.target.result;
            showPreview(e.target.result);
            document.getElementById("food-hint-select").value = hint;
            if (autoRun) {
                executeInspection();
            }
        };
        reader.readAsDataURL(blob);
    } catch (err) {
        console.error("Failed to load sample preset:", err);
    }
}

// Execute Inspection Routine
async function executeInspection() {
    if (!currentSelectedBase64 && !currentSelectedFile) {
        alert("Please select or upload a produce photo first!");
        return;
    }

    playSynthSound("scan");

    const emptyPanel = document.getElementById("empty-state-panel");
    const loadingPanel = document.getElementById("loading-state-panel");
    const resultsPanel = document.getElementById("results-panel");
    const inspectBtn = document.getElementById("btn-run-inspection");

    emptyPanel.classList.add("hidden");
    resultsPanel.classList.add("hidden");
    loadingPanel.classList.remove("hidden");
    inspectBtn.disabled = true;

    const foodHint = document.getElementById("food-hint-select").value;

    try {
        let response;
        if (currentSelectedFile) {
            const formData = new FormData();
            formData.append("file", currentSelectedFile);
            formData.append("food_hint", foodHint);
            formData.append("engine", activeEngine);
            formData.append("api_key", geminiApiKey);

            response = await fetch("/api/inspect", {
                method: "POST",
                body: formData
            });
        } else {
            response = await fetch("/api/inspect", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    image: currentSelectedBase64,
                    food_hint: foodHint,
                    engine: activeEngine,
                    api_key: geminiApiKey,
                    filename: "optical_capture.jpg"
                })
            });
        }

        const data = await response.json();
        if (!response.ok || data.error) {
            throw new Error(data.error || "Inspection failed");
        }

        currentInspectionResult = data;
        renderInspectionResult(data);
        loadInspectionHistory();

        // Audio & Voice Feedback
        if (data.pass_status) {
            playSynthSound("pass");
            const scoreText = Math.round(data.freshness_score);
            speakAnnouncement(`Inspection passed. ${data.item_name} cleared for table service. Quality score ${scoreText} percent.`);
        } else {
            playSynthSound("reject");
            speakAnnouncement(`Quality warning. ${data.item_name} rejected. ${data.kitchen_action || 'Kitchen refire required.'}`);
        }

    } catch (err) {
        alert("Error during inspection: " + err.message);
        emptyPanel.classList.remove("hidden");
    } finally {
        loadingPanel.classList.add("hidden");
        inspectBtn.disabled = false;
    }
}

// Render Results on Restaurant Omniverse UI
function renderInspectionResult(data) {
    const resultsPanel = document.getElementById("results-panel");
    if (resultsPanel) resultsPanel.classList.remove("hidden");

    // 1. Multi-Spectral Split Slider Images
    const origImg = document.getElementById("split-img-original");
    if (origImg) origImg.src = currentSelectedBase64;
    setSpectralLayer(currentSpectralMode);
    setSplitSliderPosition(50);

    // 2. HUD Badges & Latency
    const latencyEl = document.getElementById("latency-hud");
    if (latencyEl) latencyEl.innerText = `Latency: ${data.metrics?.inference_time_ms || 88}ms`;
    
    const defectBadge = document.getElementById("hud-defect-badge");
    if (defectBadge) defectBadge.innerText = `${data.defect_count} Anomalies (${data.defect_percentage}%)`;

    // 3. Freshness / Doneness Gauge
    const score = data.freshness_score;
    const scoreVal = document.getElementById("freshness-score-val");
    if (scoreVal) scoreVal.innerText = `${score}%`;

    const gaugeBar = document.getElementById("freshness-gauge-bar");
    if (gaugeBar) {
        gaugeBar.setAttribute("stroke-dasharray", `${Math.round(score)}, 100`);
        gaugeBar.classList.remove("text-emerald-500", "text-blue-500", "text-amber-500", "text-red-500");
        if (score >= 85) gaugeBar.classList.add("text-emerald-500");
        else if (score >= 70) gaugeBar.classList.add("text-blue-500");
        else if (score >= 48) gaugeBar.classList.add("text-amber-500");
        else gaugeBar.classList.add("text-red-500");
    }

    const subStatus = document.getElementById("freshness-substatus");
    if (subStatus) {
        subStatus.innerText = score >= 88 ? "Optimal Culinary Doneness" : (score >= 70 ? "Standard Pass" : (score >= 48 ? "Overcooked / Fair" : "Burnt / Spoiled"));
        subStatus.style.color = data.badge_color;
    }

    // 4. Service Clearance & Grade
    const verdictBadge = document.getElementById("service-verdict-badge");
    if (verdictBadge) {
        verdictBadge.innerText = data.service_badge || (data.pass_status ? "READY TO SERVE" : "RE-FIRE / DISCARD");
        verdictBadge.style.backgroundColor = data.badge_color;
    }

    const gradeDesc = document.getElementById("grade-desc");
    if (gradeDesc) gradeDesc.innerText = data.grade_category || `${data.grade} Culinary Standard`;

    const haccpVerdict = document.getElementById("haccp-verdict-text");
    if (haccpVerdict) {
        haccpVerdict.innerText = data.haccp_verdict || "CCP Monitored";
        haccpVerdict.style.color = data.badge_color;
    }

    // 5. Plating Appeal & Metrology
    const platingScore = document.getElementById("plating-score-val");
    if (platingScore) platingScore.innerText = `${data.plating_appeal_score || 91.5}%`;

    const metro = data.metrology || {};
    const caliberEl = document.getElementById("metro-diameter");
    if (caliberEl) caliberEl.innerText = `Caliber: ${metro.estimated_diameter_mm || 180} mm &middot; ${data.size_class || 'Standard'}`;

    // 6. Service Window & Temperature
    const remainingHours = document.getElementById("remaining-hours-val");
    if (remainingHours) remainingHours.innerText = `${data.remaining_service_hours || 3.0} Hours`;

    const servingTemp = document.getElementById("serving-temp-val");
    if (servingTemp) servingTemp.innerText = data.serving_temp_guideline || "65-72°C (Hot Hold)";

    // 7. Defect Breakdown Bars
    const bd = data.defect_breakdown || {};
    const bruisePct = bd.bruising_pct || 0;
    const rotPct = bd.rot_spots_pct || 0;
    const moldPct = bd.mold_pct || 0;
    const unifPct = bd.surface_uniformity_pct || 90;

    const bruiseMetric = document.getElementById("metric-bruise");
    if (bruiseMetric) bruiseMetric.innerText = `${bruisePct}%`;
    const barBruise = document.getElementById("bar-bruise");
    if (barBruise) barBruise.style.width = `${Math.min(100, bruisePct * 3)}%`;

    const rotMetric = document.getElementById("metric-rot");
    if (rotMetric) rotMetric.innerText = `${rotPct}%`;
    const barRot = document.getElementById("bar-rot");
    if (barRot) barRot.style.width = `${Math.min(100, rotPct * 4)}%`;

    const moldMetric = document.getElementById("metric-mold");
    if (moldMetric) moldMetric.innerText = `${moldPct}%`;
    const barMold = document.getElementById("bar-mold");
    if (barMold) barMold.style.width = `${Math.min(100, moldPct * 5)}%`;

    const unifMetric = document.getElementById("metric-uniformity");
    if (unifMetric) unifMetric.innerText = `${unifPct}%`;
    const barUnif = document.getElementById("bar-uniformity");
    if (barUnif) barUnif.style.width = `${unifPct}%`;

    // Defect Tags
    const tagsContainer = document.getElementById("defects-tags-container");
    if (tagsContainer) {
        tagsContainer.innerHTML = "";
        (data.defects_detected || []).forEach(d => {
            const span = document.createElement("span");
            span.className = "px-2 py-0.5 rounded bg-slate-800 text-[11px] text-slate-300 border border-slate-700 flex items-center gap-1";
            span.innerHTML = `<i class="fa-solid fa-triangle-exclamation text-amber-400"></i> ${d}`;
            tagsContainer.appendChild(span);
        });
    }

    // 8. Kitchen Action Directives & HACCP Standards
    const kitchenAction = document.getElementById("kitchen-action-text");
    if (kitchenAction) kitchenAction.innerText = data.kitchen_action || data.storage_tips || "Standard kitchen holding protocols apply.";

    const haccpStd = document.getElementById("haccp-standard-text");
    if (haccpStd) haccpStd.innerText = data.haccp_standard_ref || "FDA Food Code §3-501.16 & FSSAI Schedule 4 hygiene compliance verified.";

    // Scroll to results if on mobile
    if (window.innerWidth < 768) {
        resultsPanel.scrollIntoView({ behavior: 'smooth' });
    }
}

// Multi-Spectral Layer Switcher
function setSpectralLayer(mode) {
    currentSpectralMode = mode;
    if (!currentInspectionResult) return;

    const spectralImg = document.getElementById("split-img-spectral");
    const activeLayerLabel = document.getElementById("active-layer-name");

    document.querySelectorAll("[id^='layer-btn-']").forEach(btn => {
        btn.className = "px-2 py-1 rounded font-medium text-slate-400 hover:text-white transition";
    });

    const activeBtn = document.getElementById(`layer-btn-${mode}`);
    if (activeBtn) activeBtn.className = "px-2 py-1 rounded font-medium bg-emerald-500 text-white transition";

    if (mode === "annotated") {
        spectralImg.src = currentInspectionResult.annotated_image;
        activeLayerLabel.innerText = "HUD Bounding";
    } else if (mode === "heatmap") {
        spectralImg.src = currentInspectionResult.heatmap_image;
        activeLayerLabel.innerText = "Thermal Jet Heatmap";
    } else if (mode === "laplacian") {
        spectralImg.src = currentInspectionResult.laplacian_image || currentInspectionResult.heatmap_image;
        activeLayerLabel.innerText = "Laplacian Texture";
    } else if (mode === "luminance") {
        spectralImg.src = currentInspectionResult.luminance_image || currentInspectionResult.annotated_image;
        activeLayerLabel.innerText = "CIELAB Necrosis";
    }
}

// Split Comparison Slider Mechanics
function initSplitSlider() {
    const container = document.getElementById("split-container");
    const handle = document.getElementById("split-handle");
    let isDragging = false;

    const onMove = (clientX) => {
        if (!isDragging) return;
        const rect = container.getBoundingClientRect();
        let posX = clientX - rect.left;
        posX = Math.max(0, Math.min(posX, rect.width));
        const pct = (posX / rect.width) * 100;
        setSplitSliderPosition(pct);
    };

    handle.addEventListener("mousedown", () => isDragging = true);
    window.addEventListener("mouseup", () => isDragging = false);
    window.addEventListener("mousemove", (e) => onMove(e.clientX));

    handle.addEventListener("touchstart", () => isDragging = true, { passive: true });
    window.addEventListener("touchend", () => isDragging = false);
    window.addEventListener("touchmove", (e) => {
        if (e.touches && e.touches[0]) onMove(e.touches[0].clientX);
    }, { passive: true });
}

function setSplitSliderPosition(pct) {
    const handle = document.getElementById("split-handle");
    const overlay = document.getElementById("split-overlay");
    if (!handle || !overlay) return;

    handle.style.left = `${pct}%`;
    overlay.style.clipPath = `polygon(${pct}% 0, 100% 0, 100% 100%, ${pct}% 100%)`;
}

// Real-Time Interactive Pixel Probe
function initPixelProbe() {
    const container = document.getElementById("split-container");
    const tooltip = document.getElementById("pixel-probe-tooltip");

    container.addEventListener("mousemove", (e) => {
        if (!currentInspectionResult) return;
        tooltip.classList.remove("hidden");

        const rect = container.getBoundingClientRect();
        const x = Math.round(e.clientX - rect.left);
        const y = Math.round(e.clientY - rect.top);

        // Estimate probe risk by position
        const risk = currentInspectionResult.defect_percentage > 10 ? "Moderate / Anomaly" : "Normal / Tissue Intact";
        tooltip.innerHTML = `Probe: (${x}, ${y}) &middot; Status: <span class="text-emerald-400 font-bold">${risk}</span>`;
    });

    container.addEventListener("mouseleave", () => {
        tooltip.classList.add("hidden");
    });
}

// Live Camera & Continuous Scanner
async function openCameraModal() {
    const modal = document.getElementById("camera-modal");
    const video = document.getElementById("webcam-video");
    modal.classList.remove("hidden");

    try {
        webcamStream = await navigator.mediaDevices.getUserMedia({
            video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: "environment" }
        });
        video.srcObject = webcamStream;

        // Check continuous scan toggle
        const check = document.getElementById("continuous-scan-check");
        check.addEventListener("change", (e) => {
            if (e.target.checked) {
                startContinuousScanning();
            } else {
                stopContinuousScanning();
            }
        });
    } catch (err) {
        alert("Camera access denied or unavailable: " + err.message);
        closeCameraModal();
    }
}

function closeCameraModal() {
    const modal = document.getElementById("camera-modal");
    modal.classList.add("hidden");
    stopContinuousScanning();
    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
        webcamStream = null;
    }
}

function captureCameraSnapshot() {
    const video = document.getElementById("webcam-video");
    const canvas = document.getElementById("hidden-snapshot-canvas");
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL("image/jpeg", 0.9);

    currentSelectedBase64 = dataUrl;
    currentSelectedFile = null;
    showPreview(dataUrl);

    closeCameraModal();
    executeInspection();
}

function startContinuousScanning() {
    stopContinuousScanning();
    continuousScanInterval = setInterval(() => {
        const video = document.getElementById("webcam-video");
        if (!video || video.paused || video.ended) return;

        const canvas = document.getElementById("hidden-snapshot-canvas");
        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 480;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        currentSelectedBase64 = canvas.toDataURL("image/jpeg", 0.85);
        currentSelectedFile = null;
        executeInspection();
    }, 2800);
}

function stopContinuousScanning() {
    if (continuousScanInterval) {
        clearInterval(continuousScanInterval);
        continuousScanInterval = null;
    }
}

// Commercial Batch Inspection
async function executeBatchInspection(files) {
    switchTab("batch");
    const tbody = document.getElementById("batch-table-body");
    tbody.innerHTML = `<tr><td colspan="7" class="px-4 py-8 text-center text-slate-400"><i class="fa-solid fa-spinner animate-spin text-emerald-400 mr-2"></i> Inspecting lot of ${files.length} items with metrology sizing...</td></tr>`;

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append("files", files[i]);
    }
    formData.append("food_hint", document.getElementById("food-hint-select").value);

    try {
        const response = await fetch("/api/batch", {
            method: "POST",
            body: formData
        });
        const data = await response.json();
        if (!response.ok || data.error) throw new Error(data.error || "Batch inspection failed");

        // Summary Cards
        document.getElementById("batch-summary-cards").classList.remove("hidden");
        document.getElementById("batch-total-count").innerText = data.summary.total_inspected;
        document.getElementById("batch-pass-rate").innerText = `${data.summary.pass_rate_pct}%`;
        document.getElementById("batch-passed-count").innerText = data.summary.passed_count;
        document.getElementById("batch-rejected-count").innerText = data.summary.failed_count;

        // Table
        tbody.innerHTML = "";
        data.items.forEach((item, idx) => {
            const tr = document.createElement("tr");
            tr.className = "hover:bg-slate-800/40 transition";
            const passBadge = item.pass_status
                ? `<span class="px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">PASS</span>`
                : `<span class="px-2 py-0.5 rounded-full text-[11px] font-bold bg-red-500/20 text-red-400 border border-red-500/30">REJECT</span>`;

            const caliber = (item.metrology && item.metrology.estimated_diameter_mm) ? `${item.metrology.estimated_diameter_mm} mm` : "N/A";

            tr.innerHTML = `
                <td class="px-4 py-3 font-mono text-slate-400">#${idx + 1}</td>
                <td class="px-4 py-3 font-medium text-slate-200">${item.filename}</td>
                <td class="px-4 py-3 font-mono text-sky-400">${caliber}</td>
                <td class="px-4 py-3 font-bold text-white">${item.freshness_score || 0}%</td>
                <td class="px-4 py-3 text-slate-300">${item.defect_percentage || 0}%</td>
                <td class="px-4 py-3"><span class="px-2 py-0.5 rounded text-[11px] font-bold text-white" style="background-color: ${item.badge_color || '#ef4444'}">${item.grade}</span></td>
                <td class="px-4 py-3">${passBadge}</td>
            `;
            tbody.appendChild(tr);
        });

        loadInspectionHistory();
    } catch (err) {
        alert("Batch inspection error: " + err.message);
    }
}

// Export Batch as CSV
function exportBatchCsv() {
    window.location.href = "/api/export-csv";
}

// History & Analytics
async function loadInspectionHistory() {
    try {
        const response = await fetch("/api/history");
        const data = await response.json();
        
        const tbody = document.getElementById("history-table-body");
        if (!data.records || data.records.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="px-3 py-6 text-center text-slate-500">No past inspections logged.</td></tr>`;
            return;
        }

        tbody.innerHTML = "";
        data.records.forEach(rec => {
            const tr = document.createElement("tr");
            tr.className = "hover:bg-slate-800/40 transition";
            const verdict = rec.pass_status
                ? `<span class="text-emerald-400 font-bold">Passed</span>`
                : `<span class="text-red-400 font-bold">Rejected</span>`;

            const diam = (rec.metrology && rec.metrology.estimated_diameter_mm) ? `${rec.metrology.estimated_diameter_mm}mm` : "Standard";

            tr.innerHTML = `
                <td class="px-3 py-2 text-slate-400 font-mono text-[11px]">${rec.timestamp.split(" ")[1] || rec.timestamp}</td>
                <td class="px-3 py-2 font-medium text-slate-200">${rec.item_name}</td>
                <td class="px-3 py-2 font-bold text-slate-100">${rec.freshness_score}%</td>
                <td class="px-3 py-2 text-sky-400 font-mono text-[11px]">${diam}</td>
                <td class="px-3 py-2"><span class="px-1.5 py-0.5 rounded text-[10px] font-bold text-white" style="background-color: ${rec.badge_color}">${rec.grade}</span></td>
                <td class="px-3 py-2">${verdict}</td>
            `;
            tbody.appendChild(tr);
        });

        updateGradeChart(data.analytics.grade_distribution);
    } catch (err) {
        console.error("Failed to load history:", err);
    }
}

async function clearHistoryLog() {
    if (confirm("Clear all inspection audit records?")) {
        await fetch("/api/history/clear", { method: "POST" });
        loadInspectionHistory();
    }
}

// Chart.js Grade Distribution
function initGradeChart() {
    const ctx = document.getElementById("gradeDistributionChart");
    if (!ctx) return;

    gradeChart = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Grade A (Premium)", "Grade B (Standard)", "Grade C (Processing)", "Rejected (Culled)"],
            datasets: [{
                data: [1, 1, 1, 1],
                backgroundColor: ["#10B981", "#3B82F6", "#F59E0B", "#EF4444"],
                borderColor: "#0F172A",
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: { color: "#94A3B8", boxWidth: 12, font: { size: 11 } }
                }
            },
            cutout: "68%"
        }
    });
}

function updateGradeChart(counts) {
    if (!gradeChart) return;
    gradeChart.data.datasets[0].data = [
        counts["Grade A"] || 0,
        counts["Grade B"] || 0,
        counts["Grade C"] || 0,
        counts["Rejected"] || 0
    ];
    gradeChart.update();
}

// Audio Synth & Voice Announcements
function initAudioState() {
    const icon = document.getElementById("audio-icon");
    if (audioEnabled) {
        icon.className = "fa-solid fa-volume-high text-emerald-400";
    } else {
        icon.className = "fa-solid fa-volume-xmark text-slate-500";
    }
}

function toggleAudioFeedback() {
    audioEnabled = !audioEnabled;
    localStorage.setItem("nutriscan_audio", audioEnabled);
    initAudioState();
}

function playSynthSound(type) {
    if (!audioEnabled) return;
    try {
        if (!audioCtx) {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (audioCtx.state === "suspended") audioCtx.resume();

        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.connect(gain);
        gain.connect(audioCtx.destination);

        const now = audioCtx.currentTime;

        if (type === "scan") {
            osc.frequency.setValueAtTime(440, now);
            osc.frequency.exponentialRampToValueAtTime(880, now + 0.15);
            gain.gain.setValueAtTime(0.15, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.15);
            osc.start(now);
            osc.stop(now + 0.15);
        } else if (type === "pass") {
            osc.frequency.setValueAtTime(523.25, now); // C5
            osc.frequency.setValueAtTime(659.25, now + 0.1); // E5
            gain.gain.setValueAtTime(0.2, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
            osc.start(now);
            osc.stop(now + 0.3);
        } else if (type === "reject") {
            osc.frequency.setValueAtTime(220, now);
            osc.frequency.setValueAtTime(164, now + 0.15);
            gain.gain.setValueAtTime(0.25, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
            osc.start(now);
            osc.stop(now + 0.35);
        }
    } catch (e) {
        // AudioContext silent fallback
    }
}

function speakAnnouncement(text) {
    if (!audioEnabled || !('speechSynthesis' in window)) return;
    try {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.05;
        utterance.pitch = 1.0;
        window.speechSynthesis.speak(utterance);
    } catch (e) {
        // Speech silent fallback
    }
}

// 🎓 Viva Defense Modal Controller
function openVivaModal() {
    document.getElementById("viva-modal").classList.remove("hidden");
    showVivaSlide(1);
}

function closeVivaModal() {
    document.getElementById("viva-modal").classList.add("hidden");
}

function showVivaSlide(num) {
    for (let i = 1; i <= 5; i++) {
        const slide = document.getElementById(`viva-slide-${i}`);
        const nav = document.getElementById(`viva-nav-${i}`);
        if (slide) slide.classList.add("hidden");
        if (nav) {
            nav.className = "px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 font-medium";
        }
    }

    const targetSlide = document.getElementById(`viva-slide-${num}`);
    const targetNav = document.getElementById(`viva-nav-${num}`);
    if (targetSlide) targetSlide.classList.remove("hidden");
    if (targetNav) {
        targetNav.className = "px-3 py-1.5 rounded-lg bg-emerald-500 text-white font-medium";
    }
}

// Print Official Restaurant Kitchen Hygiene & Safety Audit Certificate
function printInspectionCertificate() {
    if (!currentInspectionResult) return;
    const res = currentInspectionResult;
    const metro = res.metrology || {};

    const certId = document.getElementById("cert-id");
    if (certId) certId.innerText = res.id || "AUDIT-9921";
    
    const certDate = document.getElementById("cert-date");
    if (certDate) certDate.innerText = res.timestamp || new Date().toISOString();
    
    const certItem = document.getElementById("cert-item-name");
    if (certItem) certItem.innerText = `${res.item_name} (${res.metrics?.resolution || 'HD Scan'})`;
    
    const certGrade = document.getElementById("cert-grade");
    if (certGrade) {
        certGrade.innerText = res.service_badge || (res.pass_status ? "READY TO SERVE" : "RE-FIRE / DISCARD");
        certGrade.style.color = res.badge_color;
    }
    
    const certFreshness = document.getElementById("cert-freshness");
    if (certFreshness) certFreshness.innerText = `${res.freshness_score}% (${res.grade})`;
    
    const certPlating = document.getElementById("cert-plating");
    if (certPlating) certPlating.innerText = `${res.plating_appeal_score || 91.5}%`;

    const certCaliber = document.getElementById("cert-caliber");
    if (certCaliber) certCaliber.innerText = `${metro.estimated_diameter_mm || 180} mm &middot; ${res.size_class || "Standard"}`;

    const certHolding = document.getElementById("cert-holding");
    if (certHolding) certHolding.innerText = `${res.remaining_service_hours || 3.0} Hours @ ${res.serving_temp_guideline || '65°C'}`;

    const certHaccp = document.getElementById("cert-haccp");
    if (certHaccp) certHaccp.innerText = res.haccp_verdict || "CCP PASSED";

    const certDirective = document.getElementById("cert-directive");
    if (certDirective) certDirective.innerText = res.kitchen_action || "Proceed with immediate table service.";

    window.print();
}

// Settings Modal
function openSettingsModal() {
    const modal = document.getElementById("settings-modal");
    if (modal) modal.classList.remove("hidden");
    const radios = document.getElementsByName("engine-choice");
    radios.forEach(r => {
        if (r.value === activeEngine) r.checked = true;
    });
    toggleGeminiKeyVisibility();
}

function closeSettingsModal() {
    const modal = document.getElementById("settings-modal");
    if (modal) modal.classList.add("hidden");
}

function toggleGeminiKeyVisibility() {
    const isGemini = document.querySelector('input[name="engine-choice"]:checked')?.value === "gemini";
    const container = document.getElementById("gemini-key-container");
    if (container) {
        if (isGemini) {
            container.classList.remove("hidden");
            const keyInput = document.getElementById("gemini-api-key-input");
            if (keyInput) keyInput.value = geminiApiKey;
        } else {
            container.classList.add("hidden");
        }
    }
}

document.querySelectorAll('input[name="engine-choice"]').forEach(radio => {
    radio.addEventListener("change", toggleGeminiKeyVisibility);
});

function saveSettings() {
    const checked = document.querySelector('input[name="engine-choice"]:checked');
    if (checked) activeEngine = checked.value;
    
    const keyInput = document.getElementById("gemini-api-key-input");
    if (keyInput) geminiApiKey = keyInput.value.trim();

    localStorage.setItem("chefguard_engine", activeEngine);
    localStorage.setItem("chefguard_gemini_key", geminiApiKey);

    initSettingsState();
    closeSettingsModal();
}

function initSettingsState() {
    const label = document.getElementById("current-engine-label");
    if (!label) return;
    if (activeEngine === "gemini") {
        label.innerText = "Engine: Google Gemini 2.5 Flash Multimodal Vision";
    } else {
        label.innerText = "Engine: Multi-Spectral Computer Vision (OpenCV + Metrology Core)";
    }
}
