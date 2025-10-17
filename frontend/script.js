const messagesDiv = document.getElementById("messages");
const textInput = document.getElementById("textInput");
const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const fileStatus = document.getElementById("fileStatus");
const sourceSelect = document.getElementById("sourceSelect");
const configBtn = document.getElementById("configBtn");
const sourceContainer = document.getElementById("sourceContainer");
const sendBtnIcon = document.querySelector(".send-icon i");
 
// Toggle CONFIGURE
configBtn.onclick = () => {
  sourceContainer.classList.toggle("hidden");
};
 
// File upload
uploadBtn.onclick = () => fileInput.click();
 
fileInput.addEventListener("change", () => {
  if (fileInput.files.length > 0) {
    const fileName = fileInput.files[0].name;
    fileStatus.textContent = `✅ ${fileName}`;
  } else {
    fileStatus.textContent = "";
  }
});
 
// Append message to chat
function appendMessage(text, who = "bot", meta = "") {
  const m = document.createElement("div");
  m.className = "msg " + (who === "user" ? "user" : "bot");
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = who === "user" ? "U" : "B";
  const content = document.createElement("div");
  content.className = "content";
  content.innerHTML = text + (meta ? `<div class="small">${meta}</div>` : "");
  m.appendChild(avatar);
  m.appendChild(content);
  messagesDiv.appendChild(m);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
  return m;
}
 
// Send message (click or Enter)
textInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});
sendBtnIcon.parentElement.onclick = () => sendMessage();
 
async function sendMessage() {
  const sources = sourceSelect.value;
  const text = textInput.value.trim();
  const file = fileInput.files[0];
 
  if (!text && !file) {
    alert("Type text or select an image");
    return;
  }
 
  appendMessage(text || "(image uploaded)", "user");
  const pending = appendMessage("Resolving...", "bot");
 
  const form = new FormData();
  form.append("sources", sources);
  form.append("text", text);
  if (file) form.append("file", file);
 
  try {
    const res = await fetch("http://127.0.0.1:5000/api/chat", { method: "POST", body: form });
    const json = await res.json();
    pending.remove();
 
    if (json.error) {
      appendMessage("Error: " + json.error, "bot");
      return;
    }
 
    const sol = json.result.solution || "(no solution found)";
    const src = json.result.source || "Unknown";
    const score = json.score ? ("Score: " + Number(json.score).toFixed(2)) : "";
    const container = appendMessage(`<strong>${json.result.title || ""}</strong><br/>${sol}`, "bot", `Source: ${src} ${score}`);
 
    // feedback
    const fbDiv = document.createElement("div");
    fbDiv.className = "feedback";
    const up = document.createElement("button");
    up.innerText = "👍";
    const down = document.createElement("button");
    down.innerText = "👎";
    fbDiv.appendChild(up); fbDiv.appendChild(down);
    container.querySelector(".content").appendChild(fbDiv);
 
    up.onclick = async () => {
      await sendFeedback(json.query_text, json.result.id, json.result.source, "up");
      up.style.opacity = 0.5;
    };
    down.onclick = async () => {
      await sendFeedback(json.query_text, json.result.id, json.result.source, "down");
      down.style.opacity = 0.5;
    };
 
  } catch (e) {
    pending.remove();
    appendMessage("Failed: " + e.message, "bot");
  }
 
  textInput.value = "";
  fileInput.value = "";
  fileStatus.textContent = "";
}
 
async function sendFeedback(query, result_id, source, fb) {
  await fetch("http://127.0.0.1:5000/api/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query_text: query, result_id, source, feedback: fb }),
  });
}
 
window.addEventListener("DOMContentLoaded", () => {
  appendMessage(
    `Hi, I am AI Resolver Bot! 🤖\nI can troubleshoot by analyzing the error text or image through the knowledge base and SharePoint.\n\nHow can I help you today?`,
    "bot"
  );
});