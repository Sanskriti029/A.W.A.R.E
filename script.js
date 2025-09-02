  const hamburger = document.getElementById("hamburger");
  const sidebar = document.getElementById("sidebar");
  const featuresMenu = document.getElementById("featuresMenu");
  const sections = document.querySelectorAll("section");
  const menuItems = document.querySelectorAll(".sidebar ul li");

  // Toggle sidebar
  hamburger.addEventListener("click", () => {
    sidebar.classList.toggle("open");
  });

  // Toggle features submenu
  featuresMenu.addEventListener("click", (e) => {
    if (e.target === featuresMenu) {
      const submenu = featuresMenu.querySelector("ul");
      submenu.style.display = submenu.style.display === "block" ? "none" : "block";
    }
  });

  // Show sections
  function showSection(sectionId) {
    sections.forEach(sec => sec.classList.remove("active"));
    document.getElementById(sectionId)?.classList.add("active");

    menuItems.forEach(item => item.classList.remove("active"));
    const activeItem = [...menuItems].find(li =>
      li.getAttribute("onclick")?.includes(sectionId)
    );
    if (activeItem) activeItem.classList.add("active");
  }

  // ===== AI Classifier =====
  async function classifyImage() {
    const fileInput = document.getElementById("imageUpload");
    const out = document.getElementById("result");
    if (!fileInput.files.length) {
      out.innerText = "Please upload an image.";
      return;
    }
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    out.innerText = "Classifying...";
    try {
      const response = await fetch("/predict", { method: "POST", body: formData });
      const data = await response.json();
      out.innerHTML = response.ok
        ? `Detected Waste Category: <strong>${data.prediction}</strong>`
        : "Error: " + data.error;
    } catch (err) { out.innerText = "Error: " + err.message; }
  }
  document.getElementById("classifyBtn").addEventListener("click", classifyImage);

  // ===== Recycling Guide =====
  function searchMaterial(query) {
    const guideList = document.getElementById("guideList");
    const tips = {
      plastic: "Recycle bottles",
      glass: "Separate by color",
      metal: "Aluminium is recyclable",
      organic: "Compostable",
      paper: "Recycle clean paper",
      battery: "Take to recycling center"
    };
    guideList.innerHTML = "";
    if (query.trim() !== "") {
      Object.keys(tips).forEach(k => {
        if (k.includes(query.toLowerCase())) {
          let li = document.createElement("li");
          li.textContent = k.toUpperCase() + ": " + tips[k];
          guideList.appendChild(li);
        }
      });
    }
  }

  // ===== Soil Analysis =====
  document.getElementById("soilBtn").addEventListener("click", async () => {
    const pH = document.getElementById("pH").value;
    const potash = document.getElementById("potashLevel").value;
    const out = document.getElementById("soilResult");
    if (!pH || !potash) { out.innerText = "Please enter both values."; return; }
    try {
      const res = await fetch("/soil-analysis", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ pH, potashLevel: potash })
      });
      const data = await res.json();
      out.innerText = res.ok ? data.result : "Error: " + data.error;
    } catch (e) { out.innerText = "Error: " + e.message; }
  });

  // ===== Carbon Footprint =====
  document.getElementById("calcBtn").addEventListener("click", async () => {
    const electricity = parseFloat(document.getElementById("electricity").value) || 0;
    const water = parseFloat(document.getElementById("water").value) || 0;
    const transport = parseFloat(document.getElementById("transport").value) || 0;
    const out = document.getElementById("footprintResult");
    try {
      const res = await fetch("/carbon-footprint", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ electricity, water, transport })
      });
      const data = await res.json();
      out.innerText = res.ok
        ? `Estimated Carbon Footprint:\n${data.footprint}`
        : "Error: " + data.error;
    } catch (e) { out.innerText = "Error: " + e.message; }
  });